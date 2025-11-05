"""
CSP 基本概念的形式化与接口设计

一个约束满足问题（CSP）可以形式化地定义为一个三元组：
CSP = (X, D, C)

其中：
- X 是一个变量的有限集合
- D 是一个值域集合
- C 是一个约束的有限集合
"""

from typing import List, Tuple, Set, Any, Dict, Callable, Union, Optional

# --- 类型别名，用于提高代码可读性 ---
Variable = str         # 变量使用字符串表示，如 "WA", "NT"
Value = Any            # 变量的值可以是任何类型
Domain = Set[Value]    # 值域是值的集合，目前假设为离散有限域
Scope = Tuple[Variable, ...] # 约束的作用域是变量名的元组
# 约束关系可以是显式的值组合集合，也可以是隐式的约束函数
Relation = Union[Set[Tuple[Value, ...]], Callable[..., bool]]


class Constraint:
    """
    表示一个约束 c = <S, R>

    属性:
        scope (Scope): 约束涉及的变量元组 S。
        relation (Relation): 允许的赋值组合集合 R，或者约束检查函数。

    注意:
        relation 可以是两种类型:
        1. 显式约束: Set[Tuple[Value, ...]] - 包含所有允许的值组合的集合
        2. 隐式约束: Callable[..., bool] - 接受变量值作为参数，返回布尔值表示是否满足约束
    """
    def __init__(self, scope: Scope, relation: Relation):
        if not scope:
            raise ValueError("约束的作用域不能为空")
        self.scope = scope
        self.relation = relation

    def is_satisfied(self, assignment: Dict[Variable, Value]) -> bool:
        """
        检查给定的赋值是否满足此约束

        参数:
            assignment (Dict[Variable, Value]): 变量到值的映射

        返回:
            bool: 如果赋值满足约束则返回True，否则返回False
        """
        # 检查作用域中的所有变量是否都有赋值
        for var in self.scope:
            if var not in assignment:
                return True  # 如果变量未赋值，则暂不违反约束

        # 提取作用域中变量的值
        values = tuple(assignment[var] for var in self.scope)

        # 根据约束类型进行检查
        if isinstance(self.relation, set):
            # 显式约束：检查值组合是否在允许的集合中
            return values in self.relation
        elif callable(self.relation):
            # 隐式约束：调用约束函数
            return self.relation(*values)
        else:
            raise ValueError(f"不支持的约束类型: {type(self.relation)}")

    def __repr__(self) -> str:
        """返回约束的字符串表示"""
        if isinstance(self.relation, set):
            relation_str = f"Set({len(self.relation)} combinations)"
        elif callable(self.relation):
            relation_str = f"Function({self.relation.__name__})"
        else:
            relation_str = str(self.relation)
        return f"Constraint(scope={self.scope}, relation={relation_str})"


class CSP:
    """
    表示一个约束满足问题 CSP = {X, D, C}

    属性:
        variables (Set[Variable]): 问题的所有变量集合 X。
        domains (Dict[Variable, Domain]): 变量到其值域的映射 D。
        constraints (List[Constraint]): 问题的所有约束列表 C。
    """
    def __init__(self):
        self.variables: Set[Variable] = set()
        self.domains: Dict[Variable, Domain] = {}
        self.constraints: List[Constraint] = []

    def add_variable(self, var: Variable, domain: Domain) -> None:
        """
        添加一个变量及其值域到 CSP 问题中。

        参数:
            var (Variable): 要添加的变量名。
            domain (Domain): 该变量的值域。
        """
        self.variables.add(var)
        self.domains[var] = domain

    def add_constraint(self, constraint: Constraint) -> None:
        """
        添加一个约束到 CSP 问题中。

        参数:
            constraint (Constraint): 要添加的约束对象。
        """
        # 简单校验：约束中的变量必须已在 CSP 中定义
        for var in constraint.scope:
            if var not in self.variables:
                raise ValueError(f"约束中的变量 '{var}' 尚未添加到 CSP 中")
        self.constraints.append(constraint)

    def is_consistent(self, var: Variable, value: Value, assignment: Dict[Variable, Value]) -> bool:
        """
        检查将变量var赋值为value是否与现有赋值一致

        参数:
            var (Variable): 要赋值的变量
            value (Value): 要赋的值
            assignment (Dict[Variable, Value]): 当前的赋值

        返回:
            bool: 如果一致则返回True，否则返回False
        """
        # 创建临时赋值（包含新的变量赋值）
        temp_assignment = assignment.copy()
        temp_assignment[var] = value

        # 检查所有相关约束
        for constraint in self.constraints:
            if var in constraint.scope:
                if not constraint.is_satisfied(temp_assignment):
                    return False
        return True

    def is_complete(self, assignment: Dict[Variable, Value]) -> bool:
        """
        检查赋值是否完整（所有变量都有赋值）

        参数:
            assignment (Dict[Variable, Value]): 要检查的赋值

        返回:
            bool: 如果赋值完整则返回True，否则返回False
        """
        return len(assignment) == len(self.variables)

    def is_solution(self, assignment: Dict[Variable, Value]) -> bool:
        """
        检查赋值是否是完整的解决方案

        参数:
            assignment (Dict[Variable, Value]): 要检查的赋值

        返回:
            bool: 如果是完整解决方案则返回True，否则返回False
        """
        if not self.is_complete(assignment):
            return False

        # 检查所有约束是否都满足
        for constraint in self.constraints:
            if not constraint.is_satisfied(assignment):
                return False
        return True

    def solve(self, method: str = "backtracking") -> Optional[Dict[Variable, Value]]:
        """
        Solve the CSP using the specified method.

        Args:
            method (str): The solving method to use. Currently supports:
                         - "backtracking": Basic backtracking search
                         - "backtracking_mrv": Backtracking with MRV heuristic

        Returns:
            Optional[Dict[Variable, Value]]: Solution if found, None otherwise
        """
        # Import here to avoid circular imports
        from .algorithms.backtracking import backtracking_search
        from .algorithms.heuristic_backtracking import heuristic_backtracking_search

        if method == "backtracking":
            return backtracking_search(self)
        elif method == "backtracking_mrv":
            return heuristic_backtracking_search(self)
        else:
            raise ValueError(f"Unknown solving method: {method}")

    def count_solutions(self, max_count: int = 1000) -> int:
        """
        Count the number of solutions for this CSP.

        Args:
            max_count (int): Maximum number of solutions to count

        Returns:
            int: Number of solutions found (capped at max_count)
        """
        from .algorithms.backtracking import count_solutions
        return count_solutions(self, max_count)

    def __repr__(self) -> str:
        """返回 CSP 问题的字符串表示"""
        return (
            f"CSP(\n"
            f"  Variables: {self.variables}\n"
            f"  Domains: {self.domains}\n"
            f"  Constraints: {self.constraints}\n"
            f")"
        )
