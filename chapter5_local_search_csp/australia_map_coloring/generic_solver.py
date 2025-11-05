"""
通用的回溯搜索CSP求解器

提供泛化的回溯搜索算法实现，适用于任何约束满足问题。
包含通用的启发式算法、约束传播机制和统计功能。
"""

import copy
import time
from typing import Dict, List, Tuple, Optional, Set, Any, TypeVar, Generic
from abc import ABC, abstractmethod

# 泛型类型变量
V = TypeVar('V')  # 变量类型
D = TypeVar('D')  # 值域类型


class CSPBase(ABC, Generic[V, D]):
    """
    抽象CSP基类，定义CSP问题的通用接口

    任何CSP问题都应该继承这个基类并实现相应方法
    """

    def __init__(self):
        self.variables = []  # 变量列表
        self.domains = {}    # 值域字典
        self.neighbors = {}  # 邻接关系

    @abstractmethod
    def get_variables(self) -> List[V]:
        """获取所有变量"""
        pass

    @abstractmethod
    def get_domain(self, var: V) -> List[D]:
        """获取变量的值域"""
        pass

    @abstractmethod
    def get_neighbors(self, var: V) -> List[V]:
        """获取变量的邻居"""
        pass

    @abstractmethod
    def is_consistent(self, var: V, value: D, assignment: Dict[V, D]) -> bool:
        """检查赋值是否满足约束"""
        pass

    def is_complete(self, assignment: Dict[V, D]) -> bool:
        """检查赋值是否完整（所有变量都已赋值）"""
        return len(assignment) == len(self.get_variables())

    def is_solution(self, assignment: Dict[V, D]) -> bool:
        """检查赋值是否是完整解决方案"""
        if not self.is_complete(assignment):
            return False

        for var, value in assignment.items():
            if not self.is_consistent(var, value, assignment):
                return False

        return True


