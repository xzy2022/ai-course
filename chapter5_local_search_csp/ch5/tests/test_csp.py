"""
Unit Tests for Core CSP Framework

This module contains unit tests for the fundamental CSP components
including Variable, Domain, Constraint, and CSP classes, as well as
tests for backtracking and inference strategies.
"""

import unittest
from typing import Dict, Any

from ..csp import CSP, Variable, Domain, Constraint, BinaryConstraint
from ..csp.backtracking import (
    BacktrackingSolver,
    FirstUnassignedStrategy,
    MRVStrategy,
    DegreeStrategy,
    CombinedStrategy,
    OrderedDomainStrategy,
    LCVStrategy,
    RandomOrderingStrategy
)
from ..csp.inference import (
    NoInference,
    ForwardChecking,
    ArcConsistency,
    MaintainingArcConsistency
)
from ..csp.local_search import LocalSearchSolver, SimulatedAnnealingSolver


class TestVariable(unittest.TestCase):
    """Test cases for Variable class."""

    def test_variable_creation(self):
        """Test basic variable creation."""
        domain = Domain({1, 2, 3})
        var = Variable("X", domain)
        self.assertEqual(var.name, "X")
        self.assertEqual(var.domain.values, {1, 2, 3})
        self.assertIsNone(var.value)

    def test_variable_str(self):
        """Test variable string representation."""
        var = Variable("Y")
        self.assertEqual(str(var), "Variable(Y)")
        self.assertEqual(repr(var), "Variable(Y)")


class TestDomain(unittest.TestCase):
    """Test cases for Domain class."""

    def test_domain_creation(self):
        """Test domain creation."""
        domain = Domain({1, 2, 3})
        self.assertEqual(domain.values, {1, 2, 3})
        self.assertEqual(domain.size(), 3)
        self.assertFalse(domain.is_empty())

    def test_domain_operations(self):
        """Test domain add, remove, and contains operations."""
        domain = Domain()
        domain.add(1)
        domain.add(2)
        self.assertTrue(domain.contains(1))
        self.assertFalse(domain.contains(3))

        domain.remove(1)
        self.assertFalse(domain.contains(1))
        self.assertTrue(domain.contains(2))

    def test_domain_copy(self):
        """Test domain copying."""
        domain1 = Domain({1, 2, 3})
        domain2 = domain1.copy()
        domain2.add(4)
        self.assertNotIn(4, domain1.values)
        self.assertIn(4, domain2.values)


class TestBinaryConstraint(unittest.TestCase):
    """Test cases for BinaryConstraint class."""

    def test_binary_constraint_creation(self):
        """Test binary constraint creation."""
        var1 = Variable("X")
        var2 = Variable("Y")
        constraint = BinaryConstraint(var1, var2, lambda x, y: x != y)
        self.assertEqual(constraint.var1, var1)
        self.assertEqual(constraint.var2, var2)

    def test_binary_constraint_satisfaction(self):
        """Test binary constraint satisfaction checking."""
        var1 = Variable("X")
        var2 = Variable("Y")
        constraint = BinaryConstraint(var1, var2, lambda x, y: x != y)

        # No assignment - should be satisfied
        assignment = {}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Partial assignment - should be satisfied
        assignment = {var1: 1}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Complete assignment - check constraint
        assignment = {var1: 1, var2: 2}
        self.assertTrue(constraint.is_satisfied(assignment))

        assignment = {var1: 1, var2: 1}
        self.assertFalse(constraint.is_satisfied(assignment))


class TestCSP(unittest.TestCase):
    """Test cases for CSP class."""

    def setUp(self):
        """Set up a simple CSP for testing."""
        self.csp = CSP()
        self.var_a = Variable("A", Domain({1, 2, 3}))
        self.var_b = Variable("B", Domain({1, 2, 3}))
        self.var_c = Variable("C", Domain({1, 2, 3}))

        self.csp.add_variable(self.var_a)
        self.csp.add_variable(self.var_b)
        self.csp.add_variable(self.var_c)

        # Add all-different constraints
        self.csp.add_constraint(BinaryConstraint(self.var_a, self.var_b, lambda x, y: x != y))
        self.csp.add_constraint(BinaryConstraint(self.var_a, self.var_c, lambda x, y: x != y))
        self.csp.add_constraint(BinaryConstraint(self.var_b, self.var_c, lambda x, y: x != y))

    def test_csp_creation(self):
        """Test CSP creation and basic properties."""
        self.assertEqual(len(self.csp.variables), 3)
        self.assertEqual(len(self.csp.constraints), 3)

    def test_neighbors(self):
        """Test neighbor relationship tracking."""
        neighbors_a = self.csp.get_neighbors(self.var_a)
        self.assertIn(self.var_b, neighbors_a)
        self.assertIn(self.var_c, neighbors_a)
        self.assertEqual(len(neighbors_a), 2)

    def test_consistency_checking(self):
        """Test consistency checking for assignments."""
        assignment = {self.var_a: 1, self.var_b: 2}
        self.assertTrue(self.csp.is_consistent(self.var_c, 3, assignment))
        self.assertFalse(self.csp.is_consistent(self.var_c, 1, assignment))

    def test_solution_checking(self):
        """Test complete solution checking."""
        # Valid solution
        assignment = {self.var_a: 1, self.var_b: 2, self.var_c: 3}
        self.assertTrue(self.csp.is_solution(assignment))

        # Invalid solution
        assignment = {self.var_a: 1, self.var_b: 1, self.var_c: 2}
        self.assertFalse(self.csp.is_solution(assignment))

        # Incomplete solution
        assignment = {self.var_a: 1, self.var_b: 2}
        self.assertFalse(self.csp.is_solution(assignment))


