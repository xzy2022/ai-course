"""
Sudoku CSP Solver

This module provides a complete implementation of Sudoku as a Constraint
Satisfaction Problem using the core CSP framework.

Sudoku is a classic CSP where:
- Variables: Each cell in the 9x9 grid
- Domain: Numbers 1-9
- Constraints: Each row, column, and 3x3 subgrid must contain unique numbers
"""

from .sudoku_csp import SudokuCSP
from .sudoku_parser import SudokuParser
from .sudoku_solver import SudokuSolver

__all__ = [
    "SudokuCSP",
    "SudokuParser",
    "SudokuSolver"
]