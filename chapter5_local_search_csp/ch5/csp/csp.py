"""
Core CSP Model Implementation

This module defines the fundamental components of a Constraint Satisfaction Problem:
- Variable: Represents variables in the CSP
- Domain: Represents possible values for variables
- Constraint: Represents constraints between variables
- CSP: Main class that ties everything together
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Any, Tuple, Optional


class Variable:
    """Represents a variable in a CSP problem."""

    def __init__(self, name: str, domain: Optional['Domain'] = None):
        self.name = name
        self.domain = domain or Domain()
        self.value = None

    def __str__(self):
        return f"Variable({self.name})"

    def __repr__(self):
        return self.__str__()


class Domain:
    """Represents the domain of possible values for a variable."""

    def __init__(self, values: Optional[Set[Any]] = None):
        self.values = values or set()

    def add(self, value: Any):
        self.values.add(value)

    def remove(self, value: Any):
        self.values.discard(value)

    def contains(self, value: Any) -> bool:
        return value in self.values

    def size(self) -> int:
        return len(self.values)

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def copy(self) -> 'Domain':
        return Domain(self.values.copy())


class Constraint(ABC):
    """Abstract base class for constraints."""

    def __init__(self, variables: List[Variable]):
        self.variables = variables

    @abstractmethod
    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        """Check if the constraint is satisfied given the current assignment."""
        pass

    @abstractmethod
    def get_scope(self) -> List[Variable]:
        """Return the variables involved in this constraint."""
        pass


class BinaryConstraint(Constraint):
    """Represents a binary constraint between two variables."""

    def __init__(self, var1: Variable, var2: Variable,
                 constraint_func: callable):
        super().__init__([var1, var2])
        self.var1 = var1
        self.var2 = var2
        self.constraint_func = constraint_func

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        return self.constraint_func(assignment[self.var1], assignment[self.var2])

    def get_scope(self) -> List[Variable]:
        return [self.var1, self.var2]


class CSP:
    """Main CSP class that manages variables, domains, and constraints."""

    def __init__(self):
        self.variables: List[Variable] = []
        self.domains: Dict[Variable, Domain] = {}
        self.constraints: List[Constraint] = []
        self.neighbors: Dict[Variable, Set[Variable]] = {}

    def add_variable(self, variable: Variable):
        """Add a variable to the CSP."""
        self.variables.append(variable)
        self.domains[variable] = variable.domain.copy()
        self.neighbors[variable] = set()

    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the CSP."""
        self.constraints.append(constraint)

        # Update neighbor relationships
        for var in constraint.get_scope():
            for other_var in constraint.get_scope():
                if var != other_var:
                    self.neighbors[var].add(other_var)

    def get_constraints(self, variable: Variable) -> List[Constraint]:
        """Get all constraints involving the given variable."""
        return [c for c in self.constraints if variable in c.get_scope()]

    def get_neighbors(self, variable: Variable) -> Set[Variable]:
        """Get all variables that share a constraint with the given variable."""
        return self.neighbors[variable]

    def is_consistent(self, variable: Variable, value: Any,
                     assignment: Dict[Variable, Any]) -> bool:
        """Check if assigning value to variable violates any constraints."""
        assignment_copy = assignment.copy()
        assignment_copy[variable] = value

        for constraint in self.get_constraints(variable):
            if not constraint.is_satisfied(assignment_copy):
                return False
        return True

    def is_complete(self, assignment: Dict[Variable, Any]) -> bool:
        """Check if all variables are assigned."""
        return len(assignment) == len(self.variables)

    def is_solution(self, assignment: Dict[Variable, Any]) -> bool:
        """Check if the assignment is a complete and consistent solution."""
        if not self.is_complete(assignment):
            return False

        for constraint in self.constraints:
            if not constraint.is_satisfied(assignment):
                return False
        return True