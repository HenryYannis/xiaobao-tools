#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量压缩工具 (Image Batch Compressor)

功能：
- 批量压缩图片
- 支持多种图片格式
- 自定义压缩质量
- 保持原始尺寸或调整尺寸
- 预览压缩效果

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import threading
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class ImageCompressor:
    """图片批量压缩器"""

    def __init__(self, root):
        self.root = root
        self.root.title("图片批量压缩工具")
        self.root.geometry("900x700")

        # 文件列表
        self.files = []
        self.compressed_files = []

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

        # 压缩选项
        options_frame = ttk.LabelFrame(main_frame, text="压缩选项", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 压缩质量
        ttk.Label(options_frame, text="压缩质量:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(options_frame, from_=1, to=100, variable=self.quality_var,
                                  orient=tk.HORIZONTAL, length=200)
        quality_scale.grid(row=0, column=1, padx=(0, 10))
        self.quality_label = ttk.Label(options_frame, text="85%")
        self.quality_label.grid(row=0, column=2, padx=(0, 20))
        quality_scale.configure(command=self.update_quality_label)

        # 调整尺寸
        ttk.Label(options_frame, text="调整尺寸:").grid(row=0, column=3, padx=(0, 5), sticky=tk.W)
        self.resize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, variable=self.resize_var, command=self.toggle_resize).grid(row=0, column=4, padx=(0, 10))

        self.resize_frame = ttk.Frame(options_frame)
        self.resize_frame.grid(row=0, column=5, sticky=tk.W)

        ttk.Label(self.resize_frame, text="宽度:").grid(row=0, column=0, padx=(0, 5))
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(self.resize_frame, textvariable=self.width_var, width=8)
        self.width_entry.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(self.resize_frame, text="高度:").grid(row=0, column=2, padx=(0, 5))
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(self.resize_frame, textvariable=self.height_var, width=8)
        self.height_entry.grid(row=0, column=3)

        # 保持宽高比
        self.keep_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.resize_frame, text="保持宽高比", variable=self.keep_ratio_var).grid(row=0, column=4, padx=(10, 0))

        # 输出格式
        ttk.Label(options_frame, text="输出格式:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(10, 0))
        self.format_var = tk.StringVar(value="original")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, width=15)
        format_combo['values'] = ["original", "JPEG", "PNG", "WEBP"]
        format_combo.grid(row=1, column=1, padx=(0, 20), pady=(10, 0))

        # 输出目录
        ttk.Label(options_frame, text="输出目录:").grid(row=1, column=2, padx=(0, 5), sticky=tk.W, pady=(10, 0))
        self.output_var = tk.StringVar(value="compressed")
        ttk.Entry(options_frame, textvariable=self.output_var, width=20).grid(row=1, column=3, padx=(0, 5), pady=(10, 0))
        ttk.Button(options_frame, text="浏览", command=self.browse_output).grid(row=1, column=4, pady=(10, 0))

        # 文件列表
        list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 创建Treeview
        columns = ("name", "original_size", "compressed_size", "ratio", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.tree.heading("name", text="文件名")
        self.tree.heading("original_size", text="原始大小")
        self.tree.heading("compressed_size", text="压缩后大小")
        self.tree.heading("ratio", text="压缩率")
        self.tree.heading("status", text="状态")
        self.tree.column("name", width=250)
        self.tree.column("original_size", width=100)
        self.tree.column("compressed_size", width=100)
        self.tree.column("ratio", width=100)
        self.tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(btn_frame, text="预览压缩", command=self.preview_compression).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="开始压缩", command=self.start_compression).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="打开输出目录", command=self.open_output_dir).grid(row=0, column=2, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 初始化
        self.toggle_resize()

    def update_quality_label(self, value):
        """更新质量标签"""
        self.quality_label.config(text=f"{int(float(value))}%")

    def toggle_resize(self):
        """切换调整尺寸选项"""
        if self.resize_var.get():
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
        else:
            self.width_entry.config(state="disabled")
            self.height_entry.config(state="disabled")

    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                ("所有文件", "*.*")
            ]
        )

        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.tree.insert("", tk.END, values=(
                    os.path.basename(file),
                    self.format_size(os.path.getsize(file)),
                    "-",
                    "-",
                    "待处理"
                ))

        self.file_count_var.set(f"已选择 {len(self.files)} 个文件")

    def add_directory(self):
        """添加目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if not directory:
            return

        # 遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                    filepath = os.path.join(root, file)
                    if filepath not in self.files:
                        self.files.append(filepath)
                        self.tree.insert("", tk.END, values=(
                            file,
                            self.format_size(os.path.getsize(filepath)),
                            "-",
                            "-",
                            "待处理"
                        ))

        self.file_count_var.set(f"已选择 {len(self.files)} 个文件")

    def clear_files(self):
        """清空文件列表"""
        self.files = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_count_var.set("已选择 0 个文件")

    def browse_output(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_var.set(directory)

    def format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def preview_compression(self):
        """预览压缩效果"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 预览第一个文件
        file = self.files[0]
        try:
            # 打开图片
            img = Image.open(file)
            original_size = os.path.getsize(file)

            # 压缩图片
            quality = self.quality_var.get()
            format_name = self.format_var.get()

            # 调整尺寸
            if self.resize_var.get():
                width = int(self.width_var.get())
                height = int(self.height_var.get())

                if self.keep_ratio_var.get():
                    # 保持宽高比
                    ratio = min(width / img.width, height / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((width, height), Image.Resampling.LANCZOS)

            # 保存到临时文件
            temp_file = os.path.join(os.path.dirname(file), "temp_preview.jpg")
            if format_name == "original":
                img.save(temp_file, quality=quality)
            else:
                img.save(temp_file, format=format_name, quality=quality)

            compressed_size = os.path.getsize(temp_file)

            # 删除临时文件
            os.remove(temp_file)

            # 显示预览
            ratio = (1 - compressed_size / original_size) * 100
            messagebox.showinfo("预览结果",
                              f"文件: {os.path.basename(file)}\n"
                              f"原始大小: {self.format_size(original_size)}\n"
                              f"压缩后大小: {self.format_size(compressed_size)}\n"
                              f"压缩率: {ratio:.1f}%")

        except (OSError, IOError, ValueError) as e:
            messagebox.showerror("错误", f"预览失败: {e}")

    def start_compression(self):
        """开始压缩"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return

        # 获取输出目录
        output_dir = self.output_var.get()
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.path.dirname(self.files[0]), output_dir)

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 在新线程中压缩
        thread = threading.Thread(target=self.compress_worker, args=(output_dir,))
        thread.daemon = True
        thread.start()

    def compress_worker(self, output_dir):
        """压缩工作线程"""
        total = len(self.files)
        success = 0

        for i, file in enumerate(self.files):
            try:
                # 更新状态
                self.root.after(0, self.update_status, f"正在压缩: {os.path.basename(file)}")

                # 打开图片
                img = Image.open(file)
                original_size = os.path.getsize(file)

                # 压缩图片
                quality = self.quality_var.get()
                format_name = self.format_var.get()

                # 调整尺寸
                if self.resize_var.get():
                    width = int(self.width_var.get())
                    height = int(self.height_var.get())

                    if self.keep_ratio_var.get():
                        # 保持宽高比
                        ratio = min(width / img.width, height / img.height)
                        new_width = int(img.width * ratio)
                        new_height = int(img.height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    else:
                        img = img.resize((width, height), Image.Resampling.LANCZOS)

                # 确定输出文件名
                name = os.path.basename(file)
                if format_name == "original":
                    output_file = os.path.join(output_dir, name)
                else:
                    name_without_ext = os.path.splitext(name)[0]
                    output_file = os.path.join(output_dir, f"{name_without_ext}.{format_name.lower()}")

                # 保存图片
                if format_name == "original":
                    img.save(output_file, quality=quality)
                else:
                    img.save(output_file, format=format_name, quality=quality)

                compressed_size = os.path.getsize(output_file)
                ratio = (1 - compressed_size / original_size) * 100

                # 更新UI
                self.root.after(0, self.update_file_status, i, compressed_size, ratio, "完成")
                success += 1

            except (OSError, ValueError, IOError) as e:
                logging.warning(f"压缩失败: {os.path.basename(file)}, 原因: {e}")
                self.root.after(0, self.update_file_status, i, 0, 0, f"失败: {e}")

            # 更新进度
            progress = (i + 1) / total * 100
            self.root.after(0, self.progress_var.set, progress)

        # 完成
        self.root.after(0, self.update_status, f"压缩完成，成功 {success}/{total} 个文件")
        self.root.after(0, lambda: messagebox.showinfo("完成", f"压缩完成，成功 {success}/{total} 个文件"))

    def update_status(self, status):
        """更新状态"""
        self.status_var.set(status)

    def update_file_status(self, index, compressed_size, ratio, status):
        """更新文件状态"""
        items = self.tree.get_children()
        if index < len(items):
            item = items[index]
            values = self.tree.item(item, "values")
            self.tree.item(item, values=(
                values[0],
                values[1],
                self.format_size(compressed_size) if compressed_size > 0 else "-",
                f"{ratio:.1f}%" if ratio > 0 else "-",
                status
            ))

    def open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_var.get()
        if not os.path.isabs(output_dir):
            if self.files:
                output_dir = os.path.join(os.path.dirname(self.files[0]), output_dir)
            else:
                return

        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("警告", "输出目录不存在")


def main():
    """主函数"""
    root = tk.Tk()
    app = ImageCompressor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
