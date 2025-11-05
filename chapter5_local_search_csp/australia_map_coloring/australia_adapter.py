"""
澳大利亚涂色问题的CSP适配器

将澳大利亚涂色问题的CSP模型适配到通用的CSP接口。
这个适配器展示了如何将特定问题集成到泛化求解器框架中。
"""

from typing import Dict, List
from csp_model import AustraliaMapColoringCSP, Color, Region
from generic_solver import CSPBase


class AustraliaCSPAdapter(CSPBase[Region, Color]):
    """
    澳大利亚涂色问题的CSP适配器

    将专用的AustraliaMapColoringCSP模型适配到通用的CSPBase接口，
    使其可以与GenericBacktrackSolver配合使用。
    """

    def __init__(self, csp_model: AustraliaMapColoringCSP):
        """
        初始化适配器

        Args:
            csp_model: 澳大利亚涂色问题的CSP模型
        """
        super().__init__()
        self.csp_model = csp_model
        self.domains = csp_model.domains  # 直接引用模型的值域

    def get_variables(self) -> List[Region]:
        """获取所有变量（地区）"""
        return self.csp_model.variables

    def get_domain(self, var: Region) -> List[Color]:
        """获取变量的值域（颜色）"""
        return self.csp_model.domains[var]

    def get_neighbors(self, var: Region) -> List[Region]:
        """获取变量的邻居（相邻地区）"""
        return self.csp_model.neighbors[var]

    def is_consistent(self, var: Region, value: Color, assignment: Dict[Region, Color]) -> bool:
        """检查赋值是否满足约束"""
        return self.csp_model.is_consistent(var, value, assignment)

    def print_assignment(self, assignment: Dict[Region, Color], title: str = "赋值"):
        """打印赋值（委托给原始模型）"""
        self.csp_model.print_assignment(assignment, title)

    def is_solution(self, assignment: Dict[Region, Color]) -> bool:
        """检查是否为完整解决方案（委托给原始模型）"""
        return self.csp_model.is_solution(assignment)


def create_australia_csp() -> AustraliaCSPAdapter:
    """
    便捷函数：创建澳大利亚涂色问题的CSP适配器

    Returns:
        AustraliaCSPAdapter: 已初始化的适配器实例
    """
    csp_model = AustraliaMapColoringCSP()
    return AustraliaCSPAdapter(csp_model)