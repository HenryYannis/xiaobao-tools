#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel批量处理工具 (Excel Batch Processor)

功能：
- 批量读取多个Excel文件
- 合并多个Excel文件
- 提取指定列数据
- 数据筛选和过滤
- 导出处理结果

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import sys
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class ExcelBatchProcessor:
    """Excel批量处理器"""

    def __init__(self, root):
        self.root = root
        self.root.title("Excel批量处理工具")
        self.root.geometry("1000x700")

        # 数据存储
        self.files = []
        self.dataframes = []
        self.merged_data = None

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 文件选择
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(file_frame, text="添加文件", command=self.add_files).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="添加目录", command=self.add_directory).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(file_frame, text="清空列表", command=self.clear_files).grid(row=0, column=2, padx=(0, 5))

        self.file_count_var = tk.StringVar(value="已选择 0 个文件")
        ttk.Label(file_frame, textvariable=self.file_count_var).grid(row=0, column=3, padx=(10, 0))

        # 文件列表
        file_list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="5")
        file_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.file_listbox = tk.Listbox(file_list_frame, height=6, selectmode=tk.EXTENDED)
        file_scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 处理选项
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="5")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 处理模式
        self.mode_var = tk.StringVar(value="merge")
        modes = [
            ("合并所有文件", "merge"),
            ("提取指定列", "extract"),
            ("数据筛选", "filter"),
            ("统计分析", "stats")
        ]

        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(options_frame, text=text, variable=self.mode_var,
                           value=value, command=self.update_options).grid(row=0, column=i, padx=5)

        # 选项详情
        self.options_frame = ttk.Frame(options_frame)
        self.options_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))

        # 合并选项
        self.merge_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.merge_frame, text="合并方式:").grid(row=0, column=0, padx=(0, 5))
        self.merge_method_var = tk.StringVar(value="vertical")
        ttk.Combobox(self.merge_frame, textvariable=self.merge_method_var,
                     values=["vertical", "horizontal"], state="readonly", width=15).grid(row=0, column=1)

        # 提取选项
        self.extract_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.extract_frame, text="列名 (逗号分隔):").grid(row=0, column=0, padx=(0, 5))
        self.columns_var = tk.StringVar()
        ttk.Entry(self.extract_frame, textvariable=self.columns_var, width=40).grid(row=0, column=1)

        # 筛选选项
        self.filter_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.filter_frame, text="筛选列:").grid(row=0, column=0, padx=(0, 5))
        self.filter_col_var = tk.StringVar()
        ttk.Entry(self.filter_frame, textvariable=self.filter_col_var, width=15).grid(row=0, column=1, padx=(0, 10))
        ttk.Label(self.filter_frame, text="条件:").grid(row=0, column=2, padx=(0, 5))
        self.filter_op_var = tk.StringVar(value="==")
        ttk.Combobox(self.filter_frame, textvariable=self.filter_op_var,
                     values=["==", "!=", ">", "<", ">=", "<=", "contains"], state="readonly", width=10).grid(row=0, column=3, padx=(0, 10))
        ttk.Label(self.filter_frame, text="值:").grid(row=0, column=4, padx=(0, 5))
        self.filter_val_var = tk.StringVar()
        ttk.Entry(self.filter_frame, textvariable=self.filter_val_var, width=15).grid(row=0, column=5)

        # 统计选项
        self.stats_frame = ttk.Frame(self.options_frame)
        ttk.Label(self.stats_frame, text="统计列 (逗号分隔，留空则统计所有数值列):").grid(row=0, column=0, padx=(0, 5))
        self.stats_cols_var = tk.StringVar()
        ttk.Entry(self.stats_frame, textvariable=self.stats_cols_var, width=40).grid(row=0, column=1)

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(btn_frame, text="预览数据", command=self.preview_data).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="执行处理", command=self.process_data).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="导出结果", command=self.export_data).grid(row=0, column=2, padx=5)

        # 数据预览
        preview_frame = ttk.LabelFrame(main_frame, text="数据预览", padding="5")
        preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建Treeview
        self.tree = ttk.Treeview(preview_frame, show="headings", height=15)
        preview_scrollbar_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        preview_scrollbar_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=preview_scrollbar_y.set, xscrollcommand=preview_scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        preview_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        file_list_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # 初始化显示选项
        self.update_options()

    def update_options(self):
        """更新选项显示"""
        # 隐藏所有选项框架
        for frame in [self.merge_frame, self.extract_frame, self.filter_frame, self.stats_frame]:
            frame.grid_forget()

        # 显示当前模式的选项
        mode = self.mode_var.get()
        if mode == "merge":
            self.merge_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "extract":
            self.extract_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "filter":
            self.filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "stats":
            self.stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )

        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))

        self.file_count_var.set(f"已选择 {len(self.files)} 个文件")

    def add_directory(self):
        """添加目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if not directory:
            return

        # 遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    filepath = os.path.join(root, file)
                    if filepath not in self.files:
                        self.files.append(filepath)
                        self.file_listbox.insert(tk.END, file)

        self.file_count_var.set(f"已选择 {len(self.files)} 个文件")

    def clear_files(self):
        """清空文件列表"""
        self.files = []
        self.file_listbox.delete(0, tk.END)
        self.file_count_var.set("已选择 0 个文件")

    def load_files(self):
        """加载文件"""
        self.dataframes = []
        self.status_var.set("正在加载文件...")

        for file in self.files:
            try:
                df = pd.read_excel(file)
                self.dataframes.append(df)
            except (OSError, ValueError) as e:
                messagebox.showerror("错误", f"加载文件失败: {e}")
                return False

        self.status_var.set(f"已加载 {len(self.dataframes)} 个文件")
        return True

    def preview_data(self):
        """预览数据"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 加载文件
        if not self.load_files():
            return

        # 清空预览
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 显示第一个文件的数据
        if self.dataframes:
            df = self.dataframes[0]
            self.tree["columns"] = list(df.columns)

            for col in df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)

            # 显示前100行
            for i, row in df.head(100).iterrows():
                self.tree.insert("", tk.END, values=list(row))

            self.status_var.set(f"预览第一个文件，共 {len(df)} 行")

    def process_data(self):
        """处理数据"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 加载文件
        if not self.load_files():
            return

        mode = self.mode_var.get()

        try:
            if mode == "merge":
                self.merge_data = self.merge_dataframes()
            elif mode == "extract":
                self.merge_data = self.extract_columns()
            elif mode == "filter":
                self.merge_data = self.filter_data()
            elif mode == "stats":
                self.merge_data = self.calculate_stats()

            # 显示结果
            self.display_result()
            self.status_var.set("处理完成")

        except (ValueError, KeyError) as e:
            messagebox.showerror("错误", f"处理失败: {e}")

    def merge_dataframes(self):
        """合并数据框"""
        if not self.dataframes:
            return None

        method = self.merge_method_var.get()

        if method == "vertical":
            # 垂直合并
            return pd.concat(self.dataframes, ignore_index=True)
        else:
            # 水平合并
            return pd.concat(self.dataframes, axis=1)

    def extract_columns(self):
        """提取列"""
        columns_str = self.columns_var.get()
        if not columns_str:
            messagebox.showwarning("警告", "请指定要提取的列名")
            return None

        columns = [col.strip() for col in columns_str.split(",")]

        # 合并所有数据
        merged = pd.concat(self.dataframes, ignore_index=True)

        # 检查列是否存在
        missing_cols = [col for col in columns if col not in merged.columns]
        if missing_cols:
            messagebox.showwarning("警告", f"以下列不存在: {', '.join(missing_cols)}")
            return None

        return merged[columns]

    def filter_data(self):
        """筛选数据"""
        col = self.filter_col_var.get()
        op = self.filter_op_var.get()
        val = self.filter_val_var.get()

        if not col or not val:
            messagebox.showwarning("警告", "请指定筛选条件")
            return None

        # 合并所有数据
        merged = pd.concat(self.dataframes, ignore_index=True)

        # 检查列是否存在
        if col not in merged.columns:
            messagebox.showwarning("警告", f"列 '{col}' 不存在")
            return None

        # 应用筛选
        try:
            if op == "==":
                return merged[merged[col] == val]
            elif op == "!=":
                return merged[merged[col] != val]
            elif op == ">":
                return merged[merged[col] > float(val)]
            elif op == "<":
                return merged[merged[col] < float(val)]
            elif op == ">=":
                return merged[merged[col] >= float(val)]
            elif op == "<=":
                return merged[merged[col] <= float(val)]
            elif op == "contains":
                return merged[merged[col].astype(str).str.contains(val, na=False)]
        except (ValueError, KeyError) as e:
            messagebox.showerror("错误", f"筛选失败: {e}")
            return None

    def calculate_stats(self):
        """计算统计信息"""
        # 合并所有数据
        merged = pd.concat(self.dataframes, ignore_index=True)

        # 获取统计列
        cols_str = self.stats_cols_var.get()
        if cols_str:
            cols = [col.strip() for col in cols_str.split(",")]
            # 检查列是否存在
            missing_cols = [col for col in cols if col not in merged.columns]
            if missing_cols:
                messagebox.showwarning("警告", f"以下列不存在: {', '.join(missing_cols)}")
                return None
        else:
            # 使用所有数值列
            cols = merged.select_dtypes(include=['number']).columns.tolist()

        if not cols:
            messagebox.showwarning("警告", "没有找到数值列")
            return None

        # 计算统计信息
        stats = merged[cols].describe()
        return stats

    def display_result(self):
        """显示结果"""
        if self.merge_data is None:
            return

        # 清空预览
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 设置列
        self.tree["columns"] = list(self.merge_data.columns)

        for col in self.merge_data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # 显示数据
        for i, row in self.merge_data.head(100).iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def export_data(self):
        """导出数据"""
        if self.merge_data is None:
            messagebox.showwarning("警告", "没有可导出的数据")
            return

        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="导出数据",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("CSV文件", "*.csv")]
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                self.merge_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                self.merge_data.to_excel(file_path, index=False)

            self.status_var.set(f"数据已导出到: {file_path}")
            messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")

        except (OSError, ValueError) as e:
            messagebox.showerror("错误", f"导出失败: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelBatchProcessor(root)
    root.mainloop()
