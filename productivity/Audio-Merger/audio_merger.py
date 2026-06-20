#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 音频合并工具 (Audio Merger)

功能：
- 批量合并多个音频文件
- 支持 MP3、WAV、OGG 等格式
- 图形界面操作

使用方法：
- 选择包含音频文件的目录
- 点击合并按钮

注意事项：
- 需要安装 pydub：pip install pydub
- 需要 ffmpeg 支持（可将 ffmpeg.exe 放在脚本同目录）
- Windows 系统下会自动隐藏 subprocess 窗口

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import warnings
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment
import threading
import subprocess
import sys

# Windows 下隐藏 subprocess 窗口
if sys.platform.startswith("win"):
    _original_popen = subprocess.Popen

    def _hidden_popen(*args, **kwargs):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = si
        return _original_popen(*args, **kwargs)

    subprocess.Popen = _hidden_popen

# 抑制 pydub 启动警告
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")

# 强制 ffmpeg/ffprobe 路径（脚本同目录）
script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_exe = os.path.join(script_dir, "ffmpeg.exe")
ffprobe_exe = os.path.join(script_dir, "ffprobe.exe")

os.environ["PATH"] += os.pathsep + script_dir
AudioSegment.converter = ffmpeg_exe
AudioSegment.ffprobe = ffprobe_exe

def validate_path(p):
    p = (p or "").strip()
    return os.path.normpath(p) if p and os.path.isdir(p) else None

def merge_mp3_files(input_dir, output_file, progress_callback=None):
    input_dir = validate_path(input_dir)
    if not input_dir:
        return False, "无效输入目录"

    mp3s = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.mp3')]
    if not mp3s:
        return False, "目录中没有 MP3 文件"

    mp3s.sort()
    total = len(mp3s)
    combined = AudioSegment.empty()

    for i, f in enumerate(mp3s):
        try:
            combined += AudioSegment.from_mp3(f)
            if progress_callback:
                progress_callback((i + 1) / total * 100)
        except Exception as e:
            return False, f"读取失败 {os.path.basename(f)}: {str(e)}"

    if len(combined) == 0:
        return False, "没有成功加载任何音频"

    try:
        combined.export(output_file, format="mp3", bitrate="192k")
        if progress_callback:
            progress_callback(100)
        return True, f"合并完成！保存至：{output_file}"
    except Exception as e:
        return False, f"导出失败: {str(e)}"

def pick_dir():
    root = tk.Tk(); root.withdraw()
    path = filedialog.askdirectory(title="选择 MP3 文件夹")
    root.destroy()
    return path

def pick_out(default="合并结果.mp3"):
    root = tk.Tk(); root.withdraw()
    path = filedialog.asksaveasfilename(
        title="保存合并文件",
        defaultextension=".mp3",
        filetypes=[("MP3 文件", "*.mp3")],
        initialfile=default
    )
    root.destroy()
    return path

def gui():
    root = tk.Tk()
    root.title("MP3 批量合并工具")
    root.geometry("540x420")
    root.configure(bg="#f8f9fa")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TLabel", background="#f8f9fa", font=("微软雅黑", 10))
    style.configure("TButton", font=("微软雅黑", 10))

    # 输入
    ttk.Label(root, text="MP3 文件夹：").pack(anchor="w", padx=25, pady=(25, 5))
    input_var = tk.StringVar()
    ttk.Entry(root, textvariable=input_var, width=60).pack(padx=25, fill="x", pady=4)
    ttk.Button(root, text="浏览", command=lambda: input_var.set(pick_dir() or "")).pack(pady=6)

    # 输出
    ttk.Label(root, text="输出文件：").pack(anchor="w", padx=25, pady=(15, 5))
    output_var = tk.StringVar()
    ttk.Entry(root, textvariable=output_var, width=60).pack(padx=25, fill="x", pady=4)
    ttk.Button(root, text="浏览", command=lambda: output_var.set(pick_out() or "")).pack(pady=6)

    # 状态 + 进度条
    status_var = tk.StringVar(value="就绪")
    status_label = ttk.Label(root, textvariable=status_var, font=("微软雅黑", 10), foreground="#006600")
    status_label.pack(pady=15)

    progress = ttk.Progressbar(root, orient="horizontal", length=450, mode="determinate")
    progress.pack(pady=10)

    def start():
        indir = input_var.get().strip()
        outfile = output_var.get().strip()
        if not indir or not os.path.isdir(indir):
            status_var.set("请选择有效文件夹"); status_label.config(foreground="red"); return
        if not outfile:
            status_var.set("请选择输出文件"); status_label.config(foreground="red"); return
        if not outfile.lower().endswith(".mp3"):
            outfile += ".mp3"
            output_var.set(outfile)

        status_var.set("正在合并..."); status_label.config(foreground="blue")
        progress['value'] = 0
        btn.config(state="disabled")

        def work():
            def update_prog(val):
                root.after(0, lambda v=val: progress.config(value=v))
                root.after(0, lambda v=val: status_var.set(f"正在合并... {int(v)}%"))

            ok, msg = merge_mp3_files(indir, outfile, update_prog)
            root.after(0, lambda: status_var.set(msg))
            root.after(0, lambda: status_label.config(foreground="green" if ok else "red"))
            root.after(0, lambda: btn.config(state="normal"))
            root.after(0, lambda: progress.config(value=100 if ok else 0))
            if ok:
                root.after(0, lambda: messagebox.showinfo("完成", msg))

        threading.Thread(target=work, daemon=True).start()

    btn = ttk.Button(root, text="开始合并", command=start, width=20)
    btn.pack(pady=25)

    root.mainloop()

if __name__ == "__main__":
    gui()