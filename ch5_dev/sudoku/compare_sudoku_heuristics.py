"""
Compare heuristic configurations for the Sudoku CSP solver.

This script reuses sudoku_solver.solve_sudoku_puzzle to evaluate multiple
heuristic combinations and produces a summary plot saved in ch5_dev/output/.
"""

import os
import sys
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt

# Ensure project modules resolve when run as a script.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q1_sudoku_csp import get_sample_sudoku_puzzle
from sudoku.sudoku_solver import solve_sudoku_puzzle

Result = Dict[str, object]


def evaluate_configurations(
    puzzle: Dict[Tuple[int, int], int],
    configs: Iterable[Tuple[str, Dict[str, bool]]],
) -> List[Result]:
    """Solve the puzzle under each heuristic configuration and collect metrics."""
    results: List[Result] = []
    for label, flags in configs:
        solution, metrics = solve_sudoku_puzzle(
            puzzle,
            use_mrv=flags.get("use_mrv", True),
            use_degree=flags.get("use_degree", True),
            use_lcv=flags.get("use_lcv", True),
            solver_name=f"Sudoku Solver [{label}]",
            progress_interval=10000,
        )
        results.append(
            {
                "label": label,
                "solution": solution,
                "metrics": metrics,
            }
        )
    return results


def plot_results(results: List[Result], output_dir: str) -> str:
    """Generate side-by-side bar charts for runtime and attempt counts."""
    labels = [item["label"] for item in results]
    positions = list(range(len(labels)))
    times = [item["metrics"]["time_seconds"] for item in results]
    attempts = [item["metrics"]["attempt_count"] for item in results]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(positions, times, color="#2C82C9")
    axes[0].set_title("Runtime (seconds)")
    axes[0].set_ylabel("Seconds")
    axes[0].set_xticks(positions)
    axes[0].set_xticklabels(labels, rotation=30, ha="right")

    axes[1].bar(positions, attempts, color="#F6AA1C")
    axes[1].set_title("Search Attempts")
    axes[1].set_ylabel("Attempts")
    axes[1].set_xticks(positions)
    axes[1].set_xticklabels(labels, rotation=30, ha="right")

    fig.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sudoku_heuristic_comparison.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    # Modify this list to try different heuristic combinations.
    comparison_configs: List[Tuple[str, Dict[str, bool]]] = [
        ("All heuristics", {"use_mrv": True, "use_degree": True, "use_lcv": True}),
        ("MRV only", {"use_mrv": True, "use_degree": False, "use_lcv": False}),
        ("Degree only", {"use_mrv": False, "use_degree": True, "use_lcv": False}),
        ("LCV only", {"use_mrv": False, "use_degree": False, "use_lcv": True}),
        ("No heuristics", {"use_mrv": False, "use_degree": False, "use_lcv": False}),
    ]

    puzzle = get_sample_sudoku_puzzle()
    print("Evaluating Sudoku heuristic configurations...")
    results = evaluate_configurations(puzzle, comparison_configs)

    for item in results:
        metrics = item["metrics"]
        print(
            f"- {item['label']}: "
            f"time={metrics['time_seconds']:.4f}s, "
            f"attempts={metrics['attempt_count']:,}, "
            f"depth={metrics['max_recursion_depth']}"
        )

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    output_path = plot_results(results, output_dir)
    print(f"\nSaved comparison chart to {output_path}")


if __name__ == "__main__":
    main()
