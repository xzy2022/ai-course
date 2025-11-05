"""
Core CSP (Constraint Satisfaction Problem) Framework

This module provides the fundamental components for modeling and solving
constraint satisfaction problems in a decoupled, modular way.
"""

from .csp import CSP, Variable, Domain, Constraint
from .backtracking import BacktrackingSolver
from .inference import InferenceStrategy
from .local_search import LocalSearchSolver

__all__ = [
    "CSP",
    "Variable",
    "Domain",
    "Constraint",
    "BacktrackingSolver",
    "InferenceStrategy",
    "LocalSearchSolver"
]