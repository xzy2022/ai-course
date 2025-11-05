"""
Solve Sudoku puzzles using the generic inference backtracking solver.

The solver from `csp.algorithms.inference_backtracking` supports combining
forward checking, constraint propagation, and arc consistency. This module
applies it to the Sudoku CSP model with all three techniques enabled by
default and exposes helpers for rendering grids and summarising metrics.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

# Allow running the module directly without installing the package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp.algorithms.inference_backtracking import inference_backtracking_with_metrics
from q1_sudoku_csp import (
    apply_puzzle_constraints,
    create_sudoku_csp,
    get_sample_sudoku_puzzle,
)

SudokuCell = Tuple[int, int]
SudokuGrid = Dict[SudokuCell, int]
Metrics = Dict[str, Any]

DEFAULT_TECHNIQUES: Tuple[str, ...] = (
    "forward_checking",
    "constraint_propagation",
    "arc_consistency",
)


def solve_puzzle_with_inference(
    puzzle: SudokuGrid,
    techniques: Sequence[str] = DEFAULT_TECHNIQUES,
) -> Tuple[Optional[SudokuGrid], Metrics]:
    """
    Solve the provided Sudoku puzzle using the requested inference techniques.
    """
    csp = create_sudoku_csp()
    apply_puzzle_constraints(csp, puzzle)

    solution, metrics = inference_backtracking_with_metrics(csp, techniques=techniques)

    typed_solution: Optional[SudokuGrid] = None
    if solution is not None:
        typed_solution = {(int(r), int(c)): int(value) for (r, c), value in solution.items()}
    return typed_solution, metrics


def _format_value(value: int) -> str:
    return str(value) if value != 0 else "."


def print_grid(grid: Optional[SudokuGrid], title: str) -> None:
    """Render a Sudoku grid in a human-friendly ASCII layout."""
    print(f"\n{title}")
    print("-" * len(title))
    if not grid:
        print("  (no data)")
        return

    divider = "+-------+-------+-------+"
    print(divider)
    for row in range(1, 10):
        row_cells = [_format_value(grid.get((row, col), 0)) for col in range(1, 10)]
        print("| {} {} {} | {} {} {} | {} {} {} |".format(*row_cells))
        if row % 3 == 0:
            print(divider)


def print_metrics(metrics: Metrics, techniques: Sequence[str]) -> None:
    """Pretty-print key metrics returned by the solver."""
    print("\nSolver Metrics")
    print("==============")
    print(f"Techniques:             {', '.join(techniques) or 'none'}")
    print(f"Elapsed Time:           {metrics['elapsed_seconds']:.4f} s")
    print(f"Peak Memory:            {metrics['peak_memory_mb']:.4f} MB")
    print(f"Current Memory:         {metrics['current_memory_mb']:.4f} MB")
    print(f"Nodes Expanded:         {int(metrics['nodes_expanded'])}")
    print(f"Backtracks:             {int(metrics['backtracks'])}")
    print(f"Max Depth:              {int(metrics['max_depth'])}")
    print(f"Forward Check Prunes:   {int(metrics['forward_check_prunes'])}")
    print(f"Propagation Steps:      {int(metrics['propagation_steps'])}")
    print(f"Arc Revisions:          {int(metrics['arc_revisions'])}")
    print(f"Solution Found:         {bool(metrics['solution_found'])}")
    print(f"Assignment Size:        {int(metrics['assignment_size'])}")


def analyse_solution(puzzle: SudokuGrid, solution: Optional[SudokuGrid]) -> None:
    """Report how many cells were filled and whether the solution is valid."""
    print("\nSolution Analysis")
    print("=================")
    if not solution:
        print("No solution produced.")
        return

    initial_filled = len(puzzle)
    solved_cells = len(solution)
    print(f"Initial filled cells:   {initial_filled}")
    print(f"Solved cells:           {solved_cells}")
    print(f"Cells filled by solver: {solved_cells - initial_filled}")

    def _group_valid(values: Iterable[int]) -> bool:
        vals = [v for v in values if v != 0]
        return len(vals) == 9 and set(vals) == set(range(1, 10))

    valid_rows = all(_group_valid(solution.get((r, c), 0) for c in range(1, 10)) for r in range(1, 10))
    valid_cols = all(_group_valid(solution.get((r, c), 0) for r in range(1, 10)) for c in range(1, 10))

    def _block_values(br: int, bc: int) -> Iterable[int]:
        for dr in range(3):
            for dc in range(3):
                yield solution.get((br * 3 + dr + 1, bc * 3 + dc + 1), 0)

    valid_blocks = all(_group_valid(_block_values(br, bc)) for br in range(3) for bc in range(3))

    is_valid = valid_rows and valid_cols and valid_blocks
    print(f"Rows valid:             {valid_rows}")
    print(f"Columns valid:          {valid_cols}")
    print(f"Blocks valid:           {valid_blocks}")
    print(f"Overall validity:       {'VALID' if is_valid else 'INVALID'}")


def main() -> None:
    print("Sudoku Solver (Inference Backtracking)")
    print("======================================")

    puzzle = get_sample_sudoku_puzzle()
    print_grid(puzzle, "Sample Puzzle")

    techniques = DEFAULT_TECHNIQUES
    solution, metrics = solve_puzzle_with_inference(puzzle, techniques)

    print_grid(solution, "Solved Puzzle")
    print_metrics(metrics, techniques)
    analyse_solution(puzzle, solution)


if __name__ == "__main__":
    main()
