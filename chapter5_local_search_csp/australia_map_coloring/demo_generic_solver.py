"""
泛化CSP求解器演示脚本

展示通用求解器的泛化性和灵活性，对比专用求解器和通用求解器的差异。
"""

from typing import Dict, List, Tuple
from csp_model import AustraliaMapColoringCSP, Color, Region
from generic_solver import GenericBacktrackSolver, CSPBase
from australia_adapter import create_australia_csp


class SimpleMapCSP(CSPBase[int, str]):
    """
    简化的地图涂色CSP，用于演示泛化求解器的通用性

    使用整数作为变量标识，字符串作为颜色值
    """

    def __init__(self, variables: List[int], domain: List[str], constraints: List[Tuple[int, int]]):
        """
        初始化简化地图CSP

        Args:
            variables: 变量列表（用整数标识）
            domain: 颜色值域
            constraints: 约束列表（相邻的变量对）
        """
        super().__init__()
        self.variables = variables
        self.domain = domain
        self.constraints = constraints

    def get_variables(self) -> List[int]:
        return self.variables

    def get_domain(self, var: int) -> List[str]:
        return self.domain.copy()

    def get_neighbors(self, var: int) -> List[int]:
        neighbors = []
        for constraint in self.constraints:
            if var == constraint[0]:
                neighbors.append(constraint[1])
            elif var == constraint[1]:
                neighbors.append(constraint[0])
        return neighbors

    def is_consistent(self, var: int, value: str, assignment: Dict[int, str]) -> bool:
        for neighbor in self.get_neighbors(var):
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True


def demo_australia_solver():
    """演示澳大利亚涂色问题使用泛化求解器"""
    print("=" * 80)
    print("澳大利亚涂色问题 - 泛化求解器演示")
    print("=" * 80)

    # 创建CSP适配器和泛化求解器
    csp = create_australia_csp()
    solver = GenericBacktrackSolver(csp)

    # 求解
    success, solution = solver.solve(verbose=True)

    if success:
        print("\n找到解决方案:")
        csp.print_assignment(solution, "澳大利亚地图涂色方案")

        # 验证解决方案
        if csp.is_solution(solution):
            print("[OK] 解决方案验证通过")
        else:
            print("[ERROR] 解决方案验证失败")

        # 显示泛化求解器的统计信息
        solver.print_statistics()

        # 简单的解决方案分析
        print(f"\n解决方案分析:")
        color_usage = {}
        for var, value in solution.items():
            color_usage[value.value] = color_usage.get(value.value, 0) + 1

        print(f"颜色使用统计:")
        for color, count in sorted(color_usage.items()):
            print(f"  {color}: {count} 个地区")


def demo_generic_solver():
    """演示通用求解器的泛化性"""
    print("\n" + "=" * 80)
    print("通用求解器演示 - 简化地图涂色问题")
    print("=" * 80)

    # 创建一个简化的4区域地图涂色问题
    variables = [1, 2, 3, 4]  # 4个区域
    colors = ["红", "绿", "蓝"]  # 3种颜色
    constraints = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]  # 相邻关系

    # 创建CSP实例
    simple_csp = SimpleMapCSP(variables, colors, constraints)

    # 使用通用求解器
    generic_solver = GenericBacktrackSolver(simple_csp)

    print("简化地图涂色问题:")
    print(f"  区域数量: {len(variables)}")
    print(f"  可用颜色: {len(colors)} 种")
    print(f"  约束数量: {len(constraints)}")
    print(f"  相邻关系: {constraints}")

    # 求解
    success, solution = generic_solver.solve(verbose=True)

    if success:
        print("\n简化地图解决方案:")
        for region, color in sorted(solution.items()):
            print(f"  区域 {region}: {color}")

        generic_solver.print_statistics()
    else:
        print("未找到解决方案")


