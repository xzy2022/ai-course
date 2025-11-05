"""
Unit tests for heuristic-enabled backtracking search.

Each heuristic (MRV, degree, LCV) is verified independently to ensure the
selection or ordering logic matches expectations.
"""

import os
import sys
import unittest
from typing import Dict, Set

# Ensure project root is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value  # noqa: E402
from csp.algorithms.heuristic_backtracking import (  # noqa: E402
    order_domain_values,
    select_unassigned_variable,
)


def build_neighbors(csp: CSP) -> Dict[Variable, Set[Variable]]:
    neighbors: Dict[Variable, Set[Variable]] = {var: set() for var in csp.variables}
    for constraint in csp.constraints:
        scope = constraint.scope
        for var in scope:
            others = set(scope) - {var}
            neighbors[var].update(others)
    return neighbors


class HeuristicSelectionTests(unittest.TestCase):
    def test_mrv_prefers_smallest_domain(self) -> None:
        csp = CSP()
        csp.add_variable("A", {1})
        csp.add_variable("B", {1, 2})
        csp.add_variable("C", {1, 2, 3})
        csp.add_constraint(Constraint(("A", "B"), lambda a, b: a != b))
        csp.add_constraint(Constraint(("A", "C"), lambda a, c: a != c))

        neighbors = build_neighbors(csp)
        var, legal_values = select_unassigned_variable(
            csp,
            assignment={},
            neighbors=neighbors,
            use_mrv=True,
            use_degree=False,
        )

        self.assertEqual(var, "A")
        self.assertEqual(legal_values, [1])

    def test_degree_prefers_most_constrained_variable(self) -> None:
        csp = CSP()
        for var in ("X", "Y", "Z"):
            csp.add_variable(var, {1, 2, 3})
        csp.add_constraint(Constraint(("X", "Y"), lambda x, y: x != y))
        csp.add_constraint(Constraint(("X", "Z"), lambda x, z: x != z))

        neighbors = build_neighbors(csp)
        var, _ = select_unassigned_variable(
            csp,
            assignment={},
            neighbors=neighbors,
            use_mrv=False,
            use_degree=True,
        )

        self.assertEqual(var, "X")

    def test_lcv_orders_values_by_lowest_impact(self) -> None:
        csp = CSP()
        csp.add_variable("X", {1, 2, 3})
        csp.add_variable("Y", {1, 2})
        csp.add_variable("Z", {1, 2, 3})
        csp.add_constraint(Constraint(("X", "Y"), lambda x, y: x != y))
        csp.add_constraint(Constraint(("X", "Z"), lambda x, z: x != z))

        neighbors = build_neighbors(csp)
        ordered = order_domain_values(
            csp,
            var="X",
            legal_values=[1, 2, 3],
            assignment={},
            neighbors=neighbors,
            use_lcv=True,
        )

        self.assertEqual(ordered[0], 3)
        self.assertEqual(set(ordered), {1, 2, 3})


if __name__ == "__main__":
    unittest.main()
