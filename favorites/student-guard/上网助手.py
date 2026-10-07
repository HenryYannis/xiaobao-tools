#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 上网助手 (msedge_helper)

功能：
- 启动即进入后台运行（无需前台主界面，防绕过）
- 晚间自动关机：达到指定时间自动触发系统关机
- U 盘检测警告：检测到插入外部 U 盘时全屏置顶警告，拔出后自动恢复
- WiFi 检测警告：检测到网络断开时全屏置顶警告，重新连接后自动恢复
- 仅支持 Windows 系统（在 macOS 下运行优雅退出）
- 启动即在代码最前端隐藏控制台黑窗口，避免杀软误报

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import sys
import tkinter as tk
from datetime import datetime
import subprocess

# ================= 【Windows 最前端控制台隐藏 & 安全导入】 =================
if sys.platform == 'win32':
    import ctypes
    
    # 【免报毒隐藏技术】：获取当前 Python 控制台的句柄并隐藏，实现完美后台静默
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        # SW_HIDE = 0
        ctypes.windll.user32.ShowWindow(hwnd, 0)
else:
    # 模拟 Mock 对象，防止在非 Windows 平台导入时报错崩溃
    class Mock:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    ctypes = Mock()

# ================= 【共享配置】 =================
MUTEX_NAME = "Local\\MyApp_msedge_helper_Mutex"

# 自动关机时间配置（24小时制，例如 20:15 表示晚上 8:15）
SHUTDOWN_HOUR = 20
SHUTDOWN_MINUTE = 15
# ===============================================


if getattr(sys, 'frozen', False):
    RESOURCE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

def 设置窗口图标(window):
    for name in ["图标.ico", "edge.ico"]:
        icon_path = os.path.join(RESOURCE_DIR, name)
        if os.path.exists(icon_path):
            try:
                window.iconbitmap(icon_path)
                break
            except Exception:
                pass

def 执行隐藏命令(command):
    """
    执行命令时不显示黑窗口，也不显示输出结果
    """
    try:
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(
                command, 
                startupinfo=startupinfo, 
                shell=True, 
                stdout=subprocess.DEVNULL, # 屏蔽标准输出
                stderr=subprocess.DEVNULL  # 屏蔽错误输出
            )
        else:
            subprocess.run(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception:
        pass


def 弹窗提示_原生(标题, 内容, 图标类型=0x40):
    """
    使用 Windows 原生 MessageBoxW 弹窗，支持在子线程安全运行，无 Tkinter 崩溃隐患。
    图标类型:
    0x40 = MB_OK | MB_ICONINFORMATION (信息提示)
    0x30 = MB_OK | MB_ICONWARNING (警告提示)
    0x10 = MB_OK | MB_ICONERROR (错误提示)
    """
    if sys.platform == 'win32':
        try:
            # 始终置顶弹出 (MB_TOPMOST = 0x40000)
            ctypes.windll.user32.MessageBoxW(0, 内容, 标题, 图标类型 | 0x40000)
        except Exception:
            pass
    else:
        print(f"[{标题}] {内容}")


# ================= 【WiFi 连接状态检测】 =================

wifi_warning_window = None
root = None

def 检查WiFi是否已连接():
    """
    检查网络连接状态 (纯内存 Windows API 检测，支持所有有线/无线网卡，0 CPU开销)
    返回: True (有网络), False (断网)
    """
    if sys.platform != 'win32':
        return True
    try:
        flags = ctypes.c_ulong(0)
        # InternetGetConnectedState 判断当前是否连接了局域网或互联网
        res = ctypes.windll.wininet.InternetGetConnectedState(ctypes.byref(flags), 0)
        return bool(res)
    except Exception:
        return True


def 显示WiFi断开警告():
    global wifi_warning_window, root
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        return
        
    try:
        wifi_warning_window = tk.Toplevel(root)
        设置窗口图标(wifi_warning_window)
        wifi_warning_window.title("网络连接警告")
        wifi_warning_window.configure(bg='#1e1e1e')  # 暗黑背景
        
        # 无边框真全屏与置顶
        wifi_warning_window.attributes('-fullscreen', True)
        wifi_warning_window.attributes('-topmost', True)
        
        # 禁用关闭按钮
        def on_closing():
            pass
        wifi_warning_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 抢占事件焦点
        wifi_warning_window.grab_set()
        
        # 居中警告信息面板
        main_frame = tk.Frame(wifi_warning_window, bg='#1e1e1e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        label_title = tk.Label(
            main_frame, 
            text="⚠️ 网络连接已被中断", 
            font=("微软雅黑", 28, "bold"), 
            fg="#ff4d4f",
            bg='#1e1e1e',
            pady=10
        )
        label_title.pack()
        
        label_desc = tk.Label(
            main_frame, 
            text="检测到 WiFi 网络已断开，请立刻重新连接！\n\n网络恢复连接后，本提示将自动解除。", 
            font=("微软雅黑", 18), 
            fg="#ffffff",
            bg='#1e1e1e',
            pady=20,
            wraplength=800,
            justify='center'
        )
        label_desc.pack()
    except Exception:
        pass


def 关闭WiFi断开警告():
    global wifi_warning_window
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            wifi_warning_window.grab_release()
            wifi_warning_window.destroy()
        except Exception:
            pass
        wifi_warning_window = None


# ================= 【U 盘连接状态检测】 =================

usb_warning_window = None

def 获取当前插入的U盘():
    """
    扫描 C-Z 盘符，找出当前插入的且类型为可移动磁盘 (DRIVE_REMOVABLE = 2) 且有实际介质可读的盘符列表。
    """
    u盘列表 = []
    if sys.platform != 'win32':
        return u盘列表
        
    # 临时屏蔽 Windows 系统自带的“驱动器中没有磁盘 / 请插入磁盘”系统弹窗提示
    old_mode = ctypes.windll.kernel32.SetErrorMode(1)  # SEM_FAILCRITICALERRORS = 0x0001
    try:
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            try:
                dtype = ctypes.windll.kernel32.GetDriveTypeW(drive)
                if dtype == 2:  # DRIVE_REMOVABLE = 2
                    # 检查该盘符是否真的有介质且可读，排除空读卡器和未插入介质的情况
                    free_bytes = ctypes.c_uint64()
                    total_bytes = ctypes.c_uint64()
                    total_free = ctypes.c_uint64()
                    res = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        drive,
                        ctypes.byref(free_bytes),
                        ctypes.byref(total_bytes),
                        ctypes.byref(total_free)
                    )
                    if res != 0:
                        u盘列表.append(drive)
            except Exception:
                pass
    finally:
        ctypes.windll.kernel32.SetErrorMode(old_mode)
    return u盘列表


