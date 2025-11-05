"""
澳大利亚地图涂色问题的约束满足问题（CSP）形式化模型

纯模型文件，只包含CSP的构建和基础功能，不包含测试代码。
可以被其他脚本引用进行测试和算法实现。

实现形式化的CSP模型，包括：
- 变量集合 X：澳大利亚所有州和地区
- 值域集合 D：三种颜色 {红, 绿, 蓝}
- 约束集合 C：所有相邻区域的二元约束
"""

from typing import Dict, List, Tuple, Set
from enum import Enum


class Color(Enum):
    """颜色枚举类"""
    RED = "红"
    GREEN = "绿"
    BLUE = "蓝"

    def __str__(self):
        return self.value


class Region(Enum):
    """澳大利亚州和地区枚举类"""
    WA = "西澳大利亚州"
    NT = "北领地"
    SA = "南澳大利亚州"
    QLD = "昆士兰州"
    NSW = "新南威尔士州"
    VIC = "维多利亚州"
    TAS = "塔斯马尼亚州"

    def __str__(self):
        return self.value


class AustraliaMapColoringCSP:
    """澳大利亚地图涂色问题的CSP形式化模型"""

    def __init__(self):
        """
        初始化澳大利亚地图涂色问题的CSP模型

        形式化定义：
        - 变量集合 X = {WA, NT, SA, QLD, NSW, VIC, TAS}
        - 值域集合 D_i = {红, 绿, 蓝}，其中 i ∈ X
        - 约束集合 C = {C₁, C₂, ..., C₉}
        """
        self.variables = list(Region)  # 变量集合 X
        self.colors = list(Color)      # 颜色值域
        self.domains = self._initialize_domains()  # 初始化值域集合 D

        # 邻接关系定义（基于澳大利亚地理邻接）
        self.neighbors = self._initialize_neighbors()

        # 约束集合 C
        self.constraints = self._initialize_constraints()

        # 当前解决方案（初始为空）
        self.assignment = {}

    def _initialize_domains(self) -> Dict[Region, List[Color]]:
        """
        初始化值域集合 D
        对于每个变量 i ∈ X，值域 D_i = {红, 绿, 蓝}
        """
        domains = {}
        for region in self.variables:
            domains[region] = self.colors.copy()
        return domains

    def _initialize_neighbors(self) -> Dict[Region, List[Region]]:
        """
        初始化邻接关系
        基于澳大利亚地图的实际地理邻接关系
        """
        neighbors = {
            Region.WA: [Region.NT, Region.SA],      # 西澳大利亚州与北领地、南澳大利亚州相邻
            Region.NT: [Region.WA, Region.SA, Region.QLD],  # 北领地与西澳大利亚州、南澳大利亚州、昆士兰州相邻
            Region.SA: [Region.WA, Region.NT, Region.QLD, Region.NSW, Region.VIC],  # 南澳大利亚州与多个地区相邻
            Region.QLD: [Region.NT, Region.SA, Region.NSW],  # 昆士兰州与北领地、南澳大利亚州、新南威尔士州相邻
            Region.NSW: [Region.SA, Region.QLD, Region.VIC],  # 新南威尔士州与南澳大利亚州、昆士兰州、维多利亚州相邻
            Region.VIC: [Region.SA, Region.NSW],     # 维多利亚州与南澳大利亚州、新南威尔士州相邻
            Region.TAS: []                           # 塔斯马尼亚州是岛屿，无陆地邻接
        }
        return neighbors

    def _initialize_constraints(self) -> List[Tuple[Region, Region]]:
        """
        初始化约束集合 C
        包含所有相邻区域的二元约束

        约束形式：C_i : <{X₁, X₂}, X₁ ≠ X₂>，其中 X₁, X₂ 是相邻区域
        """
        constraints = []
        processed_pairs = set()  # 避免重复添加相同的约束对

        for region in self.variables:
            for neighbor in self.neighbors[region]:
                pair = tuple(sorted([region, neighbor], key=lambda x: x.name))
                if pair not in processed_pairs:
                    constraints.append(pair)
                    processed_pairs.add(pair)

        return constraints

    def print_csp_model(self):
        """打印CSP模型的形式化描述"""
        print("=" * 60)
        print("澳大利亚地图涂色问题的CSP形式化模型")
        print("=" * 60)

        print("\n1. 变量集合 X:")
        print("   X = {", end="")
        for i, region in enumerate(self.variables):
            if i > 0:
                print(", ", end="")
            print(region.name, end="")
        print("}")

        print("\n2. 值域集合 D:")
        print("   对于每个变量 i ∈ X，值域 D_i = {红, 绿, 蓝}")
        print(f"   颜色集合: {[color.value for color in self.colors]}")

        print("\n3. 约束集合 C:")
        print("   相邻区域颜色不同的二元约束:")
        for i, (region1, region2) in enumerate(self.constraints, 1):
            print(f"   C_{i}: <{{{region1.name}, {region2.name}}}, {region1.name} ≠ {region2.name}>")

        print(f"\n   总计 {len(self.constraints)} 个约束")

        print("\n4. 邻接关系:")
        for region, neighbors in self.neighbors.items():
            if neighbors:
                print(f"   {region.name}: {[n.name for n in neighbors]}")
            else:
                print(f"   {region.name}: 无邻接区域（岛屿）")

        print("=" * 60)

    def is_consistent(self, region: Region, color: Color, assignment: Dict[Region, Color]) -> bool:
        """
        检查给定的赋值是否满足约束

        Args:
            region: 要分配颜色的区域
            color: 要分配的颜色
            assignment: 当前的赋值（部分或完整）

        Returns:
            bool: 赋值是否满足约束
        """
        # 检查该区域的所有邻居
        for neighbor in self.neighbors[region]:
            if neighbor in assignment:
                # 约束：相邻区域颜色不同
                if assignment[neighbor] == color:
                    return False
        return True

    def is_complete(self, assignment: Dict[Region, Color]) -> bool:
        """
        检查赋值是否完整（所有变量都已赋值）

        Args:
            assignment: 当前赋值

        Returns:
            bool: 赋值是否完整
        """
        return len(assignment) == len(self.variables)

    def is_solution(self, assignment: Dict[Region, Color]) -> bool:
        """
        检查赋值是否是完整的解决方案

        Args:
            assignment: 当前赋值

        Returns:
            bool: 是否是完整的解决方案
        """
        # 必须是完整赋值
        if not self.is_complete(assignment):
            return False

        # 必须满足所有约束
        for region in assignment:
            if not self.is_consistent(region, assignment[region], assignment):
                return False

        return True

    def get_unassigned_variables(self, assignment: Dict[Region, Color]) -> List[Region]:
        """
        获取未分配的变量

        Args:
            assignment: 当前赋值

        Returns:
            List[Region]: 未分配的变量列表
        """
        return [region for region in self.variables if region not in assignment]

    def get_conflicted_variables(self, assignment: Dict[Region, Color]) -> List[Region]:
        """
        获取有冲突的变量

        Args:
            assignment: 当前赋值

        Returns:
            List[Region]: 有冲突的变量列表
        """
        conflicted = []
        for region, color in assignment.items():
            if not self.is_consistent(region, color, assignment):
                conflicted.append(region)
        return conflicted

    def count_conflicts(self, assignment: Dict[Region, Color]) -> int:
        """
        计算赋值中的冲突总数

        Args:
            assignment: 当前赋值

        Returns:
            int: 冲突总数
        """
        conflicts = 0
        for region1, region2 in self.constraints:
            if region1 in assignment and region2 in assignment:
                if assignment[region1] == assignment[region2]:
                    conflicts += 1
        return conflicts

    def print_assignment(self, assignment: Dict[Region, Color], title="当前赋值"):
        """
        打印当前赋值

        Args:
            assignment: 当前赋值
            title: 标题
        """
        print(f"\n{title}:")
        print("-" * 40)
        for region in self.variables:
            if region in assignment:
                print(f"  {region.value:10s}: {assignment[region].value}")
            else:
                print(f"  {region.value:10s}: 未分配")
        print("-" * 40)

        if assignment:
            conflicts = self.get_conflicted_variables(assignment)
            if conflicts:
                print(f"冲突变量: {[r.name for r in conflicts]}")
                print(f"冲突总数: {self.count_conflicts(assignment)}")
            else:
                print("无冲突")

    def get_legal_values(self, region: Region, assignment: Dict[Region, Color]) -> List[Color]:
        """
        获取指定区域的合法颜色值

        Args:
            region: 指定区域
            assignment: 当前赋值

        Returns:
            List[Color]: 合法的颜色值列表
        """
        legal_values = []
        for color in self.domains[region]:
            if self.is_consistent(region, color, assignment):
                legal_values.append(color)
        return legal_values

    def validate_csp_model(self) -> bool:
        """
        验证CSP模型的正确性

        Returns:
            bool: 模型是否正确
        """
        print("\n验证CSP模型...")

        # 检查变量集合
        if len(self.variables) != 7:
            print(f"错误：变量集合包含 {len(self.variables)} 个变量，应该是7个")
            return False

        # 检查值域
        for region in self.variables:
            if len(self.domains[region]) != 3:
                print(f"错误：{region.name} 的值域包含 {len(self.domains[region])} 个值，应该是3个")
                return False

        # 检查约束完整性
        expected_constraints = [
            (Region.WA, Region.NT),
            (Region.WA, Region.SA),
            (Region.NT, Region.SA),
            (Region.NT, Region.QLD),
            (Region.SA, Region.QLD),
            (Region.SA, Region.NSW),
            (Region.SA, Region.VIC),
            (Region.QLD, Region.NSW),
            (Region.NSW, Region.VIC)
        ]

        for expected_pair in expected_constraints:
            normalized_expected = tuple(sorted(expected_pair, key=lambda x: x.name))
            found = False
            for constraint in self.constraints:
                normalized_constraint = tuple(sorted(constraint, key=lambda x: x.name))
                if normalized_constraint == normalized_expected:
                    found = True
                    break
            if not found:
                print(f"错误：缺少约束 {expected_pair[0].name} ≠ {expected_pair[1].name}")
                return False

        print("[OK] CSP模型验证通过")
        return True