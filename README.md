# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

```text
ammeter-test-framework/
├── Ammeters/
│   ├── Circutor_Ammeter.py
│   ├── Entes_Ammeter.py
│   ├── Greenlee_Ammeter.py
│   ├── base_ammeter.py
│   └── client.py
├── config/
│   └── config.yaml
├── examples/
│   ├── assess_accuracy.py
│   ├── compare_runs.py
│   ├── run_framework.py
│   └── run_tests.py
├── src/
│   ├── testing/
│   │   └── test_framework.py
│   └── utils/
│       ├── Utils.py
│       ├── accuracy.py
│       ├── analysis.py
│       ├── comparison.py
│       ├── config.py
│       ├── logger.py
│       └── visualization.py
├── tests/
│   ├── integration/
│   │   └── test_api.py
│   └── unit/
│       ├── test_accuracy.py
│       ├── test_analysis.py
│       └── test_comparison.py
├── main.py
├── README.md
└── requirements.txt
```

## Libraries Installed

To run this code and utilize all the bonus features (like statistical analysis and data visualization), the following Python libraries were installed via `requirements.txt`:
- **`pytest`**: For running the automated unit and integration test suites.
- **`matplotlib`**: For rendering line charts of the collected ammeter data.
- **`pyyaml`**: For parsing the configuration-driven framework approach.

## Usage Guide

The framework is driven entirely by `config/config.yaml`. Before running any commands, ensure your desired sampling rates, durations, and output paths are set correctly in the configuration file.

### 1. Start the Ammeter Emulators (Server)
Before running any tests, you must start the local ammeter emulators. This script reads `config.yaml` to dynamically bind the correct ports and commands.
```sh
python3 main.py
```
*(Leave this running in the background or in a separate terminal tab).*

### 2. Run a Simple Sequential Test
To verify the framework is connected and operational, run a simple, sequential test sequence across all three ammeters. This will print a clean terminal summary without generating archives.
```sh
python3 examples/run_tests.py
```

### 3. Run a Production Automated Test & Visualization
To run a full test against a specific ammeter, generating a JSON archive and a Matplotlib visualization line-chart:
```sh
python3 examples/run_framework.py --ammeter greenlee
```
*(Available options: `greenlee`, `entes`, `circutor`).*
The resulting JSON file and `.png` graph will automatically be saved into the `results/` directory.

### 4. Assess Accuracy & Precision (Bonus)
To determine which ammeter is the most precise and accurate, this script executes concurrent, multi-threaded sampling across all three emulators simultaneously. It calculates the Ensemble Mean (consensus) and provides a clean terminal report highlighting the winners.
```sh
python3 examples/assess_accuracy.py
```

### 5. Compare Historical Runs
If you want to evaluate two historical JSON archives side-by-side, use the comparison utility.
```sh
python3 examples/compare_runs.py
```
*(You will be prompted to paste the filenames of the two JSON files you wish to compare).*

### 6. Enable Error Simulation / Chaos Mode (Bonus)
To simulate hardware faults and network drops, open `config/config.yaml` and set:
```yaml
testing:
  error_simulation: true
```
Restart `main.py`. The emulators will now randomly sleep beyond timeouts, return malformed garbage bytes, or abruptly drop connections. The `client.py` and test framework will gracefully catch these errors and auto-recover.

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
    "stdev": 2.3266,
    "cv_percentage": 157.0753,
    "is_consistent": false
  },
  "test_id": "a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": "20260506_145000",
  "plot_path": "results/greenlee_20260506_145000_plot.png",
  "archive_path": "results/greenlee_20260506_145000_a1b2c3d4.json"
}
```

---

## Design Decisions & Bonus Features

### 1. Configuration-Driven Testing (Bonus) & Main.py Refactor
- Unified the configuration to make `config/config.yaml` and the emulator classes the single source of truth. 
- Refactored `main.py` to dynamically load port bindings and commands rather than hardcoding them. Added a robust verification loop that polls the sockets on startup instead of relying on an arbitrary `time.sleep()`.

### 2. Error Simulation / Chaos Mode (Bonus)
- Added an `error_simulation` boolean toggle in the `testing` block of `config.yaml`.
- When enabled, `main.py` passes the `chaos_mode` flag to the ammeters, causing them to randomly inject hardware faults 10% of the time (e.g., sleeping beyond the client timeout, returning malformed byte strings, or abruptly closing the connection).
- The client connection logic (`Ammeters/client.py`) was refactored with a robust `try-except` block to catch `socket.timeout`, `ValueError`, and `ConnectionError` gracefully without crashing the active test.

### 3. Accuracy Assessment & Concurrency (Bonus)
- Extracted mathematical aggregation into a dedicated, unit-tested module `src/utils/accuracy.py`.
- Created an executable script `examples/assess_accuracy.py` utilizing Python's `concurrent.futures.ThreadPoolExecutor` to simultaneously fetch samples from all emulators, calculate the ensemble mean, and highlight the most precise and accurate devices in a formatted terminal report.

### 4. Performance Consistency Evaluation (Bonus)
- Updated the core statistical payload in `src/utils/analysis.py` to compute the **Coefficient of Variation (CV %)** (`(stdev / mean) * 100`).
- Added a configurable threshold to evaluate a new boolean metric `is_consistent`, returning true only if the device's CV is below a 5.0% deviation baseline.

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