import sys
import os

# Ensure the root directory is in the python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from main import start_emulators
from src.testing.test_framework import AmmeterTestFramework

if __name__ == "__main__":
    print("Starting ammeter emulators in the background...")
    start_emulators()
    print("Emulators started. Testing the new API...\n")

    # Initialize your new framework
    # Note: We need to pass the absolute path to the config file so it works from any directory
    config_path = os.path.join(project_root, 'config', 'config.yaml')
    framework = AmmeterTestFramework(config_path=config_path)

    failures = 0

    # Test reading from each valid type
    for ammeter in ['greenlee', 'entes', 'circutor']:
        print(f"--- Requesting reading from {ammeter.upper()} ---")
        try:
            value = framework.get_single_reading(ammeter)
            if value is None:
                print(f"❌ Failed: API returned None instead of a value for {ammeter}\n")
                failures += 1
            else:
                print(f"✅ Success! API returned type: {type(value).__name__}, value: {value}\n")
        except Exception as e:
            print(f"❌ Failed to fetch {ammeter}: {e}\n")
            failures += 1

    # Test reading from an invalid type (Expected to fail)
    print(f"--- Requesting reading from UNKNOWN (Expected to raise ValueError) ---")
    try:
        framework.get_single_reading('unknown')
        print(f"❌ Failed: Expected ValueError, but reading succeeded.\n")
        failures += 1
    except ValueError as e:
        print(f"✅ Success! API correctly raised ValueError for unknown ammeter.\n")
    except Exception as e:
        print(f"❌ Failed: Expected ValueError, but got {type(e).__name__}: {e}\n")
        failures += 1

    if failures > 0:
        print(f"Integration tests failed with {failures} error(s).")
        sys.exit(1)
    else:
        print("All integration tests passed successfully!")
        sys.exit(0)
