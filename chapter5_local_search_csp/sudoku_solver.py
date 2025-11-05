"""
使用局部搜索方法求解9×9数独问题
实现基于最小冲突数（Min-Conflicts）算法的局部搜索

数独的形式化规则定义：
1. 行唯一性约束：每一行中的每个数字恰好出现一次
2. 列唯一性约束：每一列中的每个数字恰好出现一次
3. 宫唯一性约束：每个3×3的宫内，每个数字恰好出现一次
"""

import random
import time

# 简化版本，不使用numpy和matplotlib以避免版本冲突
# 如需可视化，请确保安装兼容版本的numpy<2.0和matplotlib


class SudokuLocalSearch:
    def __init__(self, initial_board):
        """
        初始化数独局部搜索求解器

        Args:
            initial_board: 9×9的初始数独棋盘，0表示空格
        """
        self.size = 9
        self.box_size = 3
        self.initial_board = [row[:] for row in initial_board]  # 深拷贝
        self.board = [row[:] for row in initial_board]  # 深拷贝
        self.fixed_cells = [[cell != 0 for cell in row] for row in initial_board]

    def get_box_position(self, row, col):
        """获取(row, col)所在3×3宫的起始位置"""
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        return box_row, box_col

    def get_valid_numbers(self, row, col):
        """
        获取(row, col)位置的有效数字（不违反约束的数字）
        实现形式化规则检查：
        - 行唯一性：∀i ∈ G, ∀j₁, j₂ ∈ G, j₁ ≠ j₂: S(i,j₁) ≠ S(i,j₂)
        - 列唯一性：∀j ∈ G, ∀i₁, i₂ ∈ G, i₁ ≠ i₂: S(i₁,j) ≠ S(i₂,j)
        - 宫唯一性：每个3×3宫内数字唯一
        """
        if self.fixed_cells[row][col]:
            return [self.board[row][col]]

        valid = list(range(1, 10))

        # 检查行约束 - 行唯一性
        for c in range(self.size):
            if c != col and self.board[row][c] != 0:
                if self.board[row][c] in valid:
                    valid.remove(self.board[row][c])

        # 检查列约束 - 列唯一性
        for r in range(self.size):
            if r != row and self.board[r][col] != 0:
                if self.board[r][col] in valid:
                    valid.remove(self.board[r][col])

        # 检查宫约束 - 宫唯一性
        box_row, box_col = self.get_box_position(row, col)
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if (r != row or c != col) and self.board[r][c] != 0:
                    if self.board[r][c] in valid:
                        valid.remove(self.board[r][c])

        return valid if valid else list(range(1, 10))  # 如果没有有效数字，返回所有数字

    def count_conflicts(self, row, col, value):
        """
        计算在(row, col)位置放置value值时的冲突数
        检查违反三个约束条件的总数
        """
        conflicts = 0

        # 检查行冲突
        for c in range(self.size):
            if c != col and self.board[row][c] == value:
                conflicts += 1

        # 检查列冲突
        for r in range(self.size):
            if r != row and self.board[r][col] == value:
                conflicts += 1

        # 检查宫冲突
        box_row, box_col = self.get_box_position(row, col)
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if (r != row or c != col) and self.board[r][c] == value:
                    conflicts += 1

        return conflicts

    def initialize_board(self):
        """初始化棋盘，为每个空格随机分配一个有效数字"""
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    valid_numbers = self.get_valid_numbers(row, col)
                    self.board[row][col] = random.choice(valid_numbers)

    def get_conflicted_cells(self):
        """获取所有冲突的单元格"""
        conflicted = []
        for row in range(self.size):
            for col in range(self.size):
                value = self.board[row][col]
                if self.count_conflicts(row, col, value) > 0:
                    conflicted.append((row, col))
        return conflicted

    def solve(self, max_iterations=1000):
        """
        使用最小冲突数算法求解数独

        Args:
            max_iterations: 最大迭代次数

        Returns:
            bool: 是否找到解
        """
        self.initialize_board()

        for iteration in range(max_iterations):
            conflicted_cells = self.get_conflicted_cells()

            # 如果没有冲突，找到解
            if not conflicted_cells:
                return True

            # 随机选择一个冲突单元格
            row, col = random.choice(conflicted_cells)

            # 如果是固定单元格，跳过
            if self.fixed_cells[row][col]:
                continue

            # 寻找最小冲突数的值
            valid_numbers = self.get_valid_numbers(row, col)
            min_conflicts = float('inf')
            best_values = []

            for value in valid_numbers:
                conflicts = self.count_conflicts(row, col, value)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_values = [value]
                elif conflicts == min_conflicts:
                    best_values.append(value)

            # 随机选择一个最小冲突数的值
            self.board[row][col] = random.choice(best_values)

        return False

    def print_board(self, title=""):
        """打印数独棋盘"""
        print(title)
        print("-" * 25)
        for i in range(self.size):
            if i % 3 == 0 and i != 0:
                print("-" * 25)

            row_str = "|"
            for j in range(self.size):
                cell_value = self.board[i][j] if self.board[i][j] != 0 else '.'
                row_str += f" {cell_value} "
                if (j + 1) % 3 == 0:
                    row_str += "|"
            print(row_str)
        print("-" * 25)

    def display_board_visual(self, title=""):
        """可视化显示数独棋盘（简化版本，返回ASCII图）"""
        print(f"\n{title}")
        print("=" * 25)
        for i in range(self.size):
            if i % 3 == 0 and i != 0:
                print("=" * 25)

            row_str = "|"
            for j in range(self.size):
                cell_value = self.board[i][j] if self.board[i][j] != 0 else '.'
                # 标记原始数字（固定）和填入数字
                if self.fixed_cells[i][j]:
                    row_str += f" \033[94m{cell_value}\033[0m "  # 蓝色
                else:
                    row_str += f" \033[91m{cell_value}\033[0m "  # 红色

                if (j + 1) % 3 == 0:
                    row_str += "|"
            print(row_str)
        print("=" * 25)
        print("(蓝色：原始数字，红色：求解填入的数字)")


