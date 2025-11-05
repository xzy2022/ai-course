"""
Graph Coloring CSP Solver

This module provides a complete implementation of the graph coloring problem
as a Constraint Satisfaction Problem using the core CSP framework.

Graph coloring is a classic CSP where:
- Variables: Each vertex in the graph
- Domain: Available colors
- Constraints: Adjacent vertices must have different colors
"""

from .graph_csp import GraphCSP, Vertex
from .graph_parser import GraphParser
from .coloring_solver import ColoringSolver

__all__ = [
    "GraphCSP",
    "Vertex",
    "GraphParser",
    "ColoringSolver"
]