def demonstrate_australia_multiple_times():
    """演示多次运行澳大利亚涂色问题的一致性"""
    print("\n" + "=" * 80)
    print("澳大利亚涂色问题 - 多次运行测试")
    print("=" * 80)

    results = []
    for i in range(3):
        print(f"\n第 {i+1} 次运行:")
        print("-" * 40)

        csp = create_australia_csp()
        solver = GenericBacktrackSolver(csp)
        success, solution = solver.solve(verbose=False)

        if success:
            print(f"[OK] 成功找到解决方案，探索节点数: {solver.nodes_explored}")
            results.append((success, solver.nodes_explored, solution))
        else:
            print("[ERROR] 未找到解决方案")
            results.append((success, solver.nodes_explored, None))

    # 分析结果一致性
    print(f"\n结果分析:")
    if all(result[0] for result in results):
        print("[OK] 所有运行都成功找到解决方案")

        # 检查解决方案的一致性
        solutions = [result[2] for result in results]
        if all(solution == solutions[0] for solution in solutions):
            print("[OK] 所有运行找到相同的解决方案")
        else:
            print("[INFO] 不同运行找到不同的解决方案（都是有效的）")

        # 性能统计
        node_counts = [result[1] for result in results]
        print(f"性能统计 - 探索节点数: 最小={min(node_counts)}, 最大={max(node_counts)}, 平均={sum(node_counts)/len(node_counts):.1f}")
    else:
        print("[ERROR] 部分运行失败")


def demo_solver_flexibility():
    """演示求解器的灵活性"""
    print("\n" + "=" * 80)
    print("求解器灵活性演示")
    print("=" * 80)

    # 创建不同规模的问题
    problems = [
        {
            "name": "3区域地图",
            "variables": [1, 2, 3],
            "colors": ["红", "绿"],
            "constraints": [(1, 2), (2, 3)]
        },
        {
            "name": "5区域地图",
            "variables": [1, 2, 3, 4, 5],
            "colors": ["红", "绿", "蓝"],
            "constraints": [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
        }
    ]

    for problem in problems:
        print(f"\n求解 {problem['name']}:")
        print("-" * 40)

        # 创建CSP
        csp = SimpleMapCSP(
            problem['variables'],
            problem['colors'],
            problem['constraints']
        )

        # 使用通用求解器
        solver = GenericBacktrackSolver(csp)
        success, solution = solver.solve(verbose=False)

        if success:
            print(f"[OK] 成功找到解决方案")
            solver.print_statistics(detailed=False)
        else:
            print("[ERROR] 未找到解决方案")


def main():
    """主演示函数"""
    print("泛化CSP求解器完整演示")
    print("展示通用求解器的泛化性、灵活性和可扩展性")
    print("=" * 80)

    # 1. 澳大利亚涂色问题演示
    demo_australia_solver()

    # 2. 简化地图涂色问题演示
    demo_generic_solver()

    # 3. 多次运行一致性测试
    demonstrate_australia_multiple_times()

    # 4. 灵活性演示
    demo_solver_flexibility()

    # 总结
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)

    print("泛化求解器的优势:")
    print("1. 通用性: 可适用于任何CSP问题")
    print("2. 可扩展性: 易于添加新的启发式和算法")
    print("3. 模块化: 清晰的接口和职责分离")
    print("4. 可重用性: 一次实现，多处使用")
    print("5. 维护性: 集中的算法逻辑，易于维护和优化")

    print("\n设计模式:")
    print("- 适配器模式: 将特定问题适配到通用接口")
    print("- 模板方法模式: 定义算法骨架，子类实现细节")
    print("- 策略模式: 可插拔的启发式算法")
    print("- 泛型编程: 类型安全的通用实现")

    print("\n适用场景:")
    print("- 教学和研究: 展示CSP算法的通用原理")
    print("- 快速原型: 快速实现新的CSP问题求解")
    print("- 生产环境: 构建可靠的约束求解系统")
    print("- 算法研究: 测试和比较不同的启发式策略")

    print("\n纯泛化架构的价值:")
    print("- 代码简洁: 没有冗余的专用代码")
    print("- 类型安全: 泛型提供编译时检查")
    print("- 易于测试: 统一的接口便于单元测试")
    print("- 性能一致: 所有问题使用相同的优化算法")


if __name__ == "__main__":
    main()