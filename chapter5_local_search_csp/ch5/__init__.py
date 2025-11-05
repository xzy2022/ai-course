"""
Chapter 5: Constraint Satisfaction Problems (CSP)

This package provides a complete, decoupled library for solving constraint satisfaction problems
using the CSP model. The library is designed with modularity in mind, allowing easy extension
and reuse across different problem domains.

Structure:
- csp/: Core CSP framework and algorithms
- sudoku/: Sudoku-specific CSP implementation
- coloring/: Graph coloring CSP implementation
- tests/: Unit tests and integration tests
"""

from .csp import CSP, Variable, Domain, Constraint
from .backtracking import BacktrackingSolver
from .inference import InferenceStrategy

__version__ = "0.1.0"
__author__ = "AI Course Team"

__all__ = [
    "CSP",
    "Variable",
    "Domain",
    "Constraint",
    "BacktrackingSolver",
    "InferenceStrategy"
]