"""
Backtracking Search Algorithm for CSP

This module implements the basic backtracking search algorithm for solving
Constraint Satisfaction Problems.

Functions Overview:
- backtracking_search(): Main entry point for basic backtracking algorithm
- count_solutions(): Count all possible solutions (with upper limit)
- _recursive_backtrack(): Core recursive implementation for basic backtracking
- _select_unassigned_variable(): Simple variable selection (first unassigned)

All functions follow a pure functional approach - they don't modify the CSP
object itself, only work with assignment dictionaries.
"""

from typing import Dict, Optional
from ..csp_core import CSP, Variable, Value


def backtracking_search(csp: CSP) -> Optional[Dict[Variable, Value]]:
    """
    Execute backtracking search to find a solution for the CSP.

    Args:
        csp (CSP): The constraint satisfaction problem to solve

    Returns:
        Optional[Dict[Variable, Value]]: A complete assignment if a solution is found,
                                        None if no solution exists
    """
    assignment: Dict[Variable, Value] = {}
    return _recursive_backtrack(csp, assignment)


def _recursive_backtrack(csp: CSP, assignment: Dict[Variable, Value]) -> Optional[Dict[Variable, Value]]:
    """
    Recursive core of the backtracking search algorithm.

    Args:
        csp (CSP): The CSP being solved
        assignment (Dict[Variable, Value]): Current partial assignment

    Returns:
        Optional[Dict[Variable, Value]]: Complete assignment if solution found,
                                        None if no solution exists from this state
    """
    # 1. Base case: if assignment is complete, return solution
    if csp.is_complete(assignment):
        return assignment

    # 2. Recursive step: select an unassigned variable
    var = _select_unassigned_variable(csp, assignment)
    if var is None:  # Should not happen theoretically, since is_complete handles it
        return None

    # 3. Iterate through domain values, trying assignments
    for value in csp.domains[var]:
        # 3.1 Consistency check
        if csp.is_consistent(var, value, assignment):
            # 3.2 Make assignment
            assignment[var] = value

            # 3.3 Recursive call
            result = _recursive_backtrack(csp, assignment)

            # 3.4 If recursive call succeeded, return result
            if result is not None:
                return result

            # 3.5 If recursive call failed, backtrack (undo assignment)
            del assignment[var]

    # 4. If all values tried and failed, return None (failure signal)
    return None


def _select_unassigned_variable(csp: CSP, assignment: Dict[Variable, Value]) -> Optional[Variable]:
    """
    Select an unassigned variable.
    This is the simplest implementation: select first unassigned variable in fixed order.

    Args:
        csp (CSP): The CSP being solved
        assignment (Dict[Variable, Value]): Current assignment

    Returns:
        Optional[Variable]: An unassigned variable, or None if all variables are assigned
    """
    for var in csp.variables:
        if var not in assignment:
            return var
    return None


# Enhanced versions with heuristics (can be implemented later)

def count_solutions(csp: CSP, max_count: int = 1000) -> int:
    """
    Count the number of solutions for a CSP (up to max_count).

    Args:
        csp (CSP): The CSP to analyze
        max_count (int): Maximum number of solutions to count (to avoid infinite loops)

    Returns:
        int: Number of solutions found (capped at max_count)
    """
    def _count_recursive(csp: CSP, assignment: Dict[Variable, Value], count: int) -> int:
        if count >= max_count:
            return count

        if csp.is_complete(assignment):
            return count + 1

        var = _select_unassigned_variable(csp, assignment)
        if var is None:
            return count

        for value in csp.domains[var]:
            if csp.is_consistent(var, value, assignment):
                assignment[var] = value
                count = _count_recursive(csp, assignment, count)
                del assignment[var]

        return count

    return _count_recursive(csp, {}, 0)
