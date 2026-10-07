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

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import sys
import time
import tkinter as tk
from datetime import datetime, timedelta
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

# ================= 【共享配置】 =================
MUTEX_NAME = "Local\\MyApp_msedge_helper_Mutex"
SHARED_MEM_NAME = "Local\\MyApp_msedge_helper_Time_Share"
global_mmap_file = None

# 自动关机时间配置（24小时制，例如 20:15 表示晚上 8:15）
SHUTDOWN_HOUR = 20
SHUTDOWN_MINUTE = 15
# ===============================================


if getattr(sys, 'frozen', False):
    RESOURCE_DIR = sys._MEIPASS
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
    """强制结束 Edge 浏览器进程 (使用纯内存 API，0进程创建)"""
    if sys.platform != 'win32': return
    try:
        kernel32 = ctypes.windll.kernel32
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_uint32),
                        ("cntUsage", ctypes.c_uint32),
                        ("th32ProcessID", ctypes.c_uint32),
                        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                        ("th32ModuleID", ctypes.c_uint32),
                        ("cntThreads", ctypes.c_uint32),
                        ("th32ParentProcessID", ctypes.c_uint32),
                        ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", ctypes.c_uint32),
                        ("szExeFile", ctypes.c_char * 260)]
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snapshot != -1:
            pe32 = PROCESSENTRY32()
            pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
            if kernel32.Process32First(snapshot, ctypes.byref(pe32)):
                while True:
                    try:
                        exe_name = pe32.szExeFile.decode('ansi', errors='ignore').lower()
                        if exe_name == 'msedge.exe':
                            hProcess = kernel32.OpenProcess(0x0001, False, pe32.th32ProcessID)
                            if hProcess:
                                kernel32.TerminateProcess(hProcess, 0)
                                kernel32.CloseHandle(hProcess)
                    except:
                        pass
                    if not kernel32.Process32Next(snapshot, ctypes.byref(pe32)):
                        break
            kernel32.CloseHandle(snapshot)
    except:
        pass


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
    设置窗口图标(窗口)
    窗口.title("上网助手")
    窗口.geometry("300x150")
    窗口.attributes('-topmost', True)
    窗口.lift()
    窗口.focus_force()
    
    标签 = tk.Label(窗口, text="请输入密码：", font=("微软雅黑", 11))
    标签.pack(pady=10)
    
    密码框 = tk.Entry(窗口, show="*", font=("微软雅黑", 11), width=20)
    密码框.pack(pady=5)
    密码框.focus()
    
    错误次数 = 0
    
    def 校验密码(event=None):
        nonlocal 错误次数
        输入 = 密码框.get()
        if 输入 == "Pythoa-Scratci":
            # 密码正确，向共享内存写入指令
            向共享内存写入命令("CMD:UNLOCK_90")
            for widget in 窗口.winfo_children():
                widget.destroy()
            tk.Label(窗口, text="联网成功，\n已获得 90 分钟的临时联网时间！", font=("微软雅黑", 11), fg="green").pack(expand=True)
            窗口.after(3000, 窗口.destroy)
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
wifi_unlocked = False
wifi_password_entry = None
wifi_confirm_button = None
root = None

