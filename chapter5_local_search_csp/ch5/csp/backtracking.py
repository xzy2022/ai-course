"""
Backtracking Search Algorithm for CSPs

This module implements various backtracking strategies for solving
constraint satisfaction problems, including different heuristics and
inference techniques.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Callable
import random

from .csp import CSP, Variable


class VariableSelectionStrategy(ABC):
    """Abstract base class for variable selection strategies."""

    @abstractmethod
    def select_variable(self, csp: CSP, assignment: Dict[Variable, Any]) -> Variable:
        """Select the next unassigned variable."""
        pass


class FirstUnassignedStrategy(VariableSelectionStrategy):
    """Select the first unassigned variable."""

    def select_variable(self, csp: CSP, assignment: Dict[Variable, Any]) -> Variable:
        for var in csp.variables:
            if var not in assignment:
                return var
        raise ValueError("All variables are assigned")


class MRVStrategy(VariableSelectionStrategy):
    """Minimum Remaining Values heuristic - select variable with smallest domain."""

    def select_variable(self, csp: CSP, assignment: Dict[Variable, Any]) -> Variable:
        unassigned = [var for var in csp.variables if var not in assignment]

        if not unassigned:
            raise ValueError("All variables are assigned")

        # Find variable with minimum domain size
        min_var = min(unassigned, key=lambda var: csp.domains[var].size())
        return min_var


class DegreeStrategy(VariableSelectionStrategy):
    """Degree heuristic - select variable involved in most constraints."""

    def select_variable(self, csp: CSP, assignment: Dict[Variable, Any]) -> Variable:
        unassigned = [var for var in csp.variables if var not in assignment]

        if not unassigned:
            raise ValueError("All variables are assigned")

        # Find variable with most unassigned neighbors
        max_var = max(unassigned,
                     key=lambda var: len([neighbor for neighbor in csp.get_neighbors(var)
                                        if neighbor not in assignment]))
        return max_var


class CombinedStrategy(VariableSelectionStrategy):
    """Combine MRV and degree heuristics."""

    def select_variable(self, csp: CSP, assignment: Dict[Variable, Any]) -> Variable:
        # First use MRV to narrow down to variables with smallest domain
        unassigned = [var for var in csp.variables if var not in assignment]

        if not unassigned:
            raise ValueError("All variables are assigned")

        min_domain_size = min(csp.domains[var].size() for var in unassigned)
        mrv_variables = [var for var in unassigned
                        if csp.domains[var].size() == min_domain_size]

        # Then use degree heuristic among MRV variables
        if len(mrv_variables) == 1:
            return mrv_variables[0]

        return max(mrv_variables,
                  key=lambda var: len([neighbor for neighbor in csp.get_neighbors(var)
                                     if neighbor not in assignment]))


class DomainOrderingStrategy(ABC):
    """Abstract base class for domain ordering strategies."""

    @abstractmethod
    def order_values(self, csp: CSP, variable: Variable,
                    assignment: Dict[Variable, Any]) -> List[Any]:
        """Return ordered list of values to try for the variable."""
        pass


class OrderedDomainStrategy(DomainOrderingStrategy):
    """Try values in the order they appear in the domain."""

    def order_values(self, csp: CSP, variable: Variable,
                    assignment: Dict[Variable, Any]) -> List[Any]:
        return list(csp.domains[variable].values)


class LCVStrategy(DomainOrderingStrategy):
    """Least Constraining Value heuristic."""

    def order_values(self, csp: CSP, variable: Variable,
                    assignment: Dict[Variable, Any]) -> List[Any]:
        values = list(csp.domains[variable].values)

        def count_conflicts(value):
            conflicts = 0
            assignment_copy = assignment.copy()
            assignment_copy[variable] = value

            for neighbor in csp.get_neighbors(variable):
                if neighbor not in assignment:
                    for neighbor_value in csp.domains[neighbor].values:
                        if not csp.is_consistent(neighbor, neighbor_value, assignment_copy):
                            conflicts += 1
            return conflicts

        # Sort by number of conflicts (least constraining first)
        return sorted(values, key=count_conflicts)


class RandomOrderingStrategy(DomainOrderingStrategy):
    """Random ordering of domain values."""

    def order_values(self, csp: CSP, variable: Variable,
                    assignment: Dict[Variable, Any]) -> List[Any]:
        values = list(csp.domains[variable].values)
        random.shuffle(values)
        return values


class BacktrackingSolver:
    """Main backtracking solver with configurable strategies."""

    def __init__(self,
                 var_selection: VariableSelectionStrategy = None,
                 domain_ordering: DomainOrderingStrategy = None,
                 inference_strategy: 'InferenceStrategy' = None):
        self.var_selection = var_selection or MRVStrategy()
        self.domain_ordering = domain_ordering or OrderedDomainStrategy()
        self.inference_strategy = inference_strategy
        self.nodes_expanded = 0
        self.backtrack_calls = 0

    def solve(self, csp: CSP) -> Optional[Dict[Variable, Any]]:
        """Solve the CSP and return a solution if found."""
        return self._backtrack(csp, {})

    def _backtrack(self, csp: CSP, assignment: Dict[Variable, Any]) -> Optional[Dict[Variable, Any]]:
        """Recursive backtracking algorithm."""
        self.backtrack_calls += 1

        # Check if assignment is complete
        if csp.is_complete(assignment):
            return assignment

        # Select next variable to assign
        var = self.var_selection.select_variable(csp, assignment)

        # Try values in order
        for value in self.domain_ordering.order_values(csp, var, assignment):
            self.nodes_expanded += 1

            if csp.is_consistent(var, value, assignment):
                assignment[var] = value

                # Apply inference if available
                inferences = {}
                if self.inference_strategy:
                    inferences = self.inference_strategy.infer(csp, var, value, assignment)

                    if inferences is None:  # Inference detected failure
                        del assignment[var]
                        continue

                # Add inferences to assignment
                for inf_var, inf_val in inferences.items():
                    assignment[inf_var] = inf_val

                # Recursive call
                result = self._backtrack(csp, assignment)
                if result is not None:
                    return result

                # Remove inferences and assignment (backtrack)
                for inf_var in inferences:
                    del assignment[inf_var]
                del assignment[var]

        return None

    def get_statistics(self) -> Dict[str, int]:
        """Return solver statistics."""
        return {
            'nodes_expanded': self.nodes_expanded,
            'backtrack_calls': self.backtrack_calls
        }