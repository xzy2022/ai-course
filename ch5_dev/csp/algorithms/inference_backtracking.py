"""
Inference-aware backtracking search.

This module introduces an extensible pipeline that can combine three classic
inference techniques for CSP search:

1. Forward Checking (FC)
2. Constraint Propagation (CP)
3. Arc Consistency (AC-3) - placeholder

Forward checking and constraint propagation are implemented. The arc-consistency
hook remains available for future extension without touching the core loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from ..csp_core import CSP, Variable, Value

Assignment = Dict[Variable, Value]
Domain = Dict[Variable, Set[Value]]
Removals = List[Tuple[Variable, Value]]


class UnknownTechniqueError(ValueError):
    """Raised when the caller requests an inference technique that is unknown."""


TechniqueHandler = Callable[["InferenceBacktrackingSolver", Variable, Assignment, Removals], bool]


@dataclass(frozen=True)
class TechniqueDefinition:
    name: str
    handler: TechniqueHandler
    description: str


def _stub_not_implemented(label: str) -> TechniqueHandler:
    def _handler(_: "InferenceBacktrackingSolver", __: Variable, ___: Assignment, ____: Removals) -> bool:
        raise NotImplementedError(f"Inference technique '{label}' is not implemented yet.")

    return _handler


def _build_neighbors(csp: CSP) -> Dict[Variable, Set[Variable]]:
    neighbors: Dict[Variable, Set[Variable]] = {var: set() for var in csp.variables}
    for constraint in csp.constraints:
        scope = constraint.scope
        for var in scope:
            others = set(scope) - {var}
            neighbors[var].update(others)
    return neighbors


class InferenceBacktrackingSolver:
    """
    Backtracking solver with pluggable inference techniques.

    The solver keeps the search loop minimal and delegates all propagation logic
    to technique handlers. Each handler receives the solver instance, newly
    assigned variable, current assignment, and a shared removals list so that
    domain pruning can be undone when backtracking.
    """

    TECHNIQUES: Dict[str, TechniqueDefinition] = {
        "forward_checking": TechniqueDefinition(
            name="forward_checking",
            handler=lambda solver, var, assignment, removals: solver._forward_check(var, assignment, removals),
            description="Prune neighbour domains that conflict with the new assignment.",
        ),
        "constraint_propagation": TechniqueDefinition(
            name="constraint_propagation",
            handler=lambda solver, var, assignment, removals: solver._constraint_propagation(var, assignment, removals),
            description="Iterative propagation that cascades pruning to secondary neighbours.",
        ),
        "arc_consistency": TechniqueDefinition(
            name="arc_consistency",
            handler=_stub_not_implemented("arc_consistency"),
            description="AC-3 enforcement on remaining arcs (placeholder).",
        ),
    }

    def __init__(self, techniques: Sequence[str] = ()) -> None:
        unknown = [name for name in techniques if name not in self.TECHNIQUES]
        if unknown:
            raise UnknownTechniqueError(f"Unknown inference technique(s): {', '.join(sorted(unknown))}")

        self.techniques = [self.TECHNIQUES[name] for name in techniques]
        self.csp: Optional[CSP] = None
        self.neighbors: Dict[Variable, Set[Variable]] = {}
        self.current_domains: Domain = {}
        self.metrics: Dict[str, Any] = {}

        # Metrics counters populated during search
        self._nodes_expanded = 0
        self._backtracks = 0
        self._max_depth = 0
        self._forward_prunes = 0
        self._propagation_steps = 0

    # ------------------------------------------------------------------ Public API

    def solve(self, csp: CSP) -> Optional[Assignment]:
        """Return a solution assignment if one exists."""
        solution, _ = self.solve_with_metrics(csp)
        return solution

    def solve_with_metrics(self, csp: CSP) -> Tuple[Optional[Assignment], Dict[str, Any]]:
        """Run search and return (solution, metrics)."""
        self._prepare(csp)
        solution = self._backtrack({}, depth=0)
        self.metrics = {
            "nodes_expanded": float(self._nodes_expanded),
            "backtracks": float(self._backtracks),
            "max_depth": float(self._max_depth),
            "forward_check_prunes": float(self._forward_prunes),
            "propagation_steps": float(self._propagation_steps),
            "techniques": ", ".join(defn.name for defn in self.techniques) or "none",
        }
        return solution, dict(self.metrics)

    # ------------------------------------------------------------------ Core search

    def _prepare(self, csp: CSP) -> None:
        self.csp = csp
        self.neighbors = _build_neighbors(csp)
        self.current_domains = {var: set(domain) for var, domain in csp.domains.items()}
        self._nodes_expanded = 0
        self._backtracks = 0
        self._max_depth = 0
        self._forward_prunes = 0
        self._propagation_steps = 0

    def _backtrack(self, assignment: Assignment, depth: int) -> Optional[Assignment]:
        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        self._nodes_expanded += 1
        self._max_depth = max(self._max_depth, depth)

        if len(assignment) == len(self.csp.variables):
            return dict(assignment)

        var = self._select_unassigned_variable(assignment)
        if var is None:
            return None

        for value in list(self.current_domains[var]):
            if not self.csp.is_consistent(var, value, assignment):
                continue

            assignment[var] = value
            removals: Removals = []

            if self._apply_inference(var, assignment, removals):
                result = self._backtrack(assignment, depth + 1)
                if result is not None:
                    return result

            self._backtracks += 1
            self._restore(removals)
            del assignment[var]

        return None

    # ------------------------------------------------------------------ Helpers

    def _select_unassigned_variable(self, assignment: Assignment) -> Optional[Variable]:
        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        unassigned = [var for var in self.csp.variables if var not in assignment]
        if not unassigned:
            return None

        # Select the variable with the smallest remaining domain to encourage early pruning.
        unassigned.sort(key=lambda var: (len(self.current_domains[var]), str(var)))
        return unassigned[0]

    def _apply_inference(self, var: Variable, assignment: Assignment, removals: Removals) -> bool:
        if not self._restrict_to_assignment(var, assignment[var], removals):
            return False

        for definition in self.techniques:
            if not definition.handler(self, var, assignment, removals):
                return False
        return True

    def _restore(self, removals: Removals) -> None:
        for var, value in reversed(removals):
            self.current_domains[var].add(value)

    # ------------------------------------------------------------------ Techniques

    def _forward_check(self, var: Variable, assignment: Assignment, removals: Removals) -> bool:
        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignment:
                continue

            for neighbor_value in list(self.current_domains[neighbor]):
                if not self.csp.is_consistent(neighbor, neighbor_value, assignment):
                    if self._prune(neighbor, neighbor_value, removals):
                        self._forward_prunes += 1

            if not self.current_domains[neighbor]:
                return False

        return True

    def _constraint_propagation(self, var: Variable, assignment: Assignment, removals: Removals) -> bool:
        if self.csp is None:
            raise RuntimeError("Solver must be prepared with a CSP before searching.")

        queue: List[Variable] = [var]

        while queue:
            current = queue.pop(0)
            for neighbor in self.neighbors.get(current, []):
                if neighbor in assignment:
                    continue

                pruned = False
                for neighbor_value in list(self.current_domains[neighbor]):
                    if not self.csp.is_consistent(neighbor, neighbor_value, assignment):
                        if self._prune(neighbor, neighbor_value, removals):
                            pruned = True

                if not self.current_domains[neighbor]:
                    return False

                if pruned:
                    queue.append(neighbor)
                    self._propagation_steps += 1

        return True

    # ------------------------------------------------------------------ Utilities

    def _restrict_to_assignment(self, var: Variable, value: Value, removals: Removals) -> bool:
        """
        Keep only the assigned value in the variable's domain so subsequent inference
        steps see the narrowed state.
        """
        if value not in self.current_domains[var]:
            return False

        for other_value in list(self.current_domains[var]):
            if other_value == value:
                continue
            self._prune(var, other_value, removals)

        return True

    def _prune(self, var: Variable, value: Value, removals: Removals) -> bool:
        """Remove a value from a domain (if still present) and record the operation."""
        domain = self.current_domains[var]
        if value not in domain:
            return False
        domain.remove(value)
        removals.append((var, value))
        return True


# ---------------------------------------------------------------------- Convenience

def inference_backtracking_search(
    csp: CSP,
    *,
    techniques: Sequence[str] = ("forward_checking",),
) -> Optional[Assignment]:
    """
    Solve the CSP using backtracking augmented with the specified inference techniques.

    Args:
        csp: Problem instance.
        techniques: Sequence of technique names to enable. Defaults to forward checking only.

    Returns:
        A satisfying assignment if one exists, otherwise None.
    """
    solver = InferenceBacktrackingSolver(techniques)
    return solver.solve(csp)


def inference_backtracking_with_metrics(
    csp: CSP,
    *,
    techniques: Sequence[str] = ("forward_checking",),
) -> Tuple[Optional[Assignment], Dict[str, Any]]:
    """
    Variant of `inference_backtracking_search` that also returns the collected metrics.
    """
    solver = InferenceBacktrackingSolver(techniques)
    return solver.solve_with_metrics(csp)


__all__ = [
    "InferenceBacktrackingSolver",
    "inference_backtracking_search",
    "inference_backtracking_with_metrics",
    "UnknownTechniqueError",
]
