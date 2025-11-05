"""
Backtracking search with selectable heuristics.

This module extends the basic backtracking strategy by optionally enabling:
- Minimum Remaining Values (MRV)
- Degree heuristic (most constrained variable)
- Least Constraining Value (LCV)

All heuristics are toggled independently via keyword arguments. By default all
three heuristics are enabled.
"""

import time
import tracemalloc
from typing import Dict, List, Optional, Tuple, Iterable, Set, Any

from ..csp_core import CSP, Variable, Value

HeuristicFlags = Tuple[bool, bool, bool]


def heuristic_backtracking_search(
    csp: CSP,
    *,
    use_mrv: bool = True,
    use_degree: bool = True,
    use_lcv: bool = True,
) -> Optional[Dict[Variable, Value]]:
    """
    Solve the given CSP using backtracking with configurable heuristics.
    """
    assignment: Dict[Variable, Value] = {}
    neighbors = _build_neighbors(csp)
    return _recursive_backtrack(
        csp,
        assignment,
        neighbors,
        (use_mrv, use_degree, use_lcv),
    )


def select_unassigned_variable(
    csp: CSP,
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
    *,
    use_mrv: bool,
    use_degree: bool,
) -> Tuple[Optional[Variable], List[Value]]:
    """
    Public helper for tests: choose next variable and return its legal values.
    """
    return _select_unassigned_variable(
        csp,
        assignment,
        neighbors,
        (use_mrv, use_degree, False),
    )


def order_domain_values(
    csp: CSP,
    var: Variable,
    legal_values: Iterable[Value],
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
    *,
    use_lcv: bool,
) -> List[Value]:
    """
    Public helper for tests: order domain values for the given variable.
    """
    return _order_domain_values(
        csp,
        var,
        list(legal_values),
        assignment,
        neighbors,
        (False, False, use_lcv),
    )


def _recursive_backtrack(
    csp: CSP,
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
    flags: HeuristicFlags,
) -> Optional[Dict[Variable, Value]]:
    use_mrv, use_degree, use_lcv = flags

    if csp.is_complete(assignment):
        return assignment

    var, legal_values = _select_unassigned_variable(
        csp,
        assignment,
        neighbors,
        flags,
    )
    if var is None or not legal_values:
        return None

    ordered_values = _order_domain_values(
        csp,
        var,
        legal_values,
        assignment,
        neighbors,
        flags,
    )

    for value in ordered_values:
        if csp.is_consistent(var, value, assignment):
            assignment[var] = value
            result = _recursive_backtrack(csp, assignment, neighbors, flags)
            if result is not None:
                return result
            del assignment[var]

    return None


def _select_unassigned_variable(
    csp: CSP,
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
    flags: HeuristicFlags,
) -> Tuple[Optional[Variable], List[Value]]:
    use_mrv, use_degree, _ = flags

    candidates: List[Tuple[Variable, List[Value], int, int]] = []
    for var in csp.variables:
        if var in assignment:
            continue
        legal_values = _get_legal_values(csp, var, assignment)
        degree = _count_unassigned_neighbors(var, neighbors, assignment)
        candidates.append((var, legal_values, len(legal_values), degree))

    if not candidates:
        return None, []

    filtered = candidates
    if use_degree:
        max_degree = max(item[3] for item in filtered)
        filtered = [item for item in filtered if item[3] == max_degree]
    if use_mrv:
        min_domain = min(item[2] for item in filtered)
        filtered = [item for item in filtered if item[2] == min_domain]

    filtered.sort(key=lambda item: (str(item[0])))
    best_var, legal_values, _, _ = filtered[0]
    return best_var, legal_values


def _order_domain_values(
    csp: CSP,
    var: Variable,
    legal_values: List[Value],
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
    flags: HeuristicFlags,
) -> List[Value]:
    _, _, use_lcv = flags

    if not use_lcv:
        return list(legal_values)

    scored: List[Tuple[int, Value]] = []
    for value in legal_values:
        impact = _count_value_impact(csp, var, value, assignment, neighbors)
        scored.append((impact, value))

    scored.sort(key=lambda item: (item[0], item[1]))
    return [value for _, value in scored]


def _count_value_impact(
    csp: CSP,
    var: Variable,
    value: Value,
    assignment: Dict[Variable, Value],
    neighbors: Dict[Variable, Set[Variable]],
) -> int:
    assignment[var] = value
    impact = 0

    for neighbor in neighbors[var]:
        if neighbor in assignment:
            continue
        legal_count = 0
        for neighbor_value in csp.domains[neighbor]:
            if csp.is_consistent(neighbor, neighbor_value, assignment):
                legal_count += 1
        impact += len(csp.domains[neighbor]) - legal_count

    del assignment[var]
    return impact