def solve_sample_sudoku():
    """求解示例数独问题"""
    # 示例9×9数独（0表示空格）
    initial_sudoku = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    print("9×9数独局部搜索求解器")
    print("=" * 40)
    print("数独规则：")
    print("1. 行唯一性约束：每一行中的每个数字恰好出现一次")
    print("2. 列唯一性约束：每一列中的每个数字恰好出现一次")
    print("3. 宫唯一性约束：每个3×3的宫内，每个数字恰好出现一次")
    print("=" * 40)

    solver = SudokuLocalSearch(initial_sudoku)

    # 显示初始状态
    solver.print_board("初始数独问题:")
    solver.display_board_visual("初始数独问题（可视化）")

    # 使用局部搜索求解
    print("\n开始使用最小冲突数算法求解...")
    start_time = time.time()

    # 使用多次尝试增加成功率
    success = False
    for attempt in range(1000):  # 尝试5次
        print(f"\n尝试第 {attempt + 1} 次求解...")
        success = solver.solve(max_iterations=5000)
        if success:
            break
        else:
            print(f"第 {attempt + 1} 次尝试失败，重新初始化...")
            solver.board = [row[:] for row in solver.initial_board]  # 重置棋盘

    end_time = time.time()
    print(f"求解时间: {end_time - start_time:.4f}秒")

    if success:
        print("\n[OK] 成功找到解！")
        solver.print_board("求解结果:")
        solver.display_board_visual("求解结果（可视化）")

        # 验证解的正确性
        if solver.verify_solution():
            print("[OK] 验证通过：解满足所有约束条件")
        else:
            print("[ERROR] 验证失败：解不满足约束条件")
    else:
        print("\n[ERROR] 在最大迭代次数内未找到解")
        solver.print_board("当前状态（可能不是最优解）:")
        solver.display_board_visual("未找到完整解（可视化）")

    return success


def main():
    """主函数"""
    # 求解示例数独
    solve_sample_sudoku()
    return  # 直接退出，不进入交互模式


# 扩展SudokuLocalSearch类，添加验证方法
def verify_solution(self):
    """
    验证当前解是否正确
    检查三个形式化约束条件：
    1. 行唯一性：每一行中的每个数字恰好出现一次
    2. 列唯一性：每一列中的每个数字恰好出现一次
    3. 宫唯一性：每个3×3的宫内，每个数字恰好出现一次
    """
    # 检查每行 - 行唯一性约束
    for row in range(self.size):
        values = [self.board[row][col] for col in range(self.size)]
        if len(set(values)) != self.size or 0 in values:
            return False

    # 检查每列 - 列唯一性约束
    for col in range(self.size):
        values = [self.board[row][col] for row in range(self.size)]
        if len(set(values)) != self.size or 0 in values:
            return False

    # 检查每个3×3宫 - 宫唯一性约束
    for box_row in range(0, self.size, self.box_size):
        for box_col in range(0, self.size, self.box_size):
            values = []
            for r in range(box_row, box_row + self.box_size):
                for c in range(box_col, box_col + self.box_size):
                    values.append(self.board[r][c])
            if len(set(values)) != self.size or 0 in values:
                return False

    return True

# 动态添加方法到类
SudokuLocalSearch.verify_solution = verify_solution


if __name__ == "__main__":
    main()