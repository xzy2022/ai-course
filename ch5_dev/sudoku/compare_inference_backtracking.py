"""
Compare inference combinations for the generic backtracking Sudoku solver.

Runs the configurable inference backtracking solver with several technique
combinations, summarises metrics, and writes comparison charts to
``ch5_dev/output/sudoku_inference_backtracking.png``.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt

# Allow executing the module directly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q1_sudoku_csp import get_sample_sudoku_puzzle
from sudoku.solve_inference_backtracking import (
    DEFAULT_TECHNIQUES,
    solve_puzzle_with_inference,
)

SudokuCell = Tuple[int, int]
SudokuGrid = Dict[SudokuCell, int]

TechniqueConfig = Tuple[str, Sequence[str]]
Result = Dict[str, object]


def evaluate_configs(
    puzzle: SudokuGrid,
    configs: Iterable[TechniqueConfig],
) -> List[Result]:
    """Execute the solver for each configuration and collect metrics."""
    results: List[Result] = []
    for label, techniques in configs:
        solution, metrics = solve_puzzle_with_inference(puzzle, techniques)
        results.append(
            {
                "label": label,
                "techniques": list(techniques),
                "solution": solution,
                "metrics": metrics,
            }
        )
    return results


def _bar_plot(ax, labels: List[str], values: List[float], title: str, ylabel: str, color: str) -> None:
    positions = list(range(len(labels)))
    ax.bar(positions, values, color=color)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=30, ha="right")


def plot_results(results: List[Result], output_dir: str) -> str:
    """Generate comparison charts for runtime, memory, and search statistics."""
    labels = [item["label"] for item in results]
    times = [item["metrics"]["elapsed_seconds"] for item in results]
    peaks = [item["metrics"]["peak_memory_mb"] for item in results]
    nodes = [item["metrics"]["nodes_expanded"] for item in results]
    backtracks = [item["metrics"]["backtracks"] for item in results]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    _bar_plot(axes[0][0], labels, times, "Runtime", "Seconds", "#2E86AB")
    _bar_plot(axes[0][1], labels, peaks, "Peak Memory", "MB", "#F18F01")
    _bar_plot(axes[1][0], labels, nodes, "Nodes Expanded", "Nodes", "#4CAF50")
    _bar_plot(axes[1][1], labels, backtracks, "Backtracks", "Count", "#C3423F")

    fig.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sudoku_inference_backtracking.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    comparison_configs: List[TechniqueConfig] = [
        ("FC + Prop + AC", DEFAULT_TECHNIQUES),
        ("Forward Checking", ("forward_checking",)),
        ("Propagation", ("constraint_propagation",)),
        ("Arc Consistency", ("arc_consistency",)),
        ("FC + AC", ("forward_checking", "arc_consistency")),
        ("FC + Prop", ("forward_checking", "constraint_propagation")),
        ("No Inference", ()),
    ]

    puzzle = get_sample_sudoku_puzzle()
    print("Evaluating inference backtracking configurations...")
    results = evaluate_configs(puzzle, comparison_configs)

    for item in results:
        metrics = item["metrics"]
        print(
            f"- {item['label']}: "
            f"time={metrics['elapsed_seconds']:.4f}s, "
            f"peak_mem={metrics['peak_memory_mb']:.4f}MB, "
            f"nodes={int(metrics['nodes_expanded'])}, "
            f"backtracks={int(metrics['backtracks'])}"
        )

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    output_path = plot_results(results, output_dir)
    print(f"\nSaved comparison chart to {output_path}")


if __name__ == "__main__":
    main()
