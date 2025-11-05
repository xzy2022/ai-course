"""
Australia Map Coloring Solver - Basic Backtracking

This script uses basic backtracking search to solve the Australia map coloring problem.
It measures and reports performance metrics including time, space, and attempt counts.
"""

import sys
import os
import time
import tracemalloc
from typing import Dict, Optional

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Variable, Value
from csp.algorithms.backtracking import backtracking_search, _recursive_backtrack
from q1_australia_csp import create_australia_map_csp


class InstrumentedBacktracking:
    """
    Wrapper class to instrument backtracking search with performance metrics
    """

    def __init__(self):
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.csp = None

    def solve_with_metrics(self, csp: CSP) -> Optional[Dict[Variable, Value]]:
        """
        Solve CSP using basic backtracking with performance measurement
        """
        self.csp = csp
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0

        # Start memory tracing
        tracemalloc.start()
        start_time = time.time()

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
            'total_variables': len(csp.variables),
            'constraints_checked': self.attempt_count * len(csp.constraints)
        }

    def _instrumented_recursive_backtrack(self, assignment: Dict[Variable, Value]) -> Optional[Dict[Variable, Value]]:
        """
        Instrumented version of recursive backtracking that tracks performance metrics
        """
        self.attempt_count += 1
        self.recursion_depth += 1
        self.max_recursion_depth = max(self.max_recursion_depth, self.recursion_depth)

        # Base case: if assignment is complete, return solution
        if self.csp.is_complete(assignment):
            self.recursion_depth -= 1
            return assignment

        # Select unassigned variable
        from csp.algorithms.backtracking import _select_unassigned_variable
        var = _select_unassigned_variable(self.csp, assignment)
        if var is None:
            self.recursion_depth -= 1
            return None

        # Try each value in the domain
        for value in self.csp.domains[var]:
            # Check consistency
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


def print_solution(solution: Dict[Variable, Value], title: str = "Solution"):
    """Print the solution in a readable format"""
    print(f"\n{title}:")
    print("-" * len(title))
    if solution:
        # Sort variables by name for consistent output
        sorted_vars = sorted(solution.keys())
        for var in sorted_vars:
            print(f"  {var}: {solution[var]}")
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
    print(f"Variables:              {metrics['total_variables']}")
    print(f"Constraints Checked:    {metrics['constraints_checked']:,}")
    print(f"Attempts per Variable:  {metrics['attempt_count'] / metrics['total_variables']:.1f}")


def main():
    """
    Main function to solve Australia map coloring using basic backtracking
    """
    print("Australia Map Coloring - Basic Backtracking Solver")
    print("=" * 55)

    # Create the CSP model
    print("Creating Australia map coloring CSP...")
    csp = create_australia_map_csp()

    print(f"Problem Details:")
    print(f"  Variables: {len(csp.variables)} (Australian states/territories)")
    print(f"  Domains: {list(csp.domains.values())[0]} (colors)")
    print(f"  Constraints: {len(csp.constraints)} (adjacency relations)")
    print(f"  Branching Factor: {len(list(csp.domains.values())[0])} (colors per variable)")

    # Solve with instrumented backtracking
    print(f"\nSolving with Basic Backtracking...")
    solver = InstrumentedBacktracking()
    solution, metrics = solver.solve_with_metrics(csp)

    # Display results
    print_solution(solution, "Basic Backtracking Solution")
    print_metrics(metrics, "Basic Backtracking")

    # Additional analysis
    if solution:
        print(f"\nSolution Verification:")
        print(f"  Complete: {csp.is_complete(solution)}")
        print(f"  Valid: {csp.is_solution(solution)}")
        print(f"  Unique Colors Used: {len(set(solution.values()))}")

        # Show color distribution
        color_counts = {}
        for color in solution.values():
            color_counts[color] = color_counts.get(color, 0) + 1
        print(f"  Color Distribution: {color_counts}")

    # Compare with built-in solver (for reference)
    print(f"\nReference: Built-in Backtracking Solver")
    print("-" * 35)
    start_time = time.time()
    builtin_solution = csp.solve(method="backtracking")
    builtin_time = time.time() - start_time

    if builtin_solution:
        print_solution(builtin_solution, "Built-in Solver Solution")
        print(f"Built-in Solver Time: {builtin_time:.6f} seconds")
        print(f"Solutions Match: {solution == builtin_solution}")

    print(f"\n{'='*55}")
    print("Australia map coloring problem solved successfully!")


if __name__ == "__main__":
    main()