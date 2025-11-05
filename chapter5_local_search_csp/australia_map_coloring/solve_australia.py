"""
澳大利亚地图涂色问题求解演示脚本

展示使用泛化回溯搜索求解器解决澳大利亚涂色问题的完整过程。
演示泛化求解器的灵活性和可扩展性。
"""

import time
from csp_model import AustraliaMapColoringCSP, Color, Region
from generic_solver import GenericBacktrackSolver
from australia_adapter import create_australia_csp


def demonstrate_basic_solution():
    """演示基本解决方案"""
    print("=" * 80)
    print("澳大利亚地图涂色问题 - 泛化求解器演示")
    print("=" * 80)

    # 1. 创建CSP适配器
    print("\n1. 创建CSP模型和适配器")
    print("-" * 40)
    csp = create_australia_csp()
    print("澳大利亚涂色问题CSP适配器创建完成")

    # 2. 验证模型
    print("\n2. 验证CSP模型")
    print("-" * 40)
    if csp.csp_model.validate_csp_model():
        print("[OK] 模型验证通过，可以开始求解")
    else:
        print("[ERROR] 模型验证失败，请检查模型定义")
        return

    # 3. 创建泛化求解器并求解
    print("\n3. 使用泛化回溯搜索求解器求解")
    print("-" * 40)
    solver = GenericBacktrackSolver(csp)

    start_time = time.time()
    success, solution = solver.solve(verbose=True)
    end_time = time.time()

    # 4. 显示结果
    print(f"\n4. 求解结果")
    print("-" * 40)
    print(f"求解时间: {end_time - start_time:.6f} 秒")

    if success:
        print("[OK] 成功找到解决方案")
        csp.print_assignment(solution, "最终解决方案")

        # 验证解决方案
        if csp.is_solution(solution):
            print("[OK] 解决方案验证通过：满足所有约束")
        else:
            print("[ERROR] 解决方案验证失败：不满足约束")

        # 分析解决方案
        analyze_solution(solution, csp)
    else:
        print("[ERROR] 未找到解决方案")

    # 5. 显示统计信息
    solver.print_statistics()

    return success, solution


def analyze_solution(solution: dict, csp):
    """分析解决方案的特点"""
    print("\n解决方案分析:")
    print("-" * 40)

    # 颜色使用统计
    color_usage = {}
    for region, color in solution.items():
        color_usage[color.value] = color_usage.get(color.value, 0) + 1

    print("颜色使用统计:")
    for color, count in color_usage.items():
        print(f"  {color}: {count} 个地区")

    # 地理分析
    print("\n地理分布:")
    for region, color in solution.items():
        neighbors_count = len(csp.csp_model.neighbors[region])
        print(f"  {region.value}: {color.value} (相邻地区: {neighbors_count}个)")


def demonstrate_heuristic_comparison():
    """演示不同启发式策略的效果对比"""
    print("\n" + "=" * 80)
    print("启发式策略效果对比")
    print("=" * 80)

    print("当前使用的启发式策略:")
    print("1. 变量选择: MRV + 度启发式")
    print("   - 优先选择值域最小的变量 (失败优先)")
    print("   - 值域相同时，选择约束最多的变量 (未来影响)")
    print("2. 值排序: LCV (最少约束值)")
    print("   - 优先选择导致最少冲突的值")
    print("3. 约束传播: AC-3 算法")
    print("   - 在赋值后立即传播约束，缩小值域")
    print("   - 提前检测失败，减少搜索空间")


def demonstrate_problem_complexity():
    """演示问题复杂度"""
    print("\n" + "=" * 80)
    print("问题复杂度分析")
    print("=" * 80)

    print("搜索空间分析:")
    print(f"- 变量数量: 7 (澳大利亚的州和地区)")
    print(f"- 每个变量的值域大小: 3 (红、绿、蓝)")
    print(f"- 理论搜索空间: 3^7 = 2,187 种可能赋值")

    print("\n约束数量:")
    csp = create_australia_csp()
    print(f"- 二元约束数量: {len(csp.csp_model.constraints)}")
    print("- 约束类型: 相邻区域颜色不同")

    print("\n约束的作用:")
    print("- 大幅减少了有效的搜索空间")
    print("- AC-3 算法进一步缩小值域")
    print("- 启发式策略引导搜索走向解")


def demonstrate_solver_flexibility():
    """演示求解器的灵活性"""
    print("\n" + "=" * 80)
    print("泛化求解器的灵活性")
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

    print("\n与特定问题求解器相比:")
    print("+ 通用性: 不局限于特定问题")
    print("+ 可维护性: 算法逻辑集中管理")
    print("+ 可扩展性: 容易添加新功能")
    print("+ 类型安全: 泛型提供编译时检查")
    print("- 便利性: 需要适配器层")


def main():
    """主函数"""
    print("澳大利亚地图涂色问题 - 泛化求解器完整演示")
    print("基于通用回溯搜索和约束满足问题理论")
    print("=" * 80)

    # 1. 基本求解演示
    success, solution = demonstrate_basic_solution()

    # 2. 启发式策略对比
    demonstrate_heuristic_comparison()

    # 3. 问题复杂度分析
    demonstrate_problem_complexity()

    # 4. 求解器灵活性展示
    demonstrate_solver_flexibility()

    # 5. 总结
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)

    if success:
        print("[OK] 成功解决了澳大利亚地图涂色问题")
        print("[OK] 验证了泛化回溯搜索算法的有效性")
        print("[OK] 展示了适配器模式的实际应用")
        print("[OK] 证明了泛化设计的优势")
    else:
        print("[ERROR] 求解失败，需要进一步调试算法")

    print("\n泛化求解器的价值:")
    print("- 一次实现，多处使用")
    print("- 类型安全，性能优异")
    print("- 易于测试，便于维护")
    print("- 架构清晰，设计优雅")

    print("\n适用场景:")
    print("- 教学和研究: 展示CSP算法的通用原理")
    print("- 快速原型: 快速实现新的CSP问题求解")
    print("- 生产环境: 构建可靠的约束求解系统")
    print("- 算法研究: 测试和比较不同的启发式策略")


if __name__ == "__main__":
    main()