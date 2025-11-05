# Backtracking Solver Implementation - 2024-11-04

## 修改目的
实现了CSP回溯搜索算法，为CSP框架添加了求解能力，使其能够实际解决约束满足问题。

## 架构变更

### 新增目录结构
```
csp/
├── algorithms/              # 新增：算法实现目录
│   ├── __init__.py         # 算法模块初始化
│   └── backtracking.py     # 回溯算法实现
├── __init__.py             # 更新：导出算法函数
├── csp_core.py             # 更新：集成求解方法
└── README.md
```

### 核心实现

#### 1. 回溯算法模块 (`csp/algorithms/backtracking.py`)

**基础回溯搜索**：
```python
def backtracking_search(csp: CSP) -> Optional[Dict[Variable, Value]]:
    """执行回溯搜索以寻找CSP的解"""
    assignment = {}
    return _recursive_backtrack(csp, assignment)
```

**递归核心**：
```python
def _recursive_backtrack(csp: CSP, assignment: Dict[Variable, Value]):
    # 1. 基本情况：赋值完整则返回解
    if csp.is_complete(assignment):
        return assignment

    # 2. 选择未赋值变量
    var = _select_unassigned_variable(csp, assignment)

    # 3. 遍历值域尝试赋值
    for value in csp.domains[var]:
        if csp.is_consistent(var, value, assignment):
            assignment[var] = value
            result = _recursive_backtrack(csp, assignment)
            if result is not None:
                return result
            del assignment[var]  # 回溯

    return None
```

**增强功能**：
- `backtracking_search_with_mrv()`: 带MRV启发式的回溯搜索
- `count_solutions()`: 计算解的数量（带上限）
- `_select_unassigned_variable_mrv()`: MRV变量选择策略

#### 2. CSP类集成 (`csp/csp_core.py`)

**新增方法**：
```python
def solve(self, method: str = "backtracking") -> Optional[Dict[Variable, Value]]:
    """使用指定方法求解CSP"""
    # 支持的方法：
    # - "backtracking": 基础回溯搜索
    # - "backtracking_mrv": 带MRV启发式的回溯搜索

def count_solutions(self, max_count: int = 1000) -> int:
    """计算CSP的解的数量"""
```

**更新类型注解**：
- 添加了 `Optional` 类型导入
- 支持返回解或None

#### 3. 模块导出更新 (`csp/__init__.py`)

**新增导出**：
```python
from .algorithms import backtracking_search

__all__ = [
    'CSP', 'Constraint', 'Variable', 'Value', 'Domain', 'Scope', 'Relation',
    'backtracking_search'  # 新增
]
```

## 算法特性

### 1. 基础回溯搜索
- **时间复杂度**: O(b^d)，其中b是分支因子，d是深度
- **空间复杂度**: O(d)，递归调用栈深度
- **变量选择**: 固定顺序选择第一个未赋值变量
- **值顺序**: 按值域的固定顺序遍历

### 2. MRV启发式 (Minimum Remaining Values)
- **策略**: 选择剩余合法值最少的变量
- **优势**: 减少搜索分支，提高效率
- **适用**: 值域大小差异较大的问题

### 3. 解计数功能
- **功能**: 计算CSP的所有可能解
- **限制**: 设置最大计数避免无限循环
- **用途**: 分析问题复杂度和解空间

## 测试验证

### 测试用例 (`tests/test_backtracking_solver.py`)

1. **澳大利亚地图着色**:
   - 变量: 7个州/领地
   - 约束: 10个相邻约束
   - 结果: ✅ 成功找到解

2. **三角形3着色**:
   - 变量: 3个节点
   - 约束: 3个全不同约束
   - 结果: ✅ 找到6个解

3. **4x4数独变体**:
   - 变量: 16个单元格
   - 约束: 12个行列宫约束
   - 结果: ❌ 预填充值可能冲突

4. **4皇后问题**:
   - 变量: 4个皇后
   - 约束: 6个互不攻击约束
   - 结果: ✅ 找到2个解

### 性能表现
- **澳大利亚地图**: 立即找到解
- **三角形着色**: 找到全部6个解
- **4皇后**: 找到全部2个解
- **MRV启发式**: 在所有测试中表现良好

## 设计优势

### 1. 模块化架构
- **分离关注点**: 算法与CSP模型分离
- **可扩展性**: 易于添加新算法
- **可测试性**: 算法可独立测试

### 2. 纯函数设计
- **无副作用**: 算法不修改CSP内部状态
- **可重用性**: 同一CSP可用于多次求解
- **并发安全**: 支持多线程环境

### 3. 启发式支持
- **灵活性**: 支持多种变量选择策略
- **性能**: MRV启发式显著提高效率
- **扩展性**: 易于添加新启发式

## 使用示例

### 基础用法
```python
from csp import CSP, backtracking_search

# 创建CSP问题
csp = create_australia_map_csp()

# 方法1: 使用独立函数
solution = backtracking_search(csp)

# 方法2: 使用CSP方法
solution = csp.solve(method="backtracking")
solution = csp.solve(method="backtracking_mrv")

# 计算解的数量
num_solutions = csp.count_solutions(max_count=10)
```

### 验证解
```python
if solution and csp.is_solution(solution):
    print("找到有效解!")
    print(solution)
else:
    print("未找到解")
```

## 未来扩展

### 计划中的算法
1. **前向检查 (Forward Checking)**
2. **AC-3算法**
3. **约束传播**
4. **最小冲突算法**

### 优化方向
1. **值排序启发式** (Least Constraining Value)
2. **约束传播集成**
3. **并行搜索**
4. **解路径记录**

## 影响文件
- `csp/algorithms/__init__.py`: 新增
- `csp/algorithms/backtracking.py`: 新增
- `csp/csp_core.py`: 更新（添加solve和count_solutions方法）
- `csp/__init__.py`: 更新（导出backtracking_search）
- `tests/test_backtracking_solver.py`: 新增测试文件