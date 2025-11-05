"""
Constraint Class Demonstration

This script demonstrates how the Constraint class works, including:
1. Explicit constraints (using sets of allowed combinations)
2. Implicit constraints (using functions)
3. How the is_satisfied method checks constraints
4. Practical examples from map coloring and Sudoku
"""

import sys
import os

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value, Domain, Scope, Relation
from typing import Dict, List, Tuple, Set


def all_different(*values: Value) -> bool:
    """
    Implicit constraint function: all values must be different
    """
    return len(set(values)) == len(values)


def not_both_red(value1: Value, value2: Value) -> bool:
    """
    Implicit constraint function: two variables cannot both be 'Red'
    """
    return not (value1 == 'Red' and value2 == 'Red')


def demo_explicit_constraint():
    """
    Demonstrate explicit constraints using sets of allowed combinations
    """
    print("=" * 80)
    print("DEMO 1: Explicit Constraint Example")
    print("=" * 80)

    # Create a simple explicit constraint: two variables must be different
    # Allowed combinations: ('Red', 'Green'), ('Red', 'Blue'), ('Green', 'Red'), etc.
    colors = {'Red', 'Green', 'Blue'}
    allowed_combinations = set()

    for color1 in colors:
        for color2 in colors:
            if color1 != color2:  # Only add different color combinations
                allowed_combinations.add((color1, color2))

    print(f"Allowed combinations for 'different colors' constraint:")
    for combo in sorted(allowed_combinations):
        print(f"  {combo}")

    # Create explicit constraint
    explicit_constraint = Constraint(('A', 'B'), allowed_combinations)

    print(f"\nConstraint: {explicit_constraint}")
    print(f"Constraint type: Explicit (Set of {len(allowed_combinations)} combinations)")

    # Test the constraint with different assignments
    test_assignments = [
        {'A': 'Red', 'B': 'Green'},    # Should satisfy
        {'A': 'Red', 'B': 'Red'},      # Should violate
        {'A': 'Blue', 'B': 'Green'},   # Should satisfy
        {'A': 'Green', 'B': 'Green'},  # Should violate
        {'A': 'Red'},                  # Should be ok (incomplete assignment)
    ]

    print(f"\nTesting explicit constraint:")
    for i, assignment in enumerate(test_assignments, 1):
        is_satisfied = explicit_constraint.is_satisfied(assignment)
        status = "SATISFIED" if is_satisfied else "VIOLATED"
        print(f"  Test {i}: {assignment} -> {status}")

    return explicit_constraint


def demo_implicit_constraint():
    """
    Demonstrate implicit constraints using functions
    """
    print("\n" + "=" * 80)
    print("DEMO 2: Implicit Constraint Example")
    print("=" * 80)

    # Create the same constraint using an implicit function
    implicit_constraint = Constraint(('A', 'B'), not_both_red)

    print(f"Constraint: {implicit_constraint}")
    print(f"Constraint type: Implicit (Function: not_both_red)")
    print(f"Function logic: return not (value1 == 'Red' and value2 == 'Red')")

    # Test the implicit constraint with the same assignments
    test_assignments = [
        {'A': 'Red', 'B': 'Green'},    # Should satisfy
        {'A': 'Red', 'B': 'Red'},      # Should violate
        {'A': 'Blue', 'B': 'Green'},   # Should satisfy
        {'A': 'Green', 'B': 'Green'},  # Should satisfy (both not red)
        {'A': 'Red'},                  # Should be ok (incomplete assignment)
    ]

    print(f"\nTesting implicit constraint:")
    for i, assignment in enumerate(test_assignments, 1):
        is_satisfied = implicit_constraint.is_satisfied(assignment)
        status = "SATISFIED" if is_satisfied else "VIOLATED"
        print(f"  Test {i}: {assignment} -> {status}")

    return implicit_constraint


def demo_sudoku_row_constraint():
    """
    Demonstrate Sudoku row constraint (all-different)
    """
    print("\n" + "=" * 80)
    print("DEMO 3: Sudoku Row Constraint (All-Different)")
    print("=" * 80)

    # Create a row constraint for Sudoku (9 variables must all be different)
    row_vars = tuple(f'cell_{i}' for i in range(1, 10))
    row_constraint = Constraint(row_vars, all_different)

    print(f"Constraint: {row_constraint}")
    print(f"Variables: {row_vars}")
    print(f"Constraint type: Implicit (Function: all_different)")
    print(f"Function logic: return len(set(values)) == len(values)")

    # Test with different row assignments
    test_rows = [
        # Valid row: all numbers 1-9 exactly once
        {f'cell_{i}': i for i in range(1, 10)},

        # Invalid row: duplicate 1, missing 2
        {f'cell_{i}': 1 if i == 2 else i for i in range(1, 10)},

        # Incomplete row: only first 5 cells filled
        {f'cell_{i}': i for i in range(1, 6)},

        # Invalid row: all cells have same value
        {f'cell_{i}': 5 for i in range(1, 10)},
    ]

    print(f"\nTesting Sudoku row constraint:")
    for i, row_assignment in enumerate(test_rows, 1):
        is_satisfied = row_constraint.is_satisfied(row_assignment)
        status = "SATISFIED" if is_satisfied else "VIOLATED"

        # Show the row values in a readable format
        values = [row_assignment.get(var, '.') for var in row_vars]
        print(f"  Test {i}: {values} -> {status}")

    return row_constraint