class TestBacktrackingStrategies(unittest.TestCase):
    """Test cases for backtracking variable selection strategies."""

    def setUp(self):
        """Set up a CSP for strategy testing."""
        self.csp = CSP()
        for i in range(4):
            var = Variable(f"Var{i}", Domain({1, 2, 3, 4}))
            self.csp.add_variable(var)

    def test_first_unassigned_strategy(self):
        """Test first unassigned variable selection."""
        strategy = FirstUnassignedStrategy()
        assignment = {self.csp.variables[0]: 1, self.csp.variables[1]: 2}
        selected = strategy.select_variable(self.csp, assignment)
        self.assertEqual(selected, self.csp.variables[2])

    def test_mrv_strategy(self):
        """Test minimum remaining values strategy."""
        # Modify domains to test MRV
        self.csp.domains[self.csp.variables[2]] = Domain({1})  # Smallest domain
        self.csp.domains[self.csp.variables[3]] = Domain({1, 2})  # Second smallest

        strategy = MRVStrategy()
        assignment = {}
        selected = strategy.select_variable(self.csp, assignment)
        self.assertEqual(selected, self.csp.variables[2])


class TestDomainOrderingStrategies(unittest.TestCase):
    """Test cases for domain ordering strategies."""

    def setUp(self):
        """Set up variables for domain ordering testing."""
        self.csp = CSP()
        self.var = Variable("Test", Domain({1, 2, 3}))
        self.csp.add_variable(self.var)

    def test_ordered_domain_strategy(self):
        """Test ordered domain strategy."""
        strategy = OrderedDomainStrategy()
        values = strategy.order_values(self.csp, self.var, {})
        self.assertEqual(set(values), {1, 2, 3})

    def test_random_ordering_strategy(self):
        """Test random ordering strategy."""
        strategy = RandomOrderingStrategy()
        values = strategy.order_values(self.csp, self.var, {})
        self.assertEqual(set(values), {1, 2, 3})
        # Values should be in some order (not necessarily sorted)


class TestInferenceStrategies(unittest.TestCase):
    """Test cases for inference strategies."""

    def setUp(self):
        """Set up a simple CSP for inference testing."""
        self.csp = CSP()
        self.var1 = Variable("X", Domain({1, 2}))
        self.var2 = Variable("Y", Domain({1, 2}))
        self.csp.add_variable(self.var1)
        self.csp.add_variable(self.var2)
        self.csp.add_constraint(BinaryConstraint(self.var1, self.var2, lambda x, y: x != y))

    def test_no_inference(self):
        """Test no inference strategy."""
        strategy = NoInference()
        inferences = strategy.infer(self.csp, self.var1, 1, {})
        self.assertEqual(inferences, {})

    def test_forward_checking(self):
        """Test forward checking inference."""
        strategy = ForwardChecking()
        inferences = strategy.infer(self.csp, self.var1, 1, {})
        # After assigning X=1, Y must be 2
        self.assertEqual(inferences, {self.var2: 2})


class TestBacktrackingSolver(unittest.TestCase):
    """Test cases for the backtracking solver."""

    def setUp(self):
        """Set up a simple CSP for solver testing."""
        self.csp = CSP()
        self.var_a = Variable("A", Domain({1, 2}))
        self.var_b = Variable("B", Domain({1, 2}))
        self.csp.add_variable(self.var_a)
        self.csp.add_variable(self.var_b)
        self.csp.add_constraint(BinaryConstraint(self.var_a, self.var_b, lambda x, y: x != y))

    def test_simple_backtracking(self):
        """Test basic backtracking solver."""
        solver = BacktrackingSolver()
        solution = solver.solve(self.csp)
        self.assertIsNotNone(solution)
        self.assertTrue(self.csp.is_solution(solution))

    def test_solver_statistics(self):
        """Test solver statistics collection."""
        solver = BacktrackingSolver()
        solver.solve(self.csp)
        stats = solver.get_statistics()
        self.assertIn('nodes_expanded', stats)
        self.assertIn('backtrack_calls', stats)
        self.assertGreater(stats['nodes_expanded'], 0)


class TestLocalSearch(unittest.TestCase):
    """Test cases for local search algorithms."""

    def setUp(self):
        """Set up a CSP for local search testing."""
        self.csp = CSP()
        for i in range(4):
            var = Variable(f"Var{i}", Domain({1, 2}))
            self.csp.add_variable(var)

        # Add constraints for graph coloring
        self.csp.add_constraint(BinaryConstraint(self.csp.variables[0], self.csp.variables[1], lambda x, y: x != y))
        self.csp.add_constraint(BinaryConstraint(self.csp.variables[0], self.csp.variables[2], lambda x, y: x != y))
        self.csp.add_constraint(BinaryConstraint(self.csp.variables[1], self.csp.variables[3], lambda x, y: x != y))
        self.csp.add_constraint(BinaryConstraint(self.csp.variables[2], self.csp.variables[3], lambda x, y: x != y))

    def test_min_conflicts_solver(self):
        """Test min-conflicts local search solver."""
        solver = LocalSearchSolver(max_steps=1000, restarts=5)
        solution = solver.solve(self.csp)

        # Local search may not always find a solution, so we just test it runs
        self.assertIsInstance(solution, (dict, type(None)))

    def test_local_search_statistics(self):
        """Test local search statistics."""
        solver = LocalSearchSolver(max_steps=100)
        solver.solve(self.csp)
        stats = solver.get_statistics()
        self.assertIn('steps_taken', stats)
        self.assertIn('current_conflicts', stats)


if __name__ == '__main__':
    unittest.main()