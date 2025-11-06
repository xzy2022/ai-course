import math
import os

# --- 常量定义 ---
PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ' '

# --- 思考过程记录 ---
thinking_log = []
indent_level = 0
step_counter = 0

def log_thinking(message):
    """记录AI的思考过程"""
    global thinking_log, step_counter
    step_counter += 1
    indent = "  " * indent_level
    thinking_log.append(f"[步骤 {step_counter}] {indent}{message}")

def save_thinking_log():
    """保存思考过程到文件"""
    with open("ai_thinking_process.txt", "w") as f:
        f.write("AI 井字棋思考过程\n")
        f.write("=" * 50 + "\n\n")
        for entry in thinking_log:
            f.write(entry + "\n")

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

def board_to_string(board):
    """将棋盘转换为字符串表示"""
    return f"{board[0]}|{board[1]}|{board[2]}\n{board[3]}|{board[4]}|{board[5]}\n{board[6]}|{board[7]}|{board[8]}"

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
    global indent_level
    
    # 1. 终止条件：检查游戏是否结束
    score = evaluate_board(board)
    if score is not 0: # 如果有人赢了
        log_thinking(f"游戏结束，分数: {score}")
        return score
    if is_board_full(board): # 如果平局
        log_thinking("棋盘已满，平局，分数: 0")
        return 0

    # 2. 递归步骤
    empty_cells = get_empty_cells(board)
    player = PLAYER_O if is_maximizing else PLAYER_X
    player_type = "AI (O)" if is_maximizing else "玩家 (X)"
    
    log_thinking(f"{player_type} 的回合，可选择的空位: {empty_cells}")

    if is_maximizing:
        # --- AI (MAX) 的回合 ---
        best_score = -math.inf
        for cell in empty_cells:
            indent_level += 1
            log_thinking(f"尝试在位置 {cell} 放置 {PLAYER_O}")
            
            # 尝试走一步
            board[cell] = PLAYER_O
            log_thinking(f"棋盘状态:\n{board_to_string(board)}")
            
            # 递归调用 Minimax，轮到 MIN 玩家
            score = minimax(board, depth + 1, False)
            log_thinking("返回分数: " + str(score))
            
            # 撤销这一步 (回溯)
            board[cell] = EMPTY
            
            # 更新最佳分数
            if score > best_score:
                best_score = score
                log_thinking(f"更新最佳分数: {best_score}")
            
            indent_level -= 1
        return best_score
    else:
        # --- 人类 (MIN) 的回合 ---
        best_score = math.inf
        for cell in empty_cells:
            indent_level += 1
            log_thinking(f"尝试在位置 {cell} 放置 {PLAYER_X}")
            
            # 尝试走一步
            board[cell] = PLAYER_X
            log_thinking(f"棋盘状态:\n{board_to_string(board)}")
            
            # 递归调用 Minimax，轮到 MAX 玩家
            score = minimax(board, depth + 1, True)
            log_thinking("返回分数: " + str(score))
            
            # 撤销这一步 (回溯)
            board[cell] = EMPTY
            
            # 更新最佳分数
            if score < best_score:
                best_score = score
                log_thinking(f"更新最佳分数: {best_score}")
            
            indent_level -= 1
        return best_score

def find_best_move(board):
    """
    为 AI (MAX 玩家) 找到最佳走法。
    遍历所有可能的走法，调用 minimax 评估，并返回得分最高的那一步。
    """
    global thinking_log, indent_level, step_counter

    # 清空之前的思考日志
    thinking_log = []
    indent_level = 0
    step_counter = 0

    log_thinking("AI 开始思考最佳走法...")
    log_thinking(f"当前棋盘状态:\n{board_to_string(board)}")
    
    best_score = -math.inf
    best_move = -1
    empty_cells = get_empty_cells(board)
    
    log_thinking(f"可选择的空位: {empty_cells}")
    log_thinking("开始逐一评估每个可选位置:")

    for i, cell in enumerate(empty_cells):
        log_thinking(f"--- 评估第 {i+1} 个位置 {cell} ---")
        indent_level += 1
        log_thinking(f"模拟在位置 {cell} 放置 {PLAYER_O}")

        # 尝试走一步
        board[cell] = PLAYER_O
        log_thinking(f"模拟后棋盘状态:\n{board_to_string(board)}")

        log_thinking("开始预测玩家的最佳回应...")

        # 调用 minimax 评估这一步的分数，注意此时轮到 MIN 玩家
        move_score = minimax(board, 0, False)
        log_thinking(f"位置 {cell} 的评估分数: {move_score}")
        log_thinking(f"解释: 分数 {move_score} 表示如果AI选择位置{cell}")
        if move_score == 1:
            log_thinking("  → AI必胜")
        elif move_score == 0:
            log_thinking("  → 平局")
        elif move_score == -1:
            log_thinking("  → 玩家必胜")

        # 撤销这一步 (回溯)
        board[cell] = EMPTY
        log_thinking("撤销模拟，恢复原棋盘状态")

        # 如果这一步的分数比当前最佳分数还高，就更新最佳走法
        if move_score > best_score:
            log_thinking(f"位置 {cell} (分数{move_score}) 比当前最佳(分数{best_score}) 更好!")
            best_score = move_score
            best_move = cell
            log_thinking(f"更新最佳走法: 位置 {cell}，分数 {best_score}")
        else:
            log_thinking(f"位置 {cell} (分数{move_score}) 不比当前最佳(分数{best_score}) 更好")

        indent_level -= 1
        log_thinking(f"--- 位置 {cell} 评估完成 ---")

    log_thinking(f"\n最终决策: AI 选择位置 {best_move}")
    log_thinking(f"原因: 这是所有选项中分数最高的 ({best_score})")
    
    # 保存思考过程到文件
    save_thinking_log()
    
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
    print("\nAI的思考过程将保存在 'ai_thinking_process.txt' 文件中。")

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
            print("AI的思考过程已保存到 'ai_thinking_process.txt' 文件中。")
            current_player = PLAYER_X

if __name__ == "__main__":
    main()