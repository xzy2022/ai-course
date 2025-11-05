"""
Graph Coloring Solver

This module provides a high-level interface for solving graph coloring problems
using various algorithms from the CSP framework.
"""

from typing import Dict, Optional, Any, List

from .graph_csp import GraphCSP
from .graph_parser import GraphParser
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


class ColoringSolver:
    """High-level interface for solving graph coloring problems."""

    def __init__(self, algorithm: str = "backtracking"):
        """
        Initialize the coloring solver.

        Args:
            algorithm: The algorithm to use ("backtracking", "min_conflicts", "simulated_annealing")
        """
        self.algorithm = algorithm
        self.solver = None
        self.graph = None
        self.solution = None
        self.statistics = {}

    def solve_graph(self, graph: GraphCSP, **kwargs) -> Optional[Dict[Variable, Any]]:
        """
        Solve a graph coloring problem.

        Args:
            graph: GraphCSP instance to solve
            **kwargs: Additional solver-specific parameters

        Returns:
            Solution assignment if found, None otherwise
        """
        self.graph = graph
        self.solver = self._create_solver(self.algorithm, **kwargs)

        # Solve using selected algorithm
        if self.algorithm == "backtracking":
            solution = self.solver.solve(graph)
            self.statistics = self.solver.get_statistics()
        else:
            # For local search, ensure we have complete assignments
            solution = self._solve_local_search(graph, **kwargs)

        self.solution = solution
        return solution

    def solve_from_adjacency_list(self, adjacency_list: Dict[str, List[str]],
                                 num_colors: int = 3, **kwargs) -> Optional[Dict[Variable, Any]]:
        """Solve a graph coloring problem from an adjacency list."""
        graph = GraphParser.parse_from_adjacency_list(adjacency_list, num_colors)
        return self.solve_graph(graph, **kwargs)

    def solve_from_edge_list(self, edges: List[tuple], vertex_ids: Optional[List[str]] = None,
                           num_colors: int = 3, **kwargs) -> Optional[Dict[Variable, Any]]:
        """Solve a graph coloring problem from an edge list."""
        graph = GraphParser.parse_from_edge_list(edges, vertex_ids, num_colors)
        return self.solve_graph(graph, **kwargs)

    def _create_solver(self, algorithm: str, **kwargs):
        """Create the appropriate solver based on algorithm choice."""
        if algorithm == "backtracking":
            # Use sophisticated backtracking with MRV, LCV, and MAC
            return BacktrackingSolver(
                var_selection=CombinedStrategy(),
                domain_ordering=LCVStrategy(),
                inference_strategy=MaintainingArcConsistency()
            )
        elif algorithm == "min_conflicts":
            max_steps = kwargs.get('max_steps', 10000)
            restarts = kwargs.get('restarts', 10)
            return LocalSearchSolver(max_steps=max_steps, restarts=restarts)
        elif algorithm == "simulated_annealing":
            return SimulatedAnnealingSolver(
                initial_temperature=kwargs.get('initial_temperature', 100.0),
                cooling_rate=kwargs.get('cooling_rate', 0.995),
                max_iterations=kwargs.get('max_iterations', 50000)
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def _solve_local_search(self, graph: GraphCSP, **kwargs) -> Optional[Dict[Variable, Any]]:
        """Handle local search algorithms which work differently."""
        solution = self.solver.solve(graph)
        self.statistics = self.solver.get_statistics()
        return solution

    def get_coloring(self) -> Dict[str, int]:
        """Get the solution as a coloring dictionary."""
        if self.solution is None or self.graph is None:
            return {}
        return self.graph.get_coloring(self.solution)

    def get_colors_used(self) -> int:
        """Get the number of colors used in the solution."""
        if self.solution is None or self.graph is None:
            return 0
        return self.graph.get_number_of_colors_used(self.solution)

    def print_solution(self):
        """Print the coloring solution."""
        if self.solution is None:
            print("No solution found")
        elif self.graph is None:
            print("No graph to display")
        else:
            self.graph.print_coloring(self.solution)

    def get_statistics(self) -> Dict[str, Any]:
        """Get solving statistics."""
        stats = {
            'algorithm': self.algorithm,
            'solver_stats': self.statistics,
            'has_solution': self.solution is not None
        }

        if self.graph:
            stats['graph_stats'] = self.graph.get_statistics()
            if self.solution:
                stats['colors_used'] = self.graph.get_number_of_colors_used(self.solution)

        return stats

    def find_minimum_colors(self, max_colors: int = 10) -> Dict[int, Dict[str, Any]]:
        """
        Find the minimum number of colors needed to color the graph.

        Returns a dictionary with results for each number of colors tested.
        """
        if self.graph is None:
            raise ValueError("No graph loaded")

        results = {}
        original_num_colors = self.graph.num_colors

        for num_colors in range(1, max_colors + 1):
            print(f"Testing with {num_colors} colors...")

            # Update graph domain
            self.graph.set_num_colors(num_colors)

            # Try to solve
            solver = ColoringSolver(self.algorithm)
            solution = solver.solve_graph(self.graph)

            results[num_colors] = {
                'solvable': solution is not None,
                'statistics': solver.get_statistics(),
                'coloring': solver.get_coloring() if solution else None
            }

            if solution is not None:
                print(f"  ✓ Solvable with {num_colors} colors")
                # Found minimum, but continue to collect all results
            else:
                print(f"  ✗ Not solvable with {num_colors} colors")

        # Restore original number of colors
        self.graph.set_num_colors(original_num_colors)

        return results

    def validate_solution(self) -> bool:
        """Validate that the current solution is a proper coloring."""
        if self.solution is None or self.graph is None:
            return False
        return self.graph.is_valid_coloring(self.solution)

    @staticmethod
    def compare_algorithms(graph: GraphCSP) -> Dict[str, Dict[str, Any]]:
        """Compare different algorithms on the same graph."""
        algorithms = ["backtracking", "min_conflicts", "simulated_annealing"]
        results = {}

        for algorithm in algorithms:
            try:
                print(f"Testing {algorithm}...")
                solver = ColoringSolver(algorithm)
                solution = solver.solve_graph(graph)
                results[algorithm] = {
                    'solution': solver.get_coloring(),
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
    def benchmark_sample_graphs() -> Dict[str, Dict[str, Any]]:
        """Benchmark all sample graphs with different algorithms."""
        sample_graphs = GraphParser.create_sample_graphs()
        results = {}

        for graph_name, graph in sample_graphs.items():
            print(f"\nBenchmarking {graph_name}...")
            print(f"Graph stats: {graph.get_statistics()}")
            results[graph_name] = ColoringSolver.compare_algorithms(graph)

        return results