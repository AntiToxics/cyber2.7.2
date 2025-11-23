"""
TCP Client - Remote Control
Author: Gilad Elran
Date: 11/11/2025

Commands:
- dir <path>: List files
- delete <file>: Delete file
- copy <src> <dst>: Copy file
- execute <program>: Run program
- screenshot_take: Take screenshot
- photo_send: Download screenshot
- exit: Disconnect
"""

import socket
import logging
import protocol

# Configuration
HOST = '127.0.0.1'
PORT = 1729

# Logging setup
logging.basicConfig(
    filename='client.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Valid Commands and Arguments
VALID_COMMANDS = {
    "DIR": 1,  # Requires 1 argument (path)
    "DELETE": 1,  # Requires 1 argument (file)
    "COPY": 2,  # Requires 2 arguments (src, dst)
    "EXECUTE": 1,  # Requires 1 argument (program)
    "SCREENSHOT_TAKE": 0,  # No arguments
    "PHOTO_SEND": 0,  # No arguments
    "EXIT": 0  # No arguments
}


# ==========================================
# Validation
# ==========================================

def validate_command(cmd_input):
    """
    בודק תקינות הפקודה לפני שליחה

    Args:
        cmd_input: הפקודה שהוקלדה

    Returns:
        (True, ""): תקין
        (False, "error message"): לא תקין
    """
    parts = cmd_input.split()

    if len(parts) == 0:
        return False, "Empty command"

    cmd = parts[0].upper()
    args = parts[1:]

    # בדיקת פקודה קיימת
    if cmd not in VALID_COMMANDS:
        valid_cmds = ', '.join(VALID_COMMANDS.keys())
        return False, f"Unknown command: {cmd}\nValid commands: {valid_cmds}"

    # בדיקת מספר ארגומנטים
    expected = VALID_COMMANDS[cmd]
    actual = len(args)

    if actual < expected:
        return False, f"{cmd} requires {expected} argument(s), got {actual}"

    if actual > expected and expected == 0:
        return False, f"{cmd} doesn't take arguments"
    if actual > expected and expected >0:
        return False, f"{cmd} requires {expected} argument(s), got {actual}"
    return True, ""


# ==========================================
# Main Client
# ==========================================

def main():
    """
    לולאת הלקוח הראשית
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # חיבור לשרת
    try:
        client_socket.connect((HOST, PORT))
        print(f"✓ Connected to server at {HOST}:{PORT}")
        print(f"Type 'exit' to disconnect\n")
        logging.info(f"Connected to server at {HOST}:{PORT}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        logging.error(f"Connection failed: {e}")
        return

    # לולאת פקודות
    while True:
        # קלט מהמשתמש
        cmd = input(">>> ").strip()
        if not cmd:
            continue

        # ✅ VALIDATION
        valid, error = validate_command(cmd)
        if not valid:
            print(f"❌ {error}")
            logging.warning(f"Invalid command: {cmd} - {error}")
            continue

        # שליחת פקודה
        try:
            protocol.send(client_socket, cmd)
            logging.info(f"Sent command: {cmd}")
        except Exception as e:
            print(f"❌ Send error: {e}")
            logging.error(f"Send error: {e}")
            break

        # קבלת תשובה
        try:
            result = protocol.recv(client_socket)
            if result is None:
                print("❌ Server closed connection")
                logging.warning("Server closed connection")
                break

            success = result[0] == "True"
            command = cmd.split()[0].upper()

            # הדפסת תוצאה
            if success:
                print(f"✓ {command} succeeded")
                logging.info(f"{command} succeeded")
            else:
                print(f"✗ {command} failed")
                logging.warning(f"{command} failed")

            # טיפול בפקודות מיוחדות

            # DIR - הצגת קבצים
            if success and command == "DIR":
                files = protocol.recv(client_socket)
                if files and files[0]:
                    print("\n📁 Files:")
                    print(files[0])
                    print()
                    logging.info(f"Received {len(files[0].split())} files")

            # PHOTO_SEND - שמירת תמונה
            if success and command == "PHOTO_SEND":
                img_result = protocol.recv(client_socket)
                if img_result and img_result[0]:
                    img_data = img_result[0]

                    # שמירה לקובץ
                    try:
                        with open("received_screen.jpg", "wb") as f:
                            f.write(img_data)
                        print(f"✓ Screenshot saved ({len(img_data):,} bytes)")
                        logging.info(f"Screenshot saved: {len(img_data)} bytes")
                    except Exception as e:
                        print(f"❌ Failed to save screenshot: {e}")
                        logging.error(f"Failed to save screenshot: {e}")

            # EXIT - ניתוק
            if command == "EXIT":
                print("👋 Disconnecting...")
                logging.info("User disconnected")
                break

        except Exception as e:
            print(f"❌ Receive error: {e}")
            logging.error(f"Receive error: {e}")
            break

    # סגירה
    client_socket.close()
    print("✓ Disconnected")
    logging.info("Connection closed")


if __name__ == "__main__":
    main()
