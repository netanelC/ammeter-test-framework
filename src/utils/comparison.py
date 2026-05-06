import json
from pathlib import Path
from typing import Dict, Any

def compare_historical_runs(file_path_1: str, file_path_2: str) -> Dict[str, Any]:
    """Compares two historical test runs side-by-side using their file paths.

    Args:
        file_path_1: Path to the first JSON result file.
        file_path_2: Path to the second JSON result file.

    Returns:
        A dictionary containing the parsed run data for comparison.

    Raises:
        FileNotFoundError: If either file does not exist.
        json.JSONDecodeError: If either file contains invalid JSON.
    """
    path1 = Path(file_path_1)
    path2 = Path(file_path_2)

    if not path1.exists() or not path2.exists():
        raise FileNotFoundError("One or both historical run files not found.")

    with path1.open('r', encoding='utf-8') as f1, path2.open('r', encoding='utf-8') as f2:
        run1_data = json.load(f1)
        run2_data = json.load(f2)

    stats1 = run1_data.get('statistics', {})
    stats2 = run2_data.get('statistics', {})

    return {
        "run1": {
            "ammeter": run1_data.get('ammeter_type'),
            "count": run1_data.get('count'),
            "duration": run1_data.get('duration_seconds'),
            "mean": stats1.get('mean'),
            "max": stats1.get('max'),
        },
        "run2": {
            "ammeter": run2_data.get('ammeter_type'),
            "count": run2_data.get('count'),
            "duration": run2_data.get('duration_seconds'),
            "mean": stats2.get('mean'),
            "max": stats2.get('max'),
        }
    }