class GenericBacktrackSolver(Generic[V, D]):
    """
    通用的回溯搜索求解器

    实现最终优化版回溯搜索算法：
    1. MRV + 度启发式的变量选择
    2. LCV值排序
    3. AC-3约束传播
    4. 完整的状态回滚
    """

    def __init__(self, csp: CSPBase[V, D]):
        """
        初始化求解器

        Args:
            csp: CSP问题实例
        """
        self.csp = csp
        self.nodes_explored = 0
        self.solution = None
        self.start_time = None
        self.end_time = None

        # 统计信息
        self.backtrack_count = 0
        self.inference_failures = 0
        self.value_tries = 0

    def solve(self, verbose: bool = True) -> Tuple[bool, Optional[Dict[V, D]]]:
        """
        求解CSP问题

        Args:
            verbose: 是否打印详细信息

        Returns:
            Tuple[bool, Optional[Dict[V, D]]]: (是否成功, 解决方案)
        """
        if verbose:
            print("开始回溯搜索求解...")
            self._print_problem_info()

        self.nodes_explored = 0
        self.backtrack_count = 0
        self.inference_failures = 0
        self.value_tries = 0
        self.solution = None
        self.start_time = time.time()

        assignment = {}
        result, final_assignment = self._backtrack(assignment, verbose)

        self.end_time = time.time()

        if result:
            self.solution = final_assignment
            if verbose:
                print(f"[OK] 求解成功！")
        else:
            if verbose:
                print(f"[INFO] 求解失败")

        return result, final_assignment

    def _backtrack(self, assignment: Dict[V, D], verbose: bool = False) -> Tuple[bool, Dict[V, D]]:
        """回溯搜索主函数（优化版）"""
        self.nodes_explored += 1

        if verbose and self.nodes_explored % 100 == 0:
            print(f"[INFO] 已探索 {self.nodes_explored} 个节点...")

        # 检查是否完成
        if self.csp.is_complete(assignment):
            return True, assignment

        # 选择未赋值的变量
        var = self._select_unassigned_variable(assignment)
        ordered_values = self._order_domain_values(var, assignment)

        # 尝试每个值
        for value in ordered_values:
            self.value_tries += 1

            if self.csp.is_consistent(var, value, assignment):
                # 记录赋值前的状态
                original_assignment = copy.deepcopy(assignment)
                original_domains = copy.deepcopy(self.csp.domains)

                # 执行赋值
                assignment[var] = value

                # 约束传播
                inferences = self._ac3_inference(var, value)

                if inferences is not None:
                    # 递归搜索
                    result, new_assignment = self._backtrack(assignment, verbose)
                    if result:
                        return True, new_assignment

                # 回滚状态
                assignment.clear()
                assignment.update(original_assignment)
                self.csp.domains.clear()
                self.csp.domains.update(original_domains)
                self.backtrack_count += 1

        return False, assignment

    def _select_unassigned_variable(self, assignment: Dict[V, D]) -> V:
        """选择未赋值的变量（MRV + 度启发式）"""
        variables = self.csp.get_variables()
        unassigned_vars = [v for v in variables if v not in assignment]

        # MRV启发式
        min_domain_size = float('inf')
        mrv_candidates = []

        for var in unassigned_vars:
            domain_size = len(self.csp.get_domain(var))
            if domain_size < min_domain_size:
                min_domain_size = domain_size
                mrv_candidates = [var]
            elif domain_size == min_domain_size:
                mrv_candidates.append(var)

        if len(mrv_candidates) == 1:
            return mrv_candidates[0]

        # 度启发式（打破平局）
        max_degree = -1
        final_candidate = mrv_candidates[0]

        for var in mrv_candidates:
            degree = self._count_unassigned_neighbors(var, assignment)
            if degree > max_degree:
                max_degree = degree
                final_candidate = var

        return final_candidate

    def _order_domain_values(self, var: V, assignment: Dict[V, D]) -> List[D]:
        """对变量的值域进行排序（LCV启发式）"""
        domain = self.csp.get_domain(var)
        value_conflicts = {}

        for value in domain:
            total_conflicts = 0
            unassigned_neighbors = self._get_unassigned_neighbors(var, assignment)

            for neighbor in unassigned_neighbors:
                for neighbor_value in self.csp.get_domain(neighbor):
                    if not self._constraint_satisfied(var, value, neighbor, neighbor_value):
                        total_conflicts += 1

            value_conflicts[value] = total_conflicts

        return sorted(domain, key=lambda v: value_conflicts[v])

    def _ac3_inference(self, var: V, value: D) -> Optional[List[Tuple[V, D]]]:
        """AC-3约束传播算法"""
        inferences = []
        queue = []

        for neighbor in self.csp.get_neighbors(var):
            queue.append((neighbor, var))

        while queue:
            (xi, xj) = queue.pop(0)
            revised = self._revise_domain(xi, xj, inferences)

            if revised:
                if len(self.csp.get_domain(xi)) == 0:
                    self.inference_failures += 1
                    return None

                for xk in self.csp.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))

        return inferences

    def _revise_domain(self, xi: V, xj: V, inferences: List[Tuple[V, D]]) -> bool:
        """修订Xi的值域，移除与Xj不一致的值"""
        revised = False
        original_domain = self.csp.get_domain(xi).copy()
        values_to_remove = []

        for xi_value in self.csp.get_domain(xi):
            consistent = False
            for xj_value in self.csp.get_domain(xj):
                if self._constraint_satisfied(xi, xi_value, xj, xj_value):
                    consistent = True
                    break

            if not consistent:
                values_to_remove.append(xi_value)

        for value in values_to_remove:
            self.csp.domains[xi].remove(value)
            if value in original_domain:
                inferences.append((xi, value))
            revised = True

        return revised

    def _count_unassigned_neighbors(self, var: V, assignment: Dict[V, D]) -> int:
        """计算变量的未赋值邻居数量"""
        count = 0
        for neighbor in self.csp.get_neighbors(var):
            if neighbor not in assignment:
                count += 1
        return count

    def _get_unassigned_neighbors(self, var: V, assignment: Dict[V, D]) -> List[V]:
        """获取变量的未赋值邻居列表"""
        return [n for n in self.csp.get_neighbors(var) if n not in assignment]

    def _constraint_satisfied(self, var1: V, value1: D, var2: V, value2: D) -> bool:
        """检查两个变量的赋值是否满足约束"""
        # 默认实现：如果两个变量相邻，它们的值必须不同
        # 子类可以重写此方法来实现更复杂的约束
        return var2 not in self.csp.get_neighbors(var1) or value1 != value2

    def _print_problem_info(self):
        """打印问题信息（泛化）"""
        variables = self.csp.get_variables()
        print(f"[INFO] 问题规模:")
        print(f"  变量数量: {len(variables)}")

        # 计算平均值域大小
        domain_sizes = [len(self.csp.get_domain(var)) for var in variables]
        avg_domain_size = sum(domain_sizes) / len(domain_sizes)
        print(f"  平均值域大小: {avg_domain_size:.1f}")

        # 计算约束数量
        total_constraints = sum(len(self.csp.get_neighbors(var)) for var in variables) // 2
        print(f"  约束数量: {total_constraints}")

        # 理论搜索空间
        search_space = 1
        for var in variables:
            search_space *= len(self.csp.get_domain(var))
        print(f"  理论搜索空间: {search_space}")

    def print_statistics(self, detailed: bool = True):
        """打印求解统计信息（泛化）"""
        print("\n" + "=" * 50)
        print("求解统计信息")
        print("=" * 50)

        # 基本统计
        print(f"探索的节点数: {self.nodes_explored}")
        print(f"回溯次数: {self.backtrack_count}")
        print(f"值尝试次数: {self.value_tries}")
        print(f"推理失败次数: {self.inference_failures}")

        # 时间统计
        if self.start_time and self.end_time:
            elapsed_time = self.end_time - self.start_time
            print(f"求解时间: {elapsed_time:.6f} 秒")
            if self.nodes_explored > 0:
                print(f"平均每节点耗时: {elapsed_time/self.nodes_explored*1000:.3f} 毫秒")

        # 效率统计
        if detailed and self.value_tries > 0:
            success_rate = 1 / self.value_tries if self.solution else 0
            print(f"值成功率: {success_rate:.2%}")

            if self.nodes_explored > 0:
                backtrack_rate = self.backtrack_count / self.nodes_explored
                print(f"回溯率: {backtrack_rate:.2%}")

        # 解决方案信息
        if self.solution:
            print(f"\n[OK] 找到解决方案")
            self._print_solution_summary()
        else:
            print(f"\n[INFO] 未找到解决方案")

        print("=" * 50)

    def _print_solution_summary(self):
        """打印解决方案摘要（泛化）"""
        print("解决方案摘要:")

        # 值使用统计
        value_usage = {}
        for var, value in self.solution.items():
            value_str = str(value)
            value_usage[value_str] = value_usage.get(value_str, 0) + 1

        print("值使用统计:")
        for value, count in sorted(value_usage.items()):
            print(f"  {value}: {count} 个变量")

        # 约束满足检查
        if self.csp.is_solution(self.solution):
            print("约束满足: 全部满足")
        else:
            print("约束满足: 存在冲突")

    def get_solution(self) -> Optional[Dict[V, D]]:
        """获取找到的解决方案"""
        return self.solution

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            'nodes_explored': self.nodes_explored,
            'backtrack_count': self.backtrack_count,
            'value_tries': self.value_tries,
            'inference_failures': self.inference_failures,
            'solution_time': (self.end_time - self.start_time) if self.start_time and self.end_time else None,
            'found_solution': self.solution is not None
        }