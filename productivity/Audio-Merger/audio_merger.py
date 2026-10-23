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
- 需要 ffmpeg 支持：优先使用系统 PATH 里的 ffmpeg，
  找不到时再找脚本同目录下的 ffmpeg.exe / ffprobe.exe
- Windows 系统下调用 ffmpeg 时会隐藏控制台窗口（只影响 pydub，不改全局 subprocess）

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import shutil
import warnings
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import subprocess
import sys

# 抑制 pydub 启动警告（找不到 ffmpeg 时 pydub 一导入就会警告，我们自己会给出提示）
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")

try:
    from pydub import AudioSegment
except ImportError:  # 没装 pydub 时不要直接崩，启动后给出安装提示
    AudioSegment = None

script_dir = os.path.dirname(os.path.abspath(__file__))

FFMPEG_DOWNLOAD_URL = "https://ffmpeg.org/download.html"
FFMPEG_MISSING_MSG = (
    "没有找到 ffmpeg / ffprobe，无法读取和导出 MP3。\n\n"
    "请任选一种方式：\n"
    "1. 安装 ffmpeg 并加入系统 PATH；\n"
    "2. 把 ffmpeg.exe 和 ffprobe.exe 放到本工具所在的文件夹：\n"
    f"   {script_dir}\n\n"
    f"下载地址：{FFMPEG_DOWNLOAD_URL}"
)
PYDUB_MISSING_MSG = "没有安装 pydub，请先执行：pip install pydub"


def find_tool(name, search_dir=None):
    """先在系统 PATH 里找，再找脚本同目录；都找不到返回 None"""
    found = shutil.which(name)
    if found:
        return found
    search_dir = search_dir or script_dir
    for candidate in (name + ".exe", name):
        path = os.path.join(search_dir, candidate)
        if os.path.isfile(path):
            return path
    return None


ffmpeg_exe = find_tool("ffmpeg")
ffprobe_exe = find_tool("ffprobe")


def _hidden_popen(*args, **kwargs):
    """Windows 下启动 ffmpeg 时不弹黑色控制台窗口"""
    if sys.platform.startswith("win") and "startupinfo" not in kwargs:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        kwargs["startupinfo"] = si
    return subprocess.Popen(*args, **kwargs)


class _PydubSubprocess:
    """只给 pydub 用的 subprocess 代理：Popen 换成隐藏窗口版，其余原样转发"""
    Popen = staticmethod(_hidden_popen)

    def __getattr__(self, name):
        return getattr(subprocess, name)


def _setup_pydub():
    if AudioSegment is None:
        return
    if ffmpeg_exe:
        AudioSegment.converter = ffmpeg_exe
    if ffprobe_exe:
        AudioSegment.ffprobe = ffprobe_exe
        # pydub 读取音频信息时只按 PATH 找 ffprobe，所以把它所在目录补进 PATH
        probe_dir = os.path.dirname(ffprobe_exe)
        if probe_dir not in os.environ.get("PATH", "").split(os.pathsep):
            os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + probe_dir
    if sys.platform.startswith("win"):
        # 只替换 pydub 模块里引用的 Popen，不再改全局的 subprocess.Popen
        import pydub.audio_segment as _seg
        import pydub.utils as _utils
        _seg.subprocess = _PydubSubprocess()
        _utils.Popen = _hidden_popen


def check_environment():
    """返回 None 表示可以开始合并，否则返回给用户看的提示"""
    if AudioSegment is None:
        return PYDUB_MISSING_MSG
    if not ffmpeg_exe or not ffprobe_exe:
        return FFMPEG_MISSING_MSG
    return None


_setup_pydub()

def validate_path(p):
    p = (p or "").strip()
    return os.path.normpath(p) if p and os.path.isdir(p) else None

def merge_mp3_files(input_dir, output_file, progress_callback=None):
    problem = check_environment()
    if problem:
        return False, problem

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
        problem = check_environment()
        if problem:
            status_var.set("缺少 ffmpeg 或 pydub"); status_label.config(foreground="red")
            messagebox.showerror("缺少运行环境", problem)
            return

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