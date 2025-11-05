"""
Australia Map Coloring CSP Model Test

This test script implements the CSP model for Australia map coloring problem, including:
1. Building a complete CSP model (with the corrected VIC-TAS constraint)
2. Visualizing the constraint relations as an undirected graph
3. Basic CSP model validation
"""

import sys
import os

# 添加父目录到路径，以便导入csp模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from csp import CSP, Constraint, Variable, Value, Domain, Scope, Relation
import networkx as nx
import matplotlib.pyplot as plt
from typing import Set, Tuple


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


def visualize_csp_graph(csp: CSP, save_path: str = None) -> None:
    """
    Visualize the constraint relation graph of CSP problem

    Args:
        csp (CSP): CSP problem to visualize
        save_path (str): Image save path, if None then display directly
    """
    # Create undirected graph
    G = nx.Graph()

    # Add all variables as nodes
    for var in csp.variables:
        G.add_node(var)

    # Add constraint relations as edges
    edges = set()
    for constraint in csp.constraints:
        if len(constraint.scope) == 2:  # Only handle binary constraints
            var1, var2 = constraint.scope
            # Add undirected edge (ensure no duplicates)
            edge = tuple(sorted([var1, var2]))
            edges.add(edge)

    G.add_edges_from(edges)

    # Set graph layout
    plt.figure(figsize=(12, 8))

    # Use spring layout, but fix some node positions for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

    # Manually adjust some key node positions to better match Australia map relative positions
    pos_adjusted = pos.copy()
    # Western Australia (WA) - leftmost
    pos_adjusted["WA"] = (-1.5, 0)
    # Northern Territory (NT) - upper middle
    pos_adjusted["NT"] = (-0.5, 0.8)
    # Queensland (QLD) - upper right
    pos_adjusted["QLD"] = (0.8, 0.6)
    # South Australia (SA) - center
    pos_adjusted["SA"] = (-0.2, 0)
    # New South Wales (NSW) - right middle
    pos_adjusted["NSW"] = (0.8, -0.2)
    # Victoria (VIC) - lower right
    pos_adjusted["VIC"] = (0.6, -0.8)
    # Tasmania (TAS) - lower rightmost
    pos_adjusted["TAS"] = (1.2, -1.2)

    # Draw graph
    nx.draw(G, pos_adjusted,
            with_labels=True,
            node_color='lightblue',
            node_size=2000,
            font_size=12,
            font_weight='bold',
            edge_color='gray',
            width=2,
            alpha=0.8)

    plt.title("Australia Map Coloring Constraint Graph\n(CSP Constraint Graph)",
              fontsize=14, fontweight='bold')

    # Add legend
    plt.text(0.02, 0.98,
             "Nodes: Australian states/territories\nEdges: Adjacency relations (constraints)",
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved to: {save_path}")
    else:
        plt.show()


def test_csp_model():
    """
    Test the completeness and correctness of CSP model
    """
    print("=" * 60)
    print("Australia Map Coloring CSP Model Test")
    print("=" * 60)

    # Create CSP model
    csp = create_australia_map_csp()

    # Test 1: Check variable set
    print("\n1. Variable Set Test:")
    expected_variables = {"WA", "NT", "QLD", "NSW", "VIC", "SA", "TAS"}
    actual_variables = csp.variables

    print(f"   Expected variables: {expected_variables}")
    print(f"   Actual variables: {actual_variables}")
    print(f"   ✓ Variable set correct: {expected_variables == actual_variables}")

    # Test 2: Check domain set
    print("\n2. Domain Set Test:")
    expected_domain = {"Red", "Green", "Blue"}
    domains_correct = True

    for var in csp.variables:
        actual_domain = csp.domains[var]
        print(f"   {var}: {actual_domain}")
        if actual_domain != expected_domain:
            domains_correct = False
            print(f"   ✗ {var} domain is incorrect")

    print(f"   ✓ All variable domains correct: {domains_correct}")

    # Test 3: Check constraint set
    print("\n3. Constraint Set Test:")
    expected_constraints = {
        frozenset({"WA", "NT"}),
        frozenset({"WA", "SA"}),
        frozenset({"NT", "SA"}),
        frozenset({"NT", "QLD"}),
        frozenset({"SA", "QLD"}),
        frozenset({"SA", "NSW"}),
        frozenset({"SA", "VIC"}),
        frozenset({"QLD", "NSW"}),
        frozenset({"NSW", "VIC"}),
        frozenset({"VIC", "TAS"})  # Corrected VIC-TAS constraint
    }

    actual_constraints = set()
    for constraint in csp.constraints:
        if len(constraint.scope) == 2:
            actual_constraints.add(frozenset(constraint.scope))

    print(f"   Expected constraint count: {len(expected_constraints)}")
    print(f"   Actual constraint count: {len(actual_constraints)}")

    missing_constraints = expected_constraints - actual_constraints
    extra_constraints = actual_constraints - expected_constraints

    if missing_constraints:
        print(f"   ✗ Missing constraints: {missing_constraints}")
    if extra_constraints:
        print(f"   ✗ Extra constraints: {extra_constraints}")

    constraints_correct = len(missing_constraints) == 0 and len(extra_constraints) == 0
    print(f"   ✓ Constraint set complete and correct: {constraints_correct}")

    # Test 4: Constraint relation verification
    print("\n4. Constraint Relation Verification:")
    colors = {"Red", "Green", "Blue"}
    relations_correct = True

    for constraint in csp.constraints:
        if len(constraint.scope) == 2:
            expected_relation_size = len(colors) * (len(colors) - 1)  # 3 * 2 = 6
            actual_relation_size = len(constraint.relation)

            if actual_relation_size != expected_relation_size:
                relations_correct = False
                var1, var2 = constraint.scope
                print(f"   ✗ Constraint {var1}-{var2} relation size incorrect: expected{expected_relation_size}, actual{actual_relation_size}")

    print(f"   ✓ All constraint relations correct: {relations_correct}")

    # Overall test results
    print("\n" + "=" * 60)
    print("Test Summary:")
    all_tests_passed = (expected_variables == actual_variables and
                       domains_correct and
                       constraints_correct and
                       relations_correct)

    if all_tests_passed:
        print("🎉 All tests passed! CSP model is complete and correct.")
        print("✓ Includes corrected VIC-TAS constraint")
        print("✓ Variables, domains, and constraint sets all meet expectations")
    else:
        print("❌ Some tests failed, please check model implementation.")

    print("=" * 60)

    return csp


def main():
    """
    Main function: run tests and visualization
    """
    # Run CSP model test
    csp = test_csp_model()

    # Visualize constraint graph
    print("\nGenerating constraint visualization graph...")
    save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "australia_map_csp_graph.png")

    try:
        visualize_csp_graph(csp, save_path)
        print(f"✓ Constraint graph saved to: {save_path}")
    except ImportError as e:
        print(f"⚠️  Cannot generate graph, missing dependencies: {e}")
        print("Please install the following dependencies: pip install networkx matplotlib")
    except Exception as e:
        print(f"❌ Error generating graph: {e}")


if __name__ == "__main__":
    main()