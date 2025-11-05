"""
Demo-style regression tests for the inference backtracking solver.

Two scenarios are covered using the Australia map colouring CSP:
1. Forward checking alone.
2. Forward checking combined with iterative constraint propagation.
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


def _assert_valid_solution(csp: CSP, adjacency: Dict[Variable, Tuple[Variable, ...]], solution: Dict[Variable, Value]) -> None:
    assert csp.is_solution(solution)
    for region, neighbours in adjacency.items():
        for neighbour in neighbours:
            assert solution[region] != solution[neighbour]


def test_forward_checking_demo() -> None:
    csp, adjacency = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking",),
    )

    assert solution is not None, "forward checking failed to find a solution"
    assert "forward_checking" in metrics["techniques"]
    _assert_valid_solution(csp, adjacency, solution)


def test_constraint_propagation_demo() -> None:
    csp, adjacency = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking", "constraint_propagation"),
    )

    assert solution is not None, "constraint propagation failed to find a solution"
    assert "constraint_propagation" in metrics["techniques"]
    assert metrics["propagation_steps"] >= 0
    _assert_valid_solution(csp, adjacency, solution)


def run_demo() -> None:
    """
    Convenience entry point: run the propagation-enabled solver and print results.
    """
    csp, _ = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking", "constraint_propagation"),
    )
    if solution is None:
        print("No solution found.")
        return

    print("Australia map colouring solution (forward checking + propagation):")
    for region in sorted(solution):
        print(f"  {region}: {solution[region]}")

    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    run_demo()
