import logging
import os
from datetime import datetime

class MinMaxSolver:
    """MinMax搜索求解器，支持Alpha-Beta剪枝和详细日志记录"""
    
    def __init__(self, nodes, root_name, log_dir="log"):
        """
        初始化求解器
        :param nodes: 节点字典（从TreeVisualizer的nodes属性获取）
        :param root_name: 根节点名称
        :param log_dir: 日志存储目录
        """
        self.nodes = nodes
        self.root_name = root_name
        self.root = nodes.get(root_name)
        self.log_dir = log_dir
        
        # 统计信息
        self.node_visits = 0
        self.pruning_count = 0
        self.current_depth = 0
        
        # 创建日志目录和初始化日志记录器
        os.makedirs(self.log_dir, exist_ok=True)
        self._setup_logger()
        
        if not self.root:
            self.logger.warning(f"根节点 '{root_name}' 不存在")
    
    def _setup_logger(self):
        """配置日志记录器"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"minmax_search_{timestamp}.log")
        
        self.logger = logging.getLogger(f"minmax_{timestamp}")
        self.logger.setLevel(logging.INFO)
        
        # 清除之前的处理器
        self.logger.handlers.clear()
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 70)
        self.logger.info("MinMax搜索日志")
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info("=" * 70)
    
    def _is_leaf(self, node):
        """判断是否为叶子节点"""
        return len(node.children) == 0
    
    def alpha_beta_search(self, node_name, depth, alpha, beta, is_maximizing, path=None):
        """
        Alpha-Beta剪枝搜索算法（基于搜索结果的伪代码实现）
        :param node_name: 当前节点名称
        :param depth: 剩余搜索深度
        :param alpha: Alpha值（MAX节点的最优下界）
        :param beta: Beta值（MIN节点的最优上界）
        :param is_maximizing: 是否为MAX节点
        :param path: 当前搜索路径
        :return: (节点值, 最优子节点名称)
        """
        if path is None:
            path = []
        
        path = path + [node_name]
        node = self.nodes.get(node_name)
        
        if node is None:
            self.logger.error(f"节点 '{node_name}' 不存在")
            return 0, None
        
        self.node_visits += 1
        self.current_depth = max(self.current_depth, len(path))
        
        # 记录节点访问信息
        self.logger.info(
            f"【访问节点】{node_name} | 深度: {len(path)-1} | "
            f"类型: {'MAX' if is_maximizing else 'MIN'} | "
            f"Alpha: {alpha:.2f} | Beta: {beta:.2f} | "
            f"路径: {' -> '.join(path)}"
        )
        
        # 叶子节点或搜索深度耗尽
        if self._is_leaf(node) or depth == 0:
            leaf_value = node.value if node.value is not None else 0
            self.logger.info(
                f"【叶子节点】{node_name} | 值: {leaf_value:.2f} | "
                f"深度: {len(path)-1} | 路径: {' -> '.join(path)}"
            )
            return leaf_value, None
        
        best_child = None
        
        if is_maximizing:
            # MAX节点：选择最大值（基于搜索结果[^16^][^18^]）
            value = float('-inf')
            for i, child in enumerate(node.children):
                child_value, _ = self.alpha_beta_search(
                    child.name, depth - 1, alpha, beta, False, path
                )
                
                # 更新最优值和子节点
                if child_value > value:
                    value = child_value
                    best_child = child.name
                
                alpha = max(alpha, value)
                
                # Beta剪枝（参考搜索结果[^18^]）
                if value >= beta:
                    self.pruning_count += 1
                    self.logger.info(
                        f"【β剪枝】{node_name} | 剪枝子节点: {child.name} "
                        f"及后续 {len(node.children)-i-1} 个节点 | "
                        f"原因: {value:.2f} >= β={beta:.2f} | "
                        f"路径: {' -> '.join(path)}"
                    )
                    break
            
            self.logger.info(
                f"【MAX返回】{node_name} | 值: {value:.2f} | "
                f"Alpha: {alpha:.2f} | Beta: {beta:.2f} | "
                f"最优子节点: {best_child}"
            )
            return value, best_child
            
        else:
            # MIN节点：选择最小值
            value = float('inf')
            for i, child in enumerate(node.children):
                child_value, _ = self.alpha_beta_search(
                    child.name, depth - 1, alpha, beta, True, path
                )
                
                # 更新最优值和子节点
                if child_value < value:
                    value = child_value
                    best_child = child.name
                
                beta = min(beta, value)
                
                # Alpha剪枝
                if value <= alpha:
                    self.pruning_count += 1
                    self.logger.info(
                        f"【α剪枝】{node_name} | 剪枝子节点: {child.name} "
                        f"及后续 {len(node.children)-i-1} 个节点 | "
                        f"原因: {value:.2f} <= α={alpha:.2f} | "
                        f"路径: {' -> '.join(path)}"
                    )
                    break
            
            self.logger.info(
                f"【MIN返回】{node_name} | 值: {value:.2f} | "
                f"Alpha: {alpha:.2f} | Beta: {beta:.2f} | "
                f"最优子节点: {best_child}"
            )
            return value, best_child
    
    def get_optimal_path(self, depth):
        """
        获取从根节点开始的最优路径
        :param depth: 搜索深度
        :return: 最优路径节点列表
        """
        if not self.root:
            return []
        
        path = []
        current_node = self.root_name
        is_maximizing = True
        
        for d in range(depth, -1, -1):
            path.append(current_node)
            node = self.nodes.get(current_node)
            
            if not node or not node.children:
                break
            
            _, best_child = self.alpha_beta_search(
                current_node, d, float('-inf'), float('inf'), is_maximizing
            )
            
            if best_child:
                current_node = best_child
                is_maximizing = not is_maximizing
            else:
                break
        
        return path
    
    def solve(self, depth=999):
        """
        执行MinMax搜索并完整记录结果
        :param depth: 最大搜索深度（默认999表示搜索到底）
        :return: 搜索结果字典
        """
        self.logger.info("开始MinMax搜索")
        self.logger.info(f"根节点: {self.root_name}")
        self.logger.info(f"最大深度: {depth if depth < 999 else '无限（搜索到叶子）'}")
        self.logger.info("-" * 70)
        
        # 重置统计信息
        self.node_visits = 0
        self.pruning_count = 0
        self.current_depth = 0
        
        # 执行Alpha-Beta搜索
        result_value, best_child = self.alpha_beta_search(
            self.root_name, depth, float('-inf'), float('inf'), True
        )
        
        # 获取最优路径
        optimal_path = self.get_optimal_path(depth)
        
        # 记录搜索结果总结
        self.logger.info("-" * 70)
        self.logger.info("搜索结果总结")
        self.logger.info("=" * 70)
        self.logger.info(f"根节点最优值: {result_value:.2f}")
        self.logger.info(f"最优子节点: {best_child}")
        self.logger.info(f"最优路径: {' -> '.join(optimal_path)}")
        self.logger.info(f"搜索最大深度: {self.current_depth-1}")
        self.logger.info(f"访问节点总数: {self.node_visits}")
        self.logger.info(f"剪枝总次数: {self.pruning_count}")
        self.logger.info(f"剪枝效率: {(self.pruning_count/(self.node_visits+1)):.2%}")
        self.logger.info("=" * 70)
        
        # 返回结构化结果
        return {
            'optimal_value': result_value,
            'best_child': best_child,
            'optimal_path': optimal_path,
            'node_visits': self.node_visits,
            'pruning_count': self.pruning_count,
            'max_depth': self.current_depth - 1
        }

# 备用函数：用于快速创建测试树
def create_test_tree():
    """创建示例树结构用于测试"""
    from tree_visualizer import TreeNode
    
    nodes = {}
    # 手动构建树
    nodes['A'] = TreeNode('A')
    nodes['B'] = TreeNode('B', 10)
    nodes['C'] = TreeNode('C')
    nodes['D'] = TreeNode('D', 50)
    nodes['E'] = TreeNode('E', 15)
    nodes['F'] = TreeNode('F', 5)
    nodes['G'] = TreeNode('G', 8)
    nodes['H'] = TreeNode('H', 20)
    
    # 构建层级关系
    nodes['A'].children = [nodes['B'], nodes['C'], nodes['D']]
    nodes['C'].children = [nodes['E'], nodes['F']]
    nodes['B'].children = [nodes['G'], nodes['H']]
    
    return nodes, 'A'