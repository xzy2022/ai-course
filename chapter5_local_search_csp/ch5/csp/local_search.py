"""
Local Search Algorithms for CSPs

This module implements local search approaches for solving CSPs,
including min-conflicts and other hill-climbing variants.
"""

import random
from typing import Dict, Optional, List, Any, Tuple

from .csp import CSP, Variable


class LocalSearchSolver:
    """Local search solver using min-conflicts algorithm."""

    def __init__(self, max_steps: int = 1000, restarts: int = 10):
        self.max_steps = max_steps
        self.restarts = restarts
        self.steps_taken = 0
        self.current_conflicts = 0

    def solve(self, csp: CSP) -> Optional[Dict[Variable, Any]]:
        """Solve the CSP using min-conflicts local search."""
        for attempt in range(self.restarts):
            solution = self._min_conflicts(csp)
            if solution is not None:
                return solution
        return None

    def _min_conflicts(self, csp: CSP) -> Optional[Dict[Variable, Any]]:
        """Min-conflicts algorithm implementation."""
        # Generate initial complete assignment
        assignment = self._generate_initial_assignment(csp)

        for step in range(self.max_steps):
            self.steps_taken = step

            # Check if current assignment is a solution
            if csp.is_solution(assignment):
                self.current_conflicts = 0
                return assignment

            # Select conflicted variable
            conflicted_vars = self._get_conflicted_variables(csp, assignment)
            if not conflicted_vars:
                return assignment

            var = random.choice(conflicted_vars)

            # Select value that minimizes conflicts
            best_value = self._choose_best_value(csp, var, assignment)
            assignment[var] = best_value

        self.current_conflicts = len(self._get_conflicted_variables(csp, assignment))
        return None

    def _generate_initial_assignment(self, csp: CSP) -> Dict[Variable, Any]:
        """Generate a complete initial assignment by randomly assigning values."""
        assignment = {}
        for var in csp.variables:
            if csp.domains[var].is_empty():
                # If domain is empty, assign None (will be detected as conflict)
                assignment[var] = None
            else:
                # Randomly select a value from the domain
                assignment[var] = random.choice(list(csp.domains[var].values))
        return assignment

    def _get_conflicted_variables(self, csp: CSP, assignment: Dict[Variable, Any]) -> List[Variable]:
        """Return list of variables that are involved in violated constraints."""
        conflicted = set()

        for constraint in csp.constraints:
            if not constraint.is_satisfied(assignment):
                # Add all variables involved in this constraint
                for var in constraint.get_scope():
                    if var in assignment:
                        conflicted.add(var)

        return list(conflicted)

    def _count_conflicts(self, csp: CSP, var: Variable, value: Any,
                        assignment: Dict[Variable, Any]) -> int:
        """Count number of constraints violated by assigning value to var."""
        assignment_copy = assignment.copy()
        assignment_copy[var] = value

        conflicts = 0
        for constraint in csp.get_constraints(var):
            if not constraint.is_satisfied(assignment_copy):
                conflicts += 1

        return conflicts

    def _choose_best_value(self, csp: CSP, var: Variable,
                          assignment: Dict[Variable, Any]) -> Any:
        """Choose value for var that minimizes conflicts."""
        if csp.domains[var].is_empty():
            return None

        best_value = None
        min_conflicts = float('inf')

        for value in csp.domains[var].values:
            conflicts = self._count_conflicts(csp, var, value, assignment)
            if conflicts < min_conflicts:
                min_conflicts = conflicts
                best_value = value
            elif conflicts == min_conflicts and random.random() < 0.5:
                # Random tie-breaking
                best_value = value

        return best_value

    def get_statistics(self) -> Dict[str, Any]:
        """Return solver statistics."""
        return {
            'steps_taken': self.steps_taken,
            'current_conflicts': self.current_conflicts
        }


class SimulatedAnnealingSolver:
    """Simulated annealing local search solver."""

    def __init__(self, initial_temperature: float = 100.0,
                 cooling_rate: float = 0.995, min_temperature: float = 0.1,
                 max_iterations: int = 10000):
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iterations = max_iterations
        self.steps_taken = 0
        self.final_temperature = 0.0

    def solve(self, csp: CSP) -> Optional[Dict[Variable, Any]]:
        """Solve the CSP using simulated annealing."""
        # Generate initial assignment
        current = self._generate_initial_assignment(csp)
        current_energy = self._calculate_energy(csp, current)

        best = current.copy()
        best_energy = current_energy

        temperature = self.initial_temperature

        for step in range(self.max_iterations):
            self.steps_taken = step

            # Check if we found a solution
            if current_energy == 0:
                self.final_temperature = temperature
                return current

            # Stop if temperature is too low
            if temperature < self.min_temperature:
                break

            # Generate neighbor by randomly modifying one variable
            neighbor = self._generate_neighbor(csp, current)
            neighbor_energy = self._calculate_energy(csp, neighbor)

            # Decide whether to accept the neighbor
            delta = neighbor_energy - current_energy
            if delta < 0 or random.random() < self._acceptance_probability(delta, temperature):
                current = neighbor
                current_energy = neighbor_energy

                if current_energy < best_energy:
                    best = current.copy()
                    best_energy = current_energy

            # Cool down
            temperature *= self.cooling_rate

        self.final_temperature = temperature

        # Return best solution found (may not be optimal)
        if best_energy == 0:
            return best
        return None

    def _generate_initial_assignment(self, csp: CSP) -> Dict[Variable, Any]:
        """Generate a complete initial assignment."""
        assignment = {}
        for var in csp.variables:
            if not csp.domains[var].is_empty():
                assignment[var] = random.choice(list(csp.domains[var].values))
        return assignment

    def _generate_neighbor(self, csp: CSP, current: Dict[Variable, Any]) -> Dict[Variable, Any]:
        """Generate a neighbor solution by randomly changing one variable."""
        neighbor = current.copy()

        # Select a random variable
        var = random.choice(csp.variables)

        if not csp.domains[var].is_empty():
            # Assign a new random value from domain
            new_value = random.choice(list(csp.domains[var].values))
            neighbor[var] = new_value

        return neighbor

    def _calculate_energy(self, csp: CSP, assignment: Dict[Variable, Any]) -> int:
        """Calculate energy (number of violated constraints)."""
        conflicts = 0
        for constraint in csp.constraints:
            if not constraint.is_satisfied(assignment):
                conflicts += 1
        return conflicts

    def _acceptance_probability(self, delta: float, temperature: float) -> float:
        """Calculate acceptance probability for simulated annealing."""
        import math
        return math.exp(-delta / temperature)

    def get_statistics(self) -> Dict[str, Any]:
        """Return solver statistics."""
        return {
            'steps_taken': self.steps_taken,
            'final_temperature': self.final_temperature
        }