import json
import os

def compare_historical_runs(file_path_1: str, file_path_2: str) -> None:
    """Compares two historical test runs side-by-side using their file paths.

    Args:
        file_path_1: Path to the first JSON result file.
        file_path_2: Path to the second JSON result file.
    """
    if not os.path.exists(file_path_1):
        print(f"Error: Could not find file -> {file_path_1}")
        return
    if not os.path.exists(file_path_2):
        print(f"Error: Could not find file -> {file_path_2}")
        return

    try:
        with open(file_path_1, 'r', encoding='utf-8') as f1:
            run1_data = json.load(f1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path_1}")
        return

    try:
        with open(file_path_2, 'r', encoding='utf-8') as f2:
            run2_data = json.load(f2)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path_2}")
        return

    stats1 = run1_data.get('statistics', {})
    stats2 = run2_data.get('statistics', {})

    m1_mean = f"{stats1.get('mean'):.4f}" if isinstance(stats1.get('mean'), float) else "N/A"
    m2_mean = f"{stats2.get('mean'):.4f}" if isinstance(stats2.get('mean'), float) else "N/A"
    m1_max = f"{stats1.get('max'):.4f}" if isinstance(stats1.get('max'), float) else "N/A"
    m2_max = f"{stats2.get('max'):.4f}" if isinstance(stats2.get('max'), float) else "N/A"
    dur1 = f"{run1_data.get('duration_seconds', 0):.4f}"
    dur2 = f"{run2_data.get('duration_seconds', 0):.4f}"

    print("\n" + "="*60)
    print(f"{'Metric':<20} | {'Run 1':<15} | {'Run 2':<15}")
    print("-" * 60)
    print(f"{'Ammeter Type':<20} | {run1_data.get('ammeter_type', 'N/A'):<15} | {run2_data.get('ammeter_type', 'N/A'):<15}")
    print(f"{'Count':<20} | {run1_data.get('count', 0):<15} | {run2_data.get('count', 0):<15}")
    print(f"{'Duration (s)':<20} | {dur1:<15} | {dur2:<15}")
    print(f"{'Mean (A)':<20} | {m1_mean:<15} | {m2_mean:<15}")
    print(f"{'Max (A)':<20} | {m1_max:<15} | {m2_max:<15}")
    print("="*60 + "\n")