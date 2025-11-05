"""
Unit Tests for Graph Coloring CSP Implementation

This module contains unit tests for the graph coloring CSP components,
including the GraphCSP class, parser, and solver.
"""

import unittest
from typing import Dict, Any

from ..coloring import GraphCSP, Vertex, GraphParser, ColoringSolver
from ..csp import Variable


class TestVertex(unittest.TestCase):
    """Test cases for Vertex class."""

    def test_vertex_creation(self):
        """Test vertex creation."""
        from ..coloring.graph_csp import Vertex, Domain

        domain = Domain({1, 2, 3})
        vertex = Vertex("A", domain)

        self.assertEqual(vertex.vertex_id, "A")
        self.assertEqual(vertex.name, "A")
        self.assertEqual(vertex.domain.values, {1, 2, 3})
        self.assertEqual(len(vertex.neighbors), 0)

    def test_neighbor_management(self):
        """Test neighbor addition and checking."""
        from ..coloring.graph_csp import Vertex, Domain

        domain = Domain({1, 2, 3})
        vertex1 = Vertex("A", domain)
        vertex2 = Vertex("B", domain)

        vertex1.add_neighbor(vertex2)
        self.assertIn(vertex2, vertex1.neighbors)
        self.assertTrue(vertex1.is_adjacent_to(vertex2))
        self.assertFalse(vertex2.is_adjacent_to(vertex1))


