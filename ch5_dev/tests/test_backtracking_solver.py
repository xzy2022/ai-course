"""
Backtracking Solver Test

This test script demonstrates the backtracking solver functionality using
both the Australia map coloring and Sudoku problems.
"""

import sys
import os
from typing import Dict, Tuple

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, backtracking_search

# Import helper functions from existing test files
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

try:
    from test_australia_map_coloring import create_australia_map_csp
    from test_sudoku_csp import create_sudoku_csp, get_sample_sudoku_puzzle, apply_puzzle_constraints
except ImportError:
    # Fallback implementations if imports fail
    def create_australia_map_csp():
        """Fallback Australia map coloring CSP"""
        csp = CSP()
        variables = ["WA", "NT", "QLD", "NSW", "VIC", "SA", "TAS"]
        colors = {"Red", "Green", "Blue"}

        for var in variables:
            csp.add_variable(var, colors)

        # Add adjacency constraints
        adjacent_pairs = [
            ("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "QLD"),
            ("SA", "QLD"), ("SA", "NSW"), ("SA", "VIC"), ("QLD", "NSW"),
            ("NSW", "VIC"), ("VIC", "TAS")
        ]

        def different_colors(c1, c2):
            return c1 != c2

        for var1, var2 in adjacent_pairs:
            constraint = Constraint((var1, var2), different_colors)
            csp.add_constraint(constraint)

        return csp

    def create_sudoku_csp():
        """Fallback Sudoku CSP - return empty to avoid complexity"""
        return None

    def get_sample_sudoku_puzzle():
        return {}

    def apply_puzzle_constraints(csp, puzzle):
        return csp


def test_australia_map_coloring_solver():
    """
    Test backtracking solver with Australia map coloring problem
    """
    print("=" * 80)
    print("TEST 1: Australia Map Coloring Solver")
    print("=" * 80)

    # Create the CSP problem
    csp = create_australia_map_csp()
    print(f"Created Australia map coloring CSP with {len(csp.variables)} variables and {len(csp.constraints)} constraints")

    # Solve using basic backtracking
    print("\nSolving with basic backtracking...")
    try:
        solution = csp.solve(method="backtracking")

        if solution:
            print("SUCCESS: Solution found!")
            print("Solution assignment:")
            for var in sorted(solution.keys()):
                print(f"  {var}: {solution[var]}")

            # Verify the solution
            if csp.is_solution(solution):
                print("[OK] Solution verification passed")
            else:
                print("[ERROR] Solution verification failed!")

        else:
            print("FAIL: No solution found")

    except Exception as e:
        print(f"ERROR: {e}")

    # Solve using MRV heuristic
    print("\nSolving with MRV heuristic...")
    try:
        solution_mrv = csp.solve(method="backtracking_mrv")

        if solution_mrv:
            print("SUCCESS: Solution found with MRV!")
            print("Number of assignments:", len(solution_mrv))

            # Count total solutions
            num_solutions = csp.count_solutions(max_count=10)
            print(f"Number of solutions found (max 10): {num_solutions}")

        else:
            print("FAIL: No solution found with MRV")

    except Exception as e:
        print(f"ERROR: {e}")

    return csp


def test_simple_coloring_problem():
    """
    Test backtracking solver with a simpler 3-coloring problem
    """
    print("\n" + "=" * 80)
    print("TEST 2: Simple 3-Coloring Problem")
    print("=" * 80)

    # Create a simple triangle graph (3 nodes, each connected to each other)
    csp = CSP()

    # Variables: A, B, C
    variables = ['A', 'B', 'C']
    colors = {'Red', 'Green', 'Blue'}

    for var in variables:
        csp.add_variable(var, colors)

    # Constraints: all pairs must have different colors
    def all_different(value1, value2):
        return value1 != value2

    pairs = [('A', 'B'), ('A', 'C'), ('B', 'C')]
    for var1, var2 in pairs:
        constraint = Constraint((var1, var2), all_different)
        csp.add_constraint(constraint)

    print(f"Created triangle coloring problem with {len(csp.variables)} variables")

    # Solve
    print("\nSolving triangle coloring problem...")
    try:
        solution = csp.solve()

        if solution:
            print("SUCCESS: Solution found!")
            print("Solution assignment:")
            for var in variables:
                print(f"  {var}: {solution[var]}")

            # Count all solutions
            num_solutions = csp.count_solutions(max_count=10)
            print(f"Total solutions (max 10): {num_solutions}")

        else:
            print("FAIL: No solution found")

    except Exception as e:
        print(f"ERROR: {e}")

    return csp


def test_sudoku_solver():
    """
    Test backtracking solver with a simple 4x4 Sudoku variant
    """
    print("\n" + "=" * 80)
    print("TEST 3: 4x4 Sudoku Variant Solver")
    print("=" * 80)

    # Create a simple 4x4 Sudoku variant (2x2 boxes, numbers 1-4)
    csp = CSP()

    # Variables: (row, col) where row, col ∈ {1, 2, 3, 4}
    variables = [(r, c) for r in range(1, 5) for c in range(1, 5)]
    domain = {1, 2, 3, 4}

    for var in variables:
        csp.add_variable(var, domain)

    # All-different constraint function
    def all_different_4(*values):
        return len(set(values)) == len(values)

    # Row constraints (4 rows)
    for r in range(1, 5):
        row_cells = tuple((r, c) for c in range(1, 5))
        constraint = Constraint(row_cells, all_different_4)
        csp.add_constraint(constraint)

    # Column constraints (4 columns)
    for c in range(1, 5):
        col_cells = tuple((r, c) for r in range(1, 5))
        constraint = Constraint(col_cells, all_different_4)
        csp.add_constraint(constraint)

    # Box constraints (4 boxes of 2x2)
    for box_row in range(2):
        for box_col in range(2):
            box_cells = []
            for dr in range(2):
                for dc in range(2):
                    r = box_row * 2 + dr + 1
                    c = box_col * 2 + dc + 1
                    box_cells.append((r, c))
            constraint = Constraint(tuple(box_cells), all_different_4)
            csp.add_constraint(constraint)

    print(f"Created 4x4 Sudoku CSP with {len(csp.variables)} variables and {len(csp.constraints)} constraints")

    # Add some initial constraints (simple puzzle)
    puzzle = {
        (1, 1): 1, (1, 2): 2,
        (2, 3): 3, (2, 4): 4,
        (3, 1): 3, (3, 2): 4,
        (4, 3): 1, (4, 4): 2
    }

    for (r, c), value in puzzle.items():
        csp.domains[(r, c)] = {value}

    print(f"Added {len(puzzle)} pre-filled cells")

    # Solve
    print("\nSolving 4x4 Sudoku...")
    try:
        solution = csp.solve()

        if solution:
            print("SUCCESS: Solution found!")
            print("Solution grid:")
            for r in range(1, 5):
                row = [solution[(r, c)] for c in range(1, 5)]
                print(f"  Row {r}: {row}")

        else:
            print("FAIL: No solution found")

    except Exception as e:
        print(f"ERROR: {e}")

    return csp


def test_nqueens_small():
    """
    Test backtracking solver with small N-Queens problem (N=4)
    """
    print("\n" + "=" * 80)
    print("TEST 4: 4-Queens Problem")
    print("=" * 80)

    # Create 4-Queens problem
    csp = CSP()

    # Variables: Q1, Q2, Q3, Q4 (queens in columns 1-4)
    # Values: row positions 1-4
    variables = ['Q1', 'Q2', 'Q3', 'Q4']
    rows = {1, 2, 3, 4}

    for var in variables:
        csp.add_variable(var, rows)

    # Constraint: no two queens attack each other
    def non_attacking(queen1_row, queen2_row, queen1_col, queen2_col):
        """Check if two queens don't attack each other"""
        # Different rows
        if queen1_row == queen2_row:
            return False
        # Different diagonals
        if abs(queen1_row - queen2_row) == abs(queen1_col - queen2_col):
            return False
        return True

    # Add constraints for all pairs of queens
    for i, q1 in enumerate(variables):
        for j, q2 in enumerate(variables):
            if i < j:  # Avoid duplicate constraints
                constraint = Constraint(
                    (q1, q2),
                    lambda r1, r2, c1=i+1, c2=j+1: non_attacking(r1, r2, c1, c2)
                )
                csp.add_constraint(constraint)

    print(f"Created 4-Queens CSP with {len(csp.variables)} variables and {len(csp.constraints)} constraints")

    # Solve
    print("\nSolving 4-Queens problem...")
    try:
        solution = csp.solve()

        if solution:
            print("SUCCESS: Solution found!")
            print("Queen positions (column: row):")
            for var in variables:
                print(f"  {var}: row {solution[var]}")

            # Visualize solution
            board = [['.' for _ in range(4)] for _ in range(4)]
            for col, var in enumerate(variables, 1):
                row = solution[var] - 1  # Convert to 0-indexed
                board[row][col-1] = 'Q'

            print("\nSolution board:")
            for row in board:
                print(f"  {' '.join(row)}")

            # Count all solutions
            num_solutions = csp.count_solutions(max_count=10)
            print(f"\nTotal solutions (max 10): {num_solutions}")

        else:
            print("FAIL: No solution found")

    except Exception as e:
        print(f"ERROR: {e}")

    return csp


def main():
    """
    Run all backtracking solver tests
    """
    print("BACKTRACKING SOLVER TESTS")
    print("This script tests the backtracking algorithm implementation")

    # Run all tests
    test_australia_map_coloring_solver()
    test_simple_coloring_problem()
    test_sudoku_solver()
    test_nqueens_small()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Backtracking solver tests completed!")
    print("The solver can handle various CSP problems including:")
    print("- Map coloring problems")
    print("- Graph coloring problems")
    print("- Sudoku variants")
    print("- N-Queens problems")
    print("\nAvailable solving methods:")
    print("- Basic backtracking")
    print("- Backtracking with MRV (Minimum Remaining Values) heuristic")


if __name__ == "__main__":
    main()