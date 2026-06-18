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

MUTEX_NAME = "Local\\MyApp_msedge_helper_Mutex"
SHARED_MEM_NAME = "Local\\MyApp_msedge_helper_Time_Share"
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


def 清空回收站():
    """
    通过 Windows API 静默清空系统回收站（无提示音、无确认框、无进度条）
    """
    if sys.platform == 'win32':
        try:
            # Flags: SHERB_NOCONFIRMATION (0x00000001) | SHERB_NOPROGRESSUI (0x00000002) | SHERB_NOSOUND (0x00000004)
            flags = 0x00000001 | 0x00000002 | 0x00000004
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
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


# ================= 【WiFi 连接状态检测】 =================

wifi_warning_window = None

def 检查WiFi是否已连接():
    """
    检查 WiFi 接口的连接状态。
    返回: True (WiFi 已连接，或系统无 WiFi 接口无需报错)，False (有 WiFi 接口但处于断开状态)
    """
    if sys.platform != 'win32':
        return True
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.run(
            'netsh wlan show interfaces',
            startupinfo=startupinfo,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        output = res.stdout
        
        # 如果系统里没有无线网卡，不判定为断开
        if "没有无线接口" in output or "no wireless interface" in output or "There is no wireless interface" in output:
            return True
            
        # 如果有无线网卡，检查其状态
        for line in output.splitlines():
            line_lower = line.lower()
            if "state" in line_lower or "状态" in line_lower:
                if "connected" in line_lower or "已连接" in line_lower:
                    return True
                if "disconnected" in line_lower or "已断开" in line_lower:
                    return False
        
        # 默认返回 True 避免误报
        return True
    except Exception:
        return True


def 显示WiFi断开警告():
    global wifi_warning_window
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            wifi_warning_window.attributes('-topmost', True)
            wifi_warning_window.focus_force()
        except Exception:
            pass
        return
        
    def 创建窗口():
        global wifi_warning_window
        try:
            wifi_warning_window = tk.Tk()
            wifi_warning_window.title("网络连接警告")
            wifi_warning_window.configure(bg='#1e1e1e')  # 暗黑背景
            
            # 最大化（保留任务栏）与置顶
            wifi_warning_window.state('zoomed')
            wifi_warning_window.attributes('-topmost', True)
            
            # 禁用关闭按钮 (X)
            def on_closing():
                pass
            wifi_warning_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # 防止最小化：如果窗口被最小化 (iconic) 或隐藏，立即恢复最大化
            def restore_window(event=None):
                try:
                    if wifi_warning_window.state() == 'iconic':
                        wifi_warning_window.state('zoomed')
                        wifi_warning_window.attributes('-topmost', True)
                except Exception:
                    pass
            wifi_warning_window.bind("<Unmap>", lambda e: wifi_warning_window.after(10, restore_window))
            wifi_warning_window.bind("<Map>", restore_window)
            
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
                text="检测到您的 WiFi 已断开，请立刻重新连接！\n\n温馨提示：即使处于断网状态，也无法打开浏览器或游玩离线小游戏。", 
                font=("微软雅黑", 18), 
                fg="#ffffff",
                bg='#1e1e1e',
                pady=20,
                wraplength=800,  # 限制文本最大换行宽度
                justify='center'
            )
            label_desc.pack()
            
            wifi_warning_window.mainloop()
        except Exception:
            pass

    threading.Thread(target=创建窗口, daemon=True).start()


def 关闭WiFi断开警告():
    global wifi_warning_window
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            wifi_warning_window.destroy()
        except Exception:
            pass
        wifi_warning_window = None


# ================= 【U 盘连接状态检测】 =================

usb_warning_window = None
usb_unlocked = False

def 获取当前插入的U盘():
    """
    扫描 C-Z 盘符，找出当前插入的且类型为可移动磁盘 (DRIVE_REMOVABLE = 2) 且有实际介质可读的盘符列表。
    """
    u盘列表 = []
    if sys.platform != 'win32':
        return u盘列表
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
    return u盘列表


def 显示U盘锁定警告():
    global usb_warning_window, usb_unlocked
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            usb_warning_window.attributes('-topmost', True)
            usb_warning_window.focus_force()
        except Exception:
            pass
        return
        
    def 创建窗口():
        global usb_warning_window, usb_unlocked
        try:
            usb_warning_window = tk.Tk()
            usb_warning_window.title("安全警告")
            usb_warning_window.configure(bg='#1e1e1e')  # 暗黑背景
            
            # 最大化且置顶
            usb_warning_window.state('zoomed')
            usb_warning_window.attributes('-topmost', True)
            
            # 禁用关闭按钮
            def on_closing():
                pass
            usb_warning_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # 防止最小化
            def restore_window(event=None):
                try:
                    if usb_warning_window.state() == 'iconic':
                        usb_warning_window.state('zoomed')
                        usb_warning_window.attributes('-topmost', True)
                except Exception:
                    pass
            usb_warning_window.bind("<Unmap>", lambda e: usb_warning_window.after(10, restore_window))
            usb_warning_window.bind("<Map>", restore_window)
            
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
                text="使用 U 盘需要输入解锁密码，或者请立即拔出 U 盘！", 
                font=("微软雅黑", 18), 
                fg="#ffffff",
                bg='#1e1e1e',
                pady=20,
                wraplength=800,
                justify='center'
            )
            label_desc.pack()
            
            # 密码输入框
            密码框 = tk.Entry(main_frame, show="*", font=("微软雅黑", 14), width=25, justify='center')
            密码框.pack(pady=10)
            密码框.focus()
            
            def 校验密码(event=None):
                global usb_unlocked
                输入 = 密码框.get()
                if 输入 == "BL233":
                    usb_unlocked = True
                    usb_warning_window.destroy()
                    弹窗_3秒自动关闭("提示", "U盘已解锁使用")
                else:
                    弹窗提示_原生("密码错误", "密码错误！", 0x10)
                    密码框.delete(0, tk.END)
                    
            密码框.bind("<Return>", 校验密码)
            
            按钮 = tk.Button(main_frame, text="确认解锁", font=("微软雅黑", 12), command=校验密码, width=12)
            按钮.pack(pady=10)
            
            usb_warning_window.mainloop()
        except Exception:
            pass

    threading.Thread(target=创建窗口, daemon=True).start()


