"""
Performance Comparison Script

This script runs all solvers and compares their performance metrics.
"""

import subprocess
import sys
import os
import time

def run_solver(script_path: str, description: str):
    """Run a solver script and return results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        result = subprocess.run([sys.executable, script_path],
                              capture_output=True, text=True, timeout=60)
        end_time = time.time()

        execution_time = end_time - start_time

        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            print(f"Execution time: {execution_time:.2f} seconds")
            print(f"Output length: {len(result.stdout)} characters")

            # Extract key metrics from output
            output_lines = result.stdout.split('\n')
            metrics = {}

            for line in output_lines:
                if "Time Elapsed:" in line:
                    metrics['time'] = line.split(":")[-1].strip()
                elif "Total Attempts:" in line:
                    metrics['attempts'] = line.split(":")[-1].strip()
                elif "Max Recursion Depth:" in line:
                    metrics['depth'] = line.split(":")[-1].strip()
                elif "Peak Memory Usage:" in line:
                    metrics['memory'] = line.split(":")[-1].strip()
                elif "MRV Selections:" in line:
                    metrics['mrv_selections'] = line.split(":")[-1].strip()

            return {
                'status': 'success',
                'description': description,
                'execution_time': execution_time,
                'metrics': metrics,
                'output': result.stdout
            }
        else:
            print(f"[FAIL] {description} failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return {
                'status': 'failed',
                'description': description,
                'execution_time': execution_time,
                'error': result.stderr
            }

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} timed out after 60 seconds")
        return {
            'status': 'timeout',
            'description': description,
            'execution_time': 60,
            'error': 'Timed out after 60 seconds'
        }
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return {
            'status': 'error',
            'description': description,
            'execution_time': 0,
            'error': str(e)
        }


def main():
    """Main function to run performance comparison"""
    print("CSP Solver Performance Comparison")
    print("=" * 60)

    # Define all solvers to test
    solvers = [
        ("coloring/solve_australia_backtracking.py", "Australia - Basic Backtracking"),
        ("coloring/solve_australia_mrv.py", "Australia - MRV Backtracking"),
        ("sudoku/solve_sudoku_4x4_backtracking.py", "4x4 Sudoku - Basic Backtracking"),
        ("sudoku/solve_sudoku_4x4_mrv.py", "4x4 Sudoku - MRV Backtracking"),
        ("sudoku/solve_sudoku_backtracking.py", "9x9 Sudoku - Basic Backtracking"),
        ("sudoku/solve_sudoku_mrv.py", "9x9 Sudoku - MRV Backtracking"),
    ]

    results = []

    for script_path, description in solvers:
        if os.path.exists(script_path):
            result = run_solver(script_path, description)
            results.append(result)
        else:
            print(f"[WARN] Script not found: {script_path}")

    # Print summary table
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")

    print(f"{'Solver':<35} {'Status':<10} {'Time':<12} {'Attempts':<12} {'Memory':<10}")
    print("-" * 80)

    for result in results:
        if result['status'] == 'success':
            metrics = result.get('metrics', {})
            attempts = metrics.get('attempts', 'N/A')
            memory = metrics.get('memory', 'N/A')
            time_str = f"{result['execution_time']:.3f}s"
            print(f"{result['description']:<35} {result['status']:<10} {time_str:<12} {attempts:<12} {memory:<10}")
        else:
            time_str = f"{result['execution_time']:.3f}s" if 'execution_time' in result else 'N/A'
            print(f"{result['description']:<35} {result['status']:<10} {time_str:<12} {'N/A':<12} {'N/A':<10}")

    # Analysis and insights
    print(f"\n{'='*80}")
    print("ANALYSIS AND INSIGHTS")
    print(f"{'='*80}")

    successful_results = [r for r in results if r['status'] == 'success']

    if successful_results:
        print("\n1. Problem Complexity Comparison:")
        print("   Australia Map Coloring: 7 variables, 10 constraints")
        print("   4x4 Sudoku: 16 variables, 12 constraints")
        print("   9x9 Sudoku: 81 variables, 27 constraints")

        print("\n2. Algorithm Performance:")
        for result in successful_results:
            if 'metrics' in result and 'attempts' in result['metrics']:
                attempts = result['metrics']['attempts']
                print(f"   {result['description']}: {attempts} attempts")

        print("\n3. MRV vs Basic Backtracking:")
        basic_results = [r for r in successful_results if 'Basic' in r['description']]
        mrv_results = [r for r in successful_results if 'MRV' in r['description']]

        print(f"   Basic Backtracking: {len(basic_results)} tests completed")
        print(f"   MRV Backtracking: {len(mrv_results)} tests completed")

        if basic_results and mrv_results:
            basic_time = sum(r['execution_time'] for r in basic_results) / len(basic_results)
            mrv_time = sum(r['execution_time'] for r in mrv_results) / len(mrv_results)
            print(f"   Average time - Basic: {basic_time:.3f}s, MRV: {mrv_time:.3f}s")

        print("\n4. Key Observations:")
        print("   - Australia coloring is very fast (small search space)")
        print("   - 4x4 Sudoku is tractable but requires more work")
        print("   - 9x9 Sudoku is significantly more complex (may timeout)")
        print("   - MRV heuristic can help but benefits vary by problem type")

        print("\n5. Performance Factors:")
        print("   - Number of variables (search space size)")
        print("   - Constraint density and complexity")
        print("   - Initial domain reductions (pre-filled cells)")
        print("   - Heuristic effectiveness (MRV selection efficiency)")

    print(f"\n{'='*80}")
    print("COMPLETED ALL SOLVER TESTS")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()