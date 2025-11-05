"""
Australia Map Coloring - Heuristic Solver

Provides a reusable helper for solving the Australia map coloring CSP with the
instrumented backtracking solver. By default all three heuristics (MRV, Degree,
LCV) are enabled.
"""

import os
import sys
from typing import Any, Dict, Optional, Tuple

# Ensure the CSP package is importable when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Variable, Value
from csp.algorithms.heuristic_backtracking import InstrumentedHeuristicBacktracking
from q1_australia_csp import create_australia_map_csp

Assignment = Dict[Variable, Value]
Metrics = Dict[str, Any]


def solve_australia_map(
    *,
    use_mrv: bool = True,
    use_degree: bool = True,
    use_lcv: bool = True,
    progress_interval: int = 0,
    solver_name: str = "Australia Heuristic Solver",
) -> Tuple[Optional[Assignment], Metrics]:
    """
    Solve the Australia map coloring CSP with the requested heuristics enabled.

    Returns the assignment and the collected metrics from the instrumented solver.
    """
    csp = create_australia_map_csp()
    solver = InstrumentedHeuristicBacktracking(
        use_mrv=use_mrv,
        use_degree=use_degree,
        use_lcv=use_lcv,
        progress_interval=progress_interval,
        name=solver_name,
    )
    solution, metrics = solver.solve_with_metrics(csp)
    typed_solution = solution if solution is None else dict(solution)
    return typed_solution, metrics


def _format_toggle(value: bool) -> str:
    return "ON" if value else "OFF"


def print_solution(solution: Optional[Assignment], title: str = "Solution") -> None:
    """Pretty-print an assignment for the Australia map coloring problem."""
    print(f"\n{title}:")
    print("-" * len(title))
    if not solution:
        print("  No solution found")
        return

    for var in sorted(solution.keys()):
        print(f"  {var}: {solution[var]}")


def print_metrics(metrics: Metrics, method_name: str) -> None:
    """Display metrics emitted by the instrumented solver."""
    print(f"\n{method_name} Performance Metrics:")
    print("=" * (len(method_name) + 22))
    print(
        "Heuristics:            "
        f"MRV={_format_toggle(metrics['use_mrv'])}, "
        f"Degree={_format_toggle(metrics['use_degree'])}, "
        f"LCV={_format_toggle(metrics['use_lcv'])}"
    )
    print(f"Time Elapsed:          {metrics['time_seconds']:.6f} seconds")
    print(f"Peak Memory Usage:      {metrics['memory_peak_mb']:.4f} MB")
    print(f"Total Attempts:         {metrics['attempt_count']:,}")
    print(f"Variable Selections:    {metrics['variable_selections']:,}")
    print(f"Assignments Made:       {metrics['domain_reductions']:,}")
    print(f"Max Recursion Depth:    {metrics['max_recursion_depth']}")
    print(f"Constraint Checks:      {metrics['constraint_checks']:,}")
    print(f"Selection/Attempt Rate: {metrics['selection_attempt_ratio']:.3f}")
    print(f"Average Domain Size:    {metrics['avg_domain_size']:.1f}")
    print(f"Efficiency (checks/attempt): {metrics['efficiency']:.1f}")
    print(f"Variables:              {metrics['total_variables']}")
    print(f"Constraints:            {metrics['constraints']}")


def main() -> None:
    """Solve and print results using default heuristic settings."""
    print("Australia Map Coloring - Heuristic Solver")
    solution, metrics = solve_australia_map()
    print_solution(solution, "Heuristic Solution")

    print_metrics(metrics, "Heuristic Solver")

    if solution:
        print("\nSolution Verification:")
        csp = create_australia_map_csp()
        print(f"  Complete: {csp.is_complete(solution)}")
        print(f"  Valid: {csp.is_solution(solution)}")
        print(f"  Unique colors used: {len(set(solution.values()))}")


if __name__ == "__main__":
    main()
