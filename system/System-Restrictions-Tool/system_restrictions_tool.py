#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 系统权限限制工具 (System Restrictions Controller)

功能：
- 禁止/允许修改桌面壁纸
- 移除/恢复桌面“了解此图片”聚焦图标
- 禁用/启用 Chrome 和 Edge 离线游戏

特点：
- 传统古早UI：使用 Windows 原生灰/白默认界面风格，布局简单直观，非花哨设计
- 零依赖：纯标准库（tkinter, winreg, ctypes）开发，开箱即用
- 提权检测：自动检测并请求管理员权限以修改系统策略
- 实时同步：启动时自动读取注册表，真实反映系统当前状态
- 智能交互：修改壁纸或图标后支持一键/自动重启资源管理器

作者：小宝科技帝国
日期：2026
"""

import os
import sys
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox
from winreg import (
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    OpenKey, CreateKey, SetValueEx, DeleteValue, QueryValueEx,
    CloseKey, REG_DWORD, KEY_READ, KEY_ALL_ACCESS
)

# --- Registry Keys ---
# 1. Wallpaper restriction
REG_WALLPAPER_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
REG_WALLPAPER_VALUE = "NoChangingWallPaper"

# 2. Spotlight "Learn about this picture" desktop icon restriction
REG_SPOTLIGHT_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
REG_SPOTLIGHT_VALUE = "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}"

# 3. Chrome Dino Game restriction
REG_CHROME_PATH = r"SOFTWARE\Policies\Google\Chrome"
REG_CHROME_VALUE = "AllowDinosaurEasterEgg"

# 4. Edge Surf Game restriction
REG_EDGE_PATH = r"SOFTWARE\Policies\Microsoft\Edge"
REG_EDGE_VALUE = "AllowSurfGame"


# --- Registry Helper Functions ---
def reg_read_dword(hkey, path, value_name):
    """读取注册表 DWORD 值，如果键或值不存在返回 None"""
    try:
        with OpenKey(hkey, path, 0, KEY_READ) as key:
            val, _ = QueryValueEx(key, value_name)
            return val
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[RegReadError] {path}\\{value_name}: {e}")
        return None


def reg_write_dword(hkey, path, value_name, value):
    """向注册表写入 DWORD 值，返回是否成功"""
    try:
        with CreateKey(hkey, path) as key:
            SetValueEx(key, value_name, 0, REG_DWORD, value)
        return True
    except PermissionError:
        print(f"[RegWritePermissionError] {path}\\{value_name}: Requires administrator privileges.")
        return False
    except Exception as e:
        print(f"[RegWriteError] {path}\\{value_name}: {e}")
        return False


def reg_delete_value(hkey, path, value_name):
    """从注册表删除特定值，如果不存在也视为成功，返回是否成功"""
    try:
        with OpenKey(hkey, path, 0, KEY_ALL_ACCESS) as key:
            DeleteValue(key, value_name)
        return True
    except FileNotFoundError:
        return True
    except PermissionError:
        print(f"[RegDeletePermissionError] {path}\\{value_name}: Requires administrator privileges.")
        return False
    except Exception as e:
        print(f"[RegDeleteError] {path}\\{value_name}: {e}")
        return False


# --- Core Logic Functions ---
def is_admin():
    """判断是否具备管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """以管理员身份重新运行程序"""
    if getattr(sys, 'frozen', False):
        executable = sys.executable
        params = ""
    else:
        executable = sys.executable
        params = f'"{__file__}"'
    try:
        # Request elevation
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        sys.exit(0)
    except Exception as e:
        print(f"提权失败: {e}")
        sys.exit(1)


def restart_explorer():
    """重启 Windows 资源管理器进程以应用桌面和壁纸配置"""
    try:
        # 强杀 explorer.exe
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # 启动 explorer.exe
        subprocess.Popen(["explorer.exe"])
        return True
    except Exception as e:
        print(f"资源管理器重启出错: {e}")
        # 保底尝试启动，防止桌面消失后无法恢复
        try:
            subprocess.Popen(["explorer.exe"])
        except:
            pass
        return False


# --- Policy Management Functions ---
def get_wallpaper_locked():
    """获取壁纸锁定的真实状态。1 表示锁定 (True)"""
    val = reg_read_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)
    return val == 1


def set_wallpaper_locked(locked):
    """设置壁纸锁定状态"""
    if locked:
        return reg_write_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)


def get_spotlight_hidden():
    """获取桌面“了解此图片”隐藏状态。1 表示隐藏 (True)"""
    val = reg_read_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)
    return val == 1


