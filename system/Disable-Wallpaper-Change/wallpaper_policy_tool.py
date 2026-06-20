#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 壁纸修改限制工具 (Wallpaper Policy Tool)

功能：
- 禁止或允许用户修改 Windows 桌面壁纸
- 通过修改注册表策略实现
- 适合公共电脑或展示环境

使用方法：
- 需要以管理员权限运行
- 点击按钮切换壁纸修改权限

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启资源管理器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import sys
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox
from winreg import (
    CreateKey, SetValueEx, DeleteValue, REG_DWORD,
    HKEY_CURRENT_USER, CloseKey, OpenKey, KEY_ALL_ACCESS
)

# 目标注册表路径和键名
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
REG_VALUE_NAME = "NoChangingWallPaper"

def restart_explorer():
    """强制重启资源管理器以应用设置"""
    try:
        # 强制结束 explorer.exe (静默，避免命令行窗口闪烁)
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"], 
            check=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # 重新启动 explorer.exe
        subprocess.Popen(["explorer.exe"])
    except Exception:
        # 失败则静默处理
        pass

def modify_wallpaper_policy(setting_value):
    """
    修改注册表以控制壁纸修改权限。
    setting_value: 1 (禁止) 或 0 (允许)
    """
    try:
        if setting_value == 1:
            # 1: 禁止修改壁纸
            hKey = CreateKey(HKEY_CURRENT_USER, REG_PATH)
            SetValueEx(hKey, REG_VALUE_NAME, 0, REG_DWORD, 1)
            CloseKey(hKey)
            status_text = "禁止"
        else:
            # 0: 允许修改壁纸 (通过删除键值实现)
            hKey = OpenKey(HKEY_CURRENT_USER, REG_PATH, 0, KEY_ALL_ACCESS)
            DeleteValue(hKey, REG_VALUE_NAME)
            CloseKey(hKey)
            status_text = "允许"

        # 成功后重启资源管理器
        restart_explorer()
        
        messagebox.showinfo("操作成功", f"壁纸修改权限已设置为：{status_text}。\n资源管理器已重启。")

    except FileNotFoundError:
        # 针对删除操作（允许修改）：如果键值本来就不存在，则视为成功
        if setting_value == 0:
            restart_explorer()
            messagebox.showinfo("操作成功", "壁纸修改权限已设置为：允许。\n(原键值不存在，资源管理器已重启)")
        else:
            # 如果是创建操作失败（权限不足或路径错误）
            messagebox.showerror("注册表错误", f"无法创建或写入注册表路径：{REG_PATH}\n请确认已通过管理员权限运行。")
    except PermissionError:
        messagebox.showerror("权限不足", "操作失败，请确保您是以管理员身份运行。")
    except Exception as e:
        messagebox.showerror("一般错误", f"修改注册表时发生错误：\n{e}")

# --- GUI 界面 ---
class WallpaperToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Windows 壁纸权限控制 (需管理员)")
        # 确保窗口在前
        master.attributes('-topmost', 1) 
        master.geometry("300x160")
        
        # 标签
        self.label = tk.Label(master, text="请选择壁纸修改权限设置：\n(操作后资源管理器将重启)", pady=10)
        self.label.pack()

        # 按钮 - 禁止修改
        self.disable_button = tk.Button(
            master, 
            text="🔴 禁止修改壁纸 (锁定)", 
            command=lambda: self.set_policy(1),
            bg="#ffcccc",
            padx=10, 
            pady=5
        )
        self.disable_button.pack(pady=5)

        # 按钮 - 允许修改
        self.enable_button = tk.Button(
            master, 
            text="🟢 允许修改壁纸 (解锁)", 
            command=lambda: self.set_policy(0),
            bg="#ccffcc",
            padx=10, 
            pady=5
        )
        self.enable_button.pack(pady=5)

    def set_policy(self, value):
        # 禁用按钮防止重复点击
        self.disable_button.config(state=tk.DISABLED)
        self.enable_button.config(state=tk.DISABLED)
        
        modify_wallpaper_policy(value)
        
        # 重新启用按钮
        self.disable_button.config(state=tk.NORMAL)
        self.enable_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = WallpaperToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()