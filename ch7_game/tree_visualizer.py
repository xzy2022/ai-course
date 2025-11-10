import plotly.graph_objects as go
from collections import deque
import re

class TreeNode:
    """树节点类，存储节点名称、值和子节点"""
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []
        
    def add_child(self, child_node):
        """添加子节点"""
        self.children.append(child_node)

class TreeVisualizer:
    """树可视化类，负责解析文件、构建树和可视化"""
    def __init__(self):
        self.root = None
        self.nodes = {}  # 名称到节点的映射
    
    def parse_file(self, filename):
        """
        解析txt文件构建树结构
        格式：父节点: 子节点1 值1 子节点2 子节点3 值3 ...
        """
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if ':' not in line:
                print(f"警告: 行 '{line}' 格式不正确，跳过")
                continue
            
            parent_part, children_part = line.split(':', 1)
            parent_name = parent_part.strip()
            
            # 获取或创建父节点
            if parent_name not in self.nodes:
                self.nodes[parent_name] = TreeNode(parent_name)
            
            parent_node = self.nodes[parent_name]
            
            # 设置根节点（第一个出现的父节点）
            if self.root is None:
                self.root = parent_node
            
            # 解析子节点部分
            tokens = children_part.strip().split()
            i = 0
            while i < len(tokens):
                token = tokens[i]
                
                # 检查是否是数字（整数或小数）
                if re.match(r'^-?\d+(\.\d+)?$', token):
                    # 是数字，赋给前一个节点作为值
                    if i > 0:
                        prev_token = tokens[i-1]
                        if prev_token in self.nodes:
                            self.nodes[prev_token].value = float(token)
                    else:
                        print(f"警告: 行 '{line}' 中的数字 '{token}' 没有对应的节点")
                    i += 1
                else:
                    # 是节点名称
                    if token not in self.nodes:
                        self.nodes[token] = TreeNode(token)
                    
                    # 添加到父节点的子节点列表
                    parent_node.add_child(self.nodes[token])
                    i += 1
    
    def calculate_positions(self):
        """使用BFS计算每个节点的位置（x, y）"""
        if not self.root:
            return {}
        
        positions = {}
        level_nodes = {}  # 每层节点列表
        
        # BFS遍历，收集每层节点
        queue = deque([(self.root, 0)])
        while queue:
            node, level = queue.popleft()
            
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
            
            for child in node.children:
                queue.append((child, level + 1))
        
        # 计算位置
        for level, nodes in level_nodes.items():
            num_nodes = len(nodes)
            for i, node in enumerate(nodes):
                # x坐标：在水平方向上均匀分布
                x = (i + 1) / (num_nodes + 1)
                # y坐标：从上到下，level越大越靠下
                y = -level
                
                positions[node.name] = (x, y)
        
        return positions
    
    def get_edges(self, positions):
        """获取所有边的坐标用于绘制"""
        edges_x = []
        edges_y = []
        
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            
            for child in node.children:
                if node.name in positions and child.name in positions:
                    x_parent, y_parent = positions[node.name]
                    x_child, y_child = positions[child.name]
                    
                    # 添加边（每段线由起点、终点和None组成，用于分隔不同边）
                    edges_x.extend([x_parent, x_child, None])
                    edges_y.extend([y_parent, y_child, None])
                
                queue.append(child)
        
        return edges_x, edges_y
    
    def visualize(self, title="树结构可视化", width=800, height=600):
        """
        使用Plotly可视化树
        返回: Plotly图形对象
        """
        if not self.root:
            print("树为空，无法可视化")
            return None
        
        positions = self.calculate_positions()
        edges_x, edges_y = self.get_edges(positions)
        
        # 创建图形
        fig = go.Figure()
        
        # 添加边
        if edges_x and edges_y:
            fig.add_trace(go.Scatter(
                x=edges_x,
                y=edges_y,
                mode='lines',
                line=dict(color='rgb(150,150,150)', width=2),
                hoverinfo='none',
                showlegend=False
            ))
        
        # 准备节点数据
        node_x = []
        node_y = []
        node_text = []
        node_hover = []
        
        for name, (x, y) in positions.items():
            node = self.nodes[name]
            node_x.append(x)
            node_y.append(y)
            
            # 节点显示文本（名称+值）
            label = name
            if node.value is not None:
                label += f"<br>{node.value}"
            
            node_text.append(label)
            
            # 悬停信息
            hover_text = f"节点: {name}"
            if node.value is not None:
                hover_text += f"<br>值: {node.value}"
            node_hover.append(hover_text)
        
        # 添加节点
        fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=40,
                color='lightblue',
                line=dict(color='rgb(50,50,50)', width=2)
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=12, color='black'),
            hovertext=node_hover,
            hoverinfo='text',
            showlegend=False
        ))
        
        # 更新布局
        fig.update_layout(
            title=title,
            title_x=0.5,
            title_font=dict(size=16),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, 1]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            plot_bgcolor='white',
            width=width,
            height=height,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig

def main():
    """主函数，用于直接运行脚本"""
    visualizer = TreeVisualizer()
    visualizer.parse_file('data.txt')
    fig = visualizer.visualize()
    if fig:
        fig.show()

if __name__ == "__main__":
    main()