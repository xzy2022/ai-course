"""
Solve Sudoku puzzles using combined heuristic and inference backtracking.

This script marries the MRV, Degree, and LCV heuristics with the inference
pipeline (forward checking, constraint propagation, arc consistency) exposed by
``InferenceBacktrackingSolver``. It reuses the Sudoku CSP model and reporting
helpers to provide an end-to-end demonstration.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# Allow the script to be executed directly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp.algorithms.inference_backtracking import InferenceBacktrackingSolver
from q1_sudoku_csp import (
    apply_puzzle_constraints,
    create_sudoku_csp,
    get_sample_sudoku_puzzle,
)
from sudoku.solve_inference_backtracking import (
    DEFAULT_TECHNIQUES as INFERENCE_DEFAULT_TECHNIQUES,
    analyse_solution,
    print_grid,
    print_metrics as print_inference_metrics,
)

SudokuCell = Tuple[int, int]
SudokuGrid = Dict[SudokuCell, int]
Metrics = Dict[str, Any]

DEFAULT_TECHNIQUES: Tuple[str, ...] = INFERENCE_DEFAULT_TECHNIQUES
DEFAULT_HEURISTIC_FLAGS = {
    "use_mrv": True,
    "use_degree": True,
    "use_lcv": True,
}


class HeuristicInferenceBacktrackingSolver(InferenceBacktrackingSolver):
    """
    Extend the inference solver with MRV, Degree, and LCV heuristics.
    """

    def __init__(
        self,
        *,
        techniques: Sequence[str] = DEFAULT_TECHNIQUES,
        use_mrv: bool = True,
        use_degree: bool = True,
        use_lcv: bool = True,
    ) -> None:
        super().__init__(techniques=techniques)
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        self._reset_heuristic_counters()

    def _reset_heuristic_counters(self) -> None:
        self.mrv_applications = 0
        self.degree_applications = 0
        self.lcv_applications = 0

    def _prepare(self, csp) -> None:  # type: ignore[override]
        super()._prepare(csp)
        self._reset_heuristic_counters()

    def _select_unassigned_variable(self, assignment):  # type: ignore[override]
        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        candidates: List[Tuple[SudokuCell, List[int], int]] = []
        for var in sorted(self.csp.variables, key=str):
            if var in assignment:
                continue

            legal_values: List[int] = []
            for value in self.current_domains[var]:
                if self.csp.is_consistent(var, value, assignment):
                    legal_values.append(value)

            degree = sum(1 for neighbor in self.neighbors.get(var, []) if neighbor not in assignment)
            candidates.append((var, legal_values, degree))

        if not candidates:
            return None

        filtered = candidates
        if self.use_degree and filtered:
            self.degree_applications += 1
            max_degree = max(item[2] for item in filtered)
            filtered = [item for item in filtered if item[2] == max_degree]

        if self.use_mrv and filtered:
            self.mrv_applications += 1
            min_domain = min(len(item[1]) for item in filtered)
            filtered = [item for item in filtered if len(item[1]) == min_domain]

        filtered.sort(key=lambda item: str(item[0]))
        selected_var, _, _ = filtered[0]
        return selected_var

    def _order_values(self, var, assignment):  # type: ignore[override]
        values = list(self.current_domains[var])
        if not self.use_lcv or not values:
            return values

        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        scored: List[Tuple[int, int]] = []
        for value in values:
            assignment[var] = value
            impact = 0
            for neighbor in self.neighbors.get(var, []):
                if neighbor in assignment:
                    continue
                for neighbor_value in self.current_domains[neighbor]:
                    if not self.csp.is_consistent(neighbor, neighbor_value, assignment):
                        impact += 1
            del assignment[var]
            scored.append((impact, value))

        self.lcv_applications += 1
        scored.sort(key=lambda item: (item[0], str(item[1])))
        return [value for _, value in scored]

    def solve_with_metrics(self, csp):  # type: ignore[override]
        solution, metrics = super().solve_with_metrics(csp)
        metrics.update(
            {
                "use_mrv": self.use_mrv,
                "use_degree": self.use_degree,
                "use_lcv": self.use_lcv,
                "mrv_applications": int(self.mrv_applications),
                "degree_applications": int(self.degree_applications),
                "lcv_applications": int(self.lcv_applications),
            }
        )
        return solution, metrics


def solve_sudoku_with_heuristic_inference(
    puzzle: SudokuGrid,
    *,
    techniques: Sequence[str] = DEFAULT_TECHNIQUES,
    use_mrv: bool = True,
    use_degree: bool = True,
    use_lcv: bool = True,
) -> Tuple[Optional[SudokuGrid], Metrics]:
    """
    Solve a Sudoku puzzle using combined heuristics and inference techniques.
    """
    csp = create_sudoku_csp()
    apply_puzzle_constraints(csp, puzzle)

    solver = HeuristicInferenceBacktrackingSolver(
        techniques=techniques,
        use_mrv=use_mrv,
        use_degree=use_degree,
        use_lcv=use_lcv,
    )
    solution, metrics = solver.solve_with_metrics(csp)

    typed_solution: Optional[SudokuGrid] = None
    if solution is not None:
        typed_solution = {(int(r), int(c)): int(value) for (r, c), value in solution.items()}
    return typed_solution, metrics


def print_combined_metrics(
    metrics: Metrics,
    techniques: Sequence[str],
    *,
    use_mrv: bool,
    use_degree: bool,
    use_lcv: bool,
) -> None:
    """Print solver metrics including heuristic usage details."""
    print_inference_metrics(metrics, techniques)
    print("\nHeuristic Metrics")
    print("-----------------")
    print(f"MRV Enabled:           {use_mrv}")
    print(f"Degree Enabled:        {use_degree}")
    print(f"LCV Enabled:           {use_lcv}")
    print(f"MRV Applications:      {metrics.get('mrv_applications', 0)}")
    print(f"Degree Applications:   {metrics.get('degree_applications', 0)}")
    print(f"LCV Applications:      {metrics.get('lcv_applications', 0)}")


def main() -> None:
    print("Sudoku Solver (Heuristics + Inference)")
    print("======================================")

    puzzle = get_sample_sudoku_puzzle()
    print_grid(puzzle, "Sample Puzzle")

    techniques = DEFAULT_TECHNIQUES
    heuristic_flags = DEFAULT_HEURISTIC_FLAGS
    solution, metrics = solve_sudoku_with_heuristic_inference(
        puzzle,
        techniques=techniques,
        **heuristic_flags,
    )

    print_grid(solution, "Solved Puzzle")
    print_combined_metrics(metrics, techniques, **heuristic_flags)
    analyse_solution(puzzle, solution)


if __name__ == "__main__":
    main()
