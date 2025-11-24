"""
TCP Server - Remote Control
Author: Gilad Elran
Date: 11/11/2025

Supported Commands:
- DIR <path>: List files in directory
- DELETE <file>: Delete a file
- COPY <src> <dst>: Copy a file
- EXECUTE <program>: Execute a program
- SCREENSHOT_TAKE: Take a screenshot
- PHOTO_SEND: Send screenshot to client
- EXIT: Close connection
"""

import socket
import glob
import os
import shutil
import subprocess
import pyautogui
import logging
import protocol

# Configuration
HOST = '0.0.0.0'
PORT = 1729

# Logging setup
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ==========================================
# Server Functions
# ==========================================

def look_for_dir(location):
    """
    מחזיר רשימת קבצים בתיקייה

    Args:
        location: נתיב לתיקייה או pattern

    Returns:
        (True, list): הצלחה ורשימת קבצים
        (False, []): כשלון
    """
    try:
        # אם זו תיקייה, נוסיף * אוטומטית
        if os.path.isdir(location):
            location = os.path.join(location, '*')

        all_items = glob.glob(location)
        # סינון - רק קבצים
        files = [f for f in all_items if os.path.isfile(f)]

        logging.info(f"DIR: {location} → {len(files)} files")
        return True, files
    except Exception as e:
        logging.error(f"DIR failed: {e}")
        return False, []


def delete(file_path):
    """
    מוחק קובץ

    Args:
        file_path: נתיב לקובץ

    Returns:
        bool: הצלחה/כשלון
    """
    try:
        os.remove(file_path)
        logging.info(f"DELETE: {file_path}")
        return True
    except Exception as e:
        logging.error(f"DELETE failed: {e}")
        return False


def copy(src, dst):
    """
    מעתיק קובץ

    Args:
        src: קובץ מקור
        dst: קובץ יעד

    Returns:
        bool: הצלחה/כשלון
    """
    try:
        shutil.copy(src, dst)
        logging.info(f"COPY: {src} → {dst}")
        return True
    except Exception as e:
        logging.error(f"COPY failed: {e}")
        return False


def execute(program):
    """
    מריץ תוכנית

    Args:
        program: נתיב לתוכנית

    Returns:
        bool: הצלחה/כשלון
    """
    try:
        subprocess.call(program)
        logging.info(f"EXECUTE: {program}")
        return True
    except Exception as e:
        logging.error(f"EXECUTE failed: {e}")
        return False


def take_screenshot():
    """
    צולם מסך ושומר כ-screen.jpg

    Returns:
        bool: הצלחה/כשלון
    """
    try:
        pyautogui.screenshot().save("screen.jpg")
        logging.info("Screenshot taken")
        return True
    except Exception as e:
        logging.error(f"Screenshot failed: {e}")
        return False


def send_screenshot():
    """
    קורא את screen.jpg ומחזיר את הנתונים

    Returns:
        (True, bytes): הצלחה ונתוני התמונה
        (False, None): כשלון
    """
    try:
        with open("screen.jpg", "rb") as f:
            data = f.read()
        logging.info(f"Screenshot ready: {len(data)} bytes")
        return True, data
    except Exception as e:
        logging.error(f"Send screenshot failed: {e}")
        return False, None


# ==========================================
# Client Handler
# ==========================================

def handle_client(client, addr):
    """
    מטפל בלקוח בודד

    Args:
        client: socket של הלקוח
        addr: כתובת הלקוח
    """
    while True:
        try:
            # קבלת פקודה
            msg = protocol.recv(client)
            if msg is None:
                logging.info(f"Client {addr} disconnected")
                break

            cmd = msg[0].upper()
            args = msg[1:]

            logging.info(f"[{addr}] Command: {cmd} {args}")

            # ביצוע פקודות
            if cmd == "DIR" and args:
                success, files = look_for_dir(args[0])
                protocol.send(client, str(success))
                if success:
                    file_list = '\n'.join(files) if files else "No files"
                    protocol.send(client, file_list)

            elif cmd == "DELETE" and args:
                success = delete(args[0])
                protocol.send(client, str(success))

            elif cmd == "COPY" and len(args) >= 2:
                success = copy(args[0], args[1])
                protocol.send(client, str(success))

            elif cmd == "EXECUTE" and args:
                success = execute(args[0])
                protocol.send(client, str(success))

            elif cmd == "TAKE_SCREENSHOT":
                success = take_screenshot()
                protocol.send(client, str(success))

            elif cmd == "PHOTO_SEND":
                success, data = send_screenshot()
                protocol.send(client, str(success))
                if success and data:
                    protocol.send(client, data)

            elif cmd == "EXIT":
                protocol.send(client, "True")
                logging.info(f"Client {addr} requested exit")
                break

            else:
                logging.warning(f"Unknown command: {cmd}")
                protocol.send(client, "False")

        except Exception as e:
            logging.error(f"Handler error: {e}")
            try:
                protocol.send(client, "False")
            except:
                break

    client.close()
    print(f"Client {addr} disconnected")


# ==========================================
# Main Server Loop
# ==========================================

def main():
    """
    לולאת השרת הראשית
    """
    # יצירת socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"Server running on {HOST}:{PORT}")
        logging.info("Server started")

        while True:
            try:
                print("Waiting for client...")
                client, addr = server_socket.accept()
                print(f"✓ Client connected: {addr}")
                logging.info(f"Client connected: {addr}")

                handle_client(client, addr)

            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down server...")
                break
            except Exception as e:
                logging.error(f"Accept error: {e}")
                print(f"Error: {e}")

    finally:
        server_socket.close()
        logging.info("Server closed")
        print("Server stopped")


if __name__ == "__main__":
    
    
    # Demi-files for asserts
    #---------------------
    with open("test_src.txt", "w") as f:
         f.write("hello")
    with open("test_src2.txt", "w") as f:
        f.write("data")
    #---------------------


    # Dir assertation
    # ---------------------
    success, files = look_for_dir(".")
    assert success is True, "Assertation FAILED"
    # ---------------------

    # Copy assertation
    # ---------------------
    assert copy("test_src2.txt", "test_dst2.txt") is True, "Assertation FAILED"
    # ---------------------


    # Delete assertation
    #-------------------
    assert delete("test_dst2.txt") is True, "Assertation FAILED"
    assert delete("test_src2.txt") is True, "Assertation FAILED"
    assert delete("test_src.txt") is True, "Assertation FAILED"
    # -------------------

    #Take_screenshot assertation
    # -------------------
    assert take_screenshot() is True, "Assertation FAILED"
    # -------------------

    logging.info("All assert tests passed")
    main()
