"""
Protocol module for client-server communication
"""

import socket

MAX_MSG_LENGTH_SIZE = 1024

def send(sock, msg):
    """
    שולח הודעה - תומך גם ב-string וגם ב-bytes
    """
    # אם זה string, ממיר רווחים ל-#
    if isinstance(msg, str):
        msg = msg.replace(" ", "#").encode()
    elif isinstance(msg, bytes):
        # אם זה bytes (כמו תמונה), שולח ישירות
        pass
    else:
        raise TypeError("msg must be str or bytes")

    if len(msg) > 10**MAX_MSG_LENGTH_SIZE - 1:
        raise Exception("Message too big")

    # שליחת האורך
    msg_length = str(len(msg)).zfill(MAX_MSG_LENGTH_SIZE)
    sock.sendall(msg_length.encode())

    # שליחת ההודעה
    sock.sendall(msg)

def recv(sock):
    """
    מקבל הודעה
    """
    # קבלת האורך
    msg_length_str = recv_all(sock, MAX_MSG_LENGTH_SIZE)
    if not msg_length_str:
        return None

    msg_length = int(msg_length_str.decode())

    # קבלת ההודעה
    msg = recv_all(sock, msg_length)
    if not msg:
        return None

    # אם זה טקסט - מפצל לפי #
    try:
        return msg.decode().split("#")
    except UnicodeDecodeError:
        # אם זה bytes (תמונה) - מחזיר ישירות
        return [msg]

def recv_all(sock, n):
    """מקבל בדיוק n בתים - פונקציה פנימית"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data