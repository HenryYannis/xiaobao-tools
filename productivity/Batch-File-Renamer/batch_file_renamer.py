#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件重命名工具 (Batch File Renamer)

功能：
- 支持多种重命名模式：添加前缀/后缀、替换字符、序号重命名、日期重命名
- 支持预览重命名结果
- 支持撤销操作（基于重命名后的实际路径）
- 支持正则表达式匹配

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class BatchFileRenamer:
    """批量文件重命名器"""

    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具")
        self.root.resizable(False, False)

        # 文件列表
        self.files = []
        self.original_names = []
        self.preview_names = []

        # 撤销数据：存储 {旧路径: 新路径} 的映射
        self.undo_data = None

        # 创建界面
        self.create_widgets()

        # 窗口居中
        self.root.update_idletasks()
        w, h = 900, 700
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 目录选择
        dir_frame = ttk.LabelFrame(main_frame, text="目录选择", padding="5")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(dir_frame, text="选择目录", command=self.select_directory).grid(row=0, column=0, padx=(0, 10))
        self.dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # 重命名模式
        mode_frame = ttk.LabelFrame(main_frame, text="重命名模式", padding="5")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.mode_var = tk.StringVar(value="prefix")
        modes = [
            ("添加前缀", "prefix"),
            ("添加后缀", "suffix"),
            ("替换字符", "replace"),
            ("序号重命名", "sequence"),
            ("日期重命名", "date"),
            ("正则替换", "regex")
        ]

        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var,
                           value=value, command=self.update_mode_options).grid(row=0, column=i, padx=5)

        # 模式选项
        options_frame = ttk.LabelFrame(main_frame, text="重命名选项", padding="5")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 前缀/后缀选项
        self.prefix_frame = ttk.Frame(options_frame)
        ttk.Label(self.prefix_frame, text="前缀/后缀:").grid(row=0, column=0, padx=(0, 5))
        self.prefix_var = tk.StringVar(value="new_")
        ttk.Entry(self.prefix_frame, textvariable=self.prefix_var, width=30).grid(row=0, column=1)

        # 替换选项
        self.replace_frame = ttk.Frame(options_frame)
        ttk.Label(self.replace_frame, text="查找:").grid(row=0, column=0, padx=(0, 5))
        self.find_var = tk.StringVar()
        ttk.Entry(self.replace_frame, textvariable=self.find_var, width=20).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(self.replace_frame, text="替换为:").grid(row=0, column=2, padx=(0, 5))
        self.replace_var = tk.StringVar()
        ttk.Entry(self.replace_frame, textvariable=self.replace_var, width=20).grid(row=0, column=3)

        # 序号选项
        self.sequence_frame = ttk.Frame(options_frame)
        ttk.Label(self.sequence_frame, text="起始序号:").grid(row=0, column=0, padx=(0, 5))
        self.start_var = tk.StringVar(value="1")
        ttk.Entry(self.sequence_frame, textvariable=self.start_var, width=10).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(self.sequence_frame, text="位数:").grid(row=0, column=2, padx=(0, 5))
        self.digits_var = tk.StringVar(value="3")
        ttk.Entry(self.sequence_frame, textvariable=self.digits_var, width=10).grid(row=0, column=3, padx=(0, 10))
        ttk.Label(self.sequence_frame, text="分隔符:").grid(row=0, column=4, padx=(0, 5))
        self.separator_var = tk.StringVar(value="_")
        ttk.Entry(self.sequence_frame, textvariable=self.separator_var, width=10).grid(row=0, column=5)

        # 日期选项
        self.date_frame = ttk.Frame(options_frame)
        ttk.Label(self.date_frame, text="日期格式:").grid(row=0, column=0, padx=(0, 5))
        self.date_format_var = tk.StringVar(value="%Y%m%d_%H%M%S")
        ttk.Entry(self.date_frame, textvariable=self.date_format_var, width=20).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(self.date_frame, text="位置:").grid(row=0, column=2, padx=(0, 5))
        self.date_pos_var = tk.StringVar(value="prefix")
        ttk.Combobox(self.date_frame, textvariable=self.date_pos_var, values=["prefix", "suffix"],
                     state="readonly", width=10).grid(row=0, column=3)

        # 正则选项
        self.regex_frame = ttk.Frame(options_frame)
        ttk.Label(self.regex_frame, text="正则表达式:").grid(row=0, column=0, padx=(0, 5))
        self.regex_pattern_var = tk.StringVar()
        ttk.Entry(self.regex_frame, textvariable=self.regex_pattern_var, width=30).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(self.regex_frame, text="替换为:").grid(row=0, column=2, padx=(0, 5))
        self.regex_replace_var = tk.StringVar()
        ttk.Entry(self.regex_frame, textvariable=self.regex_replace_var, width=30).grid(row=0, column=3)

        # 文件过滤
        filter_frame = ttk.LabelFrame(main_frame, text="文件过滤", padding="5")
        filter_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="文件扩展名 (逗号分隔):").grid(row=0, column=0, padx=(0, 5))
        self.ext_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.ext_var, width=30).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(filter_frame, text="包含关键词:").grid(row=0, column=2, padx=(0, 5))
        self.keyword_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.keyword_var, width=20).grid(row=0, column=3)

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(btn_frame, text="预览重命名", command=self.preview_rename).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="执行重命名", command=self.execute_rename).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="撤销上次", command=self.undo_rename).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_list).grid(row=0, column=3, padx=5)

        # 文件列表
        list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="5")
        list_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建Treeview
        columns = ("original", "new")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.tree.heading("original", text="原文件名")
        self.tree.heading("new", text="新文件名")
        self.tree.column("original", width=350)
        self.tree.column("new", width=350)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 初始化显示模式选项
        self.update_mode_options()

    def update_mode_options(self):
        """更新模式选项显示"""
        for frame in [self.prefix_frame, self.replace_frame, self.sequence_frame,
                      self.date_frame, self.regex_frame]:
            frame.grid_forget()

        mode = self.mode_var.get()
        if mode in ["prefix", "suffix"]:
            self.prefix_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "replace":
            self.replace_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "sequence":
            self.sequence_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "date":
            self.date_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "regex":
            self.regex_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
            self.load_files()

    def load_files(self):
        """加载文件列表"""
        directory = self.dir_var.get()
        if not directory or not os.path.exists(directory):
            return

        self.files = []
        self.original_names = []

        # 获取过滤条件
        extensions = [ext.strip().lower() for ext in self.ext_var.get().split(",") if ext.strip()]
        keyword = self.keyword_var.get().strip().lower()

        # 遍历目录
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue

            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue

            if keyword and keyword not in filename.lower():
                continue

            self.files.append(filepath)
            self.original_names.append(filename)

        # 更新显示
        self.update_file_list()
        self.status_var.set(f"已加载 {len(self.files)} 个文件")

    def update_file_list(self):
        """更新文件列表显示"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for original, new in zip(self.original_names, self.preview_names):
            self.tree.insert("", tk.END, values=(original, new))

    def preview_rename(self):
        """预览重命名结果"""
        if not self.files:
            messagebox.showwarning("警告", "请先选择目录并加载文件")
            return

        self.preview_names = []
        mode = self.mode_var.get()

        for i, filename in enumerate(self.original_names):
            name, ext = os.path.splitext(filename)

            if mode == "prefix":
                new_name = self.prefix_var.get() + filename
            elif mode == "suffix":
                new_name = name + self.prefix_var.get() + ext
            elif mode == "replace":
                new_name = filename.replace(self.find_var.get(), self.replace_var.get())
            elif mode == "sequence":
                start = int(self.start_var.get())
                digits = int(self.digits_var.get())
                separator = self.separator_var.get()
                seq_num = str(start + i).zfill(digits)
                new_name = f"{seq_num}{separator}{filename}"
            elif mode == "date":
                date_str = datetime.now().strftime(self.date_format_var.get())
                if self.date_pos_var.get() == "prefix":
                    new_name = f"{date_str}_{filename}"
                else:
                    new_name = f"{name}_{date_str}{ext}"
            elif mode == "regex":
                try:
                    new_name = re.sub(self.regex_pattern_var.get(), self.regex_replace_var.get(), filename)
                except re.error as e:
                    logging.warning(f"正则表达式错误: {e}")
                    new_name = filename
            else:
                new_name = filename

            self.preview_names.append(new_name)

        self.update_file_list()
        self.status_var.set(f"预览完成，共 {len(self.files)} 个文件")

    def execute_rename(self):
        """执行重命名"""
        if not self.files or not self.preview_names:
            messagebox.showwarning("警告", "请先预览重命名结果")
            return

        if not messagebox.askyesno("确认", f"确定要重命名 {len(self.files)} 个文件吗？"):
            return

        # 存储重命名映射：{新路径: 原路径}，用于撤销
        rename_map = {}

        # 执行重命名
        success_count = 0
        for old_path, new_name in zip(self.files, self.preview_names):
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)

            try:
                os.rename(old_path, new_path)
                rename_map[new_path] = old_path  # 新路径 -> 原路径
                success_count += 1
            except OSError as e:
                logging.error(f"重命名失败: {e}")
                messagebox.showerror("错误", f"重命名失败: {e}")

        # 保存撤销数据
        self.undo_data = rename_map

        # 重新加载文件列表
        self.load_files()
        self.preview_names = []
        self.status_var.set(f"重命名完成，成功 {success_count} 个文件")
        messagebox.showinfo("完成", f"重命名完成，成功 {success_count} 个文件")

    def undo_rename(self):
        """撤销重命名 — 使用重命名映射中的新路径恢复原名"""
        if not self.undo_data:
            messagebox.showwarning("警告", "没有可撤销的操作")
            return

        if not messagebox.askyesno("确认", "确定要撤销上次重命名操作吗？"):
            return

        # 执行撤销：从新路径恢复到原路径
        success_count = 0
        for new_path, original_path in self.undo_data.items():
            try:
                os.rename(new_path, original_path)
                success_count += 1
            except OSError as e:
                logging.error(f"撤销失败: {e}")
                messagebox.showerror("错误", f"撤销失败: {e}")

        # 清除撤销数据
        self.undo_data = None

        # 重新加载文件列表
        self.load_files()
        self.status_var.set(f"撤销完成，恢复 {success_count} 个文件")
        messagebox.showinfo("完成", f"撤销完成，恢复 {success_count} 个文件")

    def clear_list(self):
        """清空列表"""
        self.files = []
        self.original_names = []
        self.preview_names = []
        self.update_file_list()
        self.status_var.set("列表已清空")


if __name__ == "__main__":
    root = tk.Tk()
    app = BatchFileRenamer(root)
    root.mainloop()
