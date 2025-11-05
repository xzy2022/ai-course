"""
CSP Algorithms Module

This module contains various algorithms for solving Constraint Satisfaction Problems,
including backtracking search, forward checking, and AC-3 algorithm.
"""

from .backtracking import backtracking_search

__all__ = [
    'backtracking_search'
]