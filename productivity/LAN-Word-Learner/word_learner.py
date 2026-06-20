#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 局域网单词联机学习器 (LAN Word Learner)

功能：
- 局域网内多人英语单词联机学习与测试工具
- 支持服务端和客户端模式
- 趣味测试与记忆英语单词

使用方法：
- 服务端：直接运行，自动获取本机IP
- 客户端：运行后输入服务端IP地址连接

注意事项：
- 需要 tkinter 库（Python 自带）
- 需要 words.txt 单词文件（已内置默认单词）
- 服务端和客户端需要在同一局域网内

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import socket
import threading
import random
import time
import pathlib
import sys
import os
import tkinter as tk
from tkinter import messagebox

# --- Configuration ---
PORT = 12888
HOST_IP = socket.gethostbyname(socket.gethostname())  # 自动获取本机IP
GAME_DURATION_SECONDS = 180

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

WORDS_FILE = pathlib.Path(resource_path('words.txt'))

def load_words():
    if not WORDS_FILE.exists():
        return [('苹果', 'apple'), ('香蕉', 'banana'), ('猫', 'cat')]
    try:
        loaded_words = []
        with WORDS_FILE.open(encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(' ', 3)
                if len(parts) == 4:
                    english_word = parts[1].strip()
                    chinese_translation = parts[3].strip()
                    loaded_words.append((chinese_translation, english_word))
        return loaded_words if loaded_words else [('苹果', 'apple'), ('香蕉', 'banana'), ('猫', 'cat')]
    except Exception:
        return [('苹果', 'apple'), ('香蕉', 'banana'), ('猫', 'cat')]

WORDS = load_words()

class QuizGameApp:
    def __init__(self, master):
        self.master = master
        master.title("局域网单词联机学习器")

        # Game State Variables
        self.role = None
        self.socket = None
        self.opponent_addr = None
        self.current_word = None 
        self.question_type = None
        
        self.local_score = 0 
        self.opponent_score = 0 
        self.final_scores = {'host': None, 'guest': None} 
        
        self.local_ready_to_restart = False
        self.opponent_ready_to_restart = False
        
        self.game_running = threading.Event()
        self.game_timer_id = None 
        self.time_left = GAME_DURATION_SECONDS
        self.is_game_active = False 

        # --- Initial Role Selection Frame ---
        self.role_frame = tk.Frame(master, padx=20, pady=20)
        self.role_frame.pack()

        tk.Label(self.role_frame, text="欢迎使用局域网单词学习器！", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(self.role_frame, text="请选择角色模式：", font=('Arial', 14)).pack(pady=10)
        
        tk.Button(self.role_frame, text="我是服务端 (出题/计时)", command=self.setup_host, width=25, height=2).pack(pady=8)
        tk.Button(self.role_frame, text="我是客户端 (连接参与)", command=self.show_join_dialog, width=25, height=2).pack(pady=8)
        
        # 初始化时居中
        self.center_window(self.master)

    def center_window(self, win):
        """完全保留您的居中逻辑"""
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'+{x}+{y}')

    def update_scoreboard(self):
        score_text = f"我的得分: {self.local_score} | 对方得分: {self.opponent_score}"
        self.score_label.config(text=score_text)
        
    def log(self, sender, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{sender}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def setup_host(self):
        self.role = 'host'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(('', PORT))
            self.socket.settimeout(0.1)
            
            self.role_frame.destroy()
            self.setup_game_gui() # 内部已含 center_window
            
            self.start_host_thread()
            self.status_label.config(text=f"服务端已启动。IP: {socket.gethostbyname(socket.gethostname())}\n等待另一端连接...")
        except Exception as e:
            messagebox.showerror("错误", f"服务端启动失败: {e}")

    def show_join_dialog(self):
        self.join_dialog = tk.Toplevel(self.master)
        self.join_dialog.title("连接服务端")
        self.center_window(self.join_dialog)
        self.join_dialog.transient(self.master)
        self.join_dialog.grab_set()

        tk.Label(self.join_dialog, text="请输入服务端电脑名或IP地址：").pack(padx=20, pady=10)
        self.host_entry = tk.Entry(self.join_dialog, width=30)
        self.host_entry.insert(0, HOST_IP)
        self.host_entry.pack(padx=20, pady=5)
        tk.Button(self.join_dialog, text="连接", command=self.setup_guest).pack(pady=10)

    def setup_guest(self):
        host_name = self.host_entry.get().strip()
        self.join_dialog.destroy()
        try:
            host_ip = socket.gethostbyname(host_name)
        except:
            messagebox.showerror("错误", "无法解析主机名！")
            return

        self.role = 'guest'
        self.opponent_addr = (host_ip, PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.1)

        self.role_frame.destroy()
        self.setup_game_gui()
        
        self.start_guest_thread()
        self.status_label.config(text=f"正在连接服务端 {host_name}...")
        self.socket.sendto(b'PING', self.opponent_addr)

    def setup_game_gui(self):
        self.game_frame = tk.Frame(self.master, padx=20, pady=20)
        self.game_frame.pack(expand=True, anchor='center') 
        
        self.timer_label = tk.Label(self.game_frame, text=f"等待另一端连接...", font=('Arial', 14), fg='red')
        self.timer_label.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(self.game_frame, text="测试准备中...", fg='gray')
        self.status_label.pack(fill='x', pady=5)

        self.score_label = tk.Label(self.game_frame, text="我的得分: 0 | 对方得分: 0", font=('Arial', 16, 'bold'))
        self.score_label.pack(pady=10)
        
        self.type_label = tk.Label(self.game_frame, text="等待题目...", font=('Arial', 12), fg='darkgreen')
        self.type_label.pack(pady=(10, 0))
        
        self.question_text = tk.StringVar(value="等待题目...")
        tk.Label(self.game_frame, textvariable=self.question_text, font=('Arial', 28, 'bold')).pack(pady=10)
        
        self.input_prompt = tk.StringVar(value="等待指示...")
        tk.Label(self.game_frame, textvariable=self.input_prompt, font=('Arial', 12)).pack(pady=(10, 0))
        
        self.answer_entry = tk.Entry(self.game_frame, width=30, font=('Arial', 18))
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind('<Return>', lambda event: self.submit_answer())
        
        self.submit_button = tk.Button(self.game_frame, text="提交答案", command=self.submit_answer, state=tk.DISABLED, bg='lightblue')
        self.submit_button.pack(pady=10)
        
        self.restart_button = tk.Button(self.game_frame, text="请求重新开始", command=self.request_restart, state=tk.DISABLED, bg='lightgreen')
        self.restart_button.pack(pady=10)
        
        tk.Label(self.game_frame, text="--- 测试记录 ---").pack()
        self.log_text = tk.Text(self.game_frame, height=5, width=50, state=tk.DISABLED)
        self.log_text.pack(pady=10)
        
        # 布局切换后重新居中
        self.center_window(self.master)

    def reset_game_state(self):
        self.local_score = 0
        self.opponent_score = 0
        self.final_scores = {'host': None, 'guest': None}
        self.local_ready_to_restart = False
        self.opponent_ready_to_restart = False
        self.is_game_active = False 
        self.update_scoreboard()
        self.question_text.set("新测试即将开始...")
        self.timer_label.config(fg='red', text="等待对方确认...")
        self.restart_button.config(state=tk.DISABLED, text="请求重新开始") 
        self.submit_button.config(state=tk.DISABLED)

    def start_local_game(self): 
        if self.is_game_active: return
        self.is_game_active = True
        self.time_left = GAME_DURATION_SECONDS
        self.timer_label.config(text=f"剩余时间: {self.time_left}秒")
        self.update_timer()
        self.next_question()

    def request_restart(self):
        if not self.opponent_addr: return
        if self.local_ready_to_restart: return
        self.local_ready_to_restart = True
        self.restart_button.config(state=tk.DISABLED, text="等待对方确认...")
        self.socket.sendto(b'RESTART_READY', self.opponent_addr)
        self.check_all_ready_for_restart()

    def check_all_ready_for_restart(self):
        if self.local_ready_to_restart and self.opponent_ready_to_restart:
            if self.role == 'host':
                self.reset_game_state() 
                self.socket.sendto(b'START_GAME', self.opponent_addr)
                self.master.after(100, self.start_local_game) 
            else: 
                self.reset_game_state()

    def update_timer(self):
        if not self.is_game_active: return
        if self.time_left >= 0:
            self.timer_label.config(text=f"剩余时间: {self.time_left}秒")
            self.time_left -= 1
            self.game_timer_id = self.master.after(1000, self.update_timer)
        else:
            self.end_game_and_show_result()

    def end_game_and_show_result(self):
        if not self.is_game_active: return
        self.is_game_active = False
        self.submit_button.config(state=tk.DISABLED)
        self.question_text.set("测试结束，等待结果...")
        self.socket.sendto(f'FINAL_SCORE:{self.local_score}'.encode('utf8'), self.opponent_addr)
        my_role_key = 'host' if self.role == 'host' else 'guest'
        self.final_scores[my_role_key] = self.local_score
        if self.role == 'host': self.socket.sendto(b'END', self.opponent_addr)
        self.check_final_result()

    def check_final_result(self):
        host_score = self.final_scores['host']
        guest_score = self.final_scores['guest']
        if host_score is not None and guest_score is not None:
            self.display_final_result(host_score, guest_score)
            
    def display_final_result(self, host_score, guest_score):
        my_score = host_score if self.role == 'host' else guest_score
        opp_score = guest_score if self.role == 'host' else host_score
        
        if my_score > opp_score:
            msg, title = f"测试完成！\n我的得分: {my_score} 分 | 对方得分: {opp_score} 分\n您的正确率更高！", "测试结果"
        elif opp_score > my_score:
            msg, title = f"测试完成。\n我的得分: {my_score} 分 | 对方得分: {opp_score} 分\n对方的正确率更高。", "测试结果"
        else:
            msg, title = f"测试完成！\n双方得分相同，均为: {my_score}", "测试结果"
        
        messagebox.showinfo(title, msg)
        self.restart_button.config(state=tk.NORMAL, text="请求重新开始")

    def next_question(self):
        if not self.is_game_active: return
        self.current_word = random.choice(WORDS)
        self.question_type = random.choice(['中文 => 英文', '英文 => 中文'])
        chinese, english = self.current_word
        
        if self.question_type == '中文 => 英文':
            display_q, prompt = chinese, "请回答对应的【英文】"
        else:
            display_q, prompt = english, "请回答对应的【中文】"
            
        self.question_text.set(display_q)
        self.type_label.config(text=f"【出题方式：{self.question_type}】")
        self.input_prompt.set(prompt)
        self.submit_button.config(state=tk.NORMAL)
        self.answer_entry.focus_set()

    def submit_answer(self):
        """【修复】提交时实时同步分数"""
        if not self.current_word or not self.is_game_active: return
        ans = self.answer_entry.get().strip().lower()
        self.answer_entry.delete(0, tk.END)
        if not ans: return
        
        chinese, english = self.current_word
        correct = english.lower() if self.question_type == '中文 => 英文' else chinese.lower()
        
        if ans == correct:
            self.local_score += 1
            self.update_scoreboard()
            # 答对后立即通知对方
            if self.opponent_addr:
                self.socket.sendto(f'SCORE_UPDATE:{self.local_score}'.encode('utf8'), self.opponent_addr)
            self.log("你", "【答对了！】")
        else:
            self.log("你", f"【答错了！】正确答案：{correct}")
                
        self.master.after(500, self.next_question)

    def start_host_thread(self):
        self.game_running.set()
        threading.Thread(target=self.host_recv_loop, daemon=True).start()

    def start_guest_thread(self):
        self.game_running.set()
        threading.Thread(target=self.guest_recv_loop, daemon=True).start()

    def host_recv_loop(self):
        while self.game_running.is_set():
            try:
                data, addr = self.socket.recvfrom(1024)
                msg = data.decode('utf8')
                if msg == 'PING':
                    self.opponent_addr = addr
                    self.socket.sendto(b'WELCOME', addr)
                    self.master.after(0, lambda: self.status_label.config(text=f"已连接客户端"))
                    self.socket.sendto(b'START_GAME', self.opponent_addr)
                    self.master.after(100, self.start_local_game) 
                elif msg.startswith('SCORE_UPDATE:'): # 实时同步
                    self.opponent_score = int(msg.split(':')[1])
                    self.master.after(0, self.update_scoreboard)
                elif msg.startswith('FINAL_SCORE:'):
                    self.final_scores['guest'] = int(msg.split(':')[1])
                    self.opponent_score = self.final_scores['guest']
                    self.master.after(0, self.update_scoreboard)
                    self.master.after(0, self.check_final_result)
                elif msg == 'RESTART_READY':
                    self.opponent_ready_to_restart = True
                    self.master.after(0, self.check_all_ready_for_restart)
            except: continue

    def guest_recv_loop(self):
        while self.game_running.is_set():
            try:
                data, addr = self.socket.recvfrom(1024)
                msg = data.decode('utf8')
                if msg == 'WELCOME':
                    self.opponent_addr = addr # 绑定地址
                    self.master.after(0, lambda: self.status_label.config(text="成功连接服务端，等待开始..."))
                elif msg == 'START_GAME':
                    self.master.after(0, self.reset_game_state) 
                    self.master.after(100, self.start_local_game) 
                elif msg.startswith('SCORE_UPDATE:'): # 实时同步
                    self.opponent_score = int(msg.split(':')[1])
                    self.master.after(0, self.update_scoreboard)
                elif msg == 'END': 
                    self.master.after(0, self.end_game_and_show_result)
                elif msg.startswith('FINAL_SCORE:'):
                    self.final_scores['host'] = int(msg.split(':')[1])
                    self.opponent_score = self.final_scores['host']
                    self.master.after(0, self.update_scoreboard)
                    self.master.after(0, self.check_final_result)
                elif msg == 'RESTART_READY':
                    self.opponent_ready_to_restart = True
                    self.master.after(0, self.check_all_ready_for_restart)
            except: continue

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.game_running.clear()
            if self.socket: self.socket.close()
            self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = QuizGameApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()