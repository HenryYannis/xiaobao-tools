#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - Edge 下载管理器 (Edge Download Manager)

功能：
- 禁用或启用 Edge 浏览器的下载功能
- 通过修改注册表实现
- 适合公共电脑或教学环境

使用方法：
- 需要以管理员权限运行
- 点击按钮切换下载功能状态

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启 Edge 浏览器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from tkinter import messagebox
import winreg
import sys
import os
import subprocess

# 定义注册表路径和键名
REG_PATH = r"SOFTWARE\Policies\Microsoft\Edge"
REG_KEY = "DownloadRestrictions"

# Edge 进程名
EDGE_PROCESS_NAME = "msedge.exe"

def kill_edge_process():
    """使用 taskkill 命令强制终止所有 Edge 进程"""
    # taskkill /f /im msedge.exe 的含义：
    # /f: 强制终止
    # /im: 通过镜像名称（进程名）指定
    try:
        # 执行 taskkill 命令
        # subprocess.run 是比 os.system 更好的选择
        result = subprocess.run(
            f"taskkill /f /im {EDGE_PROCESS_NAME}", 
            shell=True,
            capture_output=True,
            text=True,
            check=False # 不抛出异常，即使找不到进程也继续
        )
        
        # 检查 taskkill 的输出，判断是否成功终止或未找到
        if "SUCCESS" in result.stdout or "未找到" in result.stdout or "no running instance" in result.stdout:
            # 进程成功被终止或本来就没有运行
            return True
        else:
            # 可能是权限问题或其他错误
            print(f"Taskkill Error/Output: {result.stderr or result.stdout}")
            return False

    except Exception as e:
        print(f"执行 Taskkill 出现异常: {e}")
        return False


def modify_registry(value):
    """
    修改或创建 Edge 浏览器的注册表键值。
    :param value: 0 (允许下载) 或 3 (禁止所有下载)
    """
    key = None
    try:
        # 1. 修改注册表
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        winreg.SetValueEx(key, REG_KEY, 0, winreg.REG_DWORD, value)
        
        # 2. 判断状态文案
        if value == 0:
            status_text = "已恢复：Edge 允许所有下载。"
        elif value == 3:
            status_text = "已禁用：Edge 将阻止所有下载。"
        else:
            status_text = f"设置值为 {value}"

        # 3. 杀死 Edge 进程以确保策略立即生效
        messagebox.showinfo("正在操作", f"注册表修改完成。\n{status_text}\n\n正在尝试关闭 Edge 浏览器以应用设置...")
        
        if kill_edge_process():
            messagebox.showinfo("操作成功", f"Edge 已关闭，设置已生效。\n{status_text}")
        else:
            messagebox.showwarning("部分成功", f"Edge 进程可能未能关闭（可能原因：权限不足或未运行）。\n{status_text}\n请手动重启 Edge 浏览器。")


    except PermissionError:
        messagebox.showerror("权限不足", "修改注册表失败！\n\n请务必【右键点击本程序 -> 以管理员身份运行】。")
    except Exception as e:
        messagebox.showerror("错误", f"发生意外错误: {e}")
    finally:
        if key:
            winreg.CloseKey(key)

def restore_downloads():
    """恢复下载 (设置 DownloadRestrictions = 0)"""
    modify_registry(0)

def disable_downloads():
    """彻底禁用下载 (设置 DownloadRestrictions = 3)"""
    # 修正值：3 表示禁止所有下载
    modify_registry(3) 

def create_gui():
    """创建并运行 Tkinter GUI 窗口"""
    root = tk.Tk()
    root.title("Edge 下载管控工具")

    # 窗口居中
    window_width = 320
    window_height = 240
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.resizable(False, False)

    # 标题标签
    title_label = tk.Label(root, text="Edge 浏览器下载权限管理", font=("微软雅黑", 12, "bold"))
    title_label.pack(pady=15)

    # 恢复按钮
    restore_button = tk.Button(root, text="🟢 允许所有下载", command=restore_downloads, width=22, height=2, bg="#e6ffe6", fg="green", font=("微软雅黑", 10))
    restore_button.pack(pady=5)

    # 禁用按钮
    disable_button = tk.Button(root, text="🔴 禁止所有下载", command=disable_downloads, width=22, height=2, bg="#ffe6e6", fg="red", font=("微软雅黑", 10))
    disable_button.pack(pady=5)

    # 底部提示
    tip_label = tk.Label(root, text="📢 提示：操作需要管理员权限，程序将尝试关闭 Edge。", font=("微软雅黑", 8), fg="gray")
    tip_label.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()