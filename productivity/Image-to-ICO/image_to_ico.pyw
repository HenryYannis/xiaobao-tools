#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 图片转图标 (Image to ICO Converter)

功能：
- 将 PNG、JPG 等图片格式转换为 Windows 图标格式
- 支持多种图标尺寸
- 支持批量转换

使用方法：
- 选择要转换的图片文件
- 选择输出尺寸
- 点击转换按钮

注意事项：
- 需要安装 Pillow：pip install Pillow
- 输出为 .ico 格式文件

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

class ImageToIcoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转图标")
        window_width = 500
        window_height = 400
        #self.root.geometry("500x400")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        
        # 支持的主流格式
        self.support_formats = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
        
        # 要转换的文件列表
        self.file_list = []
        
        self.create_ui()
        
    def create_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="图片转 ICO", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 文件选择按钮
        select_btn = tk.Button(
            main_frame,
            text="选择图片文件",
            command=self.select_files,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            width=20
        )
        select_btn.pack(pady=10)
        
        # 文件列表显示
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            height=8,
            width=50,
            font=("Arial", 10)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        # ICO尺寸选择
        size_frame = tk.Frame(main_frame)
        size_frame.pack(pady=10)
        
        tk.Label(size_frame, text="ICO 图标尺寸:").pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar(value="32x32")
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["16x16", "32x32", "48x48", "64x64", "128x128", "256x256"],
            width=10,
            state="readonly"
        )
        size_combo.pack(side=tk.LEFT, padx=10)
        
        # 转换按钮
        convert_btn = tk.Button(
            main_frame,
            text="开始转换",
            command=self.convert_images,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        )
        convert_btn.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            fg="#666666"
        )
        self.status_label.pack()
        
    def select_files(self):
        """选择要转换的图片文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("GIF文件", "*.gif"),
                ("BMP文件", "*.bmp"),
                ("WebP文件", "*.webp"),
                ("所有文件", "*.*")
            ]
        )
        
        if files:
            self.file_list.clear()
            self.file_listbox.delete(0, tk.END)
            
            for file_path in files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.support_formats:
                    self.file_list.append(file_path)
                    self.file_listbox.insert(tk.END, os.path.basename(file_path))
                else:
                    messagebox.showwarning(
                        "格式不支持",
                        f"文件 {os.path.basename(file_path)} 的格式不被支持，已跳过"
                    )
            
            self.update_status(f"已选择 {len(self.file_list)} 个文件")
    
    def convert_images(self):
        """转换图片为ICO格式"""
        if not self.file_list:
            messagebox.showwarning("提示", "请先选择要转换的图片文件！")
            return
        
        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存目录")
        if not save_dir:
            return
        
        # 获取选择的尺寸
        size_str = self.size_var.get()
        size = tuple(map(int, size_str.split('x')))
        
        success_count = 0
        fail_count = 0
        
        for file_path in self.file_list:
            try:
                # 打开图片
                with Image.open(file_path) as img:
                    # 转换为RGBA模式（支持透明度）
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 调整尺寸
                    img_resized = img.resize(size, Image.Resampling.LANCZOS)
                    
                    # 生成输出文件名
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_path = os.path.join(save_dir, f"{base_name}.ico")
                    
                    # 保存为ICO格式
                    img_resized.save(output_path, format='ICO', sizes=[size])
                    
                    success_count += 1
                    print(f"成功转换: {os.path.basename(file_path)} -> {os.path.basename(output_path)}")
            
            except Exception as e:
                fail_count += 1
                print(f"转换失败: {os.path.basename(file_path)} - {str(e)}")
        
        # 显示结果
        if success_count > 0:
            messagebox.showinfo(
                "转换完成",
                f"转换完成！\n成功: {success_count} 个\n失败: {fail_count} 个\n\n文件保存在: {save_dir}"
            )
            self.update_status(f"转换完成！成功 {success_count} 个")
        else:
            messagebox.showerror("转换失败", "所有文件转换失败，请检查文件格式是否正确！")
            self.update_status("转换失败")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)

def main():
    root = tk.Tk()
    app = ImageToIcoConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