def demo_efficiency_comparison():
    """
    Demonstrate the efficiency difference between explicit and implicit constraints
    """
    print("\n" + "=" * 80)
    print("DEMO 4: Efficiency Comparison")
    print("=" * 80)

    print("Comparing explicit vs implicit constraints for Sudoku row:")

    # Row variables
    row_vars = tuple(f'cell_{i}' for i in range(1, 10))
    numbers = set(range(1, 10))

    # Create explicit constraint (all permutations of 1-9)
    import itertools
    explicit_combinations = set(itertools.permutations(numbers))  # 9! = 362,880 combinations

    explicit_constraint = Constraint(row_vars, explicit_combinations)
    implicit_constraint = Constraint(row_vars, all_different)

    print(f"\nExplicit Constraint:")
    print(f"  Type: Set of allowed combinations")
    print(f"  Size: {len(explicit_combinations)} combinations")
    print(f"  Memory: ~{len(explicit_combinations) * 9 * 8} bytes (estimated)")
    print(f"  Checking: O(1) lookup in set")

    print(f"\nImplicit Constraint:")
    print(f"  Type: Function call")
    print(f"  Size: 1 function")
    print(f"  Memory: ~{len('all_different')} bytes")
    print(f"  Checking: O(n) where n is number of variables (9 in this case)")

    # Test both with the same assignment
    test_assignment = {f'cell_{i}': i for i in range(1, 10)}

    print(f"\nTesting with valid assignment: {list(test_assignment.values())}")

    # Time the explicit constraint
    import time
    start_time = time.time()
    for _ in range(1000):
        explicit_result = explicit_constraint.is_satisfied(test_assignment)
    explicit_time = time.time() - start_time

    # Time the implicit constraint
    start_time = time.time()
    for _ in range(1000):
        implicit_result = implicit_constraint.is_satisfied(test_assignment)
    implicit_time = time.time() - start_time

    print(f"Explicit constraint time (1000 calls): {explicit_time:.6f} seconds")
    print(f"Implicit constraint time (1000 calls): {implicit_time:.6f} seconds")
    print(f"Both give same result: {explicit_result == implicit_result}")

    memory_savings = len(explicit_combinations) * 9 * 8 / len('all_different')
    print(f"\nMemory savings with implicit constraint: ~{memory_savings:.0f}x reduction!")


def demo_constraint_scopes():
    """
    Demonstrate different constraint scopes (unary, binary, n-ary)
    """
    print("\n" + "=" * 80)
    print("DEMO 5: Constraint Scopes")
    print("=" * 80)

    colors = {'Red', 'Green', 'Blue'}

    # Unary constraint: a specific variable cannot be 'Red'
    def not_red(value: Value) -> bool:
        return value != 'Red'

    unary_constraint = Constraint(('A',), not_red)
    print(f"Unary Constraint: {unary_constraint}")
    print(f"  Scope: 1 variable")
    print(f"  Rule: Variable 'A' cannot be 'Red'")

    # Binary constraint: two variables must be different
    binary_constraint = Constraint(('A', 'B'), all_different)
    print(f"\nBinary Constraint: {binary_constraint}")
    print(f"  Scope: 2 variables")
    print(f"  Rule: Variables 'A' and 'B' must be different")

    # Ternary constraint: three variables must all be different
    ternary_constraint = Constraint(('A', 'B', 'C'), all_different)
    print(f"\nTernary Constraint: {ternary_constraint}")
    print(f"  Scope: 3 variables")
    print(f"  Rule: Variables 'A', 'B', and 'C' must all be different")

    # Test all constraints with the same assignment
    test_assignment = {'A': 'Red', 'B': 'Green', 'C': 'Blue'}

    print(f"\nTesting with assignment: {test_assignment}")
    print(f"Unary constraint result: {unary_constraint.is_satisfied(test_assignment)}")
    print(f"Binary constraint result: {binary_constraint.is_satisfied(test_assignment)}")
    print(f"Ternary constraint result: {ternary_constraint.is_satisfied(test_assignment)}")


def main():
    """
    Run all constraint demonstrations
    """
    print("CONSTRAINT CLASS DEMONSTRATION")
    print("This script shows how the Constraint class works in different scenarios")

    # Run all demonstrations
    demo_explicit_constraint()
    demo_implicit_constraint()
    demo_sudoku_row_constraint()
    demo_efficiency_comparison()
    demo_constraint_scopes()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Key takeaways about the Constraint class:")
    print("1. Constraints represent rules that variables must follow")
    print("2. Explicit constraints use sets of allowed combinations")
    print("3. Implicit constraints use functions to check rules")
    print("4. The is_satisfied() method checks if an assignment follows the rule")
    print("5. Implicit constraints are much more memory-efficient for large constraint spaces")
    print("6. Constraints can have different scopes: unary, binary, or n-ary")
    print("\nThe Constraint class is the building block for creating CSP problems!")


if __name__ == "__main__":
    main()