import socket
import time
import random
from abc import ABC, abstractmethod
from src.utils.logger import TestLogger

NotImplementedErrorMsg = "Subclasses must implement this property."

class AmmeterEmulatorBase(ABC):
    def __init__(self, port: int, chaos_mode: bool = False):
        self.port = port
        self.chaos_mode = chaos_mode
        self.logger = TestLogger(self.__class__.__name__).logger
        random.seed(time.time())  # Seed the random number generator for each instance

    def start_server(self):
        """
        Starts the server to listen for client requests.
        The server will run indefinitely, handling one client request at a time.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Allow the socket to be reused immediately after the program exits
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('localhost', self.port))
            s.listen()
            self.logger.info(f"{self.__class__.__name__} is running on port {self.port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    self.logger.info(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data == self.get_current_command:
                        if self.chaos_mode and random.random() < 0.10:
                            fault = random.choice(['sleep', 'garbage', 'close'])
                            if fault == 'sleep':
                                time.sleep(5) # Delay longer than typical timeout
                                current = self.measure_current()
                                try:
                                    conn.sendall(str(current).encode('utf-8'))
                                except Exception:
                                    pass
                            elif fault == 'garbage':
                                conn.sendall(b'ERR_NO_DATA')
                            elif fault == 'close':
                                # Abruptly close without sending
                                pass
                        else:
                            # Call the specific measure_current() method defined in subclasses
                            current = self.measure_current()
                            conn.sendall(str(current).encode('utf-8'))

    @property
    @abstractmethod
    def get_current_command(self) -> bytes:
        """
        This property must be implemented by each subclass to provide the specific
        command to get the current measurement.
        """
        raise NotImplementedError(NotImplementedErrorMsg)

    @abstractmethod
    def measure_current(self) -> float:
        """
        This method must be implemented by each subclass to provide the specific
        logic for current measurement.
        """
        raise NotImplementedError(NotImplementedErrorMsg)
