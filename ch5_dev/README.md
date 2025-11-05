# Chapter 5: Constraint Satisfaction Problems (CSP)

This directory contains implementations and examples for Chapter 5 on Constraint Satisfaction Problems.

## Project Structure

```
ch5_dev/
├── csp/                     # Core CSP module
│   ├── __init__.py         # Module initialization
│   ├── csp_core.py         # Core CSP classes (CSP, Constraint)
│   ├── algorithms/         # Algorithm implementations
│   │   ├── __init__.py     # Algorithm module initialization
│   │   └── backtracking.py # Backtracking search algorithms
│   └── README.md           # CSP formal definitions
├── sudoku/                 # Sudoku-specific implementations
│   └── q1_sudoku_csp.py    # Q1: Sudoku CSP model implementation
├── coloring/               # Graph coloring implementations
│   └── q1_australia_csp.py # Q1: Australia map coloring CSP model
├── tests/                  # Test suite and examples
│   ├── __init__.py
│   ├── test_australia_map_coloring.py  # Australia map coloring CSP test
│   ├── test_sudoku_csp.py              # Sudoku CSP model test
│   ├── test_constraint_examples.py     # Constraint class demonstration
│   ├── test_sudoku_row_simple.py      # Simple Sudoku constraint demo
│   ├── test_backtracking_solver.py    # Backtracking solver tests
│   └── requirements.txt                # Test dependencies
├── output/                 # Generated files (graphs, etc.)
├── logs/                   # Change logs and documentation
│   ├── 2024-11-04_CSP_Interface_Update.md
│   └── 2024-11-04_Backtracking_Solver_Implementation.md
└── README.md               # This file
```

## CSP Core Features

### Supported Constraint Types
1. **Explicit Constraints**: `Set[Tuple[Value, ...]]`
   - Direct enumeration of allowed value combinations
   - Suitable for small constraint spaces

2. **Implicit Constraints**: `Callable[..., bool]`
   - Function-based constraint checking
   - Efficient for large constraint spaces (e.g., Sudoku's all-different constraints)

### Key Classes
- `CSP`: Main problem representation class with solving capabilities
- `Constraint`: Individual constraint representation (explicit or implicit)
- Type aliases for better code readability

### Available Algorithms
- **Basic Backtracking**: Standard depth-first search with backtracking
- **MRV Backtracking**: Backtracking with Minimum Remaining Values heuristic
- **Solution Counting**: Count all possible solutions (with limits)

## Implemented Examples

### 1. Australia Map Coloring Problem
- **Location**: `tests/test_australia_map_coloring.py`
- **Variables**: 7 Australian states/territories
- **Domains**: 3 colors (Red, Green, Blue)
- **Constraints**: 10 binary adjacency constraints
- **Features**: Constraint graph visualization

### 2. Sudoku Problem
- **Location**: `tests/test_sudoku_csp.py`
- **Variables**: 81 cells in 9x9 grid
- **Domains**: Numbers 1-9
- **Constraints**: 27 all-different constraints (9 rows + 9 columns + 9 boxes)
- **Features**: Implicit constraint implementation for efficiency

### 3. Constraint Class Demonstration
- **Location**: `tests/test_constraint_examples.py`, `tests/test_sudoku_row_simple.py`
- **Purpose**: Demonstrate how Constraint class works
- **Topics**: Explicit vs implicit constraints, efficiency comparison, constraint scopes

### 4. Backtracking Solver Tests
- **Location**: `tests/test_backtracking_solver.py`
- **Problems**: Map coloring, graph coloring, Sudoku variants, N-Queens
- **Algorithms**: Basic backtracking, MRV heuristic, solution counting

### 5. Question 1 CSP Models
- **Australia Map Coloring**: `coloring/q1_australia_csp.py`
  - 7 variables (Australian states/territories)
  - 10 adjacency constraints (including VIC-TAS correction)
  - Both explicit and implicit constraint versions
- **Sudoku**: `sudoku/q1_sudoku_csp.py`
  - 81 variables (9x9 grid)
  - 27 constraints (9 rows + 9 columns + 9 boxes)
  - Sample puzzle with 30 pre-filled cells

## Running Tests

### Prerequisites
```bash
pip install -r tests/requirements.txt
```

### Australia Map Coloring Test
```bash
cd ch5_dev
python tests/test_australia_map_coloring.py
```

### Sudoku CSP Test
```bash
cd ch5_dev
python tests/test_sudoku_csp.py
```

### Constraint Class Demonstration
```bash
cd ch5_dev
python tests/test_constraint_examples.py
python tests/test_sudoku_row_simple.py
```

### Backtracking Solver Tests
```bash
cd ch5_dev
python tests/test_backtracking_solver.py
```

### Question 1 CSP Models
```bash
cd ch5_dev
python sudoku/q1_sudoku_csp.py      # Sudoku CSP model
python coloring/q1_australia_csp.py  # Australia map coloring CSP model
```

## Key Design Decisions

### Implicit vs Explicit Constraints
The CSP framework supports both implicit and explicit constraints to handle different problem types efficiently:

- **Explicit constraints** are used when the number of allowed combinations is manageable
- **Implicit constraints** are used when the constraint space is too large for enumeration
  - Example: Sudoku's all-different constraint would require storing 9! = 362,880 combinations per constraint
  - Solution: Use a simple function `lambda *values: len(set(values)) == len(values)`

### Variable Naming Convention
- Variables use string identifiers for map coloring problems
- Variables use coordinate tuples `(row, col)` for grid-based problems like Sudoku

## Future Extensions

The modular design allows for easy extension to other CSP problems:
- N-Queens problem
- Cryptarithmetic puzzles
- Scheduling problems
- Resource allocation problems

## Change Logs

All significant changes and design decisions are documented in the `logs/` directory with timestamps.

## Performance Notes

- Implicit constraints provide significant memory savings for large constraint spaces
- The framework is designed for clarity and educational purposes rather than raw performance
- Future optimizations could include constraint propagation and backtracking algorithms