"""
Backtracking search with optional inference techniques (FC, propagation, AC).

The solver mirrors the instrumented style used by the heuristic backtracking
module but focuses on inference strategies that can be freely combined with
other enhancements (e.g. heuristics) in later pipelines.
"""

import collections
import time
import tracemalloc
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ..csp_core import CSP, Variable, Value

Assignment = Dict[Variable, Value]
Domain = Dict[Variable, Set[Value]]
Removals = List[Tuple[Variable, Value]]


def _build_neighbors(csp: CSP) -> Dict[Variable, Set[Variable]]:
    neighbors: Dict[Variable, Set[Variable]] = {var: set() for var in csp.variables}
    for constraint in csp.constraints:
        scope = constraint.scope
        for var in scope:
            others = set(scope) - {var}
            neighbors[var].update(others)
    return neighbors


class InstrumentedInferenceBacktracking:
    """
    Backtracking solver that augments search with optional inference steps:

    - Forward Checking (FC)
    - Constraint Propagation (iterative queue-based propagation)
    - Arc Consistency (AC-3)
    """

    def __init__(
        self,
        *,
        use_forward_checking: bool = False,
        use_constraint_propagation: bool = False,
        use_arc_consistency: bool = False,
        progress_interval: int = 10000,
        name: str = "Inference Backtracking",
    ) -> None:
        self.use_forward_checking = use_forward_checking
        self.use_constraint_propagation = use_constraint_propagation
        self.use_arc_consistency = use_arc_consistency
        self.progress_interval = progress_interval
        self.name = name

        self.csp: Optional[CSP] = None
        self.neighbors: Dict[Variable, Set[Variable]] = {}
        self.current_domains: Domain = {}
        self._reset_counters()

    def _reset_counters(self) -> None:
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.constraint_checks = 0
        self.domain_reductions = 0
        self.variable_selections = 0
        self.start_time = 0.0
        self.last_progress_time = 0.0
        self.forward_check_calls = 0
        self.propagation_steps = 0
        self.arc_enforcements = 0

    def solve_with_metrics(self, csp: CSP) -> Tuple[Optional[Assignment], Dict[str, Any]]:
        """
        Execute backtracking search with the configured inference techniques.
        """
        self.csp = csp
        self.neighbors = _build_neighbors(csp)
        self.current_domains = {
            var: set(domain) for var, domain in csp.domains.items()
        }
        self._reset_counters()

        tracemalloc.start()
        self.start_time = time.time()
        self.last_progress_time = self.start_time

        solution = self._recursive_backtrack({})

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        metrics = {
            "time_seconds": end_time - self.start_time,
            "memory_peak_mb": peak / 1024 / 1024,
            "attempt_count": self.attempt_count,
            "max_recursion_depth": self.max_recursion_depth,
            "constraint_checks": self.constraint_checks,
            "domain_reductions": self.domain_reductions,
            "variable_selections": self.variable_selections,
            "total_variables": len(csp.variables),
            "constraints": len(csp.constraints),
            "selection_attempt_ratio": self.variable_selections / max(1, self.attempt_count),
            "use_forward_checking": self.use_forward_checking,
            "use_constraint_propagation": self.use_constraint_propagation,
            "use_arc_consistency": self.use_arc_consistency,
            "solver_name": self.name,
            "progress_interval": self.progress_interval,
            "forward_check_calls": self.forward_check_calls,
            "propagation_steps": self.propagation_steps,
            "arc_enforcements": self.arc_enforcements,
            "solution_found": solution is not None,
        }

        solution_snapshot = dict(solution) if solution is not None else None
        return solution_snapshot, metrics

    # ------------------------------------------------------------------ Search

    def _recursive_backtrack(self, assignment: Assignment) -> Optional[Assignment]:
        if self.csp is None:
            raise RuntimeError("Solver is not initialised with a CSP.")

        if self._is_complete(assignment):
            return dict(assignment)

        self.attempt_count += 1
        self.recursion_depth += 1
        self.max_recursion_depth = max(self.max_recursion_depth, self.recursion_depth)

        if self.progress_interval > 0 and self.attempt_count % self.progress_interval == 0:
            self._report_progress(len(assignment))

        var = self._select_unassigned_variable(assignment)
        if var is None:
            self.recursion_depth -= 1
            return None

        for value in self._order_domain_values(var):
            if self._is_consistent(var, value, assignment):
                assignment[var] = value
                removals: Removals = []
                self._assign_domain(var, value, removals)

                inference_ok = self._apply_inference(var, assignment, removals)
                if inference_ok:
                    result = self._recursive_backtrack(assignment)
                    if result is not None:
                        self._restore_domains(removals)
                        self.recursion_depth -= 1
                        return result

                self._restore_domains(removals)
                del assignment[var]

        self.recursion_depth -= 1
        return None

    # -------------------------------------------------------------- Infrastructure

    def _select_unassigned_variable(self, assignment: Assignment) -> Optional[Variable]:
        if self.csp is None:
            return None

        unassigned = [var for var in sorted(self.csp.variables, key=str) if var not in assignment]
        if not unassigned:
            return None
        self.variable_selections += 1
        return unassigned[0]

    def _order_domain_values(self, var: Variable) -> List[Value]:
        return sorted(self.current_domains[var])

    def _is_complete(self, assignment: Assignment) -> bool:
        if self.csp is None:
            return False
        return len(assignment) == len(self.csp.variables)

    def _is_consistent(self, var: Variable, value: Value, assignment: Assignment) -> bool:
        if self.csp is None:
            return False
        self.constraint_checks += len(self.csp.constraints)
        return self.csp.is_consistent(var, value, assignment)

    # ----------------------------------------------------------- Domain Handling

    def _assign_domain(self, var: Variable, value: Value, removals: Removals) -> None:
        current = self.current_domains[var]
        for other in list(current):
            if other != value:
                self._remove_value(var, other, removals)

    def _remove_value(self, var: Variable, value: Value, removals: Removals) -> None:
        domain = self.current_domains[var]
        if value in domain:
            domain.remove(value)
            removals.append((var, value))
            self.domain_reductions += 1

    def _restore_domains(self, removals: Removals) -> None:
        for var, value in reversed(removals):
            self.current_domains[var].add(value)

    # ----------------------------------------------------------- Inference logic

    def _apply_inference(
        self,
        var: Variable,
        assignment: Assignment,
        removals: Removals,
    ) -> bool:
        affected: List[Variable] = []
        if self.use_forward_checking:
            self.forward_check_calls += 1
            success, reduced = self._forward_check(var, assignment, removals)
            if not success:
                return False
            affected.extend(reduced)

        if self.use_constraint_propagation:
            if not affected:
                affected.extend(self.neighbors.get(var, []))
            success = self._propagate_constraints(affected, assignment, removals)
            if not success:
                return False

        if self.use_arc_consistency:
            success = self._enforce_arc_consistency(assignment, removals)
            if not success:
                return False

        return True

    def _forward_check(
        self,
        var: Variable,
        assignment: Assignment,
        removals: Removals,
    ) -> Tuple[bool, List[Variable]]:
        reduced_neighbors: List[Variable] = []
        for neighbor in self.neighbors.get(var, []):
            if neighbor in assignment:
                continue

            domain_reduced = False
            for value in list(self.current_domains[neighbor]):
                if not self._is_consistent(neighbor, value, assignment):
                    self._remove_value(neighbor, value, removals)
                    domain_reduced = True

            if domain_reduced:
                reduced_neighbors.append(neighbor)

            if not self.current_domains[neighbor]:
                return False, reduced_neighbors

        return True, reduced_neighbors

    def _propagate_constraints(
        self,
        initial_vars: Iterable[Variable],
        assignment: Assignment,
        removals: Removals,
    ) -> bool:
        queue = collections.deque(initial_vars)

        while queue:
            current = queue.popleft()
            if current in assignment:
                continue

            for neighbor in self.neighbors.get(current, []):
                if neighbor in assignment:
                    continue

                revised, ok = self._revise(current, neighbor, assignment, removals)
                if not ok:
                    return False

                if revised:
                    self.propagation_steps += 1
                    queue.append(neighbor)

        return True

    def _enforce_arc_consistency(
        self,
        assignment: Assignment,
        removals: Removals,
    ) -> bool:
        queue: collections.deque[Tuple[Variable, Variable]] = collections.deque()
        for xi in self.current_domains:
            for xj in self.neighbors.get(xi, []):
                queue.append((xi, xj))

        while queue:
            xi, xj = queue.popleft()
            revised, ok = self._revise(xi, xj, assignment, removals)
            if not ok:
                return False
            if revised:
                self.arc_enforcements += 1
                for xk in self.neighbors.get(xi, []):
                    if xk != xj:
                        queue.append((xk, xi))

        return True

    def _revise(
        self,
        xi: Variable,
        xj: Variable,
        assignment: Assignment,
        removals: Removals,
    ) -> Tuple[bool, bool]:
        revised = False
        for value in list(self.current_domains[xi]):
            if not self._has_support(xi, value, xj, assignment):
                self._remove_value(xi, value, removals)
                revised = True
            if not self.current_domains[xi]:
                return revised, False
        return revised, True

    def _has_support(
        self,
        xi: Variable,
        value: Value,
        xj: Variable,
        assignment: Assignment,
    ) -> bool:
        if xj not in self.current_domains:
            return True

        temp_assignment = dict(assignment)
        temp_assignment[xi] = value

        for neighbor_value in self.current_domains[xj]:
            temp_assignment[xj] = neighbor_value
            if self._is_consistent(xi, value, temp_assignment) and self._is_consistent(xj, neighbor_value, temp_assignment):
                return True

        return False

    # ----------------------------------------------------------- Progress report

    def _report_progress(self, assigned_count: int) -> None:
        if self.csp is None:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time
        total = len(self.csp.variables)
        filled_percentage = (assigned_count / total) * 100 if total else 0
        attempts_per_second = self.attempt_count / elapsed if elapsed > 0 else 0

        inference_state = (
            f"FC{'1' if self.use_forward_checking else '0'}"
            f"P{'1' if self.use_constraint_propagation else '0'}"
            f"AC{'1' if self.use_arc_consistency else '0'}"
        )

        print(
            f"[PROGRESS:{self.name}] Attempts: {self.attempt_count:,} | "
            f"Time: {elapsed:.1f}s | Rate: {attempts_per_second:,.0f}/s | "
            f"Filled: {filled_percentage:.1f}% | Depth: {self.recursion_depth} | "
            f"Inference: {inference_state}"
        )

        self.last_progress_time = current_time
