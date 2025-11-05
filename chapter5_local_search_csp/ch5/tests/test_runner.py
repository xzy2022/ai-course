"""
Test Runner for CSP Library

This module provides a comprehensive test runner that can execute
all tests or specific test suites, and generate reports on test results.
"""

import unittest
import sys
import time
from io import StringIO


class CSPTestResult(unittest.TestResult):
    """Custom test result class for collecting detailed information."""

    def __init__(self):
        super().__init__()
        self.test_results = []
        self.start_time = None
        self.end_time = None

    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()

    def stopTest(self, test):
        super().stopTest(test)
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        self.test_results.append({
            'test': str(test),
            'status': 'PASS' if not self.errors and not self.failures else 'FAIL',
            'duration': duration,
            'error': None,
            'failure': None
        })

        # Update the last result with error/failure information
        if self.errors and self.errors[-1][0] == test:
            self.test_results[-1]['status'] = 'ERROR'
            self.test_results[-1]['error'] = self.errors[-1][1]
        elif self.failures and self.failures[-1][0] == test:
            self.test_results[-1]['status'] = 'FAIL'
            self.test_results[-1]['failure'] = self.failures[-1][1]


def run_all_tests():
    """Run all tests in the CSP library."""
    # Import all test modules
    from .test_csp import *
    from .test_sudoku import *
    from .test_coloring import *

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test modules
    suite.addTests(loader.loadTestsFromModule(sys.modules[__name__]))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, resultclass=CSPTestResult)
    result = runner.run(suite)

    return result


def run_csp_tests():
    """Run only core CSP tests."""
    from .test_csp import *

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_sudoku_tests():
    """Run only Sudoku tests."""
    from .test_sudoku import *

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_coloring_tests():
    """Run only graph coloring tests."""
    from .test_coloring import *

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_performance_tests():
    """Run performance-focused tests."""
    print("Running Performance Tests...")
    print("=" * 50)

    # Test Sudoku solver performance
    print("\n1. Testing Sudoku Solver Performance")
    from ..sudoku import SudokuParser, SudokuSolver

    puzzles = SudokuParser.create_sample_puzzles()
    for difficulty, puzzle in puzzles.items():
        print(f"\nTesting {difficulty} puzzle:")

        # Test backtracking
        start_time = time.time()
        solver = SudokuSolver("backtracking")
        solution = solver.solve(puzzle)
        end_time = time.time()

        if solution:
            print(f"  Backtracking: {end_time - start_time:.4f}s - SUCCESS")
        else:
            print(f"  Backtracking: {end_time - start_time:.4f}s - NO SOLUTION")

        stats = solver.get_statistics()
        print(f"    Nodes expanded: {stats['solver_stats'].get('nodes_expanded', 'N/A')}")

    # Test graph coloring performance
    print("\n2. Testing Graph Coloring Performance")
    from ..coloring import GraphParser, ColoringSolver

    graphs = GraphParser.create_sample_graphs()
    for graph_name, graph in graphs.items():
        print(f"\nTesting {graph_name} graph:")
        graph_stats = graph.get_statistics()
        print(f"  Vertices: {graph_stats['num_vertices']}, Edges: {graph_stats['num_edges']}")

        # Test backtracking
        start_time = time.time()
        solver = ColoringSolver("backtracking")
        solution = solver.solve_graph(graph)
        end_time = time.time()

        if solution:
            colors_used = solver.get_colors_used()
            print(f"  Backtracking: {end_time - start_time:.4f}s - SUCCESS ({colors_used} colors)")
        else:
            print(f"  Backtracking: {end_time - start_time:.4f}s - NO SOLUTION")


def generate_test_report():
    """Generate a detailed test report."""
    print("Generating Comprehensive Test Report...")
    print("=" * 60)

    # Run all tests and collect results
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=CSPTestResult)

    # Import and run tests
    from .test_csp import *
    from .test_sudoku import *
    from .test_coloring import *

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = runner.run(suite)

    # Generate report
    print("\nTEST EXECUTION SUMMARY")
    print("=" * 30)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        print("-" * 20)
        for test, traceback in result.failures:
            print(f"FAILED: {test}")
            print(f"  {traceback.split('AssertionError:')[-1].strip()[:100]}...")

    if result.errors:
        print("\nERRORS:")
        print("-" * 20)
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(f"  {traceback.split('Error:')[-1].strip()[:100]}...")

    # Performance summary if available
    if hasattr(result, 'test_results'):
        total_time = sum(r['duration'] for r in result.test_results)
        print(f"\nTotal execution time: {total_time:.4f}s")
        print(f"Average test time: {total_time / len(result.test_results):.4f}s")


def main():
    """Main entry point for test runner."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "all"

    if command == "all":
        run_all_tests()
    elif command == "csp":
        run_csp_tests()
    elif command == "sudoku":
        run_sudoku_tests()
    elif command == "coloring":
        run_coloring_tests()
    elif command == "performance":
        run_performance_tests()
    elif command == "report":
        generate_test_report()
    else:
        print("Usage: python test_runner.py [command]")
        print("Commands:")
        print("  all        - Run all tests")
        print("  csp        - Run core CSP tests")
        print("  sudoku     - Run Sudoku tests")
        print("  coloring   - Run graph coloring tests")
        print("  performance- Run performance tests")
        print("  report     - Generate detailed test report")


if __name__ == '__main__':
    main()