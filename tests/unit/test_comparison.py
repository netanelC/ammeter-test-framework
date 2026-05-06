import json
import pytest
from src.utils.comparison import compare_historical_runs

@pytest.fixture
def create_mock_run(tmp_path):
    """Helper to create a mock JSON result file with the correct naming convention."""
    def _create(test_id, ammeter_type="greenlee", stats=None):
        data = {
            "test_id": test_id,
            "ammeter_type": ammeter_type,
            "count": 10,
            "duration_seconds": 5.0,
        }
        if stats is not None:
            data["statistics"] = stats
            
        # Mimic the real filename structure: {type}_{timestamp}_{id}.json
        file_name = f"{ammeter_type}_20260506_120000_{test_id}.json"
        file_path = tmp_path / file_name
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return str(file_path)
    return _create

def test_compare_historical_runs_happy_path(create_mock_run):
    stats = {"mean": 0.5, "max": 1.0}
    path1 = create_mock_run("id1", "greenlee", stats)
    path2 = create_mock_run("id2", "greenlee", stats)
    
    data = compare_historical_runs(path1, path2)
    
    assert data["run1"]["ammeter"] == "greenlee"
    assert data["run1"]["mean"] == 0.5
    assert data["run2"]["mean"] == 0.5

def test_compare_historical_runs_file_not_found():
    with pytest.raises(FileNotFoundError):
        compare_historical_runs("non_existent_1.json", "non_existent_2.json")

def test_compare_historical_runs_missing_stats(create_mock_run):
    path1 = create_mock_run("id1", "greenlee", stats=None)
    path2 = create_mock_run("id2", "greenlee", stats=None)
    
    data = compare_historical_runs(path1, path2)
    
    assert data["run1"]["mean"] is None
    assert data["run2"]["mean"] is None