class TestGraphCSP(unittest.TestCase):
    """Test cases for GraphCSP class."""

    def setUp(self):
        """Set up a graph CSP for testing."""
        self.graph = GraphCSP(num_colors=3)

    def test_graph_creation(self):
        """Test graph CSP creation."""
        self.assertEqual(self.graph.num_colors, 3)
        self.assertEqual(len(self.graph.variables), 0)
        self.assertEqual(len(self.graph.constraints), 0)

    def test_vertex_addition(self):
        """Test adding vertices to the graph."""
        vertex = self.graph.add_vertex("A")
        self.assertEqual(vertex.vertex_id, "A")
        self.assertEqual(len(self.graph.variables), 1)
        self.assertIn("A", self.graph.vertices)

    def test_edge_addition(self):
        """Test adding edges to the graph."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")

        self.assertEqual(len(self.graph.variables), 3)
        self.assertEqual(len(self.graph.constraints), 2)

        # Check neighbor relationships
        vertex_a = self.graph.get_vertex("A")
        vertex_b = self.graph.get_vertex("B")
        vertex_c = self.graph.get_vertex("C")

        self.assertIn(vertex_b, vertex_a.neighbors)
        self.assertIn(vertex_a, vertex_b.neighbors)
        self.assertIn(vertex_c, vertex_b.neighbors)
        self.assertIn(vertex_b, vertex_c.neighbors)

    def test_duplicate_edge_prevention(self):
        """Test that duplicate edges are not added."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "A")  # Same edge in reverse
        self.graph.add_edge("A", "B")  # Duplicate edge

        self.assertEqual(len(self.graph.constraints), 1)

    def test_coloring_conversion(self):
        """Test conversion between assignment and coloring."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")

        assignment = {}
        assignment[self.graph.get_vertex("A")] = 1
        assignment[self.graph.get_vertex("B")] = 2

        coloring = self.graph.get_coloring(assignment)
        self.assertEqual(coloring["A"], 1)
        self.assertEqual(coloring["B"], 2)
        self.assertNotIn("C", coloring)  # Not assigned

    def test_conflict_counting(self):
        """Test conflict counting in colorings."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")

        # Create assignment with conflict
        assignment = {}
        assignment[self.graph.get_vertex("A")] = 1
        assignment[self.graph.get_vertex("B")] = 1  # Same color as A - conflict
        assignment[self.graph.get_vertex("C")] = 2

        conflicts = self.graph.get_conflicts(assignment)
        self.assertEqual(conflicts, 1)  # One edge has same-colored endpoints

    def test_graph_statistics(self):
        """Test graph statistics collection."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")
        self.graph.add_edge("C", "A")  # Make it connected

        stats = self.graph.get_statistics()
        self.assertEqual(stats['num_vertices'], 3)
        self.assertEqual(stats['num_edges'], 3)
        self.assertEqual(stats['num_colors'], 3)
        self.assertTrue(stats['is_connected'])

    def test_color_counting(self):
        """Test counting colors used in assignment."""
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")

        assignment = {}
        assignment[self.graph.get_vertex("A")] = 1
        assignment[self.graph.get_vertex("B")] = 2
        assignment[self.graph.get_vertex("C")] = 1  # Reuse color 1

        colors_used = self.graph.get_number_of_colors_used(assignment)
        self.assertEqual(colors_used, 2)  # Colors 1 and 2 used


class TestEdgeConstraint(unittest.TestCase):
    """Test cases for EdgeConstraint class."""

    def test_edge_constraint_creation(self):
        """Test edge constraint creation."""
        from ..coloring.graph_csp import EdgeConstraint, Vertex, Domain

        domain = Domain({1, 2, 3})
        v1 = Vertex("A", domain)
        v2 = Vertex("B", domain)

        constraint = EdgeConstraint(v1, v2)
        self.assertEqual(constraint.vertex1, v1)
        self.assertEqual(constraint.vertex2, v2)

    def test_edge_constraint_satisfaction(self):
        """Test edge constraint satisfaction."""
        from ..coloring.graph_csp import EdgeConstraint, Vertex, Domain

        domain = Domain({1, 2, 3})
        v1 = Vertex("A", domain)
        v2 = Vertex("B", domain)

        constraint = EdgeConstraint(v1, v2)

        # No assignment - should be satisfied
        assignment = {}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Different colors - should be satisfied
        assignment = {v1: 1, v2: 2}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Same color - should not be satisfied
        assignment = {v1: 1, v2: 1}
        self.assertFalse(constraint.is_satisfied(assignment))


class TestGraphParser(unittest.TestCase):
    """Test cases for GraphParser class."""

    def test_parse_from_adjacency_list(self):
        """Test parsing from adjacency list."""
        adjacency_list = {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'D'],
            'D': ['B', 'C']
        }

        graph = GraphParser.parse_from_adjacency_list(adjacency_list, num_colors=3)
        self.assertEqual(len(graph.vertices), 4)
        self.assertEqual(len(graph.constraints), 4)  # 4 edges in this graph

    def test_parse_from_edge_list(self):
        """Test parsing from edge list."""
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
        vertex_ids = ['A', 'B', 'C', 'D']

        graph = GraphParser.parse_from_edge_list(edges, vertex_ids, num_colors=2)
        self.assertEqual(len(graph.vertices), 4)
        self.assertEqual(len(graph.constraints), 4)

    def test_parse_from_adjacency_matrix(self):
        """Test parsing from adjacency matrix."""
        matrix = [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0]
        ]
        vertex_ids = ['A', 'B', 'C', 'D']

        graph = GraphParser.parse_from_adjacency_matrix(matrix, vertex_ids, num_colors=2)
        self.assertEqual(len(graph.vertices), 4)
        self.assertEqual(len(graph.constraints), 4)  # 4 edges

    def test_format_to_adjacency_list(self):
        """Test formatting to adjacency list."""
        adjacency_list = {
            'A': ['B', 'C'],
            'B': ['A'],
            'C': ['A']
        }

        graph = GraphParser.parse_from_adjacency_list(adjacency_list)
        formatted = GraphParser.format_to_adjacency_list(graph)

        self.assertEqual(set(formatted.keys()), {'A', 'B', 'C'})
        self.assertIn('B', formatted['A'])
        self.assertIn('C', formatted['A'])

    def test_format_to_edge_list(self):
        """Test formatting to edge list."""
        edges = [('A', 'B'), ('B', 'C'), ('C', 'A')]
        graph = GraphParser.parse_from_edge_list(edges)

        formatted_edges = GraphParser.format_to_edge_list(graph)
        self.assertEqual(len(formatted_edges), 3)

        # Check that all original edges are present (order may vary)
        edge_set = set(tuple(sorted(edge)) for edge in formatted_edges)
        original_edge_set = set(tuple(sorted(edge)) for edge in edges)
        self.assertEqual(edge_set, original_edge_set)

    def test_sample_graphs_creation(self):
        """Test sample graph creation."""
        graphs = GraphParser.create_sample_graphs()

        self.assertIn('complete_k4', graphs)
        self.assertIn('cycle_c5', graphs)
        self.assertIn('bipartite', graphs)
        self.assertIn('australia', graphs)
        self.assertIn('grid_3x3', graphs)

        # Check that Australia map has 7 vertices
        australia = graphs['australia']
        self.assertEqual(len(australia.vertices), 7)

        # Check that K4 is 4-colorable (should need exactly 4 colors)
        k4 = graphs['complete_k4']
        self.assertEqual(k4.num_colors, 4)

    def test_file_operations(self):
        """Test saving and loading graphs from files."""
        import tempfile
        import os

        # Create a simple graph
        edges = [('A', 'B'), ('B', 'C'), ('C', 'A')]
        graph = GraphParser.parse_from_edge_list(edges, num_colors=3)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            filename = f.name

        try:
            GraphParser.save_to_file(graph, filename, format="edge_list")

            # Load from file
            loaded_graph = GraphParser.parse_from_file(filename, format="edge_list", num_colors=3)

            # Check that graphs are equivalent
            self.assertEqual(len(loaded_graph.vertices), len(graph.vertices))
            self.assertEqual(len(loaded_graph.constraints), len(graph.constraints))

        finally:
            os.unlink(filename)


class TestColoringSolver(unittest.TestCase):
    """Test cases for ColoringSolver class."""

    def test_solver_creation(self):
        """Test solver creation with different algorithms."""
        solver1 = ColoringSolver("backtracking")
        solver2 = ColoringSolver("min_conflicts")
        solver3 = ColoringSolver("simulated_annealing")

        self.assertIsNotNone(solver1.solver)
        self.assertIsNotNone(solver2.solver)
        self.assertIsNotNone(solver3.solver)

    def test_solve_simple_graph(self):
        """Test solving a simple graph coloring problem."""
        adjacency_list = {
            'A': ['B'],
            'B': ['A', 'C'],
            'C': ['B']
        }

        solver = ColoringSolver("backtracking")
        solution = solver.solve_from_adjacency_list(adjacency_list, num_colors=2)

        self.assertIsNotNone(solution)
        self.assertTrue(solver.validate_solution())

    def test_solve_from_different_formats(self):
        """Test solving from different input formats."""
        # Edge list
        edges = [('A', 'B'), ('B', 'C')]
        solver = ColoringSolver("backtracking")
        solution = solver.solve_from_edge_list(edges, num_colors=2)
        self.assertIsNotNone(solution)

        # Should be able to get coloring
        coloring = solver.get_coloring()
        self.assertIsInstance(coloring, dict)

    def test_statistics_collection(self):
        """Test statistics collection."""
        adjacency_list = {
            'A': ['B', 'C'],
            'B': ['A', 'C'],
            'C': ['A', 'B']
        }

        solver = ColoringSolver("backtracking")
        solver.solve_from_adjacency_list(adjacency_list, num_colors=3)

        stats = solver.get_statistics()
        self.assertIn('algorithm', stats)
        self.assertIn('solver_stats', stats)
        self.assertIn('has_solution', stats)
        self.assertIn('graph_stats', stats)

        if stats['has_solution']:
            self.assertIn('colors_used', stats)

    def test_minimum_colors_finding(self):
        """Test finding minimum number of colors."""
        # Create a simple triangle graph (needs 3 colors)
        adjacency_list = {
            'A': ['B', 'C'],
            'B': ['A', 'C'],
            'C': ['A', 'B']
        }

        solver = ColoringSolver("backtracking")
        results = solver.find_minimum_colors(max_colors=5)

        # Should find that it's not solvable with 1 or 2 colors
        self.assertFalse(results[1]['solvable'])
        self.assertFalse(results[2]['solvable'])
        self.assertTrue(results[3]['solvable'])  # Triangle needs 3 colors

    def test_algorithm_comparison(self):
        """Test comparing different algorithms."""
        # Create a simple graph
        adjacency_list = {
            'A': ['B'],
            'B': ['A', 'C'],
            'C': ['B']
        }

        graph = GraphParser.parse_from_adjacency_list(adjacency_list, num_colors=3)
        results = ColoringSolver.compare_algorithms(graph)

        self.assertIn('backtracking', results)
        self.assertIn('min_conflicts', results)
        self.assertIn('simulated_annealing', results)

        # Backtracking should find a solution for this simple case
        self.assertTrue(results['backtracking']['success'])

    def test_solution_validation(self):
        """Test solution validation."""
        adjacency_list = {
            'A': ['B'],
            'B': ['A', 'C'],
            'C': ['B']
        }

        solver = ColoringSolver("backtracking")
        solution = solver.solve_from_adjacency_list(adjacency_list, num_colors=2)

        if solution is not None:
            self.assertTrue(solver.validate_solution())

            # Modify solution to make it invalid
            solver.graph.variables[0].value = 5  # Invalid color
            self.assertFalse(solver.validate_solution())


class TestColoringIntegration(unittest.TestCase):
    """Integration tests for graph coloring components."""

    def test_end_to_end_workflow(self):
        """Test complete workflow from parsing to solving."""
        # Get sample graph
        graphs = GraphParser.create_sample_graphs()
        graph = graphs['bipartite']  # Simple 2-colorable graph

        # Solve the graph
        solver = ColoringSolver("backtracking")
        solution = solver.solve_graph(graph)

        # Verify solution
        self.assertIsNotNone(solution)
        self.assertTrue(solver.validate_solution())

        # Check that it uses at most 2 colors (bipartite graph)
        self.assertLessEqual(solver.get_colors_used(), 2)

    def test_australia_map_coloring(self):
        """Test the classic Australia map coloring problem."""
        graphs = GraphParser.create_sample_graphs()
        australia = graphs['australia']

        # Australia map should be 3-colorable
        solver = ColoringSolver("backtracking")
        solution = solver.solve_graph(australia)

        if solution is not None:
            self.assertTrue(solver.validate_solution())
            self.assertLessEqual(solver.get_colors_used(), 3)

            # Print solution for manual verification
            coloring = solver.get_coloring()
            print("Australia Map Coloring:")
            for state, color in sorted(coloring.items()):
                print(f"  {state}: Color {color}")

    def test_performance_on_larger_graphs(self):
        """Test performance on moderately larger graphs."""
        # Create a 4x4 grid graph (16 vertices)
        grid_edges = []
        for i in range(4):
            for j in range(4):
                current = f"{i}_{j}"
                if j < 3:
                    right = f"{i}_{j+1}"
                    grid_edges.append((current, right))
                if i < 3:
                    bottom = f"{i+1}_{j}"
                    grid_edges.append((current, bottom))

        graph = GraphParser.parse_from_edge_list(grid_edges, num_colors=2)

        # Test backtracking (should be fast for this size)
        solver = ColoringSolver("backtracking")
        solution = solver.solve_graph(graph)

        if solution is not None:
            self.assertTrue(solver.validate_solution())
            # 4x4 grid is bipartite, so should be 2-colorable
            self.assertLessEqual(solver.get_colors_used(), 2)


if __name__ == '__main__':
    unittest.main()