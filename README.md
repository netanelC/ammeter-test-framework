# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `Ammeters/`
  - `main.py`: Main script to start the ammeter emulators and request current measurements.
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `base_ammeter.py`: Base class for all ammeter emulators.
  - `client.py`: Client to request current measurements from the ammeter emulators.
- `config/`
  - `config.yaml`: Configuration file for the ammeter emulators.
- `examples/`
  - `run_test.py`: super lyze example for run test **don't use it**.
- `src/`
  - `testing/`
    - `AmmeterTester.py`: Class to test the ammeter emulators.
  - `utils/`
    - `config.py`: Configuration settings.
    - `logger.py`: Logging setup.
    - `Utils.py`: Utility functions, including `generate_random_float`.

## Usage

# Ammeter Emulators

## Greenlee Ammeter

- **Port**: 5000
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Calculates current using voltage (1V - 10V) and (0.1Ω - 100Ω).
- **Measurement method** : Ohm's Law: I = V / R

## ENTES Ammeter

- **Port**: 5001
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Calculates current using magnetic field strength (0.01T - 0.1T) and calibration factor (500 - 2000).
- **Measurement method** : Hall Effect: I = B * K

## CIRCUTOR Ammeter

- **Port**: 5002
- **Command**: `MEASURE_CIRCUTOR -get_measurement`
- **Measurement Logic**: Calculates current using voltage values (0.1V - 1.0V) over a number of samples and a random time step (0.001s - 0.01s).
- **Measurement method** : Rogowski Coil Integration: I = ∫V dt

To start the ammeter emulators and request current measurements, run the `main.py` script:
```sh
python3 main.py
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
**The Problem:** The framework required robust verification to ensure the Unified API and Sampling Engine edge cases work reliably.
**The Design:**
- Refactored manual test scripts into a professional `pytest` suite located in a dedicated `tests/` directory.
- Separated concerns: 
  - `tests/unit/` handles complex mathematical logic (e.g., statistical calculations) using parameterized edge-case testing.
  - `tests/integration/` handles end-to-end framework verification, utilizing `pytest` fixtures to safely spin up and tear down the background ammeter emulator threads.
- Configured a GitHub Actions CI workflow (`.github/workflows/pull-request.yaml`) to automatically install dependencies and run the full test suite on every PR, ensuring continuous quality assurance.

### 5. Statistical Analysis & Visualization (Issue #12)
**The Problem:** Raw arrays of measurements need to be analyzed to extract meaningful insights, and the data needs to be visualized as part of the bonus challenge. The framework also needed a decoupled architecture to prevent monolithic methods.
**The Design:**
- Created a robust statistical module in `src/utils/analysis.py` leveraging Python's built-in `statistics` library to compute Mean, Median, Standard Deviation, Min, and Max.
- Integrated a clean, dashboard-style visualization module in `src/utils/visualization.py` utilizing `matplotlib`. It automatically generates line plots with user-friendly grids and includes optional horizontal reference lines for `Mean` and `Max` values.
- **Decoupled Architecture:** Extracted the statistical calculation and visualization I/O logic out of the monolithic `run_test()` method into a private `_process_results()` helper method.
- **Test Artifact Cleanup:** Updated the integration test suite to utilize pytest's built-in `tmp_path` fixture. The framework dynamically overrides its `output_dir` during testing so plots are written to ephemeral directories and automatically cleaned up, keeping the workspace pristine.