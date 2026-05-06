import statistics
from typing import Dict, Any, List

def evaluate_accuracy(results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates the relative accuracy and precision of multiple ammeters based on their test results.
    
    Args:
        results: A dictionary where keys are ammeter types and values are test result dictionaries
                 (containing 'measurements' and optionally 'statistics').
                 
    Returns:
        A dictionary containing the ensemble mean, individual metrics, and identified winners.
    """
    if not results:
        raise ValueError("Cannot evaluate accuracy with empty results.")

    # Data Aggregation
    all_measurements: List[float] = []
    for data in results.values():
        measurements = data.get('measurements', [])
        all_measurements.extend(measurements)

    if not all_measurements:
        raise ValueError("No measurements found across any ammeter results.")

    ensemble_mean = statistics.mean(all_measurements)

    # Relative Accuracy Calculation
    metrics: Dict[str, Dict[str, float]] = {}
    for ammeter_type, data in results.items():
        stats = data.get('statistics', {})
        ammeter_mean = stats.get('mean', 0.0)
        cv_percentage = stats.get('cv_percentage', float('inf'))
        
        abs_error = abs(ammeter_mean - ensemble_mean)
        
        metrics[ammeter_type] = {
            'mean': ammeter_mean,
            'abs_error': abs_error,
            'cv_percentage': cv_percentage
        }

    # Scoring & Identification
    most_accurate = min(metrics.keys(), key=lambda k: metrics[k]['abs_error'])
    most_precise = min(metrics.keys(), key=lambda k: metrics[k]['cv_percentage'])

    return {
        "ensemble_mean": ensemble_mean,
        "metrics": metrics,
        "most_accurate": most_accurate,
        "most_precise": most_precise
    }
