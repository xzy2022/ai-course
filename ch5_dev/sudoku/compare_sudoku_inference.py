"""
Compare inference configurations for the Sudoku CSP solver.

Evaluates different combinations of forward checking, constraint propagation,
and arc consistency, then plots runtime and search attempts to
ch5_dev/output/sudoku_inference_comparison.png.
"""

import os
import sys
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q1_sudoku_csp import get_sample_sudoku_puzzle
from sudoku.sudoku_inference_solver import solve_sudoku_with_inference

Config = Tuple[str, Dict[str, bool]]
Result = Dict[str, object]


def evaluate_configs(
    puzzle: Dict[Tuple[int, int], int],
    configs: Iterable[Config],
) -> List[Result]:
    """Run the solver over each configuration and collect metrics."""
    results: List[Result] = []
    for label, flags in configs:
        solution, metrics = solve_sudoku_with_inference(
            puzzle,
            use_forward_checking=flags.get("use_forward_checking", True),
            use_constraint_propagation=flags.get("use_constraint_propagation", True),
            use_arc_consistency=flags.get("use_arc_consistency", True),
            solver_name=f"Sudoku Inference [{label}]",
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
    """Create bar charts for runtime and attempts and save to disk."""
    labels = [item["label"] for item in results]
    positions = list(range(len(labels)))
    times = [item["metrics"]["time_seconds"] for item in results]
    attempts = [item["metrics"]["attempt_count"] for item in results]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(positions, times, color="#2E86AB")
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
    output_path = os.path.join(output_dir, "sudoku_inference_comparison.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    # Edit this list to compare different inference combinations.
    comparison_configs: List[Config] = [
        (
            "FC + Prop + AC",
            {
                "use_forward_checking": True,
                "use_constraint_propagation": True,
                "use_arc_consistency": True,
            },
        ),
        (
            "Forward Checking only",
            {
                "use_forward_checking": True,
                "use_constraint_propagation": False,
                "use_arc_consistency": False,
            },
        ),
        (
            "Propagation only",
            {
                "use_forward_checking": False,
                "use_constraint_propagation": True,
                "use_arc_consistency": False,
            },
        ),
        (
            "Arc Consistency only",
            {
                "use_forward_checking": False,
                "use_constraint_propagation": False,
                "use_arc_consistency": True,
            },
        ),
        (
            "No inference",
            {
                "use_forward_checking": False,
                "use_constraint_propagation": False,
                "use_arc_consistency": False,
            },
        ),
    ]

    puzzle = get_sample_sudoku_puzzle()
    print("Evaluating Sudoku inference configurations...")
    results = evaluate_configs(puzzle, comparison_configs)

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
