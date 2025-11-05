"""
Demo-style test for the inference backtracking solver.

The example uses the classic Australia map colouring CSP and solves it with
pure forward checking enabled. Besides exercising the new solver module, the
demo function can be executed directly to inspect the produced assignment and
metrics.
"""

from typing import Dict, Tuple

from ch5_dev.csp.csp_core import CSP, Constraint, Variable, Value
from ch5_dev.csp.algorithms.inference_backtracking import inference_backtracking_with_metrics


def _build_australia_csp() -> Tuple[CSP, Dict[Variable, Tuple[Variable, ...]]]:
    adjacency: Dict[Variable, Tuple[Variable, ...]] = {
        "WA": ("NT", "SA"),
        "NT": ("WA", "SA", "Q"),
        "SA": ("WA", "NT", "Q", "NSW", "V"),
        "Q": ("NT", "SA", "NSW"),
        "NSW": ("Q", "SA", "V"),
        "V": ("SA", "NSW"),
        "T": (),
    }

    colors = {"red", "green", "blue"}
    csp = CSP()

    for region in adjacency:
        csp.add_variable(region, set(colors))

    def not_equal(x: Value, y: Value) -> bool:
        return x != y

    seen = set()
    for region, neighbours in adjacency.items():
        for neighbour in neighbours:
            edge = tuple(sorted((region, neighbour)))
            if edge in seen:
                continue
            seen.add(edge)
            csp.add_constraint(Constraint((region, neighbour), not_equal))

    return csp, adjacency


def test_forward_checking_demo() -> None:
    csp, adjacency = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking",),
    )

    assert solution is not None, "forward checking failed to find a solution"
    assert csp.is_solution(solution)
    assert "forward_checking" in metrics["techniques"]

    for region, neighbours in adjacency.items():
        for neighbour in neighbours:
            assert solution[region] != solution[neighbour]


def run_demo() -> None:
    """
    Execute the demo manually: prints the solution and collected metrics.
    """
    csp, _ = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking",),
    )
    if solution is None:
        print("No solution found.")
        return

    print("Australia map colouring solution (forward checking):")
    for region in sorted(solution):
        print(f"  {region}: {solution[region]}")

    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    run_demo()
