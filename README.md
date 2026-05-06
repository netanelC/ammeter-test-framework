# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `main.py`: Main script to start the ammeter emulators in the background.
- `Ammeters/`
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `base_ammeter.py`: Base class for all ammeter emulators.
  - `client.py`: Client to request current measurements from the ammeter emulators.
- `config/`
  - `config.yaml`: Configuration file for the test framework and emulators.
- `examples/`
  - `run_framework.py`: Production-ready CLI script to run automated tests.
  - `compare_runs.py`: CLI script to compare two historical JSON archives.
- `src/`
  - `testing/`
    - `test_framework.py`: Contains `AmmeterTestFramework`, the unified testing API and sampling engine.
  - `utils/`
    - `config.py`: Configuration loader.
    - `logger.py`: Logging setup and file handling.
    - `Utils.py`: Utility functions, including `generate_random_float`.
    - `analysis.py`: Statistical calculation module.
    - `visualization.py`: Matplotlib plotting module.
    - `comparison.py`: Historical run comparison utility.
- `tests/`
  - `integration/`: End-to-end pytest verification (e.g., `test_api.py`).
  - `unit/`: Isolated pytest unit tests (e.g., `test_analysis.py`, `test_comparison.py`).

## Usage

The project includes production-ready example scripts for running tests and comparing historical results:

- **Run a new test:**
  ```sh
  python3 examples/run_framework.py --ammeter greenlee
  ```
  This will execute the framework using settings in `config.yaml`, print the results in JSON format, and save the visualization/archive in the `results/` folder.

- **Compare historical runs:**
  ```sh
  python3 examples/compare_runs.py
  ```
  This script will prompt you for the filenames of two archived JSON result files in the `results/` folder and output a side-by-side terminal comparison of their statistics.

To start the ammeter emulators in the background:
```sh
python3 main.py
```

---

## Sample Test Results

When you execute a test run using the framework, it generates a comprehensive JSON report containing the raw data arrays, test metadata, and calculated statistics. Here is an example of a generated result file (`results/greenlee_20260506_145000_a1b2c3d4.json`):

```json
{
  "ammeter_type": "greenlee",
  "measurements": [
    0.5010,
    5.8526,
    0.0742,
    0.0197,
    1.2961,
    5.7601,
    0.0731,
    0.0555,
    1.1312,
    0.0484
  ],
  "count": 10,
  "expected_count": 10,
  "duration_seconds": 4.5129,
  "sampling_frequency_hz": 2.0,
  "statistics": {
    "mean": 1.4812,
    "median": 0.2876,
    "min": 0.0197,
    "max": 5.8526,
    "stdev": 2.3266
  },
  "test_id": "a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": "20260506_145000",
  "plot_path": "results/greenlee_20260506_145000_plot.png",
  "archive_path": "results/greenlee_20260506_145000_a1b2c3d4.json"
}
```

---

## Design Decisions & Bug Fixes

### 1. Emulator Communication Fix (PR #10)
**The Problem:** The initial `main.py` script failed to fetch data from the ammeter emulators.
**The Fix:** 
- Discovered discrepancies between the documented ports/commands, `main.py`, and the actual `Ammeters/*_Ammeter.py` implementations.
- Unified the configuration to make `config/config.yaml` and the emulator classes the source of truth.
- Set the ammeters to listen sequentially on ports `5000` (Greenlee), `5001` (ENTES), and `5002` (CIRCUTOR).
- Updated `main.py` to send the correct byte strings (e.g., `b'MEASURE_CIRCUTOR -get_measurement'`).
- Added `socket.SO_REUSEADDR` to `base_ammeter.py` to prevent "Address already in use" errors during rapid test iterations.