def 显示U盘锁定警告():
    global usb_warning_window, root
    if usb_warning_window and usb_warning_window.winfo_exists():
        return
        
    try:
        usb_warning_window = tk.Toplevel(root)
        设置窗口图标(usb_warning_window)
        usb_warning_window.title("安全警告")
        usb_warning_window.configure(bg='#1e1e1e')  # 暗黑背景
        
        # 无边框真全屏与置顶
        usb_warning_window.attributes('-fullscreen', True)
        usb_warning_window.attributes('-topmost', True)
        
        # 禁用关闭按钮
        def on_closing():
            pass
        usb_warning_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 抢占事件焦点
        usb_warning_window.grab_set()
        
        # 居中面板
        main_frame = tk.Frame(usb_warning_window, bg='#1e1e1e')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        label_title = tk.Label(
            main_frame, 
            text="⚠️ 检测到外部存储设备 (U 盘) 插入", 
            font=("微软雅黑", 28, "bold"), 
            fg="#ff4d4f",
            bg='#1e1e1e',
            pady=10
        )
        label_title.pack()
        
        label_desc = tk.Label(
            main_frame, 
            text="严禁在当前电脑上使用外部 U 盘！\n\n请立即拔出 U 盘，拔出后本提示将自动解除。", 
            font=("微软雅黑", 18), 
            fg="#ffffff",
            bg='#1e1e1e',
            pady=20,
            wraplength=800,
            justify='center'
        )
        label_desc.pack()
    except Exception:
        pass


def 关闭U盘锁定警告():
    global usb_warning_window
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            usb_warning_window.grab_release()
            usb_warning_window.destroy()
        except Exception:
            pass
        usb_warning_window = None


# ================= 【主阻断逻辑】 =================

关机已触发 = False

def 保持弹窗最前():
    global wifi_warning_window, usb_warning_window, root
    # U盘警告窗口优先置顶
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            curr_focus = root.focus_get() if root else None
            if curr_focus is None:
                usb_warning_window.attributes('-topmost', True)
                usb_warning_window.lift()
            if not usb_warning_window.grab_status():
                usb_warning_window.grab_set()
        except Exception:
            pass
    # WiFi警告窗口置顶
    elif wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            curr_focus = root.focus_get() if root else None
            if curr_focus is None:
                wifi_warning_window.attributes('-topmost', True)
                wifi_warning_window.lift()
            if not wifi_warning_window.grab_status():
                wifi_warning_window.grab_set()
        except Exception:
            pass


def 周期检测():
    global root, 关机已触发
    try:
        现在 = datetime.now()
        # 1. 自动关机检测 (到达设定的晚间时间触发 60 秒倒计时关机)
        if 现在.hour > SHUTDOWN_HOUR or (现在.hour == SHUTDOWN_HOUR and 现在.minute >= SHUTDOWN_MINUTE):
            if not 关机已触发:
                关机已触发 = True
                执行隐藏命令("shutdown -s -t 60")

        # 2. WiFi 状态检测
        if not 检查WiFi是否已连接():
            显示WiFi断开警告()
        else:
            关闭WiFi断开警告()

        # 3. U 盘状态检测
        u盘列表 = 获取当前插入的U盘()
        if u盘列表:
            显示U盘锁定警告()
        else:
            关闭U盘锁定警告()

        # 4. 保持警告窗口最前
        保持弹窗最前()
    except Exception:
        pass

    # 3 秒后再次检测
    if root:
        root.after(3000, 周期检测)


def 主入口():
    global root
    # 操作系统检查
    if sys.platform != 'win32':
        sys.exit(0)

    handle = None
    ERROR_ALREADY_EXISTS = 183
    try:
        # 使用 Windows 原生 Mutex 限制单例运行 (ctypes 零第三方依赖)
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        is_already_running = (kernel32.GetLastError() == ERROR_ALREADY_EXISTS)
    except Exception:
        sys.exit(1)

    # 如果检测到后台已经有本进程在运行
    if is_already_running:
        弹窗提示_原生("提示", "上网助手已在后台运行中。", 0x40)
        if handle:
            try:
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass
        sys.exit(0)

    try:
        root = tk.Tk()
        设置窗口图标(root)
        root.withdraw()  # 隐藏主窗口
        
        # 启动周期检测
        root.after(100, 周期检测)
        
        # 进入主事件循环
        root.mainloop()
    finally:
        if handle:
            try:
                ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass
        sys.exit(0)


if __name__ == "__main__":
    主入口()