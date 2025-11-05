"""
澳大利亚地图涂色问题CSP模型的测试脚本

引用 csp_model.py 中的模型进行各种测试和验证。
这个脚本可以独立运行，也可以作为其他算法的参考。
"""

import random
from csp_model import AustraliaMapColoringCSP, Color, Region


def test_csp_model():
    """测试CSP模型的基本功能"""
    print("澳大利亚地图涂色问题的CSP模型测试")
    print("=" * 60)

    # 创建CSP模型
    csp = AustraliaMapColoringCSP()

    # 打印CSP模型
    csp.print_csp_model()

    # 验证CSP模型
    csp.validate_csp_model()

    return csp


def test_basic_functionality(csp: AustraliaMapColoringCSP):
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("基本功能测试")
    print("=" * 60)

    # 测试1：空赋值
    empty_assignment = {}
    csp.print_assignment(empty_assignment, "空赋值测试")

    # 测试2：部分赋值（有效）
    partial_assignment = {
        Region.WA: Color.RED,
        Region.NT: Color.GREEN,
        Region.SA: Color.BLUE
    }
    csp.print_assignment(partial_assignment, "部分赋值测试（有效）")

    # 测试3：有冲突的赋值
    conflicted_assignment = {
        Region.WA: Color.RED,
        Region.NT: Color.RED,  # 与WA冲突
        Region.SA: Color.GREEN,
        Region.QLD: Color.BLUE
    }
    csp.print_assignment(conflicted_assignment, "有冲突的赋值测试")

    # 测试4：合法值获取
    print(f"\nWA的合法值（给定当前部分赋值）: {[c.value for c in csp.get_legal_values(Region.WA, partial_assignment)]}")
    print(f"NT的合法值（给定当前部分赋值）: {[c.value for c in csp.get_legal_values(Region.NT, partial_assignment)]}")


def test_solution_methods(csp: AustraliaMapColoringCSP):
    """测试解决方案相关方法"""
    print("\n" + "=" * 60)
    print("解决方案方法测试")
    print("=" * 60)

    # 测试完整解决方案
    valid_solution = {
        Region.WA: Color.RED,
        Region.NT: Color.GREEN,
        Region.SA: Color.BLUE,
        Region.QLD: Color.RED,
        Region.NSW: Color.GREEN,
        Region.VIC: Color.RED,
        Region.TAS: Color.BLUE
    }

    csp.print_assignment(valid_solution, "有效解决方案测试")
    print(f"是否为完整解决方案: {csp.is_solution(valid_solution)}")

    # 测试未完整赋值
    incomplete_solution = {
        Region.WA: Color.RED,
        Region.NT: Color.GREEN,
        Region.SA: Color.BLUE
    }
    csp.print_assignment(incomplete_solution, "不完整解决方案测试")
    print(f"是否为完整解决方案: {csp.is_solution(incomplete_solution)}")


def test_random_assignments(csp: AustraliaMapColoringCSP):
    """测试随机赋值功能"""
    print("\n" + "=" * 60)
    print("随机赋值测试")
    print("=" * 60)

    # 生成多个随机赋值
    for i in range(3):
        print(f"\n第 {i+1} 个随机赋值:")
        random_assignment = {}
        for region in csp.variables:
            random_assignment[region] = random.choice(csp.colors)

        csp.print_assignment(random_assignment, f"随机赋值 {i+1}")
        print(f"是否为完整解决方案: {csp.is_solution(random_assignment)}")
        print(f"冲突总数: {csp.count_conflicts(random_assignment)}")


def test_constraint_checking(csp: AustraliaMapColoringCSP):
    """测试约束检查功能"""
    print("\n" + "=" * 60)
    print("约束检查测试")
    print("=" * 60)

    # 测试各种约束情况
    test_cases = [
        {
            "name": "所有相邻区域颜色不同",
            "assignment": {
                Region.WA: Color.RED,
                Region.NT: Color.GREEN,
                Region.SA: Color.BLUE,
                Region.QLD: Color.RED,
                Region.NSW: Color.GREEN,
                Region.VIC: Color.RED,
                Region.TAS: Color.BLUE
            }
        },
        {
            "name": "WA和NT颜色相同（违反约束）",
            "assignment": {
                Region.WA: Color.RED,
                Region.NT: Color.RED,  # 违反约束
                Region.SA: Color.BLUE,
                Region.QLD: Color.GREEN,
                Region.NSW: Color.BLUE,
                Region.VIC: Color.GREEN,
                Region.TAS: Color.RED
            }
        },
        {
            "name": "SA与多个邻居冲突",
            "assignment": {
                Region.WA: Color.RED,
                Region.NT: Color.BLUE,
                Region.SA: Color.RED,  # 与WA冲突
                Region.QLD: Color.RED,  # 与SA冲突
                Region.NSW: Color.RED,  # 与SA冲突
                Region.VIC: Color.BLUE,
                Region.TAS: Color.GREEN
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        csp.print_assignment(test_case['assignment'], f"约束检查测试 {i}")

        conflicted_vars = csp.get_conflicted_variables(test_case['assignment'])
        print(f"冲突变量: {[v.name for v in conflicted_vars]}")
        print(f"冲突总数: {csp.count_conflicts(test_case['assignment'])}")


def test_domain_methods(csp: AustraliaMapColoringCSP):
    """测试值域相关方法"""
    print("\n" + "=" * 60)
    print("值域方法测试")
    print("=" * 60)

    # 测试未分配变量获取
    partial_assignment = {
        Region.WA: Color.RED,
        Region.NT: Color.GREEN,
        Region.SA: Color.BLUE
    }

    unassigned = csp.get_unassigned_variables(partial_assignment)
    print(f"未分配的变量: {[v.name for v in unassigned]}")

    # 测试每个未分配变量的合法值
    for region in unassigned:
        legal_values = csp.get_legal_values(region, partial_assignment)
        print(f"{region.name} 的合法值: {[v.value for v in legal_values]}")


def main():
    """主测试函数"""
    print("开始澳大利亚地图涂色问题CSP模型的全面测试")
    print("=" * 80)

    # 创建并测试CSP模型
    csp = test_csp_model()

    # 运行各种测试
    test_basic_functionality(csp)
    test_solution_methods(csp)
    test_random_assignments(csp)
    test_constraint_checking(csp)
    test_domain_methods(csp)

    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("CSP模型已准备好用于各种约束求解算法的实现。")
    print("=" * 80)


if __name__ == "__main__":
    main()