def 关闭U盘锁定警告():
    global usb_warning_window
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            usb_warning_window.destroy()
        except Exception:
            pass
        usb_warning_window = None


# ================= 【主阻断逻辑】 =================

def 阻断逻辑():
    try:
        # 声明 GetTickCount64 返回值类型为 64 位无符号整数
        if sys.platform == 'win32' and hasattr(ctypes, 'windll'):
            try:
                ctypes.windll.kernel32.GetTickCount64.restype = ctypes.c_uint64
            except Exception:
                pass

        # 初始化基准时间
        def 获取当前Tick():
            if sys.platform == 'win32' and hasattr(ctypes, 'windll'):
                return ctypes.windll.kernel32.GetTickCount64()
            return int(time.time() * 1000)

        基准时间 = datetime.now()
        基准Tick = 获取当前Tick()
        解锁截止单调 = 0.0

        while True:
            # 0. WiFi 状态检测
            if not 检查WiFi是否已连接():
                显示WiFi断开警告()
            else:
                关闭WiFi断开警告()

            # 0.1 U 盘状态检测
            u盘列表 = 获取当前插入的U盘()
            if u盘列表:
                if not usb_unlocked:
                    显示U盘锁定警告()
            else:
                usb_unlocked = False
                关闭U盘锁定警告()

            # 1. 检查共享内存指令
            cmd = 读共享内存()
            if cmd == "CMD:UNLOCK_90":
                写共享内存("STATUS:UNLOCKED")
                # 90分钟免限制上网
                解锁截止单调 = time.monotonic() + 90 * 60
                continue

            # 2. 防作弊检测
            now_time = datetime.now()
            now_tick = 获取当前Tick()

            # 计算流逝时间
            流逝时间_秒 = (now_time - 基准时间).total_seconds()
            流逝Tick_秒 = (now_tick - 基准Tick) / 1000.0

            # 检查是否有时间跳变（差值大于 15 秒判定为作弊）
            if abs(流逝时间_秒 - 流逝Tick_秒) > 15:
                写共享内存("STATUS:CHEAT_DETECTED")
                # 发生作弊，进入永久阻断模式
                while True:
                    禁止_edge_上网()
                    time.sleep(3)

            # 3. 检查是否在 90 分钟解锁期内
            if time.monotonic() < 解锁截止单调:
                # 处于解锁期，不执行拦截。更新状态为解锁至何时
                剩余秒数 = 解锁截止单调 - time.monotonic()
                预计恢复时间 = datetime.now() + timedelta(seconds=剩余秒数)
                写共享内存(f"STATUS:UNLOCKED_UNTIL_{预计恢复时间.strftime('%H:%M')}")
                
                # 每次重新进入正常循环时，需要重置防作弊基准，以防止解锁期结束后的时钟漂移
                基准时间 = datetime.now()
                基准Tick = 获取当前Tick()
                
                time.sleep(3)
                continue

            # 4. 正常限制逻辑：对齐整点
            现在 = datetime.now()
            当前分钟 = 现在.minute

            if 当前分钟 < 45:
                # 00 - 44 分钟：断网区间
                禁止_edge_上网()
                
                # 计算距离 45 分钟还有多少秒
                剩余秒数 = (45 - 当前分钟) * 60 - 现在.second
                # 显示预计恢复时间：当前小时的 45 分
                恢复时间 = 现在.replace(minute=45, second=0, microsecond=0)
                写共享内存(f"STATUS:BLOCK_UNTIL_{恢复时间.strftime('%H:%M')}")
                
                # 等待下一次检测，最长 3 秒
                time.sleep(min(3.0, max(0.1, 剩余秒数)))
            else:
                # 45 - 59 分钟：允许上网（恢复区间）
                # 计算距离下一个整点还有多少秒
                剩余秒数 = (60 - 当前分钟) * 60 - 现在.second
                # 显示预计断网时间：下一个整点 (当前小时 + 1 的 00 分)
                下个整点 = 现在 + timedelta(hours=1)
                下个整点 = 下个整点.replace(minute=0, second=0, microsecond=0)
                写共享内存(f"STATUS:REST_UNTIL_{下个整点.strftime('%H:%M')}")
                
                # 等待下一次检测，最长 3 秒
                time.sleep(min(3.0, max(0.1, 剩余秒数)))
    except Exception:
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
    # 清空系统回收站
    清空回收站()

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