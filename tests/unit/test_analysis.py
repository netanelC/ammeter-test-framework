import pytest
from src.utils.analysis import calculate_statistics

@pytest.mark.parametrize("measurements, expected", [
    ([1.0, 2.0, 3.0, 4.0, 5.0], {"mean": 3.0, "median": 3.0, "min": 1.0, "max": 5.0, "stdev": 1.5811388}),
    ([10.5], {"mean": 10.5, "median": 10.5, "min": 10.5, "max": 10.5, "stdev": 0.0}),
    ([-1.0, -2.0, -3.0], {"mean": -2.0, "median": -2.0, "min": -3.0, "max": -1.0, "stdev": 1.0}),
    ([1e10, 1e-10], {"mean": 5e9, "median": 5e9, "min": 1e-10, "max": 1e10, "stdev": 7071067811.865475}),
])
def test_calculate_statistics(measurements, expected):
    stats = calculate_statistics(measurements)
    assert stats == pytest.approx(expected, rel=1e-5)

def test_calculate_statistics_empty():
    with pytest.raises(ValueError, match="Cannot calculate statistics"):
        calculate_statistics([])
