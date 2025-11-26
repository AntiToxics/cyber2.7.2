"""
Protocol.py
Author: Gilad Elran
Date: 11/11/2025
Description:
This module defines a simple custom protocol for sending and receiving
messages over a TCP connection. Each message follows the format:

    length#cmd@args
"""



def send(sock, msg):
    """
    שולח הודעה בפורמט: LENGTH#CMD@ARGS
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
    מקבל הודעה בפורמט: LENGTH#CMD@ARGS
    קורא בייט בייט עד # כדי לדעת את האורך
    מחזירה את ההודעה כ list כצורתו המקורית
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
    """
    מקבל בדיוק n בתים
    מוודא שהכל נקלט

    מחזיר את ההודעה כפורמט: CMD@ARGS (bytes)
    """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
