"""
Arc-consistency demo tests for the inference backtracking solver.

These tests reuse the Australia map colouring CSP to exercise:
1. Pure arc consistency (AC-3) without forward checking.
2. The full combination of forward checking, propagation, and arc consistency.
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


def test_arc_consistency_demo() -> None:
    csp, adjacency = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("arc_consistency",),
    )

    assert solution is not None, "arc consistency failed to find a solution"
    assert "arc_consistency" in metrics["techniques"]
    assert metrics["arc_revisions"] >= 1
    _assert_valid_solution(csp, adjacency, solution)


def test_full_inference_stack_demo() -> None:
    csp, adjacency = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking", "constraint_propagation", "arc_consistency"),
    )

    assert solution is not None, "combined inference failed to find a solution"
    assert "forward_checking" in metrics["techniques"]
    assert "constraint_propagation" in metrics["techniques"]
    assert "arc_consistency" in metrics["techniques"]
    assert metrics["forward_check_prunes"] >= 1
    assert metrics["propagation_steps"] >= 0
    assert metrics["arc_revisions"] >= 0
    _assert_valid_solution(csp, adjacency, solution)


def run_demo() -> None:
    """
    Convenience entry point: run the solver with all inference techniques enabled.
    """
    csp, _ = _build_australia_csp()
    solution, metrics = inference_backtracking_with_metrics(
        csp,
        techniques=("forward_checking", "constraint_propagation", "arc_consistency"),
    )
    if solution is None:
        print("No solution found.")
        return

    print("Australia map colouring solution (FC + CP + AC-3):")
    for region in sorted(solution):
        print(f"  {region}: {solution[region]}")

    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    run_demo()
