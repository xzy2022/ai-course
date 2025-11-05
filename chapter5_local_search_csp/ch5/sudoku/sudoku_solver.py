"""
Sudoku Solver

This module provides a high-level interface for solving Sudoku puzzles
using various algorithms from the CSP framework.
"""

from typing import Dict, Optional, Any

from .sudoku_csp import SudokuCSP
from .sudoku_parser import SudokuParser
from ..csp import Variable
from ..csp.backtracking import (
    BacktrackingSolver,
    MRVStrategy,
    CombinedStrategy,
    LCVStrategy,
    ForwardChecking,
    ArcConsistency,
    MaintainingArcConsistency
)
from ..csp.local_search import LocalSearchSolver, SimulatedAnnealingSolver


class SudokuSolver:
    """High-level interface for solving Sudoku puzzles."""

    def __init__(self, algorithm: str = "backtracking"):
        """
        Initialize the Sudoku solver.

        Args:
            algorithm: The algorithm to use ("backtracking", "min_conflicts", "simulated_annealing")
        """
        self.algorithm = algorithm
        self.solver = self._create_solver(algorithm)
        self.solution = None
        self.statistics = {}

    def _create_solver(self, algorithm: str):
        """Create the appropriate solver based on algorithm choice."""
        if algorithm == "backtracking":
            # Use sophisticated backtracking with MRV, LCV, and MAC
            return BacktrackingSolver(
                var_selection=CombinedStrategy(),
                domain_ordering=LCVStrategy(),
                inference_strategy=MaintainingArcConsistency()
            )
        elif algorithm == "min_conflicts":
            return LocalSearchSolver(max_steps=10000, restarts=10)
        elif algorithm == "simulated_annealing":
            return SimulatedAnnealingSolver(
                initial_temperature=100.0,
                cooling_rate=0.995,
                max_iterations=50000
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def solve(self, puzzle: str, **kwargs) -> Optional[Dict[Variable, Any]]:
        """
        Solve a Sudoku puzzle.

        Args:
            puzzle: Sudoku puzzle as string
            **kwargs: Additional solver-specific parameters

        Returns:
            Solution assignment if found, None otherwise
        """
        # Parse the puzzle
        sudoku = SudokuParser.parse_from_string(puzzle)

        # Solve using selected algorithm
        if self.algorithm == "backtracking":
            solution = self.solver.solve(sudoku)
            self.statistics = self.solver.get_statistics()
        else:
            # For local search, we need to handle domains differently
            solution = self._solve_local_search(sudoku, **kwargs)

        self.solution = solution
        return solution

    def _solve_local_search(self, sudoku: SudokuCSP, **kwargs) -> Optional[Dict[Variable, Any]]:
        """Handle local search algorithms which work differently."""
        # Create a modified CSP where all variables have the full domain
        # Local search needs complete assignments
        modified_sudoku = SudokuCSP()
        # Copy initial values from the original puzzle
        for (row, col), var in sudoku.variables_dict.items():
            if sudoku.domains[var].size() == 1:
                # This cell has a fixed initial value
                value = next(iter(sudoku.domains[var].values))
                modified_sudoku.set_initial_value(row, col, value)

        solution = self.solver.solve(modified_sudoku)
        self.statistics = self.solver.get_statistics()
        return solution

    def solve_from_grid(self, grid: list[list[int]], **kwargs) -> Optional[Dict[Variable, Any]]:
        """Solve a Sudoku puzzle from a 2D grid."""
        puzzle_string = SudokuParser.format_to_string({})
        # Create empty assignment
        empty_assignment = {}
        sudoku = SudokuCSP()

        # Set initial values from grid
        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                if 1 <= value <= 9:
                    sudoku.set_initial_value(row, col, value)

        # Solve
        solution = self.solver.solve(sudoku)
        self.statistics = self.solver.get_statistics()
        self.solution = solution
        return solution

    def get_solution_string(self) -> str:
        """Get the solution as a string."""
        if self.solution is None:
            return ""
        return SudokuParser.format_to_string(self.solution)

    def get_solution_grid(self) -> list[list[int]]:
        """Get the solution as a 2D grid."""
        if self.solution is None:
            return [[0 for _ in range(9)] for _ in range(9)]
        return SudokuParser.format_to_grid(self.solution)

    def get_solution_pretty(self) -> str:
        """Get the solution in pretty printed format."""
        if self.solution is None:
            return "No solution found"
        return SudokuParser.format_pretty(self.solution)

    def print_solution(self):
        """Print the solution in a readable format."""
        if self.solution is None:
            print("No solution found")
        else:
            print(self.get_solution_pretty())

    def get_statistics(self) -> Dict[str, Any]:
        """Get solving statistics."""
        return {
            'algorithm': self.algorithm,
            'solver_stats': self.statistics,
            'has_solution': self.solution is not None
        }

    @staticmethod
    def solve_all_algorithms(puzzle: str) -> Dict[str, Dict[str, Any]]:
        """Solve the same puzzle using all available algorithms."""
        algorithms = ["backtracking", "min_conflicts", "simulated_annealing"]
        results = {}

        for algorithm in algorithms:
            try:
                solver = SudokuSolver(algorithm)
                solution = solver.solve(puzzle)
                results[algorithm] = {
                    'solution': solver.get_solution_string(),
                    'statistics': solver.get_statistics(),
                    'success': solution is not None
                }
            except Exception as e:
                results[algorithm] = {
                    'solution': None,
                    'statistics': {'error': str(e)},
                    'success': False
                }

        return results

    @staticmethod
    def benchmark_puzzles(puzzles: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Benchmark multiple puzzles with different algorithms."""
        results = {}

        for puzzle_name, puzzle_string in puzzles.items():
            print(f"Solving {puzzle_name} puzzle...")
            results[puzzle_name] = SudokuSolver.solve_all_algorithms(puzzle_string)

        return results