### 2. Unified Testing API (Issue #7)
**The Problem:** The exam requires a unified interface capable of communicating consistently with multiple ammeter types.
**The Design:**
- Implemented `AmmeterTestFramework` in `src/testing/test_framework.py`.
- The framework acts as an abstraction layer; users simply call `get_single_reading('greenlee')` without needing to manage raw sockets, ports, or byte commands.
- The framework dynamically reads the required connection parameters from `config/config.yaml`.
- The base `client.py` was updated to decode and return standard Python `float` types rather than printing to stdout, enabling programmatic data aggregation.

### 3. Configurable Sampling Engine (Issue #8)
**The Problem:** The framework needs a sampling mechanism to automate test runs based on configuration parameters (frequency, duration, and count).
**The Design:**
- Implemented the `run_test(ammeter_type)` method in `AmmeterTestFramework`.
- The engine dynamically reads the `testing.sampling` section of `config.yaml`.
- It supports looping based on either `measurements_count` or `total_duration_seconds`, automatically calculating the sleep delay using `sampling_frequency_hz` to ensure precise timing.
- It aggregates all measurements and returns a comprehensive metadata dictionary containing the raw array and execution stats.

### 4. Professional Testing Strategy & CI
**The Problem:** The framework required robust verification to ensure the Unified API and Sampling Engine edge cases work reliably, alongside automated quality control.
**The Design:**
- Refactored manual test scripts into a professional `pytest` suite located in a dedicated `tests/` directory.
- Separated concerns: 
  - `tests/unit/` handles complex mathematical logic (e.g., statistical calculations) using parameterized edge-case testing.
  - `tests/integration/` handles end-to-end framework verification, utilizing `pytest` fixtures to safely spin up and tear down the background ammeter emulator threads.
- Configured a GitHub Actions CI workflow (`.github/workflows/pull-request.yaml`) to automatically enforce quality standard on every PR:
  - Validates style and syntax using `ruff`.
  - Enforces static type checking with `mypy`.
  - Runs the full `pytest` suite for continuous integration.

### 5. Statistical Analysis & Visualization (Issue #12)
**The Problem:** Raw arrays of measurements need to be analyzed to extract meaningful insights, and the data needs to be visualized as part of the bonus challenge. The framework also needed a decoupled architecture to prevent monolithic methods.
**The Design:**
- Created a robust statistical module in `src/utils/analysis.py` leveraging Python's built-in `statistics` library to compute Mean, Median, Standard Deviation, Min, and Max.
- Integrated a clean, dashboard-style visualization module in `src/utils/visualization.py` utilizing `matplotlib`. It automatically generates line plots with user-friendly grids and includes optional horizontal reference lines for `Mean` and `Max` values.
- **Decoupled Architecture:** Extracted the statistical calculation and visualization I/O logic out of the monolithic `run_test()` method into a private `_process_results()` helper method.
- **Test Artifact Cleanup:** Updated the integration test suite to utilize pytest's built-in `tmp_path` fixture. The framework dynamically overrides its `output_dir` during testing so plots are written to ephemeral directories and automatically cleaned up, keeping the workspace pristine.

### 6. Result Management and Archiving System (Issue #13)
**The Problem:** The exam requires a robust result archiving system to store test runs for historical review and comparison.
**The Design:**
- Enhanced `_process_results()` to generate a unique `test_id` (UUID) and `timestamp` for every automated test run.
- Archiving mechanism dumps the entire test run metadata—including configuration parameters, raw measurements arrays, and calculated statistical metrics—to a structured JSON file.
- The JSON output is saved into the configurable `results/` directory using an identifiable naming convention (`{ammeter_type}_{timestamp}_{uuid}.json`).
- **Historical Comparison (Decoupled):** Adhering to the Single Responsibility Principle, the comparison logic was extracted into a standalone utility module (`src/utils/comparison.py`). It loads two archived JSON files by their paths and outputs a side-by-side terminal table comparing their counts, durations, and statistical metrics (Mean, Max) for clear, actionable observability. An executable example script is provided at `examples/compare_runs.py`.
- Updated the integration test suite to assert that the `archive_path` exists, the JSON structure maintains integrity, and the decoupled comparison table successfully generates.