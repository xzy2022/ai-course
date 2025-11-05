"""
Graph Parser

This module provides utilities for parsing graph structures from various formats
and converting them to internal representations for coloring problems.
"""

from typing import List, Dict, Set, Tuple, Optional

from .graph_csp import GraphCSP, Vertex
from ..csp import Variable


class GraphParser:
    """Utility class for parsing and formatting graphs for coloring problems."""

    @staticmethod
    def parse_from_adjacency_list(adjacency_list: Dict[str, List[str]],
                                 num_colors: int = 3) -> GraphCSP:
        """
        Parse a graph from an adjacency list.

        Format:
        {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'D'],
            'D': ['B', 'C']
        }
        """
        graph = GraphCSP(num_colors)

        # Add all vertices
        for vertex_id in adjacency_list.keys():
            graph.add_vertex(vertex_id)

        # Add all edges
        for vertex_id, neighbors in adjacency_list.items():
            for neighbor_id in neighbors:
                graph.add_edge(vertex_id, neighbor_id)

        return graph

    @staticmethod
    def parse_from_edge_list(edges: List[Tuple[str, str]],
                           vertex_ids: Optional[List[str]] = None,
                           num_colors: int = 3) -> GraphCSP:
        """
        Parse a graph from an edge list.

        Format:
        [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
        """
        graph = GraphCSP(num_colors)

        # If vertex_ids not provided, extract from edges
        if vertex_ids is None:
            vertex_set = set()
            for v1, v2 in edges:
                vertex_set.add(v1)
                vertex_set.add(v2)
            vertex_ids = list(vertex_set)

        # Add all vertices
        for vertex_id in vertex_ids:
            graph.add_vertex(vertex_id)

        # Add all edges
        for v1, v2 in edges:
            graph.add_edge(v1, v2)

        return graph

    @staticmethod
    def parse_from_adjacency_matrix(matrix: List[List[int]],
                                  vertex_ids: Optional[List[str]] = None,
                                  num_colors: int = 3) -> GraphCSP:
        """
        Parse a graph from an adjacency matrix.

        Format:
        [[0, 1, 0, 1],
         [1, 0, 1, 0],
         [0, 1, 0, 1],
         [1, 0, 1, 0]]
        """
        n = len(matrix)
        if vertex_ids is None:
            vertex_ids = [f"V{i}" for i in range(n)]

        if len(vertex_ids) != n:
            raise ValueError("Number of vertex IDs must match matrix size")

        graph = GraphCSP(num_colors)

        # Add all vertices
        for vertex_id in vertex_ids:
            graph.add_vertex(vertex_id)

        # Add edges based on adjacency matrix
        for i in range(n):
            for j in range(i + 1, n):  # Only upper triangle to avoid duplicates
                if matrix[i][j] == 1:
                    graph.add_edge(vertex_ids[i], vertex_ids[j])

        return graph

    @staticmethod
    def parse_from_file(filename: str, format: str = "edge_list",
                       num_colors: int = 3) -> GraphCSP:
        """
        Parse a graph from a file.

        Formats supported:
        - "edge_list": Each line contains two vertex IDs separated by space
        - "adjacency_list": Vertex ID followed by neighbors separated by space
        """
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if format == "edge_list":
            edges = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    edges.append((parts[0], parts[1]))
            return GraphParser.parse_from_edge_list(edges, num_colors=num_colors)

        elif format == "adjacency_list":
            adjacency_list = {}
            for line in lines:
                parts = line.split()
                if len(parts) >= 1:
                    vertex_id = parts[0]
                    neighbors = parts[1:] if len(parts) > 1 else []
                    adjacency_list[vertex_id] = neighbors
            return GraphParser.parse_from_adjacency_list(adjacency_list, num_colors)

        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def format_to_adjacency_list(graph: GraphCSP) -> Dict[str, List[str]]:
        """Format a graph as an adjacency list."""
        adjacency_list = {}
        for vertex_id, vertex in graph.vertices.items():
            neighbors = [neighbor.vertex_id for neighbor in vertex.neighbors]
            adjacency_list[vertex_id] = sorted(neighbors)
        return adjacency_list

    @staticmethod
    def format_to_edge_list(graph: GraphCSP) -> List[Tuple[str, str]]:
        """Format a graph as an edge list."""
        edges = set()
        for v1_id, v2_id in graph.edges:
            edges.add((v1_id, v2_id))
        return sorted(list(edges))

    @staticmethod
    def format_to_adjacency_matrix(graph: GraphCSP) -> Tuple[List[List[int]], List[str]]:
        """Format a graph as an adjacency matrix."""
        vertex_ids = sorted(graph.vertices.keys())
        n = len(vertex_ids)
        matrix = [[0 for _ in range(n)] for _ in range(n)]

        # Create vertex ID to index mapping
        id_to_index = {vertex_id: i for i, vertex_id in enumerate(vertex_ids)}

        # Fill matrix
        for v1_id, v2_id in graph.edges:
            i, j = id_to_index[v1_id], id_to_index[v2_id]
            matrix[i][j] = 1
            matrix[j][i] = 1

        return matrix, vertex_ids

    @staticmethod
    def create_sample_graphs() -> Dict[str, GraphCSP]:
        """Create sample graphs for testing."""
        graphs = {}

        # Complete graph K4
        k4_edges = [('A', 'B'), ('A', 'C'), ('A', 'D'),
                   ('B', 'C'), ('B', 'D'), ('C', 'D')]
        graphs['complete_k4'] = GraphParser.parse_from_edge_list(k4_edges, num_colors=4)

        # Cycle graph C5
        c5_edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'A')]
        graphs['cycle_c5'] = GraphParser.parse_from_edge_list(c5_edges, num_colors=3)

        # Bipartite graph
        bipartite_edges = [('A', 'D'), ('A', 'E'), ('B', 'D'), ('B', 'F'),
                          ('C', 'E'), ('C', 'F')]
        graphs['bipartite'] = GraphParser.parse_from_edge_list(bipartite_edges, num_colors=2)

        # Australia map coloring problem
        australia_adj = {
            'WA': ['NT', 'SA'],
            'NT': ['WA', 'SA', 'QLD'],
            'SA': ['WA', 'NT', 'QLD', 'NSW', 'VIC'],
            'QLD': ['NT', 'SA', 'NSW'],
            'NSW': ['SA', 'QLD', 'VIC'],
            'VIC': ['SA', 'NSW'],
            'TAS': []  # Tasmania is isolated
        }
        graphs['australia'] = GraphParser.parse_from_adjacency_list(australia_adj, num_colors=3)

        # Grid graph 3x3
        grid_edges = []
        for i in range(3):
            for j in range(3):
                current = f"{i}_{j}"
                # Add right edge
                if j < 2:
                    right = f"{i}_{j+1}"
                    grid_edges.append((current, right))
                # Add bottom edge
                if i < 2:
                    bottom = f"{i+1}_{j}"
                    grid_edges.append((current, bottom))
        graphs['grid_3x3'] = GraphParser.parse_from_edge_list(grid_edges, num_colors=2)

        return graphs

    @staticmethod
    def save_to_file(graph: GraphCSP, filename: str, format: str = "edge_list"):
        """Save a graph to a file."""
        if format == "edge_list":
            edges = GraphParser.format_to_edge_list(graph)
            with open(filename, 'w') as f:
                for v1, v2 in edges:
                    f.write(f"{v1} {v2}\n")

        elif format == "adjacency_list":
            adjacency_list = GraphParser.format_to_adjacency_list(graph)
            with open(filename, 'w') as f:
                for vertex_id, neighbors in adjacency_list.items():
                    line = vertex_id
                    if neighbors:
                        line += " " + " ".join(neighbors)
                    f.write(line + "\n")

        else:
            raise ValueError(f"Unsupported format: {format}")