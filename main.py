import threading
import time

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.client import request_current_from_ammeter


def run_greenlee_emulator():
    greenlee = GreenleeAmmeter(5000)
    greenlee.start_server()

def run_entes_emulator():
    entes = EntesAmmeter(5001)
    entes.start_server()

def run_circutor_emulator():
    circutor = CircutorAmmeter(5002)
    circutor.start_server()

def start_emulators():
    # Start each ammeter in a separate thread
    threading.Thread(target=run_greenlee_emulator, daemon=True).start()
    threading.Thread(target=run_entes_emulator, daemon=True).start()
    threading.Thread(target=run_circutor_emulator, daemon=True).start()
    
    # Wait for the servers to start, if you have problem restarting the servers between runs try increasing sleep time.
    time.sleep(5)

if __name__ == "__main__":
    print("Starting ammeter emulators...")
    start_emulators()

    # Request an initial reading just to verify connection
    request_current_from_ammeter(5000, b'MEASURE_GREENLEE -get_measurement')
    request_current_from_ammeter(5001, b'MEASURE_ENTES -get_data')
    request_current_from_ammeter(5002, b'MEASURE_CIRCUTOR -get_measurement')

    print("\nEmulators are running in the background. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive indefinitely so the daemon threads (emulators) stay up
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down emulators.")
        pass
