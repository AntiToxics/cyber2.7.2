"""
Protocol module for client-server communication
פורמט: LENGTH#MESSAGE
"""

import socket

def send(sock, msg):
    """
    שולח הודעה בפורמט: LENGTH#MESSAGE
    דוגמה: "7#dir C:\\"
    """
    # אם זה string, ממיר רווחים ל-@ (כי # תפוס!)
    if isinstance(msg, str):
        msg = msg.replace(" ", "@").encode()
    elif isinstance(msg, bytes):
        pass
    else:
        raise TypeError("msg must be str or bytes")

    # יצירת ההודעה: "LENGTH#MESSAGE"
    length = len(msg)
    full_msg = f"{length}#".encode() + msg

    sock.sendall(full_msg)

def recv(sock):
    """
    מקבל הודעה בפורמט: LENGTH#MESSAGE
    קורא בייט בייט עד # כדי לדעת את האורך
    """
    # שלב 1: קריאת האורך (עד #)
    length_str = b''
    while True:
        byte = sock.recv(1)  # קורא בייט אחד
        if not byte:
            return None  # החיבור נסגר

        if byte == b'#':
            break  # מצאנו את ה-#, סיימנו לקרוא את האורך

        length_str += byte

    # המרת האורך למספר
    try:
        length = int(length_str.decode())
    except ValueError:
        return None

    # שלב 2: קריאת ההודעה עצמה
    msg = recv_all(sock, length)
    if not msg:
        return None

    # ניסיון לפענח כטקסט
    try:
        decoded = msg.decode()
        return decoded.split("@")  # מפצל לפי @ (שהיה רווח)
    except UnicodeDecodeError:
        # אם זה bytes (תמונה)
        return [msg]

def recv_all(sock, n):
    """מקבל בדיוק n בתים"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
