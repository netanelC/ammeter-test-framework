import pytest
from src.utils.accuracy import evaluate_accuracy

def test_evaluate_accuracy_success():
    results = {
        "device1": {
            "measurements": [1.0, 2.0, 3.0],
            "statistics": {
                "mean": 2.0,
                "cv_percentage": 50.0
            }
        },
        "device2": {
            "measurements": [2.5, 3.0, 3.5],
            "statistics": {
                "mean": 3.0,
                "cv_percentage": 10.0
            }
        },
        "device3": {
            "measurements": [0.5, 1.0, 1.5],
            "statistics": {
                "mean": 1.0,
                "cv_percentage": 100.0
            }
        }
    }
    
    evaluation = evaluate_accuracy(results)
    
    # All measurements: [1.0, 2.0, 3.0, 2.5, 3.0, 3.5, 0.5, 1.0, 1.5]
    # Sum: 18.0, Count: 9, Ensemble Mean: 2.0
    assert evaluation["ensemble_mean"] == pytest.approx(2.0, rel=1e-5)
    
    # Abs Error = |Mean - Ensemble Mean|
    # device1: |2.0 - 2.0| = 0.0 -> Most Accurate
    # device2: |3.0 - 2.0| = 1.0
    # device3: |1.0 - 2.0| = 1.0
    assert evaluation["metrics"]["device1"]["abs_error"] == 0.0
    assert evaluation["metrics"]["device2"]["abs_error"] == 1.0
    assert evaluation["metrics"]["device3"]["abs_error"] == 1.0
    
    assert evaluation["most_accurate"] == "device1"
    
    # Lowest CV is device2 (10.0) -> Most Precise
    assert evaluation["most_precise"] == "device2"

def test_evaluate_accuracy_empty_results():
    with pytest.raises(ValueError, match="Cannot evaluate accuracy with empty results"):
        evaluate_accuracy({})

def test_evaluate_accuracy_no_measurements():
    results = {
        "device1": {"measurements": []},
        "device2": {"measurements": []}
    }
    with pytest.raises(ValueError, match="No measurements found across any ammeter results"):
        evaluate_accuracy(results)
