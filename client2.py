"""
Author: Gilad Elran
Program name: client.py
Description: Simple TCP client
"""

import socket
import protocol

HOST = '127.0.0.1'
PORT = 1729

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")

    while True:
        cmd = input("\nEnter command: ").strip()
        if not cmd:
            continue

        protocol.send(client_socket, cmd)

        result = protocol.recv(client_socket)
        if result is None:
            print("Server closed connection")
            break

        success = result[0] == "True"
        command = cmd.split()[0].upper()

        print(f"Command {command} {'succeeded' if success else 'failed'}")

        # DIR
        if success and command == "DIR":
            files = protocol.recv(client_socket)
            if files and files[0]:
                print("\nFiles:")
                print(files[0])

        # PHOTO_SEND
        if success and command == "PHOTO_SEND":
            img_result = protocol.recv(client_socket)  # ← הכל דרך הפרוטוקול!
            if img_result and img_result[0]:
                img_data = img_result[0]  # bytes
                print(f"Received {len(img_data)} bytes")

                with open("received_screen.jpg", "wb") as f:
                    f.write(img_data)
                print("Screenshot saved")

        if command == "EXIT":
            break

    client_socket.close()

if __name__ == "__main__":
    main()