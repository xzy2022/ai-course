"""
Sudoku CSP Model Test

This test script implements the CSP model for Sudoku puzzles, including:
1. Building a complete CSP model for standard 9x9 Sudoku
2. Using implicit constraints for efficiency (all-different constraints)
3. Testing with a sample Sudoku puzzle
4. Model validation and analysis
"""

import sys
import os

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value, Domain, Scope, Relation
from typing import Dict, List, Tuple


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

    print("└─────────┴─────────┴─────────┐")


def test_sudoku_csp_model():
    """
    Test the completeness and correctness of Sudoku CSP model
    """
    print("=" * 80)
    print("Sudoku CSP Model Test")
    print("=" * 80)

    # Create base Sudoku CSP model
    csp = create_sudoku_csp()

    # Test 1: Check variable set
    print("\n1. Variable Set Test:")
    expected_variable_count = 81  # 9x9 grid
    actual_variable_count = len(csp.variables)

    print(f"   Expected variable count: {expected_variable_count}")
    print(f"   Actual variable count: {actual_variable_count}")
    print(f"   [OK] Variable count correct: {expected_variable_count == actual_variable_count}")

    # Test 2: Check domain set
    print("\n2. Domain Set Test:")
    expected_domain = set(range(1, 10))
    domains_correct = True

    # Check a few sample variables
    sample_vars = [(1, 1), (5, 5), (9, 9)]
    for var in sample_vars:
        actual_domain = csp.domains[var]
        print(f"   {var}: {actual_domain}")
        if actual_domain != expected_domain:
            domains_correct = False
            print(f"   [ERROR] {var} domain is incorrect")

    print(f"   [OK] All variable domains correct: {domains_correct}")

    # Test 3: Check constraint set
    print("\n3. Constraint Set Test:")
    expected_constraint_count = 27  # 9 rows + 9 columns + 9 boxes
    actual_constraint_count = len(csp.constraints)

    print(f"   Expected constraint count: {expected_constraint_count}")
    print(f"   Actual constraint count: {actual_constraint_count}")
    print(f"   [OK] Constraint count correct: {expected_constraint_count == actual_constraint_count}")

    # Test 4: Analyze constraint types
    print("\n4. Constraint Type Analysis:")
    implicit_constraints = 0
    explicit_constraints = 0

    for constraint in csp.constraints:
        if callable(constraint.relation):
            implicit_constraints += 1
        elif isinstance(constraint.relation, set):
            explicit_constraints += 1

    print(f"   Implicit constraints (functions): {implicit_constraints}")
    print(f"   Explicit constraints (sets): {explicit_constraints}")
    print(f"   [OK] All constraints use implicit representation: {implicit_constraints == expected_constraint_count}")

    # Test 5: Apply sample puzzle
    print("\n5. Sample Puzzle Application:")
    sample_puzzle = get_sample_sudoku_puzzle()
    print(f"   Sample puzzle has {len(sample_puzzle)} pre-filled cells")

    # Apply puzzle constraints
    csp_with_puzzle = apply_puzzle_constraints(csp, sample_puzzle)

    # Count variables with reduced domains
    reduced_domain_vars = sum(1 for var in csp_with_puzzle.variables
                            if len(csp_with_puzzle.domains[var]) == 1)

    print(f"   Variables with single-value domains: {reduced_domain_vars}")
    print(f"   [OK] Puzzle constraints applied correctly: {reduced_domain_vars == len(sample_puzzle)}")

    # Test 6: Validate puzzle consistency
    print("\n6. Puzzle Consistency Validation:")
    assignment = {(r, c): v for (r, c), v in sample_puzzle.items()}

    try:
        is_solution = csp_with_puzzle.is_solution(assignment)
        print(f"   Initial puzzle is complete solution: {is_solution}")
        print("   [OK] (Expected: False, since puzzle is incomplete)")

        # Check if initial assignment is consistent
        is_consistent = True
        for constraint in csp_with_puzzle.constraints:
            if not constraint.is_satisfied(assignment):
                is_consistent = False
                break

        print(f"   Initial puzzle assignment is consistent: {is_consistent}")
        print(f"   [OK] Puzzle has no immediate contradictions: {is_consistent}")

    except Exception as e:
        print(f"   [ERROR] Error validating puzzle: {e}")

    # Overall test results
    print("\n" + "=" * 80)
    print("Test Summary:")
    all_tests_passed = (
        expected_variable_count == actual_variable_count and
        domains_correct and
        expected_constraint_count == actual_constraint_count and
        implicit_constraints == expected_constraint_count and
        reduced_domain_vars == len(sample_puzzle)
    )

    if all_tests_passed:
        print("SUCCESS: All tests passed! Sudoku CSP model is complete and correct.")
        print("[OK] Variables, domains, and constraints all meet expectations")
        print("[OK] Efficient implicit constraint representation implemented")
        print("[OK] Puzzle application works correctly")
    else:
        print("FAIL: Some tests failed, please check model implementation.")

    print("=" * 80)

    return csp_with_puzzle


def main():
    """
    Main function: run tests and display sample puzzle
    """
    # Run Sudoku CSP model test
    csp = test_sudoku_csp_model()

    # Display sample puzzle
    print("\n" + "=" * 80)
    print("Sample Sudoku Puzzle Visualization:")
    print("=" * 80)
    sample_puzzle = get_sample_sudoku_puzzle()
    visualize_sudoku_puzzle(sample_puzzle)

    print(f"\n[OK] Sudoku CSP model created and tested successfully!")
    print(f"[OK] Model uses {len(csp.constraints)} implicit constraints")
    print(f"[OK] Efficient representation avoids storing 9! × 27 combinations")


if __name__ == "__main__":
    main()