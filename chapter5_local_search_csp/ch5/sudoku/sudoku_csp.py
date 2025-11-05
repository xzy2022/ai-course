"""
Sudoku CSP Implementation

This module implements Sudoku as a Constraint Satisfaction Problem by extending
the core CSP framework with Sudoku-specific logic and constraints.
"""

from typing import List, Dict, Tuple, Any

from ..csp import CSP, Variable, Domain, Constraint


class SudokuVariable(Variable):
    """Specialized variable for Sudoku cells."""

    def __init__(self, row: int, col: int, domain: Domain = None):
        self.row = row
        self.col = col
        self.box = self._calculate_box(row, col)
        name = f"cell_{row}_{col}"
        super().__init__(name, domain)

    def _calculate_box(self, row: int, col: int) -> int:
        """Calculate which 3x3 box this cell belongs to."""
        return (row // 3) * 3 + (col // 3)


class SudokuConstraint(Constraint):
    """Base class for Sudoku constraints."""

    def __init__(self, variables: List[SudokuVariable]):
        super().__init__(variables)


class RowConstraint(SudokuConstraint):
    """Constraint that all numbers in a row must be unique."""

    def __init__(self, row: int, variables: List[SudokuVariable]):
        self.row = row
        super().__init__(variables)

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        row_values = []
        for var in self.variables:
            if var in assignment and assignment[var] is not None:
                row_values.append(assignment[var])

        return len(row_values) == len(set(row_values))

    def get_scope(self) -> List[Variable]:
        return self.variables


class ColumnConstraint(SudokuConstraint):
    """Constraint that all numbers in a column must be unique."""

    def __init__(self, col: int, variables: List[SudokuVariable]):
        self.col = col
        super().__init__(variables)

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        col_values = []
        for var in self.variables:
            if var in assignment and assignment[var] is not None:
                col_values.append(assignment[var])

        return len(col_values) == len(set(col_values))

    def get_scope(self) -> List[Variable]:
        return self.variables


class BoxConstraint(SudokuConstraint):
    """Constraint that all numbers in a 3x3 box must be unique."""

    def __init__(self, box: int, variables: List[SudokuVariable]):
        self.box = box
        super().__init__(variables)

    def is_satisfied(self, assignment: Dict[Variable, Any]) -> bool:
        box_values = []
        for var in self.variables:
            if var in assignment and assignment[var] is not None:
                box_values.append(assignment[var])

        return len(box_values) == len(set(box_values))

    def get_scope(self) -> List[Variable]:
        return self.variables


class SudokuCSP(CSP):
    """Complete Sudoku CSP implementation."""

    def __init__(self):
        super().__init__()
        self.grid_size = 9
        self.box_size = 3
        self.variables_dict = {}
        self._create_variables()
        self._create_constraints()

    def _create_variables(self):
        """Create all 81 variables for the Sudoku grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # By default, each cell can contain numbers 1-9
                domain = Domain(set(range(1, 10)))
                var = SudokuVariable(row, col, domain)
                self.add_variable(var)
                self.variables_dict[(row, col)] = var

    def _create_constraints(self):
        """Create all row, column, and box constraints."""
        # Row constraints
        for row in range(self.grid_size):
            row_vars = [self.variables_dict[(row, col)] for col in range(self.grid_size)]
            constraint = RowConstraint(row, row_vars)
            self.add_constraint(constraint)

        # Column constraints
        for col in range(self.grid_size):
            col_vars = [self.variables_dict[(row, col)] for row in range(self.grid_size)]
            constraint = ColumnConstraint(col, col_vars)
            self.add_constraint(constraint)

        # Box constraints
        for box in range(9):
            box_vars = []
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    var = self.variables_dict[(row, col)]
                    if var.box == box:
                        box_vars.append(var)
            constraint = BoxConstraint(box, box_vars)
            self.add_constraint(constraint)

    def set_initial_value(self, row: int, col: int, value: int):
        """Set an initial value for a cell (from the puzzle)."""
        var = self.variables_dict[(row, col)]
        # Reduce domain to just the given value
        self.domains[var] = Domain({value})
        var.domain = self.domains[var]

    def get_variable(self, row: int, col: int) -> SudokuVariable:
        """Get the variable for a specific cell."""
        return self.variables_dict[(row, col)]

    def get_assignment_grid(self, assignment: Dict[Variable, Any]) -> List[List[int]]:
        """Convert assignment to a 2D grid for display."""
        grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for (row, col), var in self.variables_dict.items():
            if var in assignment and assignment[var] is not None:
                grid[row][col] = assignment[var]
        return grid

    def print_solution(self, assignment: Dict[Variable, Any]):
        """Print the Sudoku solution in a readable format."""
        grid = self.get_assignment_grid(assignment)
        for i, row in enumerate(grid):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            row_str = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                row_str += f"{val if val != 0 else '.'} "
            print(row_str.strip())

    def validate_solution(self, assignment: Dict[Variable, Any]) -> bool:
        """Validate that the assignment is a complete and correct Sudoku solution."""
        return self.is_solution(assignment)

    def get_conflicts(self, assignment: Dict[Variable, Any]) -> int:
        """Count the number of violated constraints in the current assignment."""
        conflicts = 0
        for constraint in self.constraints:
            if not constraint.is_satisfied(assignment):
                conflicts += 1
        return conflicts