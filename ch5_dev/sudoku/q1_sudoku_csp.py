"""
Question 1: Sudoku CSP Model Implementation

This module creates a CSP model for standard 9x9 Sudoku puzzles.
It includes the complete problem definition with variables, domains, and constraints.
"""

import sys
import os
from typing import Dict, Tuple

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value, Domain, Scope, Relation


def all_different(*values: Value) -> bool:
    """
    Implicit constraint function: all values must be different

    Args:
        *values: Variable values to check

    Returns:
        bool: True if all values are different, False otherwise
    """
    return len(set(values)) == len(values)


def create_sudoku_csp() -> CSP:
    """
    Create a CSP model for standard 9x9 Sudoku problem

    Variable set X = {(r, c) | r, c ∈ {1, 2, ..., 9}}
    Domain set D = {{1, 2, ..., 9} | v ∈ X}
    Constraint set C = C_rows ∪ C_cols ∪ C_boxes

    Returns:
        CSP: Configured Sudoku CSP problem
    """
    # Create CSP instance
    csp = CSP()

    # 1. Variable Set X: All 81 cells in the 9x9 grid
    variables = [(r, c) for r in range(1, 10) for c in range(1, 10)]

    # 2. Domain Set D: Each variable can take values 1-9
    domain = set(range(1, 10))

    # Add all variables with their domains
    for var in variables:
        csp.add_variable(var, domain)

    # 3. Constraint Set C: Row, Column, and Box constraints

    # Row constraints (9 constraints)
    for r in range(1, 10):
        row_cells = tuple((r, c) for c in range(1, 10))
        row_constraint = Constraint(row_cells, all_different)
        csp.add_constraint(row_constraint)

    # Column constraints (9 constraints)
    for c in range(1, 10):
        col_cells = tuple((r, c) for r in range(1, 10))
        col_constraint = Constraint(col_cells, all_different)
        csp.add_constraint(col_constraint)

    # Box constraints (9 constraints)
    # Each box is a 3x3 subgrid
    for box_row in range(3):  # 0, 1, 2
        for box_col in range(3):  # 0, 1, 2
            box_cells = []
            for dr in range(3):
                for dc in range(3):
                    r = box_row * 3 + dr + 1
                    c = box_col * 3 + dc + 1
                    box_cells.append((r, c))
            box_constraint = Constraint(tuple(box_cells), all_different)
            csp.add_constraint(box_constraint)

    return csp


def apply_puzzle_constraints(csp: CSP, puzzle: Dict[Tuple[int, int], int]) -> CSP:
    """
    Apply initial puzzle constraints by modifying variable domains

    Args:
        csp (CSP): The Sudoku CSP problem
        puzzle (Dict[Tuple[int, int], int]): Initial puzzle state (filled cells)

    Returns:
        CSP: Modified CSP with initial constraints applied
    """
    for (row, col), value in puzzle.items():
        # Create a domain with only the given value
        single_value_domain = {value}
        csp.domains[(row, col)] = single_value_domain

    return csp


def get_sample_sudoku_puzzle() -> Dict[Tuple[int, int], int]:
    """
    Return a sample Sudoku puzzle (moderately difficult)

    0 represents empty cells in the visual representation
    The puzzle has a unique solution
    """
    puzzle = {
        (1, 1): 5, (1, 2): 3, (1, 5): 7,
        (2, 1): 6, (2, 4): 1, (2, 5): 9, (2, 6): 5,
        (3, 2): 9, (3, 3): 8, (3, 8): 6,
        (4, 1): 8, (4, 5): 6, (4, 9): 3,
        (5, 1): 4, (5, 4): 8, (5, 6): 3, (5, 9): 1,
        (6, 1): 7, (6, 5): 2, (6, 9): 6,
        (7, 2): 6, (7, 3): 2, (7, 8): 8,
        (8, 4): 4, (8, 5): 1, (8, 6): 9, (8, 9): 5,
        (9, 5): 8, (9, 8): 7, (9, 9): 9
    }

#     puzzle = {
#     (1, 1): 5, (1, 2): 3, (1, 3): 4, (1, 4): 6, (1, 5): 7, (1, 6): 8, (1, 7): 9, (1, 8): 1, (1, 9): 2,
#     (2, 1): 6, (2, 2): 7, (2, 3): 2, (2, 4): 1, (2, 5): 9, (2, 6): 5, (2, 7): 3, (2, 9): 8,
#     (3, 1): 1, (3, 2): 9, (3, 3): 8, (3, 4): 3, (3, 5): 4, (3, 6): 2, (3, 7): 5, (3, 8): 6, (3, 9): 7,
#     (4, 1): 8, (4, 2): 5, (4, 3): 9, (4, 4): 7, (4, 5): 6, (4, 6): 1, (4, 7): 4, (4, 8): 2, (4, 9): 3,
#     (5, 1): 4, (5, 2): 2, (5, 3): 6, (5, 6): 3, (5, 7): 7, (5, 8): 9, (5, 9): 1,
#     (6, 1): 7, (6, 2): 1, (6, 3): 3, (6, 4): 9, (6, 5): 2, (6, 6): 4, (6, 7): 8, (6, 8): 5, (6, 9): 6,
#     (7, 1): 9, (7, 2): 6, (7, 3): 1, (7, 4): 5, (7, 5): 3, (7, 6): 7, (7, 7): 2, (7, 8): 8, (7, 9): 4,
#     (8, 1): 2, (8, 2): 8, (8, 3): 7, (8, 4): 4, (8, 5): 1, (8, 9): 5,
#     (9, 1): 3, (9, 2): 4, (9, 3): 5, (9, 4): 2, (9, 5): 8, (9, 6): 6, (9, 7): 1, (9, 8): 7, (9, 9): 9
# }

    return puzzle


def visualize_sudoku_puzzle(puzzle: Dict[Tuple[int, int], int]) -> None:
    """
    Visualize a Sudoku puzzle in a readable format

    Args:
        puzzle (Dict[Tuple[int, int], int]): Puzzle state
    """
    print("Sudoku Puzzle:")
    print("┌─────────┬─────────┬─────────┐")

    for r in range(1, 10):
        row_str = "│"
        for c in range(1, 10):
            if c in [4, 7]:
                row_str += " │"

            if (r, c) in puzzle:
                row_str += f" {puzzle[(r, c)]}"
            else:
                row_str += " ."

        row_str += " │"
        print(row_str)

        if r in [3, 6]:
            print("├─────────┼─────────┼─────────┤")

    print("└─────────┴─────────┴─────────┘")


def main():
    """
    Main function to create and demonstrate the Sudoku CSP model
    """
    print("Question 1: Sudoku CSP Model")
    print("=" * 50)

    # Create the base Sudoku CSP model
    csp = create_sudoku_csp()

    print(f"Created Sudoku CSP with:")
    print(f"  Variables: {len(csp.variables)} (9x9 grid)")
    print(f"  Constraints: {len(csp.constraints)} (9 rows + 9 columns + 9 boxes)")
    print(f"  Domain for each variable: {{1, 2, 3, 4, 5, 6, 7, 8, 9}}")

    # Get and visualize sample puzzle
    sample_puzzle = get_sample_sudoku_puzzle()
    print(f"\nSample puzzle has {len(sample_puzzle)} pre-filled cells:")
    visualize_sudoku_puzzle(sample_puzzle)

    # Apply puzzle constraints to create specific problem instance
    csp_with_puzzle = apply_puzzle_constraints(csp, sample_puzzle)

    # Count variables with reduced domains
    single_value_vars = sum(1 for var in csp_with_puzzle.variables
                           if len(csp_with_puzzle.domains[var]) == 1)

    print(f"\nApplied puzzle constraints:")
    print(f"  Variables with single-value domains: {single_value_vars}")
    print(f"  Variables with full domains: {len(csp_with_puzzle.variables) - single_value_vars}")

    # Test if initial assignment is consistent
    initial_assignment = {(r, c): v for (r, c), v in sample_puzzle.items()}
    is_consistent = csp_with_puzzle.is_solution(initial_assignment)

    print(f"\nInitial assignment consistency:")
    print(f"  Is complete: {csp_with_puzzle.is_complete(initial_assignment)}")
    print(f"  Is consistent: {is_consistent}")

    print(f"\nSudoku CSP model created successfully!")
    print(f"Use csp.solve() to find a solution for this puzzle.")


if __name__ == "__main__":
    main()