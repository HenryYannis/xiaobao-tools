#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 井字棋游戏 (Tic Tac Toe)

功能：
- 经典的井字棋游戏
- 支持双人对战和人机对战
- 基于 tkinter 的图形界面

使用方法：
- 直接运行即可开始游戏
- 点击格子下棋
- 可切换双人对战/人机对战模式

注意事项：
- 需要 tkinter 库（Python 自带）

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from tkinter import messagebox
import random


class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("井字棋")
        self.master.resizable(False, False)

        # 游戏状态
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'  # X 先手
        self.game_over = False
        self.vs_ai = True  # 默认人机对战

        # 创建界面
        self.create_widgets()

        # 窗口居中
        self.master.update_idletasks()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() - w) // 2
        y = (self.master.winfo_screenheight() - h) // 2
        self.master.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # 模式选择
        mode_frame = tk.Frame(self.master)
        mode_frame.grid(row=0, column=0, columnspan=3, pady=5)

        self.mode_var = tk.BooleanVar(value=True)
        tk.Radiobutton(mode_frame, text="人机对战", variable=self.mode_var,
                       value=True, command=self.switch_mode).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="双人对战", variable=self.mode_var,
                       value=False, command=self.switch_mode).pack(side=tk.LEFT, padx=10)

        # 标题标签
        self.title_label = tk.Label(
            self.master,
            text="井字棋 - 你是 X (人机对战)",
            font=('Arial', 16, 'bold')
        )
        self.title_label.grid(row=1, column=0, columnspan=3, pady=10)

        # 游戏板按钮
        self.buttons = []
        for i in range(9):
            button = tk.Button(
                self.master,
                text=' ',
                font=('Arial', 30, 'bold'),
                width=4,
                height=2,
                bg='#f0f0f0',
                activebackground='#e0e0e0',
                command=lambda i=i: self.on_click(i)
            )
            row = (i // 3) + 2
            col = i % 3
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(button)

        # 重置按钮
        self.reset_button = tk.Button(
            self.master,
            text="重新开始",
            font=('Arial', 12),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            command=self.reset_game
        )
        self.reset_button.grid(row=5, column=0, columnspan=3, pady=10)

    def switch_mode(self):
        """切换对战模式"""
        self.vs_ai = self.mode_var.get()
        self.reset_game()

    def on_click(self, index):
        """处理玩家点击"""
        if self.board[index] == ' ' and not self.game_over:
            if self.vs_ai:
                # 人机模式：玩家是 X
                if self.current_player == 'X':
                    self.make_move(index, 'X')
                    if not self.game_over:
                        self.master.after(500, self.computer_move)
            else:
                # 双人模式：X 和 O 轮流
                self.make_move(index, self.current_player)
                if not self.game_over:
                    self.current_player = 'O' if self.current_player == 'X' else 'X'
                    self.title_label.config(text=f"井字棋 - 轮到 {self.current_player}")

    def make_move(self, index, player):
        """在指定位置下棋"""
        self.board[index] = player
        color = '#333' if player == 'X' else '#FF5733'
        self.buttons[index].config(
            text=player,
            state='disabled',
            disabledforeground=color
        )

        # 检查胜负
        winner = self.check_winner()
        if winner:
            self.game_over = True
            if self.vs_ai:
                msg = "恭喜你赢了！" if winner == 'X' else "电脑赢了！"
            else:
                msg = f"玩家 {winner} 赢了！"
            messagebox.showinfo("游戏结束", msg)
            self.disable_all_buttons()
        elif ' ' not in self.board:
            self.game_over = True
            messagebox.showinfo("游戏结束", "平局！")
            self.disable_all_buttons()

    def computer_move(self):
        """电脑AI移动"""
        if self.game_over:
            return

        # 策略1：检查电脑是否能赢
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O'
                if self.check_winner() == 'O':
                    self.board[i] = ' '
                    self.make_move(i, 'O')
                    return
                self.board[i] = ' '

        # 策略2：阻止玩家赢
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'X'
                if self.check_winner() == 'X':
                    self.board[i] = ' '
                    self.make_move(i, 'O')
                    return
                self.board[i] = ' '

        # 策略3：占中心
        if self.board[4] == ' ':
            self.make_move(4, 'O')
            return

        # 策略4：占角落
        corners = [0, 2, 6, 8]
        available_corners = [i for i in corners if self.board[i] == ' ']
        if available_corners:
            move = random.choice(available_corners)
            self.make_move(move, 'O')
            return

        # 策略5：随机占空位
        available_moves = [i for i in range(9) if self.board[i] == ' ']
        if available_moves:
            move = random.choice(available_moves)
            self.make_move(move, 'O')

    def check_winner(self):
        """检查是否有玩家获胜"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 行
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 列
            [0, 4, 8], [2, 4, 6]              # 对角线
        ]

        for pattern in win_patterns:
            a, b, c = pattern
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]

        return None

    def disable_all_buttons(self):
        """禁用所有按钮"""
        for button in self.buttons:
            button.config(state='disabled')

    def reset_game(self):
        """重置游戏"""
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False

        for button in self.buttons:
            button.config(
                text=' ',
                state='normal',
                bg='#f0f0f0'
            )

        if self.vs_ai:
            self.title_label.config(text="井字棋 - 你是 X (人机对战)")
        else:
            self.title_label.config(text="井字棋 - 轮到 X (双人对战)")


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
