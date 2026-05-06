import statistics
from typing import Dict, List, Any

def calculate_statistics(measurements: List[float], cv_threshold: float = 5.0) -> Dict[str, Any]:
    """Calculates statistical metrics for a given list of measurements."""
    if not measurements:
        raise ValueError("Cannot calculate statistics on an empty list. Please increase the measurement count or duration to collect data.")
    
    mean_val = statistics.mean(measurements)
    stdev_val = statistics.stdev(measurements) if len(measurements) > 1 else 0.0
    
    cv_percentage = (stdev_val / mean_val * 100) if mean_val != 0 else 0.0
    is_consistent = cv_percentage <= cv_threshold
    
    return {
        "mean": mean_val,
        "median": statistics.median(measurements),
        "min": min(measurements),
        "max": max(measurements),
        "stdev": stdev_val,
        "cv_percentage": cv_percentage,
        "is_consistent": is_consistent
    }
