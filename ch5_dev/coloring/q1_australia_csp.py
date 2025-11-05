"""
Question 1: Australia Map Coloring CSP Model Implementation

This module creates a CSP model for the Australia map coloring problem.
It includes the complete problem definition with variables, domains, and constraints.
"""

import sys
import os
from typing import Set, Tuple

# Add parent directory to path to import csp module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value, Domain, Scope, Relation


def create_australia_map_csp() -> CSP:
    """
    Create the CSP model for Australia map coloring problem

    Variable set X = {WA, NT, QLD, NSW, VIC, SA, TAS}
    Domain set D_v = {Red, Green, Blue} for all v in X
    Constraint set C contains all binary constraints for adjacent regions with different colors

    Returns:
        CSP: Configured Australia map coloring CSP problem
    """
    # Create CSP instance
    csp = CSP()

    # Define variables and domains
    variables = ["WA", "NT", "QLD", "NSW", "VIC", "SA", "TAS"]
    colors = {"Red", "Green", "Blue"}  # Using English color names

    # Add all variables and their domains
    for var in variables:
        csp.add_variable(var, colors)

    # Define adjacency relations (constraint scopes)
    # Based on actual Australia map adjacency
    adjacent_pairs = [
        ("WA", "NT"),    # Constraint 1: WA adjacent to NT
        ("WA", "SA"),    # Constraint 2: WA adjacent to SA
        ("NT", "SA"),    # Constraint 3: NT adjacent to SA
        ("NT", "QLD"),   # Constraint 4: NT adjacent to QLD
        ("SA", "QLD"),   # Constraint 5: SA adjacent to QLD
        ("SA", "NSW"),   # Constraint 6: SA adjacent to NSW
        ("SA", "VIC"),   # Constraint 7: SA adjacent to VIC
        ("QLD", "NSW"),  # Constraint 8: QLD adjacent to NSW
        ("NSW", "VIC"),  # Constraint 9: NSW adjacent to VIC
        ("VIC", "TAS")   # Constraint 10: VIC adjacent to TAS (corrected constraint)
    ]

    # Create constraints: adjacent regions must have different colors
    for var1, var2 in adjacent_pairs:
        # Create constraint scope
        scope = (var1, var2)

        # Create constraint relation: combinations with different colors only
        relation = set()
        for color1 in colors:
            for color2 in colors:
                if color1 != color2:  # Adjacent regions must have different colors
                    relation.add((color1, color2))

        # Create and add constraint
        constraint = Constraint(scope, relation)
        csp.add_constraint(constraint)

    return csp


def create_australia_map_csp_implicit() -> CSP:
    """
    Create the Australia map coloring CSP using implicit constraints (functions)

    This version demonstrates the use of implicit constraints instead of explicit sets.

    Returns:
        CSP: Configured Australia map coloring CSP problem with implicit constraints
    """
    # Create CSP instance
    csp = CSP()

    # Define variables and domains
    variables = ["WA", "NT", "QLD", "NSW", "VIC", "SA", "TAS"]
    colors = {"Red", "Green", "Blue"}

    # Add all variables and their domains
    for var in variables:
        csp.add_variable(var, colors)

    # Define adjacency relations
    adjacent_pairs = [
        ("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "QLD"),
        ("SA", "QLD"), ("SA", "NSW"), ("SA", "VIC"), ("QLD", "NSW"),
        ("NSW", "VIC"), ("VIC", "TAS")
    ]

    # Create implicit constraint function
    def different_colors(color1: Value, color2: Value) -> bool:
        """Constraint function: two adjacent regions must have different colors"""
        return color1 != color2

    # Create constraints using implicit function
    for var1, var2 in adjacent_pairs:
        constraint = Constraint((var1, var2), different_colors)
        csp.add_constraint(constraint)

    return csp


def print_csp_analysis(csp: CSP, title: str = "CSP Analysis") -> None:
    """
    Print analysis of the CSP model

    Args:
        csp (CSP): The CSP to analyze
        title (str): Title for the analysis
    """
    print(f"\n{title}")
    print("=" * len(title))

    print(f"Variables: {len(csp.variables)}")
    print(f"  {list(csp.variables)}")

    print(f"Domains: {len(csp.variables)} variables, each with domain {list(csp.domains.values())[0]}")
    for var in sorted(csp.variables):
        print(f"  {var}: {csp.domains[var]}")

    print(f"Constraints: {len(csp.constraints)}")
    implicit_count = sum(1 for c in csp.constraints if callable(c.relation))
    explicit_count = sum(1 for c in csp.constraints if isinstance(c.relation, set))
    print(f"  Implicit constraints (functions): {implicit_count}")
    print(f"  Explicit constraints (sets): {explicit_count}")

    print("Adjacency relations:")
    for i, constraint in enumerate(csp.constraints, 1):
        print(f"  {i:2d}: {constraint.scope[0]} - {constraint.scope[1]} (must be different)")


def test_csp_models():
    """
    Test both explicit and implicit constraint versions of the Australia map coloring CSP
    """
    print("Question 1: Australia Map Coloring CSP Model")
    print("=" * 60)

    # Create explicit constraint version
    csp_explicit = create_australia_map_csp()
    print_csp_analysis(csp_explicit, "Explicit Constraint Version")

    # Create implicit constraint version
    csp_implicit = create_australia_map_csp_implicit()
    print_csp_analysis(csp_implicit, "Implicit Constraint Version")

    # Verify both models have the same structure
    print(f"\nModel Comparison:")
    print(f"Same variables: {csp_explicit.variables == csp_implicit.variables}")
    print(f"Same constraint count: {len(csp_explicit.constraints) == len(csp_implicit.constraints)}")

    # Test a sample assignment
    sample_assignment = {
        "WA": "Red", "NT": "Green", "QLD": "Blue",
        "NSW": "Red", "VIC": "Green", "SA": "Blue", "TAS": "Red"
    }

    print(f"\nSample Assignment Test:")
    print(f"Assignment: {sample_assignment}")

    print(f"Explicit model satisfaction: {csp_explicit.is_solution(sample_assignment)}")
    print(f"Implicit model satisfaction: {csp_implicit.is_solution(sample_assignment)}")

    # Test invalid assignment
    invalid_assignment = {
        "WA": "Red", "NT": "Red",  # Same color for adjacent regions
        "QLD": "Blue", "NSW": "Red", "VIC": "Green", "SA": "Blue", "TAS": "Red"
    }

    print(f"\nInvalid Assignment Test:")
    print(f"Assignment: {invalid_assignment}")
    print(f"Should fail because WA and NT are both Red (adjacent)")

    print(f"Explicit model satisfaction: {csp_explicit.is_solution(invalid_assignment)}")
    print(f"Implicit model satisfaction: {csp_implicit.is_solution(invalid_assignment)}")

    return csp_explicit, csp_implicit


def main():
    """
    Main function to create and demonstrate the Australia map coloring CSP model
    """
    csp_explicit, csp_implicit = test_csp_models()

    print(f"\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("[OK] Australia map coloring CSP model created successfully")
    print("[OK] Both explicit and implicit constraint versions implemented")
    print("[OK] 7 variables (Australian states/territories)")
    print("[OK] 10 adjacency constraints (including corrected VIC-TAS)")
    print("[OK] 3 colors available (Red, Green, Blue)")
    print("\nUse csp.solve() to find a valid coloring solution!")


if __name__ == "__main__":
    main()