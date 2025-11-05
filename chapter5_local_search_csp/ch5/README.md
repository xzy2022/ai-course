# Chapter 5: Constraint Satisfaction Problems (CSP) Library

这是一个完整的、使用CSP模型解决约束满足问题的库。该库采用解耦的设计模式，提供了高度模块化的组件，可以轻松扩展到不同的约束满足问题域。

## 项目结构

```
ch5/
├── __init__.py              # 主包初始化
├── csp/                     # 核心CSP框架
│   ├── __init__.py
│   ├── csp.py              # 基础CSP模型（Variable, Domain, Constraint, CSP）
│   ├── backtracking.py     # 回溯搜索算法
│   ├── inference.py        # 推理策略（前向检查、弧一致性等）
│   └── local_search.py     # 局部搜索算法
├── sudoku/                  # 数独问题实现
│   ├── __init__.py
│   ├── sudoku_csp.py       # 数独CSP模型
│   ├── sudoku_parser.py    # 数独解析器
│   └── sudoku_solver.py    # 数独求解器
├── coloring/                # 图着色问题实现
│   ├── __init__.py
│   ├── graph_csp.py        # 图着色CSP模型
│   ├── graph_parser.py     # 图解析器
│   └── coloring_solver.py  # 图着色求解器
├── tests/                   # 测试套件
│   ├── __init__.py
│   ├── test_csp.py         # 核心CSP测试
│   ├── test_sudoku.py      # 数独测试
│   ├── test_coloring.py    # 图着色测试
│   └── test_runner.py      # 测试运行器
└── README.md               # 本文档
```

## 核心特性

### CSP框架组件

1. **变量 (Variable)**: 表示CSP中的变量
2. **域 (Domain)**: 表示变量的可能取值
3. **约束 (Constraint)**: 表示变量间的约束关系
4. **CSP类**: 整合所有组件的主要类

### 求解算法

1. **回溯搜索 (Backtracking Search)**
   - 多种变量选择策略（MRV、度启发式等）
   - 多种域值排序策略（LCV、随机排序等）
   - 多种推理策略（前向检查、弧一致性等）

2. **局部搜索 (Local Search)**
   - 最小冲突算法
   - 模拟退火算法

### 问题域实现

1. **数独 (Sudoku)**
   - 完整的9x9数独CSP模型
   - 多种输入格式支持
   - 多种求解算法
   - 难度等级支持

2. **图着色 (Graph Coloring)**
   - 灵活的图结构表示
   - 多种图格式支持
   - 最小着色数查找
   - 经典问题（如澳大利亚地图着色）

## 使用示例

### 数独求解

```python
from ch5.sudoku import SudokuSolver, SudokuParser

# 使用解析器获取示例谜题
puzzles = SudokuParser.create_sample_puzzles()
easy_puzzle = puzzles["easy"]

# 创建求解器并求解
solver = SudokuSolver("backtracking")  # 或 "min_conflicts", "simulated_annealing"
solution = solver.solve(easy_puzzle)

if solution:
    solver.print_solution()
    stats = solver.get_statistics()
    print(f"求解统计: {stats}")
```

### 图着色求解

```python
from ch5.coloring import ColoringSolver, GraphParser

# 创建简单的图
adjacency_list = {
    'A': ['B', 'C'],
    'B': ['A', 'C'],
    'C': ['A', 'B']
}

# 创建求解器并求解
solver = ColoringSolver("backtracking")
solution = solver.solve_from_adjacency_list(adjacency_list, num_colors=3)

if solution:
    solver.print_solution()
    print(f"使用颜色数: {solver.get_colors_used()}")
```

### 使用核心CSP框架

```python
from ch5.csp import CSP, Variable, Domain, BinaryConstraint
from ch5.csp.backtracking import BacktrackingSolver, MRVStrategy

# 创建自定义CSP
csp = CSP()

# 添加变量
var_a = Variable("A", Domain({1, 2, 3}))
var_b = Variable("B", Domain({1, 2, 3}))
csp.add_variable(var_a)
csp.add_variable(var_b)

# 添加约束
csp.add_constraint(BinaryConstraint(var_a, var_b, lambda x, y: x != y))

# 求解
solver = BacktrackingSolver(var_selection=MRVStrategy())
solution = solver.solve(csp)
```

## 测试

运行所有测试：
```bash
cd ch5/tests
python test_runner.py all
```

运行特定测试套件：
```bash
python test_runner.py csp        # 核心CSP测试
python test_runner.py sudoku     # 数独测试
python test_runner.py coloring   # 图着色测试
python test_runner.py performance # 性能测试
```

生成详细测试报告：
```bash
python test_runner.py report
```

## 扩展指南

### 添加新的CSP问题

1. **创建问题特定的变量类**（如需要）
```python
from ch5.csp import Variable

class MyVariable(Variable):
    def __init__(self, name, domain=None):
        super().__init__(name, domain)
        # 添加特定属性
```

2. **创建问题特定的约束类**
```python
from ch5.csp import Constraint

class MyConstraint(Constraint):
    def is_satisfied(self, assignment):
        # 实现约束检查逻辑
        pass
```

3. **创建问题特定的CSP类**
```python
from ch5.csp import CSP

class MyCSP(CSP):
    def __init__(self):
        super().__init__()
        # 添加变量和约束
```

4. **创建解析器和解算器**
```python
# 解析器用于从不同格式创建CSP实例
# 解算器提供高级接口和特定算法优化
```

### 添加新的求解算法

1. **变量选择策略**
```python
from ch5.csp.backtracking import VariableSelectionStrategy

class MyVariableStrategy(VariableSelectionStrategy):
    def select_variable(self, csp, assignment):
        # 实现变量选择逻辑
        pass
```

2. **推理策略**
```python
from ch5.csp.inference import InferenceStrategy

class MyInferenceStrategy(InferenceStrategy):
    def infer(self, csp, variable, value, assignment):
        # 实现推理逻辑
        pass
```

3. **局部搜索算法**
```python
from ch5.csp.local_search import LocalSearchSolver

class MyLocalSearchSolver(LocalSearchSolver):
    def solve(self, csp):
        # 实现搜索算法
        pass
```

## 设计原则

1. **解耦设计**: 各组件相互独立，易于测试和扩展
2. **策略模式**: 支持多种算法策略，便于比较和优化
3. **抽象接口**: 提供清晰的抽象接口，隐藏实现细节
4. **可扩展性**: 易于添加新的问题域和算法
5. **测试驱动**: 完整的测试套件确保代码质量

## 性能考虑

1. **算法选择**: 不同问题适合不同算法，根据问题特性选择
2. **启发式策略**: MRV、LCV等启发式策略可显著提高性能
3. **推理技术**: 前向检查和弧一致性可减少搜索空间
4. **问题建模**: 良好的约束建模对性能至关重要

## 依赖关系

- Python 3.7+
- 标准库: unittest, typing, random, time, collections, io
- 无外部依赖，纯Python实现

## 许可证

本项目仅用于教学目的。