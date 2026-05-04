

import time
from typing import Optional
from ..utils.config import load_config
from Ammeters.client import request_current_from_ammeter


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)

    def get_single_reading(self, ammeter_type: str) -> Optional[float]:
        """Fetches a single current reading from the specified ammeter.

        Args:
            ammeter_type: The string identifier of the ammeter (e.g., 'greenlee').

        Returns:
            The current measurement as a float, or None if the request fails.

        Raises:
            ValueError: If the ammeter_type is not defined in the configuration.
        """
        if ammeter_type not in self.config.get('ammeters', {}):
            raise ValueError(f"Unknown ammeter type: {ammeter_type}")

        ammeter_config = self.config['ammeters'][ammeter_type]
        port = ammeter_config['port']
        command = ammeter_config['command'].encode('utf-8')

        return request_current_from_ammeter(port, command)

    def run_test(self, ammeter_type: str) -> dict:
        """Runs a sampling test against the specified ammeter.

        Args:
            ammeter_type: The ammeter identifier (e.g., 'greenlee').

        Returns:
            A dictionary containing the test results and metadata.
        """
        sampling_cfg = self.config.get('testing', {}).get('sampling', {})

        # Parse parameters, fallback to defaults if NULL or missing
        count = sampling_cfg.get('measurements_count')
        duration = sampling_cfg.get('total_duration_seconds')
        frequency = sampling_cfg.get('sampling_frequency_hz')

        freq_val = float(frequency) if frequency and frequency != 'NULL' else 1.0
        delay = 1.0 / freq_val

        limit_by_count = count is not None and count != 'NULL'
        limit_by_duration = duration is not None and duration != 'NULL'

        measurements = []
        start_time = time.time()

        if limit_by_count:
            max_count = int(count)
            for _ in range(max_count):
                val = self.get_single_reading(ammeter_type)
                if val is not None:
                    measurements.append(val)
                # To ensure precise timing, wait the exact delay
                time.sleep(delay)
        elif limit_by_duration:
            max_duration = float(duration)
            while (time.time() - start_time) < max_duration:
                val = self.get_single_reading(ammeter_type)
                if val is not None:
                    measurements.append(val)
                time.sleep(delay)
        else:
            # Default fallback if config is completely empty
            for _ in range(10):
                val = self.get_single_reading(ammeter_type)
                if val is not None:
                    measurements.append(val)
                time.sleep(delay)

        actual_duration = time.time() - start_time

        return {
            "ammeter_type": ammeter_type,
            "measurements": measurements,
            "count": len(measurements),
            "expected_count": count,
            "duration_seconds": actual_duration,
            "sampling_frequency_hz": freq_val
        }