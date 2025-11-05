# CSP Interface Update - 2024-11-04

## 修改目的
为了支持数独等复杂CSP问题，对CSP接口进行了扩展，增加对隐式约束的支持。

## 修改内容

### 1. 类型定义更新 (`csp_core.py`)
- **原来的Relation类型**: `Set[Tuple[Value, ...]]` (仅支持显式约束)
- **更新后的Relation类型**: `Union[Set[Tuple[Value, ...]], Callable[..., bool]]` (支持显式和隐式约束)

### 2. Constraint类增强
- **新增方法**: `is_satisfied(assignment: Dict[Variable, Value]) -> bool`
  - 支持检查给定赋值是否满足约束
  - 能够处理显式约束和隐式约束两种类型

- **更新方法**: `__repr__`
  - 改进了约束的字符串表示
  - 区分显示约束(显示组合数量)和隐式约束(显示函数名)

### 3. CSP类增强
- **新增方法**: `is_consistent(var, value, assignment) -> bool`
  - 检查将变量赋值是否与现有赋值一致

- **新增方法**: `is_complete(assignment) -> bool`
  - 检查赋值是否完整(所有变量都有赋值)

- **新增方法**: `is_solution(assignment) -> bool`
  - 检查赋值是否是完整的解决方案

## 技术细节

### 显式约束 vs 隐式约束
- **显式约束**: 明确列出所有允许的值组合，适用于组合数量较少的情况
  - 例子: `{"红", "绿"}, {"绿", "红"}` 表示两个变量必须不同
- **隐式约束**: 使用函数检查约束是否满足，适用于组合数量巨大的情况
  - 例子: `lambda x, y: x != y` 表示两个变量必须不同

### 数独问题的应用
对于数独问题，使用隐式约束可以避免存储9! = 362,880个组合的巨大集合：
```python
# 显式约束方式(不实用)
relation = set(permutations([1,2,3,4,5,6,7,8,9]))

# 隐式约束方式(高效)
def all_different(*values):
    return len(set(values)) == len(values)
```

## 兼容性
- 修改保持了向后兼容性，现有的显式约束代码无需更改
- 新增的功能为可选使用，不影响现有实现

## 影响的文件
- `csp/csp_core.py`: 主要修改文件
- `csp/__init__.py`: 更新模块描述