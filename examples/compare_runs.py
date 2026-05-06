import sys
from pathlib import Path

# Ensure the root directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.comparison import compare_historical_runs
from src.utils.config import load_config

def main():
    print("=== Ammeter Test Framework - Historical Comparison ===\n")
    
    # Load config to find the output directory dynamically
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / 'config' / 'config.yaml'
    config = load_config(str(config_path))
    output_dir = Path(config.get('result_management', {}).get('output_dir', 'results'))
    
    # Setup CLI argument parser
    import argparse
    parser = argparse.ArgumentParser(description="Compare two historical ammeter test runs.")
    parser.add_argument('--file1', type=str, help='Filename of the first test run')
    parser.add_argument('--file2', type=str, help='Filename of the second test run')
    args = parser.parse_args()

    # Interactive Fallback Logic
    file1 = args.file1
    file2 = args.file2

    if not file1:
        file1 = input(f"Enter the filename for Run 1 (located in {output_dir}/): ").strip()
    if not file2:
        file2 = input(f"Enter the filename for Run 2 (located in {output_dir}/): ").strip()

    if not file1 or not file2:
        print("\nError: Both filenames must be provided. Exiting.")
        sys.exit(1)

    # Safely construct full paths
    path1 = Path(file1) if Path(file1).is_absolute() else output_dir / file1
    path2 = Path(file2) if Path(file2).is_absolute() else output_dir / file2

    print(f"\nComparing [{file1}] vs [{file2}]...\n")
    
    # Execute Comparison
    try:
        comparison_data = compare_historical_runs(str(path1), str(path2))
        
        # Simple table formatting
        run1 = comparison_data['run1']
        run2 = comparison_data['run2']

        m1_mean = f"{run1.get('mean'):.4f}" if run1.get('mean') is not None else "N/A"
        m2_mean = f"{run2.get('mean'):.4f}" if run2.get('mean') is not None else "N/A"
        m1_max = f"{run1.get('max'):.4f}" if run1.get('max') is not None else "N/A"
        m2_max = f"{run2.get('max'):.4f}" if run2.get('max') is not None else "N/A"
        dur1 = f"{run1.get('duration', 0):.4f}"
        dur2 = f"{run2.get('duration', 0):.4f}"

        print("\n" + "="*60)
        print(f"{'Metric':<20} | {'Run 1':<15} | {'Run 2':<15}")
        print("-" * 60)
        print(f"{'Ammeter Type':<20} | {run1.get('ammeter') or 'N/A':<15} | {run2.get('ammeter') or 'N/A':<15}")
        print(f"{'Count':<20} | {run1.get('count') or 0:<15} | {run2.get('count') or 0:<15}")
        print(f"{'Duration (s)':<20} | {dur1:<15} | {dur2:<15}")
        print(f"{'Mean (A)':<20} | {m1_mean:<15} | {m2_mean:<15}")
        print(f"{'Max (A)':<20} | {m1_max:<15} | {m2_max:<15}")
        print("="*60 + "\n")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Comparison failed: {e}")

if __name__ == "__main__":
    main()
