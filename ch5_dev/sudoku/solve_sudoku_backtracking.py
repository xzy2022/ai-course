"""
Sudoku Solver - Basic Backtracking

This script uses basic backtracking search to solve Sudoku puzzles.
It measures and reports performance metrics including time, space, and attempt counts.
"""

import sys
import os
import time
import tracemalloc
from typing import Dict, Optional, Tuple

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Variable, Value
from csp.algorithms.backtracking import backtracking_search
from q1_sudoku_csp import create_sudoku_csp, get_sample_sudoku_puzzle, apply_puzzle_constraints


class InstrumentedBacktracking:
    """
    Wrapper class to instrument backtracking search with performance metrics
    """

    def __init__(self):
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.constraint_checks = 0
        self.csp = None
        self.progress_interval = 10000  # Report progress every 10,000 attempts
        self.last_progress_time = time.time()
        self.start_time = None

    def solve_with_metrics(self, csp: CSP) -> Optional[Dict[Variable, Value]]:
        """
        Solve CSP using basic backtracking with performance measurement
        """
        self.csp = csp
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.constraint_checks = 0

        # Start memory tracing and timing
        tracemalloc.start()
        start_time = time.time()
        self.start_time = start_time
        self.last_progress_time = start_time

        print("Starting Sudoku solver - this may take some time...")
        print("Progress will be reported every 10,000 attempts")
        print("-" * 50)

        # Solve using instrumented backtracking
        assignment = {}
        solution = self._instrumented_recursive_backtrack(assignment)

        # Calculate metrics
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        time_elapsed = end_time - start_time
        memory_peak = peak / 1024 / 1024  # Convert to MB

        return solution, {
            'time_seconds': time_elapsed,
            'memory_peak_mb': memory_peak,
            'attempt_count': self.attempt_count,
            'max_recursion_depth': self.max_recursion_depth,
            'constraint_checks': self.constraint_checks,
            'total_variables': len(csp.variables),
            'constraints': len(csp.constraints),
            'avg_domain_size': self._calculate_average_domain_size(),
            'efficiency': self._calculate_efficiency()
        }

    def _calculate_average_domain_size(self) -> float:
        """Calculate average domain size for unassigned variables"""
        if not self.csp:
            return 0
        domain_sizes = [len(self.csp.domains[var]) for var in self.csp.variables]
        return sum(domain_sizes) / len(domain_sizes)

    def _calculate_efficiency(self) -> float:
        """Calculate solving efficiency (constraints checked per attempt)"""
        if self.attempt_count == 0:
            return 0
        return self.constraint_checks / self.attempt_count

    def _report_progress(self):
        """Report progress to show the solver is still running"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        time_since_last_report = current_time - self.last_progress_time

        # Calculate filled cells percentage
        filled_cells = sum(1 for var in self.csp.variables
                          if len(self.csp.domains[var]) == 1)
        total_cells = len(self.csp.variables)
        filled_percentage = (filled_cells / total_cells) * 100

        # Calculate attempts per second
        attempts_per_second = self.attempt_count / elapsed_time if elapsed_time > 0 else 0

        print(f"[PROGRESS] Attempts: {self.attempt_count:,} | "
              f"Time: {elapsed_time:.1f}s | "
              f"Rate: {attempts_per_second:,.0f}/s | "
              f"Filled: {filled_percentage:.1f}% | "
              f"Depth: {self.recursion_depth}")

        self.last_progress_time = current_time

    def _instrumented_recursive_backtrack(self, assignment: Dict[Variable, Value]) -> Optional[Dict[Variable, Value]]:
        """
        Instrumented version of recursive backtracking that tracks performance metrics
        """
        self.attempt_count += 1
        self.recursion_depth += 1
        self.max_recursion_depth = max(self.max_recursion_depth, self.recursion_depth)

        # Report progress periodically
        if self.attempt_count % self.progress_interval == 0:
            self._report_progress()

        # Base case: if assignment is complete, return solution
        if self.csp.is_complete(assignment):
            self.recursion_depth -= 1
            return assignment

        # Select unassigned variable (simple strategy: first unassigned)
        var = self._select_unassigned_variable(assignment)
        if var is None:
            self.recursion_depth -= 1
            return None

        # Try each value in the domain
        for value in self.csp.domains[var]:
            # Check consistency
            self.constraint_checks += len(self.csp.constraints)
            if self.csp.is_consistent(var, value, assignment):
                # Make assignment
                assignment[var] = value

                # Recursive call
                result = self._instrumented_recursive_backtrack(assignment)

                # If successful, return result
                if result is not None:
                    self.recursion_depth -= 1
                    return result

                # Backtrack
                del assignment[var]

        self.recursion_depth -= 1
        return None

    def _select_unassigned_variable(self, assignment: Dict[Variable, Value]) -> Optional[Variable]:
        """Select the first unassigned variable"""
        for var in self.csp.variables:
            if var not in assignment:
                return var
        return None


def print_sudoku_solution(solution: Dict[Tuple[int, int], int], title: str = "Sudoku Solution"):
    """Print the Sudoku solution in grid format"""
    print(f"\n{title}:")
    print("-" * len(title))
    if solution:
        print("┌─────────┬─────────┬─────────┐")
        for r in range(1, 10):
            row_str = "│"
            for c in range(1, 10):
                if c in [4, 7]:
                    row_str += " │"
                value = solution.get((r, c), 0)
                row_str += f" {value}" if value != 0 else " ."
            row_str += " │"
            print(row_str)
            if r in [3, 6]:
                print("├─────────┼─────────┼─────────┤")
        print("└─────────┴─────────┴─────────┘")
    else:
        print("  No solution found")


def print_metrics(metrics: Dict, method_name: str = "Basic Backtracking"):
    """Print performance metrics"""
    print(f"\n{method_name} Performance Metrics:")
    print("=" * (len(method_name) + 22))
    print(f"Time Elapsed:          {metrics['time_seconds']:.6f} seconds")
    print(f"Peak Memory Usage:      {metrics['memory_peak_mb']:.4f} MB")
    print(f"Total Attempts:         {metrics['attempt_count']:,}")
    print(f"Max Recursion Depth:    {metrics['max_recursion_depth']}")
    print(f"Constraint Checks:      {metrics['constraint_checks']:,}")
    print(f"Variables:              {metrics['total_variables']}")
    print(f"Constraints:            {metrics['constraints']}")
    print(f"Avg Domain Size:        {metrics['avg_domain_size']:.1f}")
    print(f"Efficiency:             {metrics['efficiency']:.1f} checks/attempt")
    print(f"Attempts per Variable:  {metrics['attempt_count'] / metrics['total_variables']:.1f}")


def analyze_solution_complexity(solution: Dict[Tuple[int, int], int],
                              original_puzzle: Dict[Tuple[int, int], int]):
    """Analyze the complexity and characteristics of the solution"""
    print(f"\nSolution Analysis:")
    print(f"  Original filled cells:    {len(original_puzzle)}")
    print(f"  Solution filled cells:    {len(solution)}")
    print(f"  Cells solved by algorithm: {len(solution) - len(original_puzzle)}")
    print(f"  Solution completeness:     {len(solution) == 81}")

    # Check if solution is valid
    if solution:
        row_counts = {}
        col_counts = {}
        box_counts = {}

        for (r, c), value in solution.items():
            # Count by rows
            row_counts.setdefault(r, set()).add(value)
            # Count by columns
            col_counts.setdefault(c, set()).add(value)
            # Count by boxes
            box_row, box_col = (r-1)//3, (c-1)//3
            box_key = (box_row, box_col)
            box_counts.setdefault(box_key, set()).add(value)

        # Check for duplicates
        valid = True
        for counts, name in [(row_counts, "rows"), (col_counts, "columns"), (box_counts, "boxes")]:
            for key, values in counts.items():
                if len(values) != 9:
                    valid = False
                    print(f"  Invalid: {name} {key} has duplicates")

        if valid:
            print(f"  Solution validity:         VALID")


def main():
    """
    Main function to solve Sudoku using basic backtracking
    """
    print("Sudoku Solver - Basic Backtracking")
    print("=" * 40)

    # Create the CSP model
    print("Creating Sudoku CSP...")
    csp = create_sudoku_csp()

    print(f"Problem Details:")
    print(f"  Variables: {len(csp.variables)} (9x9 grid)")
    print(f"  Domains: {list(csp.domains.values())[0]} (digits)")
    print(f"  Constraints: {len(csp.constraints)} (9 rows + 9 cols + 9 boxes)")
    print(f"  Branching Factor: {len(list(csp.domains.values())[0])} (digits per cell)")

    # Get sample puzzle
    original_puzzle = get_sample_sudoku_puzzle()
    print(f"\nSample Puzzle: {len(original_puzzle)} pre-filled cells")

    # Apply puzzle constraints
    csp_with_puzzle = apply_puzzle_constraints(csp, original_puzzle)

    # Count variables with reduced domains
    single_value_vars = sum(1 for var in csp_with_puzzle.variables
                           if len(csp_with_puzzle.domains[var]) == 1)
    print(f"  Variables with single-value domains: {single_value_vars}")
    print(f"  Variables with full domains: {len(csp.variables) - single_value_vars}")

    # Solve with instrumented backtracking
    print(f"\nSolving with Basic Backtracking...")
    print("(This may take some time for 9x9 Sudoku...)")

    solver = InstrumentedBacktracking()
    solution, metrics = solver.solve_with_metrics(csp_with_puzzle)

    # Display results
    print_sudoku_solution(solution, "Basic Backtracking Solution")
    print_metrics(metrics, "Basic Backtracking")

    # Analyze solution
    analyze_solution_complexity(solution, original_puzzle)

    # Compare with built-in solver (for reference)
    print(f"\nReference: Built-in Backtracking Solver")
    print("-" * 35)
    start_time = time.time()
    builtin_solution = csp_with_puzzle.solve(method="backtracking")
    builtin_time = time.time() - start_time

    if builtin_solution:
        print(f"Built-in Solver Time: {builtin_time:.6f} seconds")
        print(f"Solutions Match: {solution == builtin_solution}")

    print(f"\n{'='*40}")
    print("Sudoku puzzle solved successfully!")
    print("\nNote: Sudoku is significantly more complex than map coloring")
    print("due to the larger search space and numerous constraints.")


if __name__ == "__main__":
    main()