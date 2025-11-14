"""
Author: Gilad Elran
Program name: server.py
Description: TCP server
"""

import socket
import glob
import os
import shutil
import subprocess
import pyautogui
import logging
import protocol

HOST = '0.0.0.0'
PORT = 1729

logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def look_for_dir(location):
    try:
        if os.path.isdir(location):
            location = os.path.join(location, '*')

        all_items = glob.glob(location)
        files = [f for f in all_items if os.path.isfile(f)]

        logging.info(f"DIR: {location} -> {len(files)} files")
        return True, files
    except Exception as e:
        logging.error(f"DIR failed: {e}")
        return False, []

def delete(file_path):
    try:
        os.remove(file_path)
        logging.info(f"DELETE: {file_path}")
        return True
    except Exception as e:
        logging.error(f"DELETE failed: {e}")
        return False

def copy(src, dst):
    try:
        shutil.copy(src, dst)
        logging.info(f"COPY: {src} -> {dst}")
        return True
    except Exception as e:
        logging.error(f"COPY failed: {e}")
        return False

def execute(program):
    try:
        subprocess.call(program)
        logging.info(f"EXECUTE: {program}")
        return True
    except Exception as e:
        logging.error(f"EXECUTE failed: {e}")
        return False

def take_screenshot():
    try:
        pyautogui.screenshot().save("screen.jpg")
        logging.info("Screenshot taken")
        return True
    except Exception as e:
        logging.error(f"Screenshot failed: {e}")
        return False

def send_screenshot():
    try:
        with open("screen.jpg", "rb") as f:
            return True, f.read()
    except Exception as e:
        logging.error(f"Send screenshot failed: {e}")
        return False, None

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"Server running on {HOST}:{PORT}")
    logging.info("Server started")

    while True:
        try:
            print("Waiting for client...")
            client, addr = server_socket.accept()
            print(f"Client connected: {addr}")
            logging.info(f"Client: {addr}")

            handle_client(client, addr)

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            logging.error(f"Error: {e}")

    server_socket.close()

def handle_client(client, addr):
    while True:
        try:
            msg = protocol.recv(client)
            if msg is None:
                break

            cmd = msg[0].upper()
            args = msg[1:]

            logging.info(f"Command: {cmd} {args}")

            if cmd == "DIR" and args:
                success, files = look_for_dir(args[0])
                protocol.send(client, str(success))
                if success:
                    protocol.send(client, '\n'.join(files) if files else "No files")

            elif cmd == "DELETE" and args:
                success = delete(args[0])
                protocol.send(client, str(success))

            elif cmd == "COPY" and len(args) >= 2:
                success = copy(args[0], args[1])
                protocol.send(client, str(success))

            elif cmd == "EXECUTE" and args:
                success = execute(args[0])
                protocol.send(client, str(success))

            elif cmd == "SCREENSHOT_TAKE":
                success = take_screenshot()
                protocol.send(client, str(success))

            elif cmd == "PHOTO_SEND":
                success, data = send_screenshot()
                protocol.send(client, str(success))
                if success:
                    protocol.send(client, data)  # ← הכל דרך הפרוטוקול!

            elif cmd == "EXIT":
                protocol.send(client, "True")
                logging.info(f"Client {addr} exit")
                break

            else:
                protocol.send(client, "False")

        except Exception as e:
            logging.error(f"Handler error: {e}")
            try:
                protocol.send(client, "False")
            except:
                break

    client.close()
    print(f"Client {addr} disconnected")

if __name__ == "__main__":
    main()