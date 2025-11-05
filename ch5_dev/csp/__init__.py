"""
CSP (Constraint Satisfaction Problem) 模块

这个模块提供了约束满足问题的基本概念和接口设计，支持显式和隐式约束，
以及多种求解算法。
"""

from .csp_core import CSP, Constraint, Variable, Value, Domain, Scope, Relation
from .algorithms import backtracking_search

__all__ = [
    'CSP',
    'Constraint',
    'Variable',
    'Value',
    'Domain',
    'Scope',
    'Relation',
    'backtracking_search'
]