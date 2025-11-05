"""
Sudoku Inference Solver

Uses the InstrumentedInferenceBacktracking solver to apply forward checking,
constraint propagation, and arc consistency while solving Sudoku puzzles. All
three inference techniques are enabled by default, and the module exposes
helpers for pretty-printing grids, metrics, and solution analysis.
"""

import os
import sys
from typing import Any, Dict, Optional, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp.algorithms.inference_backtracking import InstrumentedInferenceBacktracking
from q1_sudoku_csp import (
    apply_puzzle_constraints,
    create_sudoku_csp,
    get_sample_sudoku_puzzle,
)

SudokuCell = Tuple[int, int]
Assignment = Dict[SudokuCell, int]
Metrics = Dict[str, Any]


def solve_sudoku_with_inference(
    puzzle: Assignment,
    *,
    use_forward_checking: bool = True,
    use_constraint_propagation: bool = True,
    use_arc_consistency: bool = True,
    progress_interval: int = 10000,
    solver_name: str = "Sudoku Inference Solver",
) -> Tuple[Optional[Assignment], Metrics]:
    """Solve the given Sudoku puzzle using the requested inference settings."""
    csp = create_sudoku_csp()
    apply_puzzle_constraints(csp, puzzle)

    solver = InstrumentedInferenceBacktracking(
        use_forward_checking=use_forward_checking,
        use_constraint_propagation=use_constraint_propagation,
        use_arc_consistency=use_arc_consistency,
        progress_interval=progress_interval,
        name=solver_name,
    )

    solution, metrics = solver.solve_with_metrics(csp)
    typed_solution = solution if solution is None else dict(solution)
    return typed_solution, metrics


def _toggle(value: bool) -> str:
    return "ON" if value else "OFF"


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


def print_solver_metrics(metrics: Metrics, label: str) -> None:
    """Pretty-print the key metrics collected by the inference solver."""
    print(f"\n{label} Metrics:")
    print("=" * (len(label) + 9))
    print(
        "Inference:             "
        f"FC={_toggle(metrics['use_forward_checking'])}, "
        f"Propagate={_toggle(metrics['use_constraint_propagation'])}, "
        f"AC={_toggle(metrics['use_arc_consistency'])}"
    )
    print(f"Time Elapsed:          {metrics['time_seconds']:.6f} seconds")
    print(f"Peak Memory Usage:      {metrics['memory_peak_mb']:.4f} MB")
    print(f"Total Attempts:         {metrics['attempt_count']:,}")
    print(f"Variable Selections:    {metrics['variable_selections']:,}")
    print(f"Assignments Made:       {metrics['domain_reductions']:,}")
    print(f"Max Recursion Depth:    {metrics['max_recursion_depth']}")
    print(f"Constraint Checks:      {metrics['constraint_checks']:,}")
    print(f"Selection/Attempt Rate: {metrics['selection_attempt_ratio']:.3f}")
    print(f"Forward Check Calls:    {metrics['forward_check_calls']:,}")
    print(f"Propagation Steps:      {metrics['propagation_steps']:,}")
    print(f"Arc Enforcements:       {metrics['arc_enforcements']:,}")
    print(f"Variables:              {metrics['total_variables']}")
    print(f"Constraints:            {metrics['constraints']}")


def analyze_solution(puzzle: Assignment, solution: Optional[Assignment], label: str) -> None:
    """Summarise solver progress and validate Sudoku constraints."""
    print(f"\nSolution Analysis ({label}):")
    if not solution:
        print("  No solution available.")
        return

    original_filled = len(puzzle)
    solved_cells = len(solution)
    print(f"  Original filled cells: {original_filled}")
    print(f"  Solved cells:          {solved_cells}")
    print(f"  Cells filled by solver: {solved_cells - original_filled}")

    def valid_group(values) -> bool:
        return len(values) == 9 and set(values) == set(range(1, 10))

    valid = True
    for r in range(1, 10):
        row = [solution.get((r, c), 0) for c in range(1, 10)]
        if not valid_group(row):
            print(f"  Invalid row detected: {r}")
            valid = False

    for c in range(1, 10):
        column = [solution.get((r, c), 0) for r in range(1, 10)]
        if not valid_group(column):
            print(f"  Invalid column detected: {c}")
            valid = False

    for br in range(3):
        for bc in range(3):
            block = []
            for dr in range(3):
                for dc in range(3):
                    r = br * 3 + dr + 1
                    col = bc * 3 + dc + 1
                    block.append(solution.get((r, col), 0))
            if not valid_group(block):
                print(f"  Invalid box detected at top-left ({br * 3 + 1}, {bc * 3 + 1})")
                valid = False

    print(f"  Solution validity:    {'VALID' if valid else 'INVALID'}")


def main() -> None:
    print("Sudoku Inference Solver")
    print("=======================")

    puzzle = get_sample_sudoku_puzzle()
    print_sudoku_grid(puzzle, "Sample Puzzle")

    solution, metrics = solve_sudoku_with_inference(puzzle)
    print_sudoku_grid(solution, "Inference Solution")
    print_solver_metrics(metrics, "Inference Solver")
    analyze_solution(puzzle, solution, "Inference Solver")


if __name__ == "__main__":
    main()