def set_spotlight_hidden(hidden):
    """设置桌面“了解此图片”隐藏状态"""
    if hidden:
        return reg_write_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE, 1)
    else:
        # 写入 0 或者删除值均可，这里删除还原默认
        return reg_delete_value(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)


def get_browser_games_disabled():
    """
    检查离线游戏禁用状态。
    Chrome: AllowDinosaurEasterEgg = 0 表示禁用
    Edge: AllowSurfGame = 0 表示禁用
    """
    chrome_hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE)
    chrome_hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE)
    edge_hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE)
    edge_hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE)

    is_dino_disabled = (chrome_hklm == 0 or chrome_hkcu == 0)
    is_surf_disabled = (edge_hklm == 0 or edge_hkcu == 0)

    return is_dino_disabled or is_surf_disabled


def set_browser_games_disabled(disabled):
    """设置浏览器离线游戏禁用状态"""
    success = True
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE, 0)
        s2 = reg_write_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE, 0)
        s3 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE, 0)
        s4 = reg_write_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE, 0)
        success = s1 or s2 or s3 or s4
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE)
        s2 = reg_delete_value(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE)
        s3 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE)
        s4 = reg_delete_value(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE)
        success = s1 and s2 and s3 and s4

    return success


# --- Classic GUI Implementation ---
class RestrictionsToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("系统权限控制中心")
        self.root.resizable(False, False)

        # 居中窗口 (紧凑古早尺寸)
        w, h = 480, 260
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.auto_restart_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_status()

    def _build_ui(self):
        # 头部标题
        title_label = tk.Label(
            self.root,
            text="系统限制与策略控制中心",
            font=("微软雅黑", 12, "bold")
        )
        title_label.pack(pady=(10, 2))

        subtitle_label = tk.Label(
            self.root,
            text="管理学校机房、演示环境或公共设备的安全策略",
            font=("微软雅黑", 9),
            fg="gray"
        )
        subtitle_label.pack(pady=(0, 5))

        # 主设置 LabelFrame
        content_frame = tk.LabelFrame(
            self.root,
            text="策略设置",
            font=("微软雅黑", 9),
            padx=15,
            pady=10
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # 1. 桌面壁纸限制
        wp_frame = tk.Frame(content_frame)
        wp_frame.pack(fill=tk.X, pady=4)
        self.wp_lbl = tk.Label(wp_frame, text="壁纸修改权限：读取中...", font=("微软雅黑", 9))
        self.wp_lbl.pack(side=tk.LEFT)
        self.wp_btn = tk.Button(
            wp_frame,
            text="读取中...",
            font=("微软雅黑", 9),
            width=10,
            command=self.toggle_wallpaper
        )
        self.wp_btn.pack(side=tk.RIGHT)

        # 2. 桌面“了解此图片”
        sp_frame = tk.Frame(content_frame)
        sp_frame.pack(fill=tk.X, pady=4)
        self.sp_lbl = tk.Label(sp_frame, text="桌面“了解此图片”：读取中...", font=("微软雅黑", 9))
        self.sp_lbl.pack(side=tk.LEFT)
        self.sp_btn = tk.Button(
            sp_frame,
            text="读取中...",
            font=("微软雅黑", 9),
            width=10,
            command=self.toggle_spotlight
        )
        self.sp_btn.pack(side=tk.RIGHT)

        # 3. 浏览器离线游戏限制
        bg_frame = tk.Frame(content_frame)
        bg_frame.pack(fill=tk.X, pady=4)
        self.bg_lbl = tk.Label(bg_frame, text="浏览器离线小游戏：读取中...", font=("微软雅黑", 9))
        self.bg_lbl.pack(side=tk.LEFT)
        self.bg_btn = tk.Button(
            bg_frame,
            text="读取中...",
            font=("微软雅黑", 9),
            width=10,
            command=self.toggle_browser_games
        )
        self.bg_btn.pack(side=tk.RIGHT)

        # 底部栏
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=15, pady=5, side=tk.BOTTOM)

        # 自动重启资源管理器勾选框
        self.chk = tk.Checkbutton(
            footer_frame,
            text="修改后自动重启资源管理器",
            variable=self.auto_restart_var,
            font=("微软雅黑", 9)
        )
        self.chk.pack(side=tk.LEFT)

        # 手动重启按钮
        self.restart_btn = tk.Button(
            footer_frame,
            text="重启资源管理器",
            font=("微软雅黑", 9),
            command=self.manual_restart_explorer
        )
        self.restart_btn.pack(side=tk.RIGHT)

        # 最底部状态栏 (原生凹陷样式)
        self.status_lbl = tk.Label(
            self.root,
            text="系统权限：已获得管理员权限",
            font=("微软雅黑", 8),
            anchor="w",
            bd=1,
            relief=tk.SUNKEN,
            padx=5,
            pady=2
        )
        self.status_lbl.pack(fill=tk.X, side=tk.BOTTOM)

    def refresh_status(self):
        """读取系统真实注册表状态并更新UI文字"""
        # 1. 壁纸限制状态
        wp_locked = get_wallpaper_locked()
        if wp_locked:
            self.wp_lbl.configure(text="壁纸修改权限：已禁止")
            self.wp_btn.configure(text="允许修改")
        else:
            self.wp_lbl.configure(text="壁纸修改权限：正常")
            self.wp_btn.configure(text="禁止修改")

        # 2. 了解此图片状态
        sp_hidden = get_spotlight_hidden()
        if sp_hidden:
            self.sp_lbl.configure(text="桌面“了解此图片”：已隐藏")
            self.sp_btn.configure(text="恢复显示")
        else:
            self.sp_lbl.configure(text="桌面“了解此图片”：正常显示")
            self.sp_btn.configure(text="隐藏图标")

        # 3. 浏览器游戏状态
        bg_disabled = get_browser_games_disabled()
        if bg_disabled:
            self.bg_lbl.configure(text="浏览器离线小游戏：已禁用")
            self.bg_btn.configure(text="启用游戏")
        else:
            self.bg_lbl.configure(text="浏览器离线小游戏：正常启用")
            self.bg_btn.configure(text="禁用游戏")

    def trigger_explorer_update(self, action_name):
        """根据自动重启选项，自动或手动重启资源管理器"""
        if self.auto_restart_var.get():
            self.status_lbl.configure(text=f"正在重启资源管理器...")
            self.root.update()
            if restart_explorer():
                self.status_lbl.configure(text="设置已保存，资源管理器已成功重启。")
            else:
                self.status_lbl.configure(text="设置已保存，但资源管理器重启失败。")
        else:
            messagebox.showinfo(
                "操作成功",
                f"设置已修改。\n\n请点击右下角的“重启资源管理器”按钮以应用更改！"
            )
            self.status_lbl.configure(text="设置已保存，等待重启资源管理器...")

    def toggle_wallpaper(self):
        """切换壁纸锁状态"""
        current_state = get_wallpaper_locked()
        next_state = not current_state
        if set_wallpaper_locked(next_state):
            self.refresh_status()
            self.trigger_explorer_update("壁纸限制")
        else:
            messagebox.showerror("错误", "修改壁纸锁定状态失败，请确认是否以管理员权限运行。")

    def toggle_spotlight(self):
        """切换桌面“了解此图片”隐藏状态"""
        current_state = get_spotlight_hidden()
        next_state = not current_state
        if set_spotlight_hidden(next_state):
            self.refresh_status()
            self.trigger_explorer_update("了解此图片")
        else:
            messagebox.showerror("错误", "修改“了解此图片”隐藏状态失败，请确认是否以管理员权限运行。")

    def toggle_browser_games(self):
        """切换浏览器游戏禁用状态"""
        current_state = get_browser_games_disabled()
        next_state = not current_state
        if set_browser_games_disabled(next_state):
            self.refresh_status()
            action = "禁用游戏" if next_state else "启用游戏"
            messagebox.showinfo(
                "操作成功",
                f"离线小游戏设置已保存！\n\n请重新启动 Chrome 或 Edge 浏览器使策略生效。"
            )
            self.status_lbl.configure(text="设置已保存，需要重启浏览器生效。")
        else:
            messagebox.showerror("错误", "修改浏览器游戏限制失败，请检查管理员权限。")

    def manual_restart_explorer(self):
        """手动重启资源管理器"""
        self.status_lbl.configure(text="正在手动重启资源管理器...")
        self.root.update()
        if restart_explorer():
            self.status_lbl.configure(text="资源管理器重启成功。")
            messagebox.showinfo("提示", "资源管理器已成功重启，更改已生效。")
        else:
            self.status_lbl.configure(text="资源管理器重启失败。")
            messagebox.showerror("错误", "无法重启资源管理器，请尝试手动重启。")


def main():
    if sys.platform != "win32":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("系统不支持", "本工具仅支持 Windows 操作系统。")
        sys.exit(1)

    if not is_admin():
        run_as_admin()
        return

    root = tk.Tk()
    app = RestrictionsToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
