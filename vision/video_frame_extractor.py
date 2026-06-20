#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 批量视频截图提取器 (Video Frame Extractor)
功能：一键载入本地任意格式视频（MP4/MKV/AVI等），支持配置等时间步长（例如每 5 秒提取一张）全自动无损批量导出高清截图；
     同时提供预览滑块，支持手动单张截取精准画面帧。截图自动归档保存于专属目录下。
受众：影视解说自媒体人、影视创作者、写电影剧透解析的内容博主、计算机视觉数据集采集人员。

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 终端彩色输出
COLOR_GREEN = "\033[92m"
COLOR_RESET = "\033[0m"

# 尝试导入 OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

class VideoExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量视频截图提取器")
        self.root.geometry("520x495")
        self.root.resizable(False, False)
        
        self.video_path = ""
        self.output_dir = ""
        self.is_processing = False
        
        self.setup_ui()
        
        if not OPENCV_AVAILABLE:
            messagebox.showerror("依赖缺失", "检测到未安装 OpenCV 库，部分核心视觉处理将无法启动。\n请先在根目录下执行: pip install -r requirements.txt")

    def setup_ui(self):
        # 头部横幅
        header = tk.Label(self.root, text="🎬 批量视频截图与画面帧提取器", font=("Helvetica", 14, "bold"), fg="#0969da")
        header.pack(pady=15)
        
        # 视频选择区
        video_frame = tk.LabelFrame(self.root, text=" 1. 选择目标视频 ", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        video_frame.pack(padx=20, fill="x", pady=5)
        
        self.video_path_label = tk.Label(video_frame, text="尚未选择任何视频文件", wraplength=450, anchor="w", fg="#57606a")
        self.video_path_label.pack(side="left", fill="x", expand=True)
        
        select_btn = tk.Button(video_frame, text="选择视频", command=self.select_video, bg="#f6f8fa", relief="groove")
        select_btn.pack(side="right", padx=5)

        # 参数配置区
        param_frame = tk.LabelFrame(self.root, text=" 2. 配置提取参数 ", font=("Helvetica", 10, "bold"), padx=10, pady=15)
        param_frame.pack(padx=20, fill="x", pady=10)
        
        # 等步长提取配置
        interval_frame = tk.Frame(param_frame)
        interval_frame.pack(fill="x", pady=5)
        
        self.mode_var = tk.StringVar(value="interval")
        
        rb_interval = tk.Radiobutton(interval_frame, text="等时间间隔批量提取: 每隔 ", variable=self.mode_var, value="interval", font=("Helvetica", 10))
        rb_interval.pack(side="left")
        
        self.interval_entry = tk.Entry(interval_frame, width=5, justify="center")
        self.interval_entry.insert(0, "5")
        self.interval_entry.pack(side="left", padx=2)
        
        tk.Label(interval_frame, text=" 秒截图一张", font=("Helvetica", 10)).pack(side="left")
        
        # 单张精准提取说明
        rb_manual = tk.Radiobutton(param_frame, text="手动提取精准视频帧 (在下方滑块选择)", variable=self.mode_var, value="manual", font=("Helvetica", 10))
        rb_manual.pack(anchor="w", pady=5)
        
        # 精准预览滑块
        slider_frame = tk.Frame(param_frame)
        slider_frame.pack(fill="x", pady=5)
        
        self.frame_slider = ttk.Scale(slider_frame, from_=0, to=100, orient="horizontal", command=self.on_slider_move)
        self.frame_slider.pack(fill="x", side="left", expand=True, padx=5)
        
        self.slider_label = tk.Label(slider_frame, text="0.0s", width=8, fg="#0969da", font=("Helvetica", 10, "bold"))
        self.slider_label.pack(side="right")

        # 进度指示器
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        
        self.status_label = tk.Label(self.root, text="就绪。期待一键提取高清画面", font=("Helvetica", 10), fg="#57606a")
        self.status_label.pack(pady=2)

        # 核心启动按钮区
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="🚀 启动批量无损提取", font=("Helvetica", 11, "bold"), bg="#0969da", fg="white",
                                   relief="flat", activebackground="#0c54b6", command=self.start_extraction)
        self.start_btn.grid(row=0, column=0, padx=15, ipady=4, ipadx=10)
        
        self.single_grab_btn = tk.Button(btn_frame, text="📸 截取当前滑块帧", font=("Helvetica", 11, "bold"), bg="#2da44e", fg="white",
                                         relief="flat", activebackground="#2c974b", command=self.grab_single_frame)
        self.single_grab_btn.grid(row=0, column=1, padx=15, ipady=4, ipadx=10)

        # 分割线与底栏
        sep = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        sep.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        author_frame = tk.Frame(self.root, pady=4)
        author_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            author_frame,
            text="作者：小宝科技站 (",
            font=("微软雅黑", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=(15, 0))

        link_lbl = tk.Label(
            author_frame,
            text="xbkjz.cn",
            font=("微软雅黑", 8, "underline"),
            fg="#0066CC",
            cursor="hand2"
        )
        link_lbl.pack(side=tk.LEFT)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))
        link_lbl.bind("<Enter>", lambda e: link_lbl.configure(fg="#0044AA"))
        link_lbl.bind("<Leave>", lambda e: link_lbl.configure(fg="#0066CC"))

        tk.Label(
            author_frame,
            text=")",
            font=("微软雅黑", 8),
            fg="gray"
        ).pack(side=tk.LEFT)

    def select_video(self):
        if self.is_processing:
            return
        selected = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.mkv *.avi *.mov *.flv"), ("所有文件", "*.*")]
        )
        if selected:
            self.video_path = os.path.abspath(selected)
            self.video_path_label.config(text=os.path.basename(self.video_path), fg="#24292f")
            
            # 设置输出目录
            parent_dir = os.path.dirname(self.video_path)
            base_name = os.path.splitext(os.path.basename(self.video_path))[0]
            self.output_dir = os.path.join(parent_dir, f"截图_{base_name}")
            
            # 初始化滑块范围
            if OPENCV_AVAILABLE:
                cap = cv2.VideoCapture(self.video_path)
                if cap.isOpened():
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    self.frame_slider.config(to=total_frames - 1)
                cap.release()

    def on_slider_move(self, value):
        """当用户拖动滑块时，估算时间点并显示"""
        if not self.video_path or not OPENCV_AVAILABLE:
            return
        
        frame_idx = int(float(value))
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            # 计算对应的秒数
            seconds = frame_idx / fps if fps > 0 else 0
            self.slider_label.config(text=f"{seconds:.1f}s")
        cap.release()

    def start_extraction(self):
        """核心批量提取控制器"""
        if not OPENCV_AVAILABLE:
            messagebox.showerror("错误", "OpenCV 库未安装，无法进行视频截图！")
            return
        if not self.video_path:
            messagebox.showwarning("警告", "请先选择需要提取的视频文件！")
            return
        if self.is_processing:
            return
        
        try:
            seconds_interval = float(self.interval_entry.get())
            if seconds_interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "时间间隔必须是大于 0 的数值")
            return

        self.is_processing = True
        self.start_btn.config(state="disabled", text="正在批量截图中...")
        self.single_grab_btn.config(state="disabled")
        
        # 开启后台子线程，防止 GUI 失去响应
        thread = threading.Thread(target=self.run_batch_extraction, args=(seconds_interval,))
        thread.daemon = True
        thread.start()

    def run_batch_extraction(self, interval):
        """子线程运行的批量提取核心循环"""
        # 创建专属输出文件夹
        os.makedirs(self.output_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("错误", "视频加载失败，请确保格式正确！"))
            self.root.after(0, self.reset_buttons)
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0 or total_frames <= 0:
            self.root.after(0, lambda: messagebox.showerror("错误", "无法解析视频帧率信息。"))
            cap.release()
            self.root.after(0, self.reset_buttons)
            return

        # 等时间步长对应的帧间隔
        frame_step = int(fps * interval)
        if frame_step <= 0:
            frame_step = 1

        extracted_count = 0
        current_frame = 0
        
        print(f"{COLOR_GREEN}[INFO]{COLOR_RESET} 开始批量无损导出...")
        
        while current_frame < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = cap.read()
            if not ret:
                break
                
            # 保存图像
            sec = current_frame / fps
            out_filename = f"frame_{extracted_count:04d}_time_{sec:.1f}s.jpg"
            out_path = os.path.join(self.output_dir, out_filename)
            cv2.imwrite(out_path, frame)
            
            extracted_count += 1
            current_frame += frame_step
            
            # 更新进度条
            prog = (current_frame / total_frames) * 100
            self.root.after(0, lambda p=prog: self.progress_var.set(p))
            self.root.after(0, lambda c=extracted_count: self.status_label.config(text=f"已成功提取并无损保存 {c} 张截图...", fg="#0969da"))

        cap.release()
        self.root.after(0, lambda: self.progress_var.set(100))
        self.root.after(0, lambda: messagebox.showinfo("大功告成", f"批量提取成功！共导出 {extracted_count} 张高清截图。\n已自动保存在视频目录下的:\n{os.path.basename(self.output_dir)} 文件夹内。"))
        self.root.after(0, self.reset_buttons)

    def grab_single_frame(self):
        """精准提取滑块选定的一帧并保存"""
        if not OPENCV_AVAILABLE:
            messagebox.showerror("错误", "OpenCV 库未安装，无法提取视频截图！")
            return
        if not self.video_path:
            messagebox.showwarning("警告", "请先选择需要提取的视频文件！")
            return
        
        # 创建输出文件夹
        os.makedirs(self.output_dir, exist_ok=True)
        
        frame_idx = int(self.frame_slider.get())
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                sec = frame_idx / fps if fps > 0 else 0
                out_filename = f"manual_frame_{frame_idx}_time_{sec:.1f}s.jpg"
                out_path = os.path.join(self.output_dir, out_filename)
                cv2.imwrite(out_path, frame)
                messagebox.showinfo("截图成功", f"当前帧已成功无损截取并保存！\n路径: {os.path.basename(out_path)}")
            else:
                messagebox.showerror("错误", "无法截取当前画面帧。")
        cap.release()

    def reset_buttons(self):
        self.is_processing = False
        self.start_btn.config(state="normal", text="🚀 启动批量无损提取")
        self.single_grab_btn.config(state="normal")
        self.status_label.config(text="就绪。期待一键提取高清画面", fg="#57606a")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = VideoExtractorApp(app_root)
    app_root.mainloop()
