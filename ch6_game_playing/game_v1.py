import math

# --- 常量定义 ---
PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ' '

# --- 游戏逻辑函数 ---

def print_board(board):
    """打印当前棋盘状态"""
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---|---|---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---|---|---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()

def check_winner(board, player):
    """检查指定玩家是否获胜"""
    # 所有可能的获胜组合 (行, 列, 对角线)
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 行
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 列
        [0, 4, 8], [2, 4, 6]              # 对角线
    ]
    for condition in win_conditions:
        if board[condition[0]] == player and \
           board[condition[1]] == player and \
           board[condition[2]] == player:
            return True
    return False

def is_board_full(board):
    """检查棋盘是否已满（平局）"""
    return EMPTY not in board

def get_empty_cells(board):
    """获取所有空格子的索引"""
    return [i for i, cell in enumerate(board) if cell == EMPTY]

# --- Minimax 算法 ---

def evaluate_board(board):
    """
    评估当前棋盘状态。
    这是 Minimax 的终点函数。
    返回 +1 (AI赢), -1 (玩家赢), 0 (平局或未结束)。
    """
    if check_winner(board, PLAYER_O):  # AI (O) 赢了
        return 1
    if check_winner(board, PLAYER_X):  # 玩家 (X) 赢了
        return -1
    return 0  # 平局或游戏未结束

def minimax(board, depth, is_maximizing):
    """
    Minimax 算法的核心递归函数。
    - board: 当前棋盘状态
    - depth: 当前搜索深度 (对于井字棋可以省略，但保留是好习惯)
    - is_maximizing: 当前是 MAX 玩家 (AI) 还是 MIN 玩家 (人类) 的回合
    """
    # 1. 终止条件：检查游戏是否结束
    score = evaluate_board(board)
    if score is not 0: # 如果有人赢了
        return score
    if is_board_full(board): # 如果平局
        return 0

    # 2. 递归步骤
    empty_cells = get_empty_cells(board)

    if is_maximizing:
        # --- AI (MAX) 的回合 ---
        best_score = -math.inf
        for cell in empty_cells:
            # 尝试走一步
            board[cell] = PLAYER_O
            # 递归调用 Minimax，轮到 MIN 玩家
            score = minimax(board, depth + 1, False)
            # 撤销这一步 (回溯)
            board[cell] = EMPTY
            # 更新最佳分数
            best_score = max(score, best_score)
        return best_score
    else:
        # --- 人类 (MIN) 的回合 ---
        best_score = math.inf
        for cell in empty_cells:
            # 尝试走一步
            board[cell] = PLAYER_X
            # 递归调用 Minimax，轮到 MAX 玩家
            score = minimax(board, depth + 1, True)
            # 撤销这一步 (回溯)
            board[cell] = EMPTY
            # 更新最佳分数
            best_score = min(score, best_score)
        return best_score

def find_best_move(board):
    """
    为 AI (MAX 玩家) 找到最佳走法。
    遍历所有可能的走法，调用 minimax 评估，并返回得分最高的那一步。
    """
    best_score = -math.inf
    best_move = -1
    empty_cells = get_empty_cells(board)

    for cell in empty_cells:
        # 尝试走一步
        board[cell] = PLAYER_O
        # 调用 minimax 评估这一步的分数，注意此时轮到 MIN 玩家
        move_score = minimax(board, 0, False)
        # 撤销这一步 (回溯)
        board[cell] = EMPTY
        
        # 如果这一步的分数比当前最佳分数还高，就更新最佳走法
        if move_score > best_score:
            best_score = move_score
            best_move = cell
            
    return best_move

# --- 主游戏循环 ---

def main():
    """主函数，运行游戏"""
    board = [EMPTY] * 9
    current_player = PLAYER_X  # 人类玩家先手

    print("欢迎来到井字棋游戏！")
    print("你是 'X'，AI 是 'O'。")
    print("输入数字 0-8 来放置你的棋子，对应位置如下：")
    print(" 0 | 1 | 2 ")
    print("---|---|---")
    print(" 3 | 4 | 5 ")
    print("---|---|---")
    print(" 6 | 7 | 8 ")

    while True:
        print_board(board)

        # 检查游戏是否结束
        if check_winner(board, PLAYER_X):
            print("恭喜你，你赢了！")
            break
        if check_winner(board, PLAYER_O):
            print("AI 赢了！再接再厉。")
            break
        if is_board_full(board):
            print("平局！")
            break

        # 玩家回合
        if current_player == PLAYER_X:
            try:
                move = int(input("轮到你了，请输入你的走法 (0-8): "))
                if move not in get_empty_cells(board):
                    print("无效的走法，请选择一个空格子。")
                    continue
                board[move] = PLAYER_X
                current_player = PLAYER_O
            except (ValueError, IndexError):
                print("无效输入，请输入 0 到 8 之间的数字。")
        
        # AI 回合
        else:
            print("AI 正在思考...")
            move = find_best_move(board)
            board[move] = PLAYER_O
            print(f"AI 选择了位置 {move}")
            current_player = PLAYER_X

if __name__ == "__main__":
    main()