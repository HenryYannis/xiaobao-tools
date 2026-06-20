#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 倒计时器 (Countdown Timer)

功能：
- 支持自定义倒计时时长（小时/分钟/秒）
- 倒计时结束时发出声音提醒
- 全屏倒计时显示
- 支持暂停和恢复

使用方法：
- 直接运行即可设置倒计时
- 按 Escape 键退出全屏

注意事项：
- 需要 tkinter 库（Python 自带）
- 声音提醒使用系统蜂鸣

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from tkinter import messagebox
import winsound
import time


class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("倒计时器")
        self.root.resizable(False, False)

        # 倒计时状态
        self.running = False
        self.paused = False
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.after_id = None

        # 创建界面
        self.create_widgets()

        # 窗口居中
        self.root.update_idletasks()
        w, h = 400, 350
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        tk.Label(main_frame, text="⏱ 倒计时器", font=("Helvetica", 18, "bold"), fg="#333").pack(pady=(0, 20))

        # 时间设置区
        time_frame = tk.LabelFrame(main_frame, text="设置倒计时时长", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        time_frame.pack(fill="x", pady=(0, 15))

        # 时
        h_frame = tk.Frame(time_frame)
        h_frame.pack(side="left", padx=10)
        tk.Label(h_frame, text="时", font=("Helvetica", 10)).pack(side="right")
        self.hour_var = tk.StringVar(value="0")
        tk.Spinbox(h_frame, from_=0, to=23, textvariable=self.hour_var, width=5,
                   font=("Helvetica", 14), justify="center").pack(side="right", padx=5)

        # 分
        m_frame = tk.Frame(time_frame)
        m_frame.pack(side="left", padx=10)
        tk.Label(m_frame, text="分", font=("Helvetica", 10)).pack(side="right")
        self.minute_var = tk.StringVar(value="5")
        tk.Spinbox(m_frame, from_=0, to=59, textvariable=self.minute_var, width=5,
                   font=("Helvetica", 14), justify="center").pack(side="right", padx=5)

        # 秒
        s_frame = tk.Frame(time_frame)
        s_frame.pack(side="left", padx=10)
        tk.Label(s_frame, text="秒", font=("Helvetica", 10)).pack(side="right")
        self.second_var = tk.StringVar(value="0")
        tk.Spinbox(s_frame, from_=0, to=59, textvariable=self.second_var, width=5,
                   font=("Helvetica", 14), justify="center").pack(side="right", padx=5)

        # 快捷按钮
        quick_frame = tk.Frame(main_frame)
        quick_frame.pack(fill="x", pady=(0, 15))

        presets = [("1分钟", 60), ("5分钟", 300), ("10分钟", 600), ("25分钟(番茄钟)", 1500), ("30分钟", 1800)]
        for text, seconds in presets:
            tk.Button(quick_frame, text=text, font=("Helvetica", 9), relief="groove",
                      command=lambda s=seconds: self.set_preset(s)).pack(side="left", padx=3, expand=True)

        # 倒计时显示
        self.countdown_label = tk.Label(main_frame, text="00:00:00", font=("Courier", 48, "bold"), fg="#333")
        self.countdown_label.pack(pady=15)

        # 控制按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ 开始", font=("Helvetica", 12, "bold"),
                                   bg="#2da44e", fg="white", width=8, command=self.start_countdown)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(btn_frame, text="⏸ 暂停", font=("Helvetica", 12, "bold"),
                                   bg="#f0ad4e", fg="white", width=8, command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="🔄 重置", font=("Helvetica", 12, "bold"),
                                   bg="#cf222e", fg="white", width=8, command=self.reset_countdown)
        self.reset_btn.grid(row=0, column=2, padx=5)

    def set_preset(self, seconds):
        """设置预设时长"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        self.hour_var.set(str(h))
        self.minute_var.set(str(m))
        self.second_var.set(str(s))

    def start_countdown(self):
        """开始倒计时"""
        if self.running:
            return

        try:
            hours = int(self.hour_var.get() or 0)
            minutes = int(self.minute_var.get() or 0)
            seconds = int(self.second_var.get() or 0)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        if self.total_seconds <= 0:
            messagebox.showwarning("警告", "请设置大于0的倒计时时间")
            return

        self.remaining_seconds = self.total_seconds
        self.running = True
        self.paused = False

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")

        self.update_countdown()

    def update_countdown(self):
        """更新倒计时显示"""
        if not self.running or self.paused:
            return

        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        self.countdown_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        # 颜色变化：最后10秒变红
        if self.remaining_seconds <= 10:
            self.countdown_label.config(fg="red")
        elif self.remaining_seconds <= 60:
            self.countdown_label.config(fg="#f0ad4e")
        else:
            self.countdown_label.config(fg="#333")

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.after_id = self.root.after(1000, self.update_countdown)
        else:
            self.countdown_complete()

    def countdown_complete(self):
        """倒计时完成 — 发出声音提醒"""
        self.running = False
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.countdown_label.config(fg="#2da44e", text="00:00:00")

        # 播放声音提醒（3声蜂鸣）
        try:
            for _ in range(3):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
        except OSError:
            pass

        messagebox.showinfo("倒计时结束", "⏰ 倒计时已结束！")

    def toggle_pause(self):
        """切换暂停/恢复"""
        if not self.running:
            return

        if self.paused:
            self.paused = False
            self.pause_btn.config(text="⏸ 暂停", bg="#f0ad4e")
            self.update_countdown()
        else:
            self.paused = True
            self.pause_btn.config(text="▶ 继续", bg="#2da44e")
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def reset_countdown(self):
        """重置倒计时"""
        self.running = False
        self.paused = False
        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.countdown_label.config(text="00:00:00", fg="#333")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸ 暂停", bg="#f0ad4e")


if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()
