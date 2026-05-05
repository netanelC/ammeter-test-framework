

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

        # Extract raw configuration values
        count = sampling_cfg.get('measurements_count')
        duration = sampling_cfg.get('total_duration_seconds')
        frequency = sampling_cfg.get('sampling_frequency_hz')

        # Calculate the delay between samples based on the target frequency
        freq_val = float(frequency) if frequency and frequency != 'NULL' else 1.0
        delay = 1.0 / freq_val

        # Determine which constraints have been explicitly configured
        limit_by_count = count is not None and count != 'NULL'
        limit_by_duration = duration is not None and duration != 'NULL'

        # Enforce that the test is bounded by at least one constraint to prevent infinite loops
        if not limit_by_count and not limit_by_duration:
            raise ValueError("Both measurements_count and total_duration_seconds are missing or NULL. At least one must be provided.")

        # Convert limits to infinity if they are not configured, so the while loop ignores them
        max_count = int(count) if limit_by_count else float('inf')
        max_duration = float(duration) if limit_by_duration else float('inf')

        measurements = []
        start_time = time.time()

        # The loop terminates when the *earliest* condition is met (either max count or max duration)
        while len(measurements) < max_count and (time.time() - start_time) < max_duration:
            val = self.get_single_reading(ammeter_type)
            if val is not None:
                measurements.append(val)
            
            # Prevent an unnecessary trailing sleep delay if we've just hit the exact count limit
            if len(measurements) >= max_count:
                break
                
            # Wait for the next sampling cycle to maintain the requested frequency
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