def _get_legal_values(
    csp: CSP,
    var: Variable,
    assignment: Dict[Variable, Value],
) -> List[Value]:
    legal = []
    for value in csp.domains[var]:
        if csp.is_consistent(var, value, assignment):
            legal.append(value)
    return legal


def _count_unassigned_neighbors(
    var: Variable,
    neighbors: Dict[Variable, Set[Variable]],
    assignment: Dict[Variable, Value],
) -> int:
    return sum(1 for neighbor in neighbors[var] if neighbor not in assignment)


def _build_neighbors(csp: CSP) -> Dict[Variable, Set[Variable]]:
    neighbors: Dict[Variable, Set[Variable]] = {var: set() for var in csp.variables}
    for constraint in csp.constraints:
        scope = constraint.scope
        for var in scope:
            others = set(scope) - {var}
            neighbors[var].update(others)
    return neighbors


class InstrumentedHeuristicBacktracking:
    """
    Backtracking solver that records detailed metrics while applying heuristics.

    The implementation mirrors the behaviour of :func:`heuristic_backtracking_search`
    but captures search statistics (attempt counts, depth, constraint checks, etc.)
    and optionally reports progress.
    """

    def __init__(
        self,
        *,
        use_mrv: bool = True,
        use_degree: bool = True,
        use_lcv: bool = True,
        progress_interval: int = 10000,
        name: str = "Heuristic Backtracking",
    ) -> None:
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        self.progress_interval = progress_interval
        self.name = name

        self.csp: Optional[CSP] = None
        self.neighbors: Dict[Variable, Set[Variable]] = {}
        self._reset_counters()

    def _reset_counters(self) -> None:
        self.attempt_count = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.constraint_checks = 0
        self.domain_reductions = 0
        self.variable_selections = 0
        self.mrv_applications = 0
        self.degree_applications = 0
        self.lcv_applications = 0
        self.start_time = 0.0
        self.last_progress_time = 0.0
        self.initial_assignment_size = 0

    def solve_with_metrics(
        self,
        csp: CSP,
        initial_assignment: Optional[Dict[Variable, Value]] = None,
    ) -> Tuple[Optional[Dict[Variable, Value]], Dict[str, Any]]:
        """
        Execute heuristic backtracking while capturing search metrics.
        """
        self.csp = csp
        self.neighbors = _build_neighbors(csp)
        self._reset_counters()

        tracemalloc.start()
        self.start_time = time.time()
        self.last_progress_time = self.start_time

        assignment: Dict[Variable, Value] = {}
        if initial_assignment:
            for var, value in initial_assignment.items():
                if var not in csp.variables:
                    raise ValueError(f"Initial assignment contains unknown variable: {var}")
                if value not in csp.domains[var]:
                    raise ValueError(
                        f"Initial assignment for {var} uses value {value} which is outside its domain."
                    )
                if not csp.is_consistent(var, value, assignment):
                    raise ValueError(f"Initial assignment is inconsistent for variable {var}.")
                assignment[var] = value
        self.initial_assignment_size = len(assignment)

        solution = self._instrumented_recursive_backtrack(assignment)

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        time_elapsed = end_time - self.start_time
        memory_peak = peak / 1024 / 1024
        solution_snapshot = dict(solution) if solution is not None else None

        metrics: Dict[str, Any] = {
            "time_seconds": time_elapsed,
            "memory_peak_mb": memory_peak,
            "attempt_count": self.attempt_count,
            "max_recursion_depth": self.max_recursion_depth,
            "constraint_checks": self.constraint_checks,
            "domain_reductions": self.domain_reductions,
            "variable_selections": self.variable_selections,
            "mrv_applications": self.mrv_applications,
            "degree_applications": self.degree_applications,
            "lcv_applications": self.lcv_applications,
            "selection_attempt_ratio": self.variable_selections / max(1, self.attempt_count),
            "total_variables": len(csp.variables),
            "constraints": len(csp.constraints),
            "avg_domain_size": self._calculate_average_domain_size(),
            "efficiency": self._calculate_efficiency(),
            "use_mrv": self.use_mrv,
            "use_degree": self.use_degree,
            "use_lcv": self.use_lcv,
            "solver_name": self.name,
            "progress_interval": self.progress_interval,
            "solution_found": solution is not None,
            "initial_assignment_size": self.initial_assignment_size,
        }

        return solution_snapshot, metrics

    def _instrumented_recursive_backtrack(
        self,
        assignment: Dict[Variable, Value],
    ) -> Optional[Dict[Variable, Value]]:
        if self.csp is None:
            raise RuntimeError("Solver must be initialised with a CSP before searching.")

        self.attempt_count += 1
        self.recursion_depth += 1
        self.max_recursion_depth = max(self.max_recursion_depth, self.recursion_depth)

        if self.progress_interval > 0 and self.attempt_count % self.progress_interval == 0:
            self._report_progress(len(assignment))

        if self.csp.is_complete(assignment):
            self.recursion_depth -= 1
            return assignment

        var, legal_values = self._select_unassigned_variable(assignment)
        if var is None or not legal_values:
            self.recursion_depth -= 1
            return None

        ordered_values = self._order_domain_values(var, legal_values, assignment)
        if not ordered_values:
            self.recursion_depth -= 1
            return None

        for value in ordered_values:
            assignment[var] = value
            self.domain_reductions += 1

            result = self._instrumented_recursive_backtrack(assignment)
            if result is not None:
                self.recursion_depth -= 1
                return result

            del assignment[var]

        self.recursion_depth -= 1
        return None

    def _select_unassigned_variable(
        self,
        assignment: Dict[Variable, Value],
    ) -> Tuple[Optional[Variable], List[Value]]:
        if self.csp is None:
            raise RuntimeError("Solver must be initialised with a CSP before searching.")

        candidates: List[Tuple[Variable, List[Value], int]] = []
        for var in sorted(self.csp.variables, key=str):
            if var in assignment:
                continue

            legal_values = []
            for value in self.csp.domains[var]:
                if self._is_consistent(var, value, assignment):
                    legal_values.append(value)

            degree = _count_unassigned_neighbors(var, self.neighbors, assignment)
            candidates.append((var, legal_values, degree))

        if not candidates:
            return None, []

        self.variable_selections += 1
        filtered = candidates

        if self.use_degree:
            self.degree_applications += 1
            max_degree = max(item[2] for item in filtered)
            filtered = [item for item in filtered if item[2] == max_degree]

        if self.use_mrv:
            self.mrv_applications += 1
            min_domain = min(len(item[1]) for item in filtered)
            filtered = [item for item in filtered if len(item[1]) == min_domain]

        filtered.sort(key=lambda item: str(item[0]))
        selected_var, legal_values, _ = filtered[0]
        return selected_var, list(legal_values)

    def _order_domain_values(
        self,
        var: Variable,
        legal_values: List[Value],
        assignment: Dict[Variable, Value],
    ) -> List[Value]:
        if not self.use_lcv:
            return list(legal_values)

        if self.csp is None:
            raise RuntimeError("Solver must be initialised with a CSP before searching.")

        self.lcv_applications += 1
        scored: List[Tuple[int, Value]] = []

        for value in legal_values:
            impact = self._count_value_impact(var, value, assignment)
            scored.append((impact, value))

        scored.sort(key=lambda item: (item[0], str(item[1])))
        return [value for _, value in scored]

    def _count_value_impact(
        self,
        var: Variable,
        value: Value,
        assignment: Dict[Variable, Value],
    ) -> int:
        if self.csp is None:
            raise RuntimeError("Solver must be initialised with a CSP before searching.")

        impact = 0
        assignment[var] = value

        for neighbor in self.neighbors[var]:
            if neighbor in assignment:
                continue

            for neighbor_value in self.csp.domains[neighbor]:
                if not self._is_consistent(neighbor, neighbor_value, assignment):
                    impact += 1

        del assignment[var]
        return impact

    def _is_consistent(
        self,
        var: Variable,
        value: Value,
        assignment: Dict[Variable, Value],
    ) -> bool:
        if self.csp is None:
            raise RuntimeError("Solver must be initialised with a CSP before searching.")

        self.constraint_checks += len(self.csp.constraints)
        return self.csp.is_consistent(var, value, assignment)

    def _calculate_average_domain_size(self) -> float:
        if not self.csp:
            return 0.0
        domain_sizes = [len(self.csp.domains[var]) for var in self.csp.variables]
        return sum(domain_sizes) / len(domain_sizes)

    def _calculate_efficiency(self) -> float:
        if self.attempt_count == 0:
            return 0.0
        return self.constraint_checks / self.attempt_count

    def _report_progress(self, assigned_count: int) -> None:
        if not self.csp:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time
        total = len(self.csp.variables)
        filled_percentage = (assigned_count / total) * 100 if total else 0
        attempts_per_second = self.attempt_count / elapsed if elapsed > 0 else 0
        heuristic_state = f"M{'1' if self.use_mrv else '0'}D{'1' if self.use_degree else '0'}L{'1' if self.use_lcv else '0'}"

        print(
            f"[PROGRESS:{self.name}] Attempts: {self.attempt_count:,} | "
            f"Time: {elapsed:.1f}s | Rate: {attempts_per_second:,.0f}/s | "
            f"Filled: {filled_percentage:.1f}% | Depth: {self.recursion_depth} | "
            f"Heuristics: {heuristic_state}"
        )

        self.last_progress_time = current_time
