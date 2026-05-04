from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

def request_current_from_ammeter(port: int, command: bytes) -> Optional[float]:
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)
        if data:
            current = data.decode('utf-8')
            print(f"Received current measurement from port {port}: {current} A")
            return float(current)
        else:
            print("No data received.")
            return None

