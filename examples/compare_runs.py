import os
import sys
import argparse

# Ensure the root directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.comparison import compare_historical_runs
from src.utils.config import load_config

def main():
    print("=== Ammeter Test Framework - Historical Comparison ===\n")
    
    # 1. Load config to find the output directory dynamically
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(project_root, 'config', 'config.yaml')
    config = load_config(config_path)
    output_dir = config.get('result_management', {}).get('output_dir', 'results')
    
    # 2. Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Compare two historical ammeter test runs.")
    parser.add_argument('--file1', type=str, help='Filename of the first test run')
    parser.add_argument('--file2', type=str, help='Filename of the second test run')
    args = parser.parse_args()

    # 3. Interactive Fallback Logic
    file1 = args.file1
    file2 = args.file2

    if not file1:
        file1 = input(f"Enter the filename for Run 1 (located in {output_dir}/): ").strip()
    if not file2:
        file2 = input(f"Enter the filename for Run 2 (located in {output_dir}/): ").strip()

    if not file1 or not file2:
        print("\nError: Both filenames must be provided. Exiting.")
        sys.exit(1)

    # 4. Safely construct full paths
    # If the user typed the full path, use it. Otherwise, prepend the output_dir.
    path1 = file1 if os.path.isabs(file1) else os.path.join(output_dir, file1)
    path2 = file2 if os.path.isabs(file2) else os.path.join(output_dir, file2)

    print(f"\nComparing [{file1}] vs [{file2}]...\n")
    
    # 5. Execute Comparison
    compare_historical_runs(path1, path2)

if __name__ == "__main__":
    main()
