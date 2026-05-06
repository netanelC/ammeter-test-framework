import threading
import time
import socket

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.client import request_current_from_ammeter
from src.utils.config import load_config
from src.utils.logger import TestLogger

logger = TestLogger("Main").logger

def run_greenlee_emulator(port: int, chaos_mode: bool = False):
    greenlee = GreenleeAmmeter(port, chaos_mode=chaos_mode)
    greenlee.start_server()

def run_entes_emulator(port: int, chaos_mode: bool = False):
    entes = EntesAmmeter(port, chaos_mode=chaos_mode)
    entes.start_server()

def run_circutor_emulator(port: int, chaos_mode: bool = False):
    circutor = CircutorAmmeter(port, chaos_mode=chaos_mode)
    circutor.start_server()

def wait_for_port(port: int, timeout: int = 5):
    """Wait until a port is bound and listening before proceeding."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(0.1)
    return False

def start_emulators(config: dict):
    chaos_mode = config.get("testing", {}).get("error_simulation", False)
    
    greenlee_cfg = config.get("ammeters", {}).get("greenlee", {})
    entes_cfg = config.get("ammeters", {}).get("entes", {})
    circutor_cfg = config.get("ammeters", {}).get("circutor", {})
    
    # Start each ammeter in a separate thread
    threading.Thread(target=run_greenlee_emulator, args=(greenlee_cfg.get('port', 5000), chaos_mode), daemon=True).start()
    threading.Thread(target=run_entes_emulator, args=(entes_cfg.get('port', 5001), chaos_mode), daemon=True).start()
    threading.Thread(target=run_circutor_emulator, args=(circutor_cfg.get('port', 5002), chaos_mode), daemon=True).start()
    
    # Robustly wait for the servers to start
    ports_to_wait = [greenlee_cfg.get('port', 5000), entes_cfg.get('port', 5001), circutor_cfg.get('port', 5002)]
    for port in ports_to_wait:
        if not wait_for_port(port):
            logger.warning(f"Timeout waiting for emulator on port {port} to start.")

if __name__ == "__main__":
    config = load_config("config/config.yaml")
    chaos_mode = config.get("testing", {}).get("error_simulation", False)
    
    logger.info(f"Starting ammeter emulators... (Chaos Mode: {chaos_mode})")
    start_emulators(config)

    # Request an initial reading just to verify connection dynamically
    logger.info("Verifying connections...")
    for name, cfg in config.get("ammeters", {}).items():
        port = cfg.get("port")
        command = cfg.get("command", "").encode("utf-8")
        if port and command:
            request_current_from_ammeter(port, command)

    logger.info("Emulators are running in the background. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive indefinitely so the daemon threads (emulators) stay up
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down emulators.")
        pass
