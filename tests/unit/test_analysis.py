import pytest
from src.utils.analysis import calculate_statistics

@pytest.mark.parametrize("measurements, expected", [
    ([1.0, 2.0, 3.0, 4.0, 5.0], {"mean": 3.0, "median": 3.0, "min": 1.0, "max": 5.0, "stdev": 1.5811388, "cv_percentage": 52.7046276, "is_consistent": False}),
    ([10.5], {"mean": 10.5, "median": 10.5, "min": 10.5, "max": 10.5, "stdev": 0.0, "cv_percentage": 0.0, "is_consistent": True}),
    ([-1.0, -2.0, -3.0], {"mean": -2.0, "median": -2.0, "min": -3.0, "max": -1.0, "stdev": 1.0, "cv_percentage": -50.0, "is_consistent": True}),
    ([1e10, 1e-10], {"mean": 5e9, "median": 5e9, "min": 1e-10, "max": 1e10, "stdev": 7071067811.865475, "cv_percentage": 141.421356, "is_consistent": False}),
])
def test_calculate_statistics(measurements, expected):
    stats = calculate_statistics(measurements)
    
    # Check boolean explicitly, then remove before approx to avoid strict type issues
    assert stats["is_consistent"] == expected["is_consistent"]
    del stats["is_consistent"]
    
    expected_floats = {k: v for k, v in expected.items() if k != "is_consistent"}
    assert stats == pytest.approx(expected_floats, rel=1e-5)

def test_calculate_statistics_empty():
    with pytest.raises(ValueError, match="Cannot calculate statistics"):
        calculate_statistics([])
