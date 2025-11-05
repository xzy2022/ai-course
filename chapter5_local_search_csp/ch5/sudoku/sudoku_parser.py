"""
Sudoku Parser

This module provides utilities for parsing Sudoku puzzles from various formats
and converting them to/from internal representations.
"""

from typing import List, Dict, Tuple, Optional

from .sudoku_csp import SudokuCSP, SudokuVariable
from ..csp import Variable


class SudokuParser:
    """Utility class for parsing and formatting Sudoku puzzles."""

    @staticmethod
    def parse_from_string(puzzle_string: str) -> SudokuCSP:
        """
        Parse a Sudoku puzzle from a string representation.

        String format:
        - 81 characters representing the grid
        - '.' or '0' for empty cells
        - '1'-'9' for filled cells
        - Whitespace is ignored
        """
        # Remove whitespace
        cleaned = ''.join(c for c in puzzle_string if c not in ' \t\n\r')

        if len(cleaned) != 81:
            raise ValueError(f"Expected 81 characters, got {len(cleaned)}")

        sudoku = SudokuCSP()

        for i, char in enumerate(cleaned):
            row = i // 9
            col = i % 9

            if char in '123456789':
                sudoku.set_initial_value(row, col, int(char))
            elif char in '.0':
                # Empty cell, leave domain as all numbers 1-9
                pass
            else:
                raise ValueError(f"Invalid character '{char}' at position {i}")

        return sudoku

    @staticmethod
    def parse_from_grid(grid: List[List[int]]) -> SudokuCSP:
        """
        Parse a Sudoku puzzle from a 2D grid.

        Grid format:
        - 9x9 list of lists
        - 0 for empty cells
        - 1-9 for filled cells
        """
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError("Grid must be 9x9")

        sudoku = SudokuCSP()

        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                if 1 <= value <= 9:
                    sudoku.set_initial_value(row, col, value)
                elif value == 0:
                    # Empty cell, leave domain as all numbers 1-9
                    pass
                else:
                    raise ValueError(f"Invalid value {value} at position ({row}, {col})")

        return sudoku

    @staticmethod
    def parse_from_file(filename: str) -> SudokuCSP:
        """Parse a Sudoku puzzle from a file."""
        with open(filename, 'r') as f:
            content = f.read()
        return SudokuParser.parse_from_string(content)

    @staticmethod
    def format_to_string(assignment: Dict[Variable, Any]) -> str:
        """Format a Sudoku assignment as a string."""
        sudoku = SudokuCSP()
        grid = sudoku.get_assignment_grid(assignment)

        result = ""
        for row in grid:
            for val in row:
                if val == 0:
                    result += '.'
                else:
                    result += str(val)
        return result

    @staticmethod
    def format_to_grid(assignment: Dict[Variable, Any]) -> List[List[int]]:
        """Format a Sudoku assignment as a 2D grid."""
        sudoku = SudokuCSP()
        return sudoku.get_assignment_grid(assignment)

    @staticmethod
    def format_to_file(assignment: Dict[Variable, Any], filename: str):
        """Save a Sudoku assignment to a file."""
        puzzle_string = SudokuParser.format_to_string(assignment)
        with open(filename, 'w') as f:
            f.write(puzzle_string)

    @staticmethod
    def format_pretty(assignment: Dict[Variable, Any]) -> str:
        """Format a Sudoku assignment in a pretty printed format."""
        sudoku = SudokuCSP()
        grid = sudoku.get_assignment_grid(assignment)

        result = []
        for i, row in enumerate(grid):
            if i % 3 == 0 and i != 0:
                result.append("-" * 21)

            row_str = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "

                if val == 0:
                    row_str += ". "
                else:
                    row_str += f"{val} "

            result.append(row_str.strip())

        return '\n'.join(result)

    @staticmethod
    def create_sample_puzzles() -> Dict[str, str]:
        """Return a dictionary of sample Sudoku puzzles."""
        return {
            "easy": (
                "53..7...."
                "6..195..."
                ".98....6."
                "8...6...3"
                "4..8.3..1"
                "7...2...6"
                ".6....28."
                "...419..5"
                "....8..79"
            ),
            "medium": (
                ".....6.."
                "...78...."
                "..9..1..5"
                ".8..4..2."
                "4....7..."
                "..3..6.1."
                "6..2....9"
                "....4.3.."
                "....9..1."
            ),
            "hard": (
                "8........"
                "..36....."
                ".7..9.2.."
                ".5...7..."
                "....457.."
                "...1...3."
                "..1....68"
                "..85...1."
                ".9....4.."
            ),
            "expert": (
                "....8...."
                "...5.1..."
                ".8..3...."
                "....2...."
                "..6.9.5.."
                "....1...."
                "....4..7."
                "...2.3..."
                "....6...."
            )
        }