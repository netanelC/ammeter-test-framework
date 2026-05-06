

import time
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
import typing
from ..utils.config import load_config
from ..utils.analysis import calculate_statistics
from ..utils.visualization import generate_simple_plot
from Ammeters.client import request_current_from_ammeter
from ..utils.logger import TestLogger

logger = TestLogger("AmmeterTestFramework").logger

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

        # Helper to convert 'NULL' string or None to real Python None
        def normalize(val):
            return None if val is None or val == 'NULL' else val

        count = normalize(sampling_cfg.get('measurements_count'))
        duration = normalize(sampling_cfg.get('total_duration_seconds'))
        frequency = normalize(sampling_cfg.get('sampling_frequency_hz'))

        # Calculate the delay between samples based on the target frequency
        freq_val = float(frequency) if frequency is not None else 1.0
        delay = 1.0 / freq_val

        if count is None and duration is None:
            raise ValueError("Both measurements_count and total_duration_seconds are missing. At least one must be provided.")

        # Convert limits to infinity if they are not configured, so the while loop ignores them
        max_count = int(count) if count is not None else float('inf')
        max_duration = float(duration) if duration is not None else float('inf')

        measurements: typing.List[float] = []
        start_time = time.time()

        # The loop terminates when the *earliest* condition is met (either max count or max duration)
        while len(measurements) < max_count and (time.time() - start_time) < max_duration:
            val = self.get_single_reading(ammeter_type)
            if val is not None:
                measurements.append(val)
                logger.debug(f"Captured reading: {val}")
            
            # Prevent an unnecessary trailing sleep delay if we've just hit the exact count limit
            if len(measurements) >= max_count:
                break
            # Wait for the next sampling cycle to maintain the requested frequency
            time.sleep(delay)

        actual_duration = time.time() - start_time
        logger.info(f"Test run completed for {ammeter_type}. Collected {len(measurements)} samples.")

        result = {
            "ammeter_type": ammeter_type,
            "measurements": measurements,
            "count": len(measurements),
            "expected_count": count,
            "duration_seconds": actual_duration,
            "sampling_frequency_hz": freq_val
        }

        return self._process_results(result)

    def _process_results(self, result: dict) -> dict:
        """Helper method to handle statistical calculations, visualization, and JSON archiving."""
        analysis_cfg = self.config.get('analysis', {})
        measurements: typing.List[float] = result.get('measurements', [])
        
        if analysis_cfg.get('statistical_metrics'):
            result['statistics'] = calculate_statistics(measurements)

        output_dir = Path(self.config.get('result_management', {}).get('output_dir', 'results'))

        vis_cfg = analysis_cfg.get('visualization', {})
        if vis_cfg.get('enabled'):
            stats = result.get('statistics')
            plot_path = generate_simple_plot(
                ammeter_type=result['ammeter_type'], 
                measurements=measurements, 
                output_dir=str(output_dir),
                stats=stats
            )
            if plot_path:
                result['plot_path'] = plot_path

        output_dir.mkdir(parents=True, exist_ok=True)
        test_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result['test_id'] = test_id
        result['timestamp'] = timestamp
        
        json_filename = f"{result['ammeter_type']}_{timestamp}_{test_id[:8]}.json"
        json_filepath = output_dir / json_filename
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        result['archive_path'] = str(json_filepath)
        logger.info(f"Results archived to {json_filepath}")

        return result
