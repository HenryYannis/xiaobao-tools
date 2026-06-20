#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 临时密码生成器 (Temporary Password Generator)

功能：
- 生成高强度随机临时密码
- 支持自定义密码长度（默认 16 位）
- 支持包含大小写字母、数字和符号
- 使用 secrets 模块确保密码学安全

使用方法：
- 直接运行即可生成密码
- 复制生成的密码使用

注意事项：
- 需要 tkinter 库（Python 自带）
- 生成的密码仅用于临时用途

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from tkinter import messagebox
import secrets
import string
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class SecurityApp:
    def __init__(self, master):
        self.master = master
        master.title("安全设置")
        master.resizable(False, False)

        # 居中显示内容
        main_frame = tk.Frame(master)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 标题
        title_label = tk.Label(main_frame, text="安全问题设置", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 安全问题提示
        question_label = tk.Label(main_frame, text="请设置安全问题(例如: 您的注册手机号):")
        question_label.pack(pady=(0, 10))

        # 输入框
        self.security_entry = tk.Entry(main_frame, width=30, font=("Arial", 12))
        self.security_entry.pack(pady=(0, 20))
        self.security_entry.focus_set()

        # 确认按钮
        confirm_button = tk.Button(main_frame, text="确认", width=10,
                                   command=self.set_security_question)
        confirm_button.pack()

        # 窗口居中
        master.update_idletasks()
        w, h = 400, 250
        x = (master.winfo_screenwidth() - w) // 2
        y = (master.winfo_screenheight() - h) // 2
        master.geometry(f"{w}x{h}+{x}+{y}")

    def set_security_question(self):
        security_answer = self.security_entry.get().strip()

        # 简单验证输入不为空
        if not security_answer:
            messagebox.showerror("错误", "安全问题不能为空!")
            return

        self.security_answer = security_answer

        # 关闭当前窗口，打开新窗口
        self.master.destroy()
        self.open_new_window()

    def open_new_window(self):
        new_window = tk.Tk()
        new_window.title("密码找回")
        NewPasswordWindow(new_window, self.security_answer)


class NewPasswordWindow:
    # 密码字符集
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SYMBOLS = "!@#$%^&*_-+="

    def __init__(self, master, security_answer):
        self.master = master
        self.security_answer = security_answer
        master.title("忘记密码")
        master.resizable(False, False)

        # 居中显示内容
        main_frame = tk.Frame(master)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 标题
        title_label = tk.Label(main_frame, text="密码找回", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 提示信息
        info_label = tk.Label(main_frame, text="请输入您设置的安全问题答案:")
        info_label.pack(pady=(0, 10))

        # 输入框
        self.answer_entry = tk.Entry(main_frame, width=30, font=("Arial", 12))
        self.answer_entry.pack(pady=(0, 20))
        self.answer_entry.focus_set()

        # 密码长度配置
        len_frame = tk.Frame(main_frame)
        len_frame.pack(pady=(0, 10))
        tk.Label(len_frame, text="密码长度:").pack(side=tk.LEFT, padx=5)
        self.length_var = tk.IntVar(value=16)
        length_spin = tk.Spinbox(len_frame, from_=8, to=64, textvariable=self.length_var, width=5)
        length_spin.pack(side=tk.LEFT, padx=5)

        # 密码选项
        opt_frame = tk.Frame(main_frame)
        opt_frame.pack(pady=(0, 10))

        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        tk.Checkbutton(opt_frame, text="大写字母", variable=self.use_upper).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opt_frame, text="数字", variable=self.use_digits).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(opt_frame, text="符号", variable=self.use_symbols).pack(side=tk.LEFT, padx=5)

        # 按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        # 找回密码按钮
        reset_button = tk.Button(button_frame, text="找回密码", width=12,
                                 command=self.reset_password)
        reset_button.pack(side=tk.LEFT, padx=10)

        # 返回按钮
        back_button = tk.Button(button_frame, text="返回", width=12,
                                command=self.master.destroy)
        back_button.pack(side=tk.LEFT, padx=10)

        # 窗口居中
        master.update_idletasks()
        w, h = 450, 350
        x = (master.winfo_screenwidth() - w) // 2
        y = (master.winfo_screenheight() - h) // 2
        master.geometry(f"{w}x{h}+{x}+{y}")

    def reset_password(self):
        entered_answer = self.answer_entry.get().strip()

        if entered_answer != self.security_answer:
            messagebox.showerror("错误", "安全问题答案不正确!")
            return

        # 生成临时密码
        temp_password = self.generate_temp_password()

        # 显示临时密码
        message = f"您的临时密码已生成:\n\n{temp_password}\n\n"
        message += f"密码长度: {len(temp_password)} 位\n"
        message += "请妥善保管，此密码仅用于临时用途。"
        messagebox.showinfo("临时密码", message)

    def generate_temp_password(self):
        """使用 secrets 模块生成密码学安全的高强度临时密码"""
        length = self.length_var.get()

        # 构建字符集（始终包含小写字母）
        alphabet = self.LOWERCASE
        required_chars = [secrets.choice(self.LOWERCASE)]

        if self.use_upper.get():
            alphabet += self.UPPERCASE
            required_chars.append(secrets.choice(self.UPPERCASE))
        if self.use_digits.get():
            alphabet += self.DIGITS
            required_chars.append(secrets.choice(self.DIGITS))
        if self.use_symbols.get():
            alphabet += self.SYMBOLS
            required_chars.append(secrets.choice(self.SYMBOLS))

        # 确保密码长度至少为 8
        length = max(length, 8)

        # 生成密码：先用必选字符保证多样性，再用 secrets 填充剩余位
        remaining_length = length - len(required_chars)
        password_chars = required_chars + [secrets.choice(alphabet) for _ in range(remaining_length)]

        # 安全打乱顺序
        secrets.SystemRandom().shuffle(password_chars)

        return ''.join(password_chars)


if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityApp(root)
    root.mainloop()
