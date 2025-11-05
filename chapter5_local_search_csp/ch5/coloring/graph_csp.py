"""
Graph Coloring CSP Implementation

This module implements graph coloring as a Constraint Satisfaction Problem
by extending the core CSP framework with graph-specific logic.
"""

from typing import List, Dict, Set, Tuple, Any, Optional

from ..csp import CSP, Variable, Domain, Constraint


class Vertex(Variable):
    """Specialized variable for graph vertices."""

    def __init__(self, vertex_id: str, domain: Domain = None, neighbors: Set['Vertex'] = None):
        self.vertex_id = vertex_id
        self.neighbors = neighbors or set()
        super().__init__(vertex_id, domain)

    def add_neighbor(self, vertex: 'Vertex'):
        """Add an adjacent vertex."""
        self.neighbors.add(vertex)

    def is_adjacent_to(self, vertex: 'Vertex') -> bool:
        """Check if this vertex is adjacent to another vertex."""
        return vertex in self.neighbors

    def __str__(self):
        return f"Vertex({self.vertex_id})"

    def __repr__(self):
        return self.__str__()


class EdgeConstraint(Constraint):
    """Constraint that adjacent vertices must have different colors."""

    def __init__(self, vertex1: Vertex, vertex2: Vertex):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        super().__init__([vertex1, vertex2])

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        if self.vertex1 not in assignment or self.vertex2 not in assignment:
            return True

        return assignment[self.vertex1] != assignment[self.vertex2]

    def get_scope(self) -> List[Variable]:
        return [self.vertex1, self.vertex2]


class AllDifferentConstraint(Constraint):
    """Constraint that all vertices in a set must have different colors."""

    def __init__(self, vertices: List[Vertex]):
        super().__init__(vertices)

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        assigned_values = []
        for var in self.variables:
            if var in assignment and assignment[var] is not None:
                assigned_values.append(assignment[var])

        return len(assigned_values) == len(set(assigned_values))

    def get_scope(self) -> List[Variable]:
        return self.variables


class GraphCSP(CSP):
    """Complete graph coloring CSP implementation."""

    def __init__(self, num_colors: int = 3):
        super().__init__()
        self.num_colors = num_colors
        self.vertices: Dict[str, Vertex] = {}
        self.edges: Set[Tuple[str, str]] = set()
        self.default_domain = Domain(set(range(num_colors)))

    def add_vertex(self, vertex_id: str, domain: Optional[Domain] = None) -> Vertex:
        """Add a vertex to the graph."""
        if vertex_id in self.vertices:
            raise ValueError(f"Vertex {vertex_id} already exists")

        vertex_domain = domain or self.default_domain.copy()
        vertex = Vertex(vertex_id, vertex_domain)
        self.vertices[vertex_id] = vertex
        self.add_variable(vertex)
        return vertex

    def add_edge(self, vertex1_id: str, vertex2_id: str):
        """Add an edge between two vertices."""
        if vertex1_id not in self.vertices:
            self.add_vertex(vertex1_id)
        if vertex2_id not in self.vertices:
            self.add_vertex(vertex2_id)

        vertex1 = self.vertices[vertex1_id]
        vertex2 = self.vertices[vertex2_id]

        # Add adjacency relationship
        vertex1.add_neighbor(vertex2)
        vertex2.add_neighbor(vertex1)

        # Track edges
        edge = tuple(sorted([vertex1_id, vertex2_id]))
        if edge not in self.edges:
            self.edges.add(edge)
            constraint = EdgeConstraint(vertex1, vertex2)
            self.add_constraint(constraint)

    def get_vertex(self, vertex_id: str) -> Vertex:
        """Get a vertex by its ID."""
        if vertex_id not in self.vertices:
            raise ValueError(f"Vertex {vertex_id} not found")
        return self.vertices[vertex_id_id]

    def set_num_colors(self, num_colors: int):
        """Update the number of available colors."""
        self.num_colors = num_colors
        self.default_domain = Domain(set(range(num_colors)))

        # Update domains of all vertices
        for vertex in self.vertices.values():
            if vertex.domain == self.default_domain:
                vertex.domain = self.default_domain.copy()
                self.domains[vertex] = vertex.domain

    def add_all_different_constraint(self, vertex_ids: List[str]):
        """Add an all-different constraint to a set of vertices."""
        vertices = [self.vertices[vid] for vid in vertex_ids]
        constraint = AllDifferentConstraint(vertices)
        self.add_constraint(constraint)

    def get_coloring(self, assignment: Dict[Variable, Any]) -> Dict[str, int]:
        """Convert assignment to a coloring dictionary."""
        coloring = {}
        for vertex in self.variables:
            if vertex in assignment and assignment[vertex] is not None:
                coloring[vertex.vertex_id] = assignment[vertex]
        return coloring

    def get_number_of_colors_used(self, assignment: Dict[Variable, Any]) -> int:
        """Count the number of different colors used in the assignment."""
        colors_used = set()
        for vertex in self.variables:
            if vertex in assignment and assignment[vertex] is not None:
                colors_used.add(assignment[vertex])
        return len(colors_used)

    def is_valid_coloring(self, assignment: Dict[Variable, Any]) -> bool:
        """Check if the assignment is a valid coloring."""
        return self.is_solution(assignment)

    def get_conflicts(self, assignment: Dict[Variable, Any]) -> int:
        """Count the number of edges with same-colored endpoints."""
        conflicts = 0
        for v1_id, v2_id in self.edges:
            v1 = self.vertices[v1_id]
            v2 = self.vertices[v2_id]

            if v1 in assignment and v2 in assignment:
                if assignment[v1] == assignment[v2]:
                    conflicts += 1

        return conflicts

    def print_coloring(self, assignment: Dict[Variable, Any]):
        """Print the coloring assignment."""
        coloring = self.get_coloring(assignment)
        print("Graph Coloring Assignment:")
        for vertex_id, color in sorted(coloring.items()):
            print(f"  {vertex_id}: Color {color}")

        colors_used = self.get_number_of_colors_used(assignment)
        print(f"Total colors used: {colors_used}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            'num_vertices': len(self.vertices),
            'num_edges': len(self.edges),
            'num_colors': self.num_colors,
            'is_connected': self._is_connected()
        }

    def _is_connected(self) -> bool:
        """Check if the graph is connected."""
        if not self.vertices:
            return True

        # BFS traversal
        start_vertex = next(iter(self.vertices.values()))
        visited = set()
        queue = [start_vertex]

        while queue:
            current = queue.pop(0)
            if current.vertex_id not in visited:
                visited.add(current.vertex_id)
                queue.extend([neighbor for neighbor in current.neighbors
                            if neighbor.vertex_id not in visited])

        return len(visited) == len(self.vertices)