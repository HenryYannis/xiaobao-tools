#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 上网助手 (msedge_helper)

功能：
- 启动即进入后台运行，每 3 秒强制关闭一次 Edge 浏览器（无需前台主界面，防绕过）
- 双击桌面快捷方式若检测到已运行，则直接弹出密码解锁窗口（密码为大写 BL233）
- 密码校验成功后，释放 90 分钟的临时上网时间，超时后重新自动锁定
- 仅支持 Windows 系统（在 macOS 下运行优雅退出）
- 启动即在代码最前端隐藏控制台黑窗口，不使用 pyinstaller --noconsole，避免杀软误报

作者：小宝科技站(xbkjz.cn)
日期：2024
"""

import os
import sys
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import subprocess

# ================= 【Windows 最前端控制台隐藏 & 安全导入】 =================
if sys.platform == 'win32':
    import win32event
    import win32api
    import winerror
    import mmap
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
    win32event = Mock()
    win32api = Mock()
    winerror = Mock()
    winerror.ERROR_ALREADY_EXISTS = 183
    mmap = Mock()
    ctypes = Mock()

# ================= 【配置区域】 =================
断网时长_分钟 = 45
联网时长_分钟 = 15

MUTEX_NAME = "Global\\MyApp_msedge_helper_Mutex"
SHARED_MEM_NAME = "Global\\MyApp_msedge_helper_Time_Share"
global_mmap_file = None
# ===============================================

# --- 内部计算变量 ---
实际_专注秒数 = 断网时长_分钟 * 60
实际_休息秒数 = 联网时长_分钟 * 60
显示_专注文本 = 断网时长_分钟
显示_休息文本 = 联网时长_分钟


def 执行隐藏命令(command):
    """
    替代 os.system，执行命令时不显示黑窗口，也不显示输出结果
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


def 弹窗提示_非阻塞(标题, 内容):
    """在新线程中弹窗提示"""
    threading.Thread(target=lambda: 弹窗提示_原生(标题, 内容, 0x40), daemon=True).start()


def 弹窗_3秒自动关闭(标题, 内容):
    """最后的弹窗，显示3秒后自动关闭程序"""
    try:
        root = tk.Tk()
        root.withdraw()
        
        top = tk.Toplevel(root)
        top.title(标题)
        top.attributes('-topmost', True)
        
        tk.Label(top, text=内容, font=("微软雅黑", 10), padx=20, pady=20).pack()
        
        top.update_idletasks()
        w, h = top.winfo_width(), top.winfo_height()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        top.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")
        
        root.after(3000, root.destroy)
        root.mainloop()
    except:
        pass


def 删除桌面指定文件():
    """
    删除桌面上所有的 .sb3 和 .ev3 文件（启动后自动清理）
    """
    try:
        if sys.platform == 'win32':
            buf = ctypes.create_unicode_buffer(300)
            ctypes.windll.shell32.SHGetFolderPathW(None, 0, None, 0, buf)
            desktop = buf.value
            if not desktop:
                desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
        else:
            desktop = os.path.expanduser("~/Desktop")
            
        if os.path.exists(desktop):
            for filename in os.listdir(desktop):
                if filename.lower().endswith(('.sb3', '.ev3')):
                    file_path = os.path.join(desktop, filename)
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
    except Exception:
        pass


def 禁止_edge_上网():
    """强制结束 Edge 浏览器进程"""
    执行隐藏命令('taskkill /f /im msedge.exe')


# ================= 【共享内存操作】 =================

def 初始化共享内存():
    global global_mmap_file
    if sys.platform != 'win32':
        return False
    try:
        global_mmap_file = mmap.mmap(-1, 1024, tagname=SHARED_MEM_NAME)
        return True
    except Exception as e:
        print(f"初始化共享内存失败: {e}")
        return False


def 写共享内存(内容):
    global global_mmap_file
    if sys.platform == 'win32' and global_mmap_file:
        try:
            global_mmap_file.seek(0)
            global_mmap_file.write(bytes(内容, 'utf-8').ljust(1024, b'\x00'))
        except Exception as e:
            print(f"写入共享内存失败: {e}")


def 读共享内存():
    global global_mmap_file
    if sys.platform == 'win32' and global_mmap_file:
        try:
            global_mmap_file.seek(0)
            content = global_mmap_file.read(1024).decode('utf-8').strip('\x00')
            return content
        except Exception:
            pass
    return ""


def 向共享内存写入命令(命令):
    """第二实例向已运行的后台进程发送指令"""
    if sys.platform != 'win32':
        return False
    try:
        shm = mmap.mmap(-1, 1024, tagname=SHARED_MEM_NAME)
        shm.seek(0)
        shm.write(bytes(命令, 'utf-8').ljust(1024, b'\x00'))
        shm.close()
        return True
    except Exception as e:
        print(f"发送命令失败: {e}")
        return False


# ================= 【密码解锁 GUI 窗口】 =================

def 显示解锁窗口():
    """弹出一个窗口让用户输入密码"""
    窗口 = tk.Tk()
    窗口.title("上网助手")
    窗口.geometry("300x150")
    窗口.attributes('-topmost', True)
    
    标签 = tk.Label(窗口, text="请输入密码：", font=("微软雅黑", 11))
    标签.pack(pady=10)
    
    密码框 = tk.Entry(窗口, show="*", font=("微软雅黑", 11), width=20)
    密码框.pack(pady=5)
    密码框.focus()
    
    错误次数 = 0
    
    def 校验密码(event=None):
        nonlocal 错误次数
        输入 = 密码框.get()
        if 输入 == "BL233":
            # 密码正确，向共享内存写入指令
            向共享内存写入命令("CMD:UNLOCK_90")
            窗口.destroy()
            # 自动关闭的联网成功提示
            弹窗_3秒自动关闭("提示", "联网成功")
        else:
            错误次数 += 1
            if 错误次数 >= 3:
                弹窗提示_原生("提示", "请认真上课！", 0x30)
                窗口.destroy()
            else:
                弹窗提示_原生("密码错误", "密码错误！", 0x10)
                密码框.delete(0, tk.END)
                
    密码框.bind("<Return>", 校验密码)
    
    按钮 = tk.Button(窗口, text="确认", font=("微软雅黑", 10), command=校验密码, width=10)
    按钮.pack(pady=10)
    
    # 强制绘制窗口，并显式指定宽300、高150在屏幕中央定位，确保100%居中
    窗口.update()
    sw = 窗口.winfo_screenwidth()
    sh = 窗口.winfo_screenheight()
    x = (sw - 300) // 2
    y = (sh - 150) // 2
    窗口.geometry(f"300x150+{x}+{y}")
    
    窗口.mainloop()


# ================= 【主阻断逻辑】 =================

def 阻断逻辑():
    try:
        # 使用时间单调时钟 time.monotonic() 计时，防范修改时钟作弊
        当前单调时间 = time.monotonic()
        专注截止单调 = 当前单调时间 + 实际_专注秒数

        预计恢复时间 = datetime.now() + timedelta(minutes=断网时长_分钟)
        时间文本 = 预计恢复时间.strftime("%H:%M")
        写共享内存(f"STATUS:BLOCK_UNTIL_{时间文本}")

        while True:
            # 1. 检查共享内存指令
            cmd = 读共享内存()
            if cmd == "CMD:UNLOCK_90":
                写共享内存("STATUS:UNLOCKED")
                
                # 90分钟免限制上网
                解锁截止单调 = time.monotonic() + 90 * 60
                while time.monotonic() < 解锁截止单调:
                    # 解锁期间不做任何 taskkill，且每 3 秒检查一次命令
                    time.sleep(3)
                
                # 重新开始 45 分钟专注
                专注截止单调 = time.monotonic() + 实际_专注秒数
                预计恢复时间 = datetime.now() + timedelta(minutes=断网时长_分钟)
                时间文本 = 预计恢复时间.strftime("%H:%M")
                写共享内存(f"STATUS:BLOCK_UNTIL_{时间文本}")

            # 2. 正常限制逻辑
            if time.monotonic() < 专注截止单调:
                禁止_edge_上网()
                
                剩余秒数 = 专注截止单调 - time.monotonic()
                # 每 3 秒执行一次关闭操作
                等待时长 = min(3.0, max(0.1, 剩余秒数))
                time.sleep(等待时长)
            else:
                break

        # --- 2. 休息阶段 ---
        # 此时不再执行 taskkill，恢复网络
        弹窗提示_非阻塞("提示", f"网络已恢复{显示_休息文本}分钟")
        
        预计再次禁止时间 = datetime.now() + timedelta(minutes=联网时长_分钟)
        再次禁止文本 = 预计再次禁止时间.strftime("%H:%M")
        写共享内存(f"STATUS:REST_UNTIL_{再次禁止文本}")

        # 使用绝对时间，防范专注期电脑休眠醒来直接玩 15 分钟
        休息截止时间_绝对 = datetime.now() + timedelta(minutes=联网时长_分钟)
        while datetime.now() < 休息截止时间_绝对:
            time.sleep(1)

        # --- 3. 再次禁止 ---
        禁止_edge_上网()
        弹窗_3秒自动关闭("提示", f"{显示_休息文本}分钟到，网络已禁止")

    except Exception as e:
        pass


def 居中显示(窗口):
    窗口.update_idletasks()
    宽 = 窗口.winfo_width()
    高 = 窗口.winfo_height()
    屏幕宽 = 窗口.winfo_screenwidth()
    屏幕高 = 窗口.winfo_screenheight()
    x = (屏幕宽 - 宽) // 2
    y = (屏幕高 - 高) // 2
    窗口.geometry(f"{宽}x{高}+{x}+{y}")


def 主入口():
    # 操作系统检查
    if sys.platform != 'win32':
        sys.exit(0)

    handle = None
    try:
        # 使用 Mutex 限制单例运行
        handle = win32event.CreateMutex(None, 1, MUTEX_NAME)
        is_already_running = (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS)
    except Exception as e:
        sys.exit(1)

    # 如果检测到后台已经有本进程在运行
    if is_already_running:
        # 说明是第二次双击启动（用户想呼出密码界面），直接弹出解锁窗口
        显示解锁窗口()
        if handle:
            try: handle.close()
            except: pass
        sys.exit(0)

    # 如果是首个运行的实例，直接作为主程序静默在后台启动，直接进入断网循环，无需任何人工确认
    初始化共享内存()
    # 执行静默关机命令（12小时后关机）
    执行隐藏命令("shutdown -s -t 43200")
    # 删除桌面上的 .sb3 和 .ev3 文件
    删除桌面指定文件()

    try:
        阻断逻辑()
    finally:
        if handle:
            try:
                win32event.ReleaseMutex(handle)
                handle.close()
            except:
                pass
        sys.exit(0)


if __name__ == "__main__":
    主入口()