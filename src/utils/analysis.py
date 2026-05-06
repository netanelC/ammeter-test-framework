import statistics
from typing import Dict, List

def calculate_statistics(measurements: List[float]) -> Dict[str, float]:
    """Calculates statistical metrics for a given list of measurements."""
    if not measurements:
        raise ValueError("Cannot calculate statistics on an empty list. Please increase the measurement count or duration to collect data.")
    
    return {
        "mean": statistics.mean(measurements),
        "median": statistics.median(measurements),
        "min": min(measurements),
        "max": max(measurements),
        "stdev": statistics.stdev(measurements) if len(measurements) > 1 else 0.0
    }
