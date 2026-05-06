import sys
from pathlib import Path
import concurrent.futures

# Ensure the parent directory is in the sys.path so we can import src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.testing.test_framework import AmmeterTestFramework
from src.utils.accuracy import evaluate_accuracy

def run_ammeter_test(ammeter_type):
    framework = AmmeterTestFramework()
    
    # Disable visualization to prevent matplotlib threading crashes (double free/corruption)
    if 'analysis' in framework.config and 'visualization' in framework.config['analysis']:
        framework.config['analysis']['visualization']['enabled'] = False
        
    # run_test handles sampling and returns a dictionary of results
    return framework.run_test(ammeter_type)

def main():
    print("Starting Accuracy Assessment...")
    ammeters = ['greenlee', 'entes', 'circutor']
    results = {}
    
    # 1. Concurrency: Run tests simultaneously
    print("Running tests concurrently for all ammeters...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_ammeter = {executor.submit(run_ammeter_test, a): a for a in ammeters}
        for future in concurrent.futures.as_completed(future_to_ammeter):
            ammeter_type = future_to_ammeter[future]
            try:
                data = future.result()
                results[ammeter_type] = data
            except Exception as exc:
                print(f"{ammeter_type} generated an exception: {exc}")

    try:
        # Evaluate accuracy, data aggregation, relative accuracy calculation, scoring & identification
        evaluation = evaluate_accuracy(results)
    except ValueError as e:
        print(f"Error during accuracy evaluation: {e}. Exiting.")
        sys.exit(1)

    # CLI Output
    print(f"\n--- Accuracy Assessment Report ---")
    print(f"Ensemble Mean (Consensus): {evaluation['ensemble_mean']:.6f} A\n")

    print(f"{'Ammeter':<12} | {'Mean (A)':<12} | {'Abs Error (A)':<15} | {'CV (%)':<10}")
    print("-" * 57)
    
    most_accurate = evaluation['most_accurate']
    most_precise = evaluation['most_precise']
    
    for ammeter_type, mets in evaluation['metrics'].items():
        mean_str = f"{mets['mean']:.6f}"
        err_str = f"{mets['abs_error']:.6f}"
        cv_str = f"{mets['cv_percentage']:.4f}"
        
        flags = []
        if ammeter_type == most_accurate:
            flags.append("🏆 Most Accurate")
        if ammeter_type == most_precise:
            flags.append("🎯 Most Precise")
            
        flag_str = " ".join(flags)
        
        print(f"{ammeter_type.capitalize():<12} | {mean_str:<12} | {err_str:<15} | {cv_str:<10} {flag_str}")

    print("\nSummary:")
    print(f"- The Most Accurate Ammeter is: **{most_accurate.capitalize()}**")
    print(f"- The Most Precise/Reliable Ammeter is: **{most_precise.capitalize()}**")

if __name__ == "__main__":
    main()
