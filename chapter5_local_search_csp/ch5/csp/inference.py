"""
Inference Strategies for CSPs

This module implements various inference techniques that can be combined
with backtracking to prune the search space and improve efficiency.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

from .csp import CSP, Variable


class InferenceStrategy(ABC):
    """Abstract base class for inference strategies."""

    @abstractmethod
    def infer(self, csp: CSP, variable: Variable, value: Any,
             assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        """
        Perform inference after assigning value to variable.
        Returns dictionary of inferred assignments, or None if failure detected.
        """
        pass


class NoInference(InferenceStrategy):
    """No inference - returns empty dictionary."""

    def infer(self, csp: CSP, variable: Variable, value: Any,
             assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        return {}


class ForwardChecking(InferenceStrategy):
    """Forward checking inference."""

    def infer(self, csp: CSP, variable: Variable, value: Any,
             assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        inferences = {}
        assignment_copy = assignment.copy()
        assignment_copy[variable] = value

        for neighbor in csp.get_neighbors(variable):
            if neighbor not in assignment:
                # Remove values from neighbor's domain that conflict with current assignment
                conflicting_values = set()
                for neighbor_value in csp.domains[neighbor].values:
                    if not csp.is_consistent(neighbor, neighbor_value, assignment_copy):
                        conflicting_values.add(neighbor_value)

                # If domain becomes empty, return failure
                if csp.domains[neighbor].size() - len(conflicting_values) == 0:
                    return None

                # If only one value remains, make that an inference
                remaining_values = csp.domains[neighbor].values - conflicting_values
                if len(remaining_values) == 1:
                    inferred_value = remaining_values.pop()
                    inferences[neighbor] = inferred_value

        return inferences


class ArcConsistency(InferenceStrategy):
    """Arc consistency (AC-3) inference."""

    def infer(self, csp: CSP, variable: Variable, value: Any,
             assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        # Store original domains to restore later
        original_domains = {var: domain.copy() for var, domain in csp.domains.items()}

        # Apply forward checking first
        fc_inferences = ForwardChecking().infer(csp, variable, value, assignment)
        if fc_inferences is None:
            return None

        # Apply FC inferences to domains
        for inf_var, inf_val in fc_inferences.items():
            csp.domains[inf_var] = {inf_val}

        # Run AC-3 on remaining unassigned variables
        if self._ac3(csp, assignment):
            # Collect single-value domains as inferences
            inferences = fc_inferences.copy()
            for var in csp.variables:
                if var not in assignment and csp.domains[var].size() == 1:
                    inferences[var] = next(iter(csp.domains[var].values))
            return inferences
        else:
            # Restore original domains and return failure
            for var, domain in original_domains.items():
                csp.domains[var] = domain
            return None

    def _ac3(self, csp: CSP, assignment: Dict[Variable, Any]) -> bool:
        """AC-3 algorithm for arc consistency."""
        from collections import deque

        # Initialize queue with all arcs (Xi, Xj) where Xi is unassigned
        queue = deque()
        for var in csp.variables:
            if var not in assignment:
                for neighbor in csp.get_neighbors(var):
                    if neighbor not in assignment:
                        queue.append((var, neighbor))

        while queue:
            xi, xj = queue.popleft()

            if self._revise(csp, xi, xj):
                if csp.domains[xi].is_empty():
                    return False

                # Add all neighboring arcs (Xk, Xi) to queue
                for xk in csp.get_neighbors(xi):
                    if xk != xj and xk not in assignment:
                        queue.append((xk, xi))

        return True

    def _revise(self, csp: CSP, xi: Variable, xj: Variable) -> bool:
        """Revise domain of Xi by removing values that have no supporting values in Xj."""
        revised = False
        values_to_remove = set()

        for xi_value in csp.domains[xi].values:
            has_support = False
            for xj_value in csp.domains[xj].values:
                if csp.is_consistent(xi, xi_value, {xj: xj_value}):
                    has_support = True
                    break

            if not has_support:
                values_to_remove.add(xi_value)

        if values_to_remove:
            for value in values_to_remove:
                csp.domains[xi].remove(value)
            revised = True

        return revised


class MaintainingArcConsistency(InferenceStrategy):
    """Maintaining Arc Consistency (MAC) inference."""

    def infer(self, csp: CSP, variable: Variable, value: Any,
             assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        # Store original domains
        original_domains = {var: domain.copy() for var, domain in csp.domains.items()}

        # Set the assigned variable's domain to just the assigned value
        csp.domains[variable] = {value}

        # Run AC-3 on all arcs
        if self._ac3_all(csp, assignment):
            # Collect inferences (single-value domains for unassigned variables)
            inferences = {}
            for var in csp.variables:
                if var not in assignment and csp.domains[var].size() == 1:
                    inferences[var] = next(iter(csp.domains[var].values))
            return inferences
        else:
            # Restore original domains and return failure
            for var, domain in original_domains.items():
                csp.domains[var] = domain
            return None

    def _ac3_all(self, csp: CSP, assignment: Dict[Variable, Any]) -> bool:
        """AC-3 on all arcs in the CSP."""
        from collections import deque

        # Initialize queue with all arcs
        queue = deque()
        for var in csp.variables:
            for neighbor in csp.get_neighbors(var):
                queue.append((var, neighbor))

        while queue:
            xi, xj = queue.popleft()

            if self._revise(csp, xi, xj):
                if csp.domains[xi].is_empty():
                    return False

                for xk in csp.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))

        return True

    def _revise(self, csp: CSP, xi: Variable, xj: Variable) -> bool:
        """Revise domain of Xi by removing values that have no supporting values in Xj."""
        revised = False
        values_to_remove = set()

        for xi_value in csp.domains[xi].values:
            has_support = False
            for xj_value in csp.domains[xj].values:
                if csp.is_consistent(xi, xi_value, {xj: xj_value}):
                    has_support = True
                    break

            if not has_support:
                values_to_remove.add(xi_value)

        if values_to_remove:
            for value in values_to_remove:
                csp.domains[xi].remove(value)
            revised = True

        return revised