"""
Sudoku Heuristic Solver

Provides a reusable helper around the instrumented heuristic backtracking solver
for Sudoku puzzles. All three heuristics (MRV, Degree, LCV) are enabled by
default, and the module exposes minimal utilities for inspecting the results.
"""

import os
import sys
from typing import Any, Dict, Optional, Tuple

# Ensure we can import the CSP package when executed as a script.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp.algorithms.heuristic_backtracking import InstrumentedHeuristicBacktracking
from q1_sudoku_csp import (
    apply_puzzle_constraints,
    create_sudoku_csp,
    get_sample_sudoku_puzzle,
)

SudokuCell = Tuple[int, int]
Assignment = Dict[SudokuCell, int]
Metrics = Dict[str, Any]


def solve_sudoku_puzzle(
    puzzle: Assignment,
    *,
    use_mrv: bool = True,
    use_degree: bool = True,
    use_lcv: bool = True,
    progress_interval: int = 10000,
    solver_name: str = "Sudoku Heuristic Solver",
) -> Tuple[Optional[Assignment], Metrics]:
    """
    Solve a Sudoku puzzle using the instrumented heuristic backtracking solver.
    """
    csp = create_sudoku_csp()
    apply_puzzle_constraints(csp, puzzle)

    solver = InstrumentedHeuristicBacktracking(
        use_mrv=use_mrv,
        use_degree=use_degree,
        use_lcv=use_lcv,
        progress_interval=progress_interval,
        name=solver_name,
    )

    solution, metrics = solver.solve_with_metrics(csp, initial_assignment=puzzle)
    typed_solution = solution if solution is None else dict(solution)
    return typed_solution, metrics


def print_sudoku_grid(grid: Optional[Assignment], title: str) -> None:
    """Render a Sudoku grid in ASCII form."""
    print(f"\n{title}:")
    print("-" * len(title))
    if not grid:
        print("  No data available.")
        return

    line_sep = "+-------+-------+-------+"
    print(line_sep)
    for r in range(1, 10):
        row_values = [
            str(grid.get((r, c), ".")) if grid.get((r, c), 0) != 0 else "."
            for c in range(1, 10)
        ]
        print("| {} {} {} | {} {} {} | {} {} {} |".format(*row_values))
        if r % 3 == 0:
            print(line_sep)


def _toggle_label(value: bool) -> str:
    return "ON" if value else "OFF"


def print_solver_metrics(metrics: Metrics, label: str) -> None:
    """Pretty-print key metrics captured by the solver."""
    print(f"\n{label} Metrics:")
    print("=" * (len(label) + 9))
    print(
        "Heuristics:            "
        f"MRV={_toggle_label(metrics['use_mrv'])}, "
        f"Degree={_toggle_label(metrics['use_degree'])}, "
        f"LCV={_toggle_label(metrics['use_lcv'])}"
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
    print(f"Initial Assignment:     {metrics.get('initial_assignment_size', 0)} cells")


def analyze_solution(
    puzzle: Assignment,
    solution: Optional[Assignment],
    label: str,
) -> None:
    """Report how many cells were filled and validate Sudoku constraints."""
    print(f"\nSolution Analysis ({label}):")
    if not solution:
        print("  No solution available.")
        return

    original_filled = len(puzzle)
    solved_cells = len(solution)
    print(f"  Original filled cells: {original_filled}")
    print(f"  Solved cells:          {solved_cells}")
    print(f"  Cells filled by solver: {solved_cells - original_filled}")

    def is_valid_group(values) -> bool:
        return len(values) == 9 and set(values) == set(range(1, 10))

    valid = True
    for r in range(1, 10):
        row = [solution.get((r, c), 0) for c in range(1, 10)]
        if not is_valid_group(row):
            print(f"  Invalid row detected: {r}")
            valid = False

    for c in range(1, 10):
        column = [solution.get((r, c), 0) for r in range(1, 10)]
        if not is_valid_group(column):
            print(f"  Invalid column detected: {c}")
            valid = False

    for box_row in range(3):
        for box_col in range(3):
            block = []
            for dr in range(3):
                for dc in range(3):
                    r = box_row * 3 + dr + 1
                    c = box_col * 3 + dc + 1
                    block.append(solution.get((r, c), 0))
            if not is_valid_group(block):
                print(
                    f"  Invalid box detected: top-left ({box_row * 3 + 1}, {box_col * 3 + 1})"
                )
                valid = False

    print(f"  Solution validity:    {'VALID' if valid else 'INVALID'}")


def main() -> None:
    print("Sudoku Heuristic Solver")
    print("=======================")

    puzzle = get_sample_sudoku_puzzle()
    print_sudoku_grid(puzzle, "Sample Puzzle")

    solution, metrics = solve_sudoku_puzzle(puzzle)
    print_sudoku_grid(solution, "Solved Puzzle")
    print_solver_metrics(metrics, "Heuristic Solver")
    analyze_solution(puzzle, solution, "Heuristic Solver")


if __name__ == "__main__":
    main()
