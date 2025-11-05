"""
Compare heuristic configurations for the Australia map coloring CSP.

This script reuses the australia_solver module to evaluate different heuristic
combinations and plots their performance metrics. The resulting chart is saved
under ch5_dev/output/.
"""

import os
import sys
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt

# Allow importing sibling modules when executed as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coloring.australia_solver import solve_australia_map

Result = Dict[str, object]


def evaluate_configurations(configs: Iterable[Tuple[str, Dict[str, bool]]]) -> List[Result]:
    """Run the solver for each named configuration and collect metrics."""
    results: List[Result] = []
    for label, flags in configs:
        solution, metrics = solve_australia_map(
            use_mrv=flags.get("use_mrv", True),
            use_degree=flags.get("use_degree", True),
            use_lcv=flags.get("use_lcv", True),
            solver_name=f"Australia Solver [{label}]",
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
    """Generate bar charts for time and attempt metrics and save the figure."""
    labels = [item["label"] for item in results]
    positions = range(len(labels))
    times = [item["metrics"]["time_seconds"] for item in results]
    attempts = [item["metrics"]["attempt_count"] for item in results]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(positions, times, color="#2E86AB")
    axes[0].set_title("Runtime (seconds)")
    axes[0].set_ylabel("Seconds")
    axes[0].set_xticks(list(positions))
    axes[0].set_xticklabels(labels, rotation=30, ha="right")

    axes[1].bar(positions, attempts, color="#F6AA1C")
    axes[1].set_title("Search Attempts")
    axes[1].set_ylabel("Attempts")
    axes[1].set_xticks(list(positions))
    axes[1].set_xticklabels(labels, rotation=30, ha="right")

    fig.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "australia_heuristic_comparison.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    # Edit the combinations below to compare different heuristic settings.
    comparison_configs: List[Tuple[str, Dict[str, bool]]] = [
        ("All heuristics", {"use_mrv": True, "use_degree": True, "use_lcv": True}),
        ("MRV only", {"use_mrv": True, "use_degree": False, "use_lcv": False}),
        ("Degree only", {"use_mrv": False, "use_degree": True, "use_lcv": False}),
        ("LCV only", {"use_mrv": False, "use_degree": False, "use_lcv": True}),
        ("No heuristics", {"use_mrv": False, "use_degree": False, "use_lcv": False}),
    ]

    print("Evaluating Australia map coloring heuristics...")
    results = evaluate_configurations(comparison_configs)

    for item in results:
        metrics = item["metrics"]
        print(
            f"- {item['label']}: "
            f"time={metrics['time_seconds']:.6f}s, "
            f"attempts={metrics['attempt_count']}, "
            f"depth={metrics['max_recursion_depth']}"
        )

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    output_path = plot_results(results, output_dir)
    print(f"\nSaved comparison chart to {output_path}")


if __name__ == "__main__":
    main()
