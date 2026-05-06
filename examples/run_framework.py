import json
import argparse
import sys
from pathlib import Path

# Ensure the root directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.testing.test_framework import AmmeterTestFramework

def main():
    parser = argparse.ArgumentParser(description="Production-ready test runner for the Ammeter Framework")
    parser.add_argument('--ammeter', type=str, default='greenlee', choices=['greenlee', 'entes', 'circutor'],
                        help="Which ammeter to test (default: greenlee)")
    args = parser.parse_args()

    print(f"--- Running test against {args.ammeter.upper()} ---")
    try:
        framework = AmmeterTestFramework()
        result = framework.run_test(args.ammeter)
        
        print("\n" + "="*50)
        print("TEST RESULTS:")
        print("="*50)
        print(json.dumps(result, indent=2, default=str))
        
        if 'plot_path' in result:
            print(f"\n📊 Visualization saved to: {result['plot_path']}")
        if 'archive_path' in result:
            print(f"💾 Results archived at: {result['archive_path']}")
            
    except Exception as e:
        print(f"\n❌ Framework execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