def 检查WiFi是否已连接():
    """
    检查网络连接状态 (重构为极速纯内存 Windows API 检测，支持所有有线/无线网卡，0 CPU开销)
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
    global wifi_warning_window, wifi_password_entry, wifi_confirm_button, wifi_unlocked, root
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            # 仅当应用失去焦点，或者焦点既不在密码框也不在确认按钮上时，才恢复焦点
            curr_focus = root.focus_get() if root else None
            if curr_focus is None:
                wifi_warning_window.attributes('-topmost', True)
                wifi_warning_window.lift()
                if wifi_password_entry and wifi_password_entry.winfo_exists():
                    wifi_password_entry.focus_force()
                else:
                    wifi_warning_window.focus_force()
            elif curr_focus != wifi_password_entry and curr_focus != wifi_confirm_button:
                if wifi_password_entry and wifi_password_entry.winfo_exists():
                    wifi_password_entry.focus()
        except Exception:
            pass
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
            text="检测到 WiFi 已断开，请立刻重新连接！\n\n如需临时关闭全屏提示，请输入解锁密码：", 
            font=("微软雅黑", 18), 
            fg="#ffffff",
            bg='#1e1e1e',
            pady=20,
            wraplength=800,  # 限制文本最大换行宽度
            justify='center'
        )
        label_desc.pack()
        
        # 密码输入框
        密码框 = tk.Entry(main_frame, show="*", font=("微软雅黑", 14), width=25, justify='center')
        密码框.pack(pady=10)
        密码框.focus_force()
        wifi_password_entry = 密码框
        
        def 校验密码(event=None):
            global wifi_unlocked
            输入 = 密码框.get()
            if 输入 == "Pythoa-Scratci":
                wifi_unlocked = True
                关闭WiFi断开警告()
                弹出临时提示("提示", "WiFi断网警告已解锁")
            else:
                弹窗提示_原生("密码错误", "密码错误！", 0x10)
                密码框.delete(0, tk.END)
                密码框.focus()
                
        密码框.bind("<Return>", 校验密码)
        
        按钮 = tk.Button(main_frame, text="确认解锁", font=("微软雅黑", 12), command=校验密码, width=12)
        按钮.pack(pady=10)
        wifi_confirm_button = 按钮
    except Exception:
        pass


def 关闭WiFi断开警告():
    global wifi_warning_window, wifi_password_entry, wifi_confirm_button
    if wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            wifi_warning_window.grab_release()
            wifi_warning_window.destroy()
        except Exception:
            pass
        wifi_warning_window = None
        wifi_password_entry = None
        wifi_confirm_button = None


# ================= 【U 盘连接状态检测】 =================

usb_warning_window = None
usb_unlocked = False
usb_password_entry = None
usb_confirm_button = None

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


def 弹出临时提示(标题, 内容):
    global root
    try:
        top = tk.Toplevel(root)
        设置窗口图标(top)
        top.title(标题)
        top.attributes('-topmost', True)
        tk.Label(top, text=内容, font=("微软雅黑", 10), padx=20, pady=20).pack()
        top.update_idletasks()
        w, h = top.winfo_width(), top.winfo_height()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        top.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")
        root.after(3000, top.destroy)
    except Exception:
        pass


def 显示U盘锁定警告():
    global usb_warning_window, usb_password_entry, usb_confirm_button, usb_unlocked, root
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            # 仅当应用失去焦点，或者焦点既不在密码框也不在确认按钮上时，才恢复焦点
            curr_focus = root.focus_get() if root else None
            if curr_focus is None:
                usb_warning_window.attributes('-topmost', True)
                usb_warning_window.lift()
                if usb_password_entry and usb_password_entry.winfo_exists():
                    usb_password_entry.focus_force()
                else:
                    usb_warning_window.focus_force()
            elif curr_focus != usb_password_entry and curr_focus != usb_confirm_button:
                if usb_password_entry and usb_password_entry.winfo_exists():
                    usb_password_entry.focus()
        except Exception:
            pass
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
        密码框.focus_force()
        usb_password_entry = 密码框
        
        def 校验密码(event=None):
            global usb_unlocked
            输入 = 密码框.get()
            if 输入 == "Pythoa-Scratci":
                usb_unlocked = True
                关闭U盘锁定警告()
                弹出临时提示("提示", "U盘已解锁使用")
            else:
                弹窗提示_原生("密码错误", "密码错误！", 0x10)
                密码框.delete(0, tk.END)
                密码框.focus()
                
        密码框.bind("<Return>", 校验密码)
        
        按钮 = tk.Button(main_frame, text="确认解锁", font=("微软雅黑", 12), command=校验密码, width=12)
        按钮.pack(pady=10)
        usb_confirm_button = 按钮
    except Exception:
        pass


def 关闭U盘锁定警告():
    global usb_warning_window, usb_password_entry, usb_confirm_button
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            usb_warning_window.grab_release()
            usb_warning_window.destroy()
        except Exception:
            pass
        usb_warning_window = None
        usb_password_entry = None
        usb_confirm_button = None


# ================= 【主阻断逻辑】 =================

解锁截止单调 = 0.0
关机已触发 = False

def 保持弹窗最前():
    global wifi_warning_window, usb_warning_window
    # U盘警告窗口在最上
    if usb_warning_window and usb_warning_window.winfo_exists():
        try:
            curr_focus = root.focus_get() if root else None
            # 只有当应用失去焦点时，才强制 lift，避免频繁调用 lift 干扰输入
            if curr_focus is None:
                usb_warning_window.attributes('-topmost', True)
                usb_warning_window.lift()
            if not usb_warning_window.grab_status():
                usb_warning_window.grab_set()
        except Exception:
            pass
    # WiFi警告窗口
    elif wifi_warning_window and wifi_warning_window.winfo_exists():
        try:
            curr_focus = root.focus_get() if root else None
            # 只有当应用失去焦点时，才强制 lift
            if curr_focus is None:
                wifi_warning_window.attributes('-topmost', True)
                wifi_warning_window.lift()
            if not wifi_warning_window.grab_status():
                wifi_warning_window.grab_set()
        except Exception:
            pass


def 周期检测():
    global 解锁截止单调, usb_unlocked, wifi_unlocked, root, 关机已触发
    try:
        现在 = datetime.now()
        # 0. 自动关机检测 (比如晚上 8:15 之后自动关机)
        if 现在.hour > SHUTDOWN_HOUR or (现在.hour == SHUTDOWN_HOUR and 现在.minute >= SHUTDOWN_MINUTE):
            if not 关机已触发:
                关机已触发 = True
                # 启动 60 秒倒计时关机
                执行隐藏命令("shutdown -s -t 60")

        # 0.1 WiFi 状态检测
        if not 检查WiFi是否已连接():
            if not wifi_unlocked:
                显示WiFi断开警告()
        else:
            wifi_unlocked = False
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
            解锁截止单调 = time.monotonic() + 90 * 60

        # 2. 正常限制/放行逻辑
        if time.monotonic() < 解锁截止单调:
            # 处于解锁期，不执行拦截。更新状态为解锁至何时
            剩余秒数 = 解锁截止单调 - time.monotonic()
            预计恢复时间 = datetime.now() + timedelta(seconds=剩余秒数)
            写共享内存(f"STATUS:UNLOCKED_UNTIL_{预计恢复时间.strftime('%H:%M')}")
        else:
            # 正常限制逻辑：对齐整点
            现在 = datetime.now()
            当前分钟 = 现在.minute

            if 当前分钟 < 45:
                # 00 - 44 分钟：断网区间
                禁止_edge_上网()
                恢复时间 = 现在.replace(minute=45, second=0, microsecond=0)
                写共享内存(f"STATUS:BLOCK_UNTIL_{恢复时间.strftime('%H:%M')}")
            else:
                # 45 - 59 分钟：允许上网（恢复区间）
                下个整点 = 现在 + timedelta(hours=1)
                下个整点 = 下个整点.replace(minute=0, second=0, microsecond=0)
                写共享内存(f"STATUS:REST_UNTIL_{下个整点.strftime('%H:%M')}")
                
        # 保持警告窗口最前
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

    # 如果是首个运行的实例，直接作为主程序静默在后台启动，无须人工确认
    初始化共享内存()
    # 删除桌面上的 .sb3 和 .ev3 文件
    删除桌面指定文件()
    # 清空系统回收站
    清空回收站()

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
                win32event.ReleaseMutex(handle)
                handle.close()
            except:
                pass
        sys.exit(0)


if __name__ == "__main__":
    主入口()