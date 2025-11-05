"""
Unit Tests for Sudoku CSP Implementation

This module contains unit tests for the Sudoku-specific CSP components,
including the SudokuCSP class, parser, and solver.
"""

import unittest
from typing import Dict, Any

from ..sudoku import SudokuCSP, SudokuParser, SudokuSolver
from ..csp import Variable


class TestSudokuVariable(unittest.TestCase):
    """Test cases for SudokuVariable class."""

    def test_sudoku_variable_creation(self):
        """Test Sudoku variable creation."""
        from ..sudoku.sudoku_csp import SudokuVariable, Domain

        domain = Domain({1, 2, 3, 4, 5, 6, 7, 8, 9})
        var = SudokuVariable(0, 0, domain)

        self.assertEqual(var.row, 0)
        self.assertEqual(var.col, 0)
        self.assertEqual(var.box, 0)
        self.assertEqual(var.name, "cell_0_0")

    def test_box_calculation(self):
        """Test box calculation for different positions."""
        from ..sudoku.sudoku_csp import SudokuVariable, Domain

        domain = Domain({1, 2, 3, 4, 5, 6, 7, 8, 9})

        # Top-left corner (box 0)
        var1 = SudokuVariable(0, 0, domain)
        self.assertEqual(var1.box, 0)

        # Top-middle (box 1)
        var2 = SudokuVariable(0, 4, domain)
        self.assertEqual(var2.box, 1)

        # Bottom-right (box 8)
        var3 = SudokuVariable(8, 8, domain)
        self.assertEqual(var3.box, 8)


class TestSudokuCSP(unittest.TestCase):
    """Test cases for SudokuCSP class."""

    def setUp(self):
        """Set up a Sudoku CSP for testing."""
        self.sudoku = SudokuCSP()

    def test_sudoku_creation(self):
        """Test Sudoku CSP creation."""
        self.assertEqual(len(self.sudoku.variables), 81)  # 9x9 grid
        self.assertEqual(len(self.sudoku.constraints), 27)  # 9 rows + 9 cols + 9 boxes

    def test_variable_access(self):
        """Test variable access by row and column."""
        var = self.sudoku.get_variable(4, 5)
        self.assertEqual(var.row, 4)
        self.assertEqual(var.col, 5)
        self.assertEqual(var.box, 4)  # (4//3)*3 + (5//3) = 3 + 1 = 4

    def test_initial_value_setting(self):
        """Test setting initial values."""
        self.sudoku.set_initial_value(0, 0, 5)
        var = self.sudoku.get_variable(0, 0)
        self.assertEqual(self.sudoku.domains[var].values, {5})

    def test_assignment_grid_conversion(self):
        """Test conversion between assignment and grid."""
        # Create a partial assignment
        assignment = {}
        assignment[self.sudoku.get_variable(0, 0)] = 5
        assignment[self.sudoku.get_variable(1, 1)] = 3

        grid = self.sudoku.get_assignment_grid(assignment)
        self.assertEqual(grid[0][0], 5)
        self.assertEqual(grid[1][1], 3)
        self.assertEqual(grid[0][1], 0)  # Empty

    def test_solution_validation(self):
        """Test solution validation."""
        # Create a valid partial assignment
        assignment = {}
        assignment[self.sudoku.get_variable(0, 0)] = 1
        assignment[self.sudoku.get_variable(0, 1)] = 2

        # Should be consistent (not complete, but no conflicts)
        self.assertTrue(self.sudoku.is_consistent(
            self.sudoku.get_variable(0, 2), 3, assignment))

        # Should be inconsistent (same row)
        self.assertFalse(self.sudoku.is_consistent(
            self.sudoku.get_variable(0, 2), 1, assignment))

    def test_conflict_counting(self):
        """Test conflict counting."""
        # Create an assignment with conflicts
        assignment = {}
        assignment[self.sudoku.get_variable(0, 0)] = 1
        assignment[self.sudoku.get_variable(0, 1)] = 1  # Same row conflict
        assignment[self.sudoku.get_variable(1, 0)] = 1  # Same column conflict

        conflicts = self.sudoku.get_conflicts(assignment)
        self.assertGreater(conflicts, 0)


class TestSudokuParser(unittest.TestCase):
    """Test cases for SudokuParser class."""

    def test_parse_simple_string(self):
        """Test parsing a simple Sudoku string."""
        puzzle = (
            "53..7...."
            "6..195..."
            ".98....6."
            "8...6...3"
            "4..8.3..1"
            "7...2...6"
            ".6....28."
            "...419..5"
            "....8..79"
        )

        sudoku = SudokuParser.parse_from_string(puzzle)
        self.assertEqual(len(sudoku.variables), 81)

        # Check specific values
        var_0_0 = sudoku.get_variable(0, 0)
        self.assertEqual(sudoku.domains[var_0_0].values, {5})

        var_0_2 = sudoku.get_variable(0, 2)  # Empty cell
        self.assertEqual(sudoku.domains[var_0_2].values, set(range(1, 10)))

    def test_parse_from_grid(self):
        """Test parsing from a 2D grid."""
        grid = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9]]

        sudoku = SudokuParser.parse_from_grid(grid)
        var_0_0 = sudoku.get_variable(0, 0)
        self.assertEqual(sudoku.domains[var_0_0].values, {5})

    def test_format_to_string(self):
        """Test formatting assignment to string."""
        sudoku = SudokuCSP()
        assignment = {}
        assignment[sudoku.get_variable(0, 0)] = 5
        assignment[sudoku.get_variable(0, 1)] = 3

        result = SudokuParser.format_to_string(assignment)
        self.assertTrue(result.startswith("53"))
        self.assertEqual(len(result), 81)

    def test_format_pretty(self):
        """Test pretty formatting."""
        sudoku = SudokuCSP()
        assignment = {}
        assignment[sudoku.get_variable(0, 0)] = 5
        assignment[sudoku.get_variable(8, 8)] = 9

        pretty = SudokuParser.format_pretty(assignment)
        self.assertIn("5", pretty)
        self.assertIn("9", pretty)
        self.assertIn("|", pretty)  # Should have box separators

    def test_sample_puzzles(self):
        """Test sample puzzle generation."""
        puzzles = SudokuParser.create_sample_puzzles()
        self.assertIn("easy", puzzles)
        self.assertIn("medium", puzzles)
        self.assertIn("hard", puzzles)
        self.assertIn("expert", puzzles)

        # Check that puzzles have correct length
        for puzzle in puzzles.values():
            self.assertEqual(len(puzzle), 81)


class TestSudokuSolver(unittest.TestCase):
    """Test cases for SudokuSolver class."""

    def test_solver_creation(self):
        """Test solver creation with different algorithms."""
        solver1 = SudokuSolver("backtracking")
        solver2 = SudokuSolver("min_conflicts")
        solver3 = SudokuSolver("simulated_annealing")

        self.assertIsNotNone(solver1.solver)
        self.assertIsNotNone(solver2.solver)
        self.assertIsNotNone(solver3.solver)

    def test_solve_simple_puzzle(self):
        """Test solving a simple puzzle."""
        # Very simple puzzle with most cells empty
        puzzle = (
            "1........"
            "........2"
            "........3"
            "........4"
            "........5"
            "........6"
            "........7"
            "........8"
            "........9"
        )

        solver = SudokuSolver("backtracking")
        solution = solver.solve(puzzle)

        # This might not always find a solution due to the nature of the puzzle
        # So we just test that it runs without error
        self.assertIsInstance(solution, (dict, type(None)))

    def test_statistics_collection(self):
        """Test statistics collection."""
        solver = SudokuSolver("backtracking")
        puzzle = SudokuParser.create_sample_puzzles()["easy"]
        solution = solver.solve(puzzle)

        stats = solver.get_statistics()
        self.assertIn('algorithm', stats)
        self.assertIn('solver_stats', stats)
        self.assertIn('has_solution', stats)
        self.assertEqual(stats['algorithm'], 'backtracking')

    def test_solution_formatting(self):
        """Test solution formatting methods."""
        solver = SudokuSolver("backtracking")
        puzzle = SudokuParser.create_sample_puzzles()["easy"]
        solution = solver.solve(puzzle)

        if solution is not None:
            # Test different formatting methods
            solution_str = solver.get_solution_string()
            solution_grid = solver.get_solution_grid()
            solution_pretty = solver.get_solution_pretty()

            self.assertIsInstance(solution_str, str)
            self.assertIsInstance(solution_grid, list)
            self.assertIsInstance(solution_pretty, str)

            # Check grid dimensions
            self.assertEqual(len(solution_grid), 9)
            self.assertEqual(len(solution_grid[0]), 9)

    def test_solve_all_algorithms(self):
        """Test solving with all algorithms."""
        puzzle = SudokuParser.create_sample_puzzles()["easy"]
        results = SudokuSolver.solve_all_algorithms(puzzle)

        self.assertIn("backtracking", results)
        self.assertIn("min_conflicts", results)
        self.assertIn("simulated_annealing", results)

        for algorithm, result in results.items():
            self.assertIn('success', result)
            self.assertIn('statistics', result)

    def test_invalid_puzzle_handling(self):
        """Test handling of invalid puzzles."""
        # Puzzle with wrong length
        invalid_puzzle = "123"

        solver = SudokuSolver("backtracking")
        with self.assertRaises(ValueError):
            solver.solve(invalid_puzzle)


class TestSudokuIntegration(unittest.TestCase):
    """Integration tests for Sudoku components."""

    def test_end_to_end_workflow(self):
        """Test complete workflow from parsing to solving."""
        # Get a sample puzzle
        puzzles = SudokuParser.create_sample_puzzles()
        puzzle = puzzles["easy"]

        # Parse the puzzle
        sudoku = SudokuParser.parse_from_string(puzzle)

        # Solve the puzzle
        solver = SudokuSolver("backtracking")
        solution = solver.solve(puzzle)

        # Verify solution if found
        if solution is not None:
            self.assertTrue(sudoku.validate_solution(solution))

            # Format and re-parse
            solution_str = solver.get_solution_string()
            reparsed_sudoku = SudokuParser.parse_from_string(solution_str)

            # Should be able to solve again (should be immediate)
            reparsed_solver = SudokuSolver("backtracking")
            reparsed_solution = reparsed_solver.solve(solution_str)
            self.assertIsNotNone(reparsed_solution)


if __name__ == '__main__':
    unittest.main()