"""
Simple Sudoku Row Constraint Example

A focused demonstration of how the row_constraint = Constraint(row_cells, all_different)
works in the context of Sudoku.
"""

import sys
import os

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import Constraint


def all_different(*values):
    """Simple all_different function for Sudoku constraints"""
    return len(set(values)) == len(values)


def main():
    """
    Demonstrate exactly how a Sudoku row constraint works
    """
    print("SUDOKU ROW CONSTRAINT EXPLANATION")
    print("=" * 50)

    # Step 1: Define what a row represents in Sudoku
    print("\nStep 1: What is a Sudoku row?")
    print("A Sudoku row has 9 cells, each must contain a number 1-9")
    print("All numbers in a row must be different (no duplicates)")

    # Step 2: Define the row cells
    row_cells = []
    for i in range(1, 10):  # cells 1 through 9
        row_cells.append(f'row1_cell{i}')

    print(f"\nStep 2: Define the row cells")
    print(f"Row cells: {row_cells}")

    # Step 3: Create the constraint
    row_constraint = Constraint(tuple(row_cells), all_different)

    print(f"\nStep 3: Create the constraint")
    print(f"row_constraint = Constraint(row_cells, all_different)")
    print(f"Constraint: {row_constraint}")

    # Step 4: Show what all_different function does
    print(f"\nStep 4: The all_different function")
    print(f"def all_different(*values):")
    print(f"    return len(set(values)) == len(values)")
    print(f"")
    print(f"This function returns True if all input values are different")
    print(f"It converts values to a set (removes duplicates) and compares lengths")

    # Step 5: Test with different scenarios
    print(f"\nStep 5: Testing the constraint")

    # Test 1: Valid complete row
    valid_row = {f'row1_cell{i}': i for i in range(1, 10)}
    result1 = row_constraint.is_satisfied(valid_row)
    print(f"\nTest 1 - Valid complete row:")
    print(f"Assignment: {list(valid_row.values())}")
    print(f"all_different(1,2,3,4,5,6,7,8,9) = {result1}")
    print(f"Result: {'SATISFIED' if result1 else 'VIOLATED'}")

    # Test 2: Invalid row (duplicate)
    invalid_row = valid_row.copy()
    invalid_row['row1_cell5'] = 3  # Change 5 to 3 (duplicate)
    result2 = row_constraint.is_satisfied(invalid_row)
    print(f"\nTest 2 - Invalid row (duplicate):")
    print(f"Assignment: {list(invalid_row.values())}")
    print(f"all_different(1,2,3,4,3,6,7,8,9) = {result2}")
    print(f"Reason: {3} appears twice")
    print(f"Result: {'SATISFIED' if result2 else 'VIOLATED'}")

    # Test 3: Partial row (incomplete assignment)
    partial_row = {f'row1_cell{i}': i for i in range(1, 6)}  # Only first 5 cells
    result3 = row_constraint.is_satisfied(partial_row)
    print(f"\nTest 3 - Partial row (incomplete):")
    print(f"Assignment: {[partial_row.get(cell, '.') for cell in row_cells]}")
    print(f"Note: Cells 6-9 are not assigned yet")
    print(f"Result: {'SATISFIED' if result3 else 'VIOLATED'}")
    print(f"Reason: Incomplete assignments don't violate constraints")

    # Step 6: Why this is efficient
    print(f"\nStep 6: Why this approach is efficient")
    print(f"Instead of storing all 362,880 valid permutations of (1,2,3,4,5,6,7,8,9),")
    print(f"we just check if values are different using a simple function.")
    print(f"Memory savings: ~2,000,000x reduction!")
    print(f"Checking is fast: just convert to set and compare lengths")

    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("The row_constraint represents the rule:")
    print("'All 9 cells in a Sudoku row must contain different numbers'")
    print("It uses a function to check this rule efficiently without")
    print("storing millions of possible valid combinations.")


if __name__ == "__main__":
    main()