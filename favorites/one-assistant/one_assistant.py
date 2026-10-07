#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 (Lab Policy Configurator)

核心管控项目：
1. Edge 浏览器访问管控（白名单锁定、启动主页直达、禁用 Surf 冲浪小游戏、禁止下载）
2. Chrome 浏览器访问管控（白名单锁定、启动主页直达、禁用 Dino 恐龙小游戏、禁止下载）
3. 桌面与文件系统规范（统一壁纸与锁屏防篡改、始终显示文件后缀名、隐藏聚焦图标）
4. 编程环境优化（清华 / 阿里 pip 镜像源配置、解除 Windows 260 字符长路径限制）

设计规范：
- 零依赖：纯 Python 标准库（tkinter, winreg, ctypes, socket）
- 极简中性视觉：配色不超过 3 种中性色调，无 3D 凹凸复古感，无 emoji 图标

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import sys
import time
import tempfile
import ctypes
import configparser
import shutil
import subprocess
import socket
import webbrowser
import tkinter as tk
from tkinter import messagebox, scrolledtext
from winreg import (
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    OpenKey, CreateKey, SetValueEx, DeleteValue, DeleteKey,
    EnumKey, QueryValueEx, REG_DWORD, REG_SZ, KEY_READ, KEY_ALL_ACCESS
)

# --- 路径与资源配置 ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
if getattr(sys, 'frozen', False):
    RESOURCE_DIR = sys._MEIPASS
else:
    RESOURCE_DIR = _SCRIPT_DIR

# pip 镜像源地址
PYPI_TUNA_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
PYPI_ALIYUN_URL = "https://mirrors.aliyun.com/pypi/simple/"

# 浏览器默认启动直达地址（可修改为任意业务或发布网址）
DEFAULT_STARTUP_URL = "https://xbkjz.cn/edu"

# 壁纸图片文件名与锁屏路径
WALLPAPER_FILENAME = "bizhi.jpg"
_LOCKSCREEN_REG_PATH = r"SOFTWARE\Policies\Microsoft\Windows\Personalization"
_LOCKSCREEN_REG_VALUE = "LockScreenImage"
_WALLPAPER_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
_WALLPAPER_DEPLOY_PATH = os.path.join(_WALLPAPER_DEPLOY_DIR, WALLPAPER_FILENAME)

# 白名单配置文件与默认规则
WHITELIST_FILENAME = "whitelist.txt"
DEFAULT_ALLOWLIST = [
    # 本地与浏览器内部协议
    "localhost",
    "127.0.0.1",
    "file://*",
    "edge://*",
    "chrome://*",
    # 必应、MSN 与微软底层服务 (保障新标签页与系统弹窗畅通)
    "bing.com",
    "bing.net",
    "bingapis.com",
    "msn.cn",
    "msn.com",
    "microsoft.com",
    "live.com",
    "azureedge.net",
    "aka.ms",
    # 小宝科技站 & xbyxz.cn
    "xbkjz.cn",
    "xbyxz.cn",
    # 中国电子学会
    "qceit.org.cn",
    # Tinkercad 建模与电路
    "tinkercad.com",
    # 信息学奥赛一本通
    "ybt.ssoier.cn",
]

# --- 注册表路径常量 ---
# 桌面个性化
REG_WALLPAPER_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
REG_WALLPAPER_VALUE = "NoChangingWallPaper"
REG_SPOTLIGHT_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
REG_SPOTLIGHT_VALUE = "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}"

# 浏览器基础键路径
REG_EDGE_PATH = r"SOFTWARE\Policies\Microsoft\Edge"
REG_CHROME_PATH = r"SOFTWARE\Policies\Google\Chrome"

# 浏览器通用子键与值名
REG_BROWSER_BLOCKLIST_SUBKEY = "URLBlocklist"
REG_BROWSER_ALLOWLIST_SUBKEY = "URLAllowlist"
REG_BROWSER_DOWNLOAD_VALUE = "DownloadRestrictions"

# 离线游戏值名
REG_EDGE_GAME_VALUE = "AllowSurfGame"
REG_CHROME_GAME_VALUE = "AllowDinosaurEasterEgg"

# 系统与文件配置
REG_LONGPATHS_PATH = r"SYSTEM\CurrentControlSet\Control\FileSystem"
REG_LONGPATHS_VALUE = "LongPathsEnabled"
REG_EXPLORER_ADVANCED_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
REG_HIDE_FILE_EXT_VALUE = "HideFileExt"


# --- 辅助函数：系统信息 ---
def get_device_info():
    """获取本机计算机名与局域网 IP"""
    try:
        hostname = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return hostname, ip
    except Exception:
        try:
            return socket.gethostname(), socket.gethostbyname(socket.gethostname())
        except Exception:
            return "PC-STUDENT", "127.0.0.1"


# --- 辅助函数：壁纸与锁屏 ---
def get_wallpaper_source_path():
    return os.path.join(RESOURCE_DIR, WALLPAPER_FILENAME)

def 设置窗口图标(window):
    icon_path = os.path.join(RESOURCE_DIR, "system.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception:
            pass

def _deploy_wallpaper():
    src = get_wallpaper_source_path()
    if not os.path.exists(src):
        return None, f"未找到壁纸文件：{src}"
    try:
        os.makedirs(_WALLPAPER_DEPLOY_DIR, exist_ok=True)
        shutil.copy2(src, _WALLPAPER_DEPLOY_PATH)
        return _WALLPAPER_DEPLOY_PATH, ""
    except Exception as e:
        return src, str(e)

def set_desktop_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return bool(result)

def set_lockscreen_image(image_path):
    try:
        with CreateKey(HKEY_LOCAL_MACHINE, _LOCKSCREEN_REG_PATH) as key:
            SetValueEx(key, _LOCKSCREEN_REG_VALUE, 0, REG_SZ, image_path)
        return True
    except Exception as e:
        print(f"[LockScreenError] {e}")
        return False

def apply_wallpaper_and_lockscreen():
    path, err = _deploy_wallpaper()
    if path is None:
        return False, f"壁纸文件无法访问：{err}"
    wp_ok = set_desktop_wallpaper(path)
    ls_ok = set_lockscreen_image(path)
    if wp_ok and ls_ok:
        return True, "桌面壁纸与锁屏已配置完成"
    elif wp_ok:
        return True, "桌面壁纸已设置，锁屏设置失败"
    else:
        return False, "壁纸设置失败"


# --- 辅助函数：注册表底层读写 ---
def reg_read_value(hkey, path, value_name):
    """读取注册表键值，自动返回对应类型（DWORD为int，SZ为str）"""
    try:
        with OpenKey(hkey, path, 0, KEY_READ) as key:
            val, _ = QueryValueEx(key, value_name)
            return val
    except Exception:
        return None

# 兼容别名
reg_read_dword = reg_read_value
reg_read_string = reg_read_value

def reg_write_value(hkey, path, value_name, value, reg_type=REG_DWORD):
    try:
        with CreateKey(hkey, path) as key:
            SetValueEx(key, value_name, 0, reg_type, value)
        return True
    except Exception as e:
        print(f"[RegWriteError] {path}\\{value_name}: {e}")
        return False

def reg_write_dword(hkey, path, value_name, value):
    return reg_write_value(hkey, path, value_name, value, REG_DWORD)

def reg_write_string(hkey, path, value_name, value):
    return reg_write_value(hkey, path, value_name, value, REG_SZ)

def reg_delete_value(hkey, path, value_name):
    try:
        with OpenKey(hkey, path, 0, KEY_ALL_ACCESS) as key:
            DeleteValue(key, value_name)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        return False

def reg_delete_key_tree(hkey, subkey_path):
    """递归删除指定注册表键及其所有子项"""
    try:
        with OpenKey(hkey, subkey_path, 0, KEY_ALL_ACCESS) as key:
            while True:
                try:
                    sub = EnumKey(key, 0)
                    reg_delete_key_tree(key, sub)
                except OSError:
                    break
        DeleteKey(hkey, subkey_path)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        return False


# --- 系统核心功能 ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if getattr(sys, 'frozen', False):
        executable = sys.executable
        params = "--elevated"
    else:
        executable = sys.executable
        params = f'"{__file__}" --elevated'
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        if int(ret) <= 32:
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"提权失败: {e}")
        sys.exit(1)

def restart_explorer():
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        subprocess.Popen(["explorer.exe"])
        return True
    except Exception as e:
        try:
            subprocess.Popen(["explorer.exe"])
        except Exception:
            pass
        return False

def kill_browser_process(process_image):
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", process_image],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(0.5)
        return True
    except Exception:
        return False

def kill_edge_process():
    return kill_browser_process("msedge.exe")

def kill_chrome_process():
    return kill_browser_process("chrome.exe")


# --- 白名单读写配置 ---
def get_whitelist_filepath():
    return os.path.join(_SCRIPT_DIR, WHITELIST_FILENAME)

def load_whitelist():
    filepath = get_whitelist_filepath()
    if not os.path.exists(filepath):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# 机房教学策略配置 - 浏览器允许访问的网址白名单\n")
                f.write("\n".join(DEFAULT_ALLOWLIST) + "\n")
        except Exception:
            pass
        return list(DEFAULT_ALLOWLIST)
    
    rules = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(line)
    except Exception:
        return list(DEFAULT_ALLOWLIST)
    return rules if rules else list(DEFAULT_ALLOWLIST)

def save_whitelist(rules):
    filepath = get_whitelist_filepath()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# 机房教学策略配置 - 浏览器允许访问的网址白名单\n")
            for r in rules:
                r = r.strip()
                if r:
                    f.write(r + "\n")
        return True
    except Exception:
        return False


# --- 通用浏览器策略辅助函数 ---
def _get_browser_whitelist_status(base_reg_path):
    for hkey in (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER):
        val = reg_read_string(hkey, fr"{base_reg_path}\{REG_BROWSER_BLOCKLIST_SUBKEY}", "1")
        if val == "*":
            return True
    return False

def _set_browser_whitelist(base_reg_path, enabled, custom_rules=None):
    if custom_rules is None:
        custom_rules = load_whitelist()

    block_path = fr"{base_reg_path}\{REG_BROWSER_BLOCKLIST_SUBKEY}"
    allow_path = fr"{base_reg_path}\{REG_BROWSER_ALLOWLIST_SUBKEY}"
    success = True

    for hkey in (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER):
        if enabled:
            b_ok = reg_write_string(hkey, block_path, "1", "*")
            reg_delete_key_tree(hkey, allow_path)
            try:
                with CreateKey(hkey, allow_path) as key:
                    for idx, rule in enumerate(custom_rules, 1):
                        SetValueEx(key, str(idx), 0, REG_SZ, rule.strip())
                a_ok = True
            except Exception:
                a_ok = False
            # 禁用浏览器后台常驻与启动增强，防止进程无法退出导致策略未重新加载
            reg_write_dword(hkey, base_reg_path, "StartupBoostEnabled", 0)
            reg_write_dword(hkey, base_reg_path, "BackgroundModeEnabled", 0)
            success = success and (b_ok and a_ok)
        else:
            b_ok = reg_delete_key_tree(hkey, block_path)
            a_ok = reg_delete_key_tree(hkey, allow_path)
            reg_delete_value(hkey, base_reg_path, "StartupBoostEnabled")
            reg_delete_value(hkey, base_reg_path, "BackgroundModeEnabled")
            success = success and (b_ok and a_ok)
    return success

# --- 桌面快捷方式管理 (解决单机环境下浏览器启动直达) ---
def _run_vbs_script(vbs_code):
    vbs_path = os.path.join(tempfile.gettempdir(), f"_shortcut_{os.getpid()}.vbs")
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_code)
        res = subprocess.run(
            ["cscript", "//nologo", vbs_path],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return res.stdout.strip()
    except Exception:
        return ""
    finally:
        try:
            if os.path.exists(vbs_path):
                os.remove(vbs_path)
        except Exception:
            pass

def get_browser_exe_path(browser_name):
    if "Edge" in browser_name:
        candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        ]
    else:
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

def get_desktop_shortcut_paths(browser_name):
    shortcut_filename = "Microsoft Edge.lnk" if "Edge" in browser_name else "Google Chrome.lnk"
    desktops = [
        os.path.expanduser(r"~\Desktop"),
        os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop")
    ]
    return [os.path.join(d, shortcut_filename) for d in desktops if os.path.isdir(d)]

def get_browser_shortcut_status(browser_name, target_url=DEFAULT_STARTUP_URL):
    paths = get_desktop_shortcut_paths(browser_name)
    for p in paths:
        if os.path.isfile(p):
            vbs = f'''Set ws = CreateObject("WScript.Shell")
Set lnk = ws.CreateShortcut("{p}")
WScript.Echo lnk.Arguments
'''
            args = _run_vbs_script(vbs)
            if target_url in args:
                return True
    return False

def unpin_browser_from_taskbar(browser_name):
    """从任务栏取消固定并删除指定浏览器的任务栏快捷方式"""
    taskbar_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar")
    keyword = "edge" if "Edge" in browser_name else "chrome"

    # 1. 直接删除任务栏固定快捷方式文件
    if os.path.isdir(taskbar_dir):
        for fname in os.listdir(taskbar_dir):
            if keyword in fname.lower() and fname.lower().endswith(".lnk"):
                try:
                    os.remove(os.path.join(taskbar_dir, fname))
                except Exception:
                    pass

    # 2. 调用 Windows Shell COM 动词取消固定 (Windows 10/11 双重保障)
    app_name = "Microsoft Edge" if "Edge" in browser_name else "Google Chrome"
    vbs = f'''On Error Resume Next
Set objShell = CreateObject("Shell.Application")
Set objFolder = objShell.Namespace("shell:::{{4234d49b-0245-4df3-b780-3893943456e1}}")
If Not objFolder Is Nothing Then
    For Each item In objFolder.Items
        If InStr(LCase(item.Name), LCase("{app_name}")) > 0 Then
            For Each verb In item.Verbs
                strVerb = Replace(verb.Name, "&", "")
                If InStr(strVerb, "从任务栏取消固定") > 0 Or InStr(LCase(strVerb), "unpin from taskbar") > 0 Then
                    verb.DoIt
                End If
            Next
        End If
    Next
End If
'''
    _run_vbs_script(vbs)
    return True

def set_browser_shortcut(browser_name, enabled, target_url=DEFAULT_STARTUP_URL):
    exe_path = get_browser_exe_path(browser_name)
    if not exe_path:
        return False

    # 开启桌面直达时，自动从任务栏删除固定图标，确保学生只能从桌面直达进入
    if enabled:
        unpin_browser_from_taskbar(browser_name)

    paths = get_desktop_shortcut_paths(browser_name)
    user_desktop_lnk = os.path.join(os.path.expanduser(r"~\Desktop"), "Microsoft Edge.lnk" if "Edge" in browser_name else "Google Chrome.lnk")
    if user_desktop_lnk not in paths:
        paths.append(user_desktop_lnk)

    args_str = target_url if enabled else ""
    for p in paths:
        if not os.path.isfile(p) and p != user_desktop_lnk:
            continue
        vbs = f'''Set ws = CreateObject("WScript.Shell")
Set lnk = ws.CreateShortcut("{p}")
lnk.TargetPath = "{exe_path}"
lnk.Arguments = "{args_str}"
lnk.WorkingDirectory = "{os.path.dirname(exe_path)}"
lnk.Save
'''
        _run_vbs_script(vbs)
    return True

def _get_browser_downloads_disabled(base_reg_path):
    hklm_val = reg_read_dword(HKEY_LOCAL_MACHINE, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE)
    hkcu_val = reg_read_dword(HKEY_CURRENT_USER, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE)
    return hklm_val == 3 or hkcu_val == 3

def _set_browser_downloads_disabled(base_reg_path, disabled):
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE, 3)
        s2 = reg_write_dword(HKEY_CURRENT_USER, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE, 3)
        return s1 or s2
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE)
        s2 = reg_delete_value(HKEY_CURRENT_USER, base_reg_path, REG_BROWSER_DOWNLOAD_VALUE)
        return s1 and s2


def _get_browser_game_disabled(base_reg_path, game_value_name):
    hklm = reg_read_value(HKEY_LOCAL_MACHINE, base_reg_path, game_value_name)
    hkcu = reg_read_value(HKEY_CURRENT_USER, base_reg_path, game_value_name)
    return hklm == 0 or hkcu == 0

def _set_browser_game_disabled(base_reg_path, game_value_name, disabled):
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, base_reg_path, game_value_name, 0)
        s2 = reg_write_dword(HKEY_CURRENT_USER, base_reg_path, game_value_name, 0)
        return s1 or s2
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, base_reg_path, game_value_name)
        s2 = reg_delete_value(HKEY_CURRENT_USER, base_reg_path, game_value_name)
        return s1 and s2


# --- Edge 专属函数 ---
def get_edge_whitelist_locked():
    return _get_browser_whitelist_status(REG_EDGE_PATH)

def set_edge_whitelist_locked(enabled, custom_rules=None):
    return _set_browser_whitelist(REG_EDGE_PATH, enabled, custom_rules)

def get_edge_startup_status():
    return get_browser_shortcut_status("Edge")

def set_edge_startup(enabled, target_url=DEFAULT_STARTUP_URL):
    return set_browser_shortcut("Edge", enabled, target_url)

def get_edge_game_disabled():
    return _get_browser_game_disabled(REG_EDGE_PATH, REG_EDGE_GAME_VALUE)

def set_edge_game_disabled(disabled):
    return _set_browser_game_disabled(REG_EDGE_PATH, REG_EDGE_GAME_VALUE, disabled)

def get_edge_downloads_disabled():
    return _get_browser_downloads_disabled(REG_EDGE_PATH)

def set_edge_downloads_disabled(disabled):
    return _set_browser_downloads_disabled(REG_EDGE_PATH, disabled)


# --- Chrome 专属函数 ---
def get_chrome_whitelist_locked():
    return _get_browser_whitelist_status(REG_CHROME_PATH)

def set_chrome_whitelist_locked(enabled, custom_rules=None):
    return _set_browser_whitelist(REG_CHROME_PATH, enabled, custom_rules)

def get_chrome_startup_status():
    return get_browser_shortcut_status("Chrome")

def set_chrome_startup(enabled, target_url=DEFAULT_STARTUP_URL):
    return set_browser_shortcut("Chrome", enabled, target_url)

def get_chrome_game_disabled():
    return _get_browser_game_disabled(REG_CHROME_PATH, REG_CHROME_GAME_VALUE)

def set_chrome_game_disabled(disabled):
    return _set_browser_game_disabled(REG_CHROME_PATH, REG_CHROME_GAME_VALUE, disabled)

def get_chrome_downloads_disabled():
    return _get_browser_downloads_disabled(REG_CHROME_PATH)

def set_chrome_downloads_disabled(disabled):
    return _set_browser_downloads_disabled(REG_CHROME_PATH, disabled)


# --- 浏览器集中配置映射 ---
BROWSERS = {
    "Edge": {
        "name": "Edge",
        "cmd": "msedge",
        "proc": "msedge.exe",
        "game_label": "离线冲浪游戏 (Surf)",
        "game_short_name": "冲浪游戏",
        "get_wl": get_edge_whitelist_locked,
        "set_wl": set_edge_whitelist_locked,
        "get_startup": get_edge_startup_status,
        "set_startup": set_edge_startup,
        "get_game": get_edge_game_disabled,
        "set_game": set_edge_game_disabled,
        "get_dl": get_edge_downloads_disabled,
        "set_dl": set_edge_downloads_disabled,
    },
    "Chrome": {
        "name": "Chrome",
        "cmd": "chrome",
        "proc": "chrome.exe",
        "game_label": "离线恐龙游戏 (Dino)",
        "game_short_name": "恐龙游戏",
        "get_wl": get_chrome_whitelist_locked,
        "set_wl": set_chrome_whitelist_locked,
        "get_startup": get_chrome_startup_status,
        "set_startup": set_chrome_startup,
        "get_game": get_chrome_game_disabled,
        "set_game": set_chrome_game_disabled,
        "get_dl": get_chrome_downloads_disabled,
        "set_dl": set_chrome_downloads_disabled,
    }
}


# --- 云端白名单静默同步配置与任务调度 ---
CLOUD_WHITELIST_URL = "https://xbkjz.cn/edu/whitelist.txt"
CLOUD_SYNC_TASK_NAME = "XiaobaoPolicySync"
CLOUD_SYNC_SCRIPT_FILENAME = "Sync-Whitelist.ps1"
CLOUD_SYNC_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
CLOUD_SYNC_SCRIPT_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, CLOUD_SYNC_SCRIPT_FILENAME)
CLOUD_SYNC_LOG_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, "sync.log")

SYNC_SCRIPT_CONTENT = """# ==============================================================================
# 机房教学策略 - 浏览器白名单静默同步脚本 (PowerShell 原生版)
# 设计原则：
# 1. 兼容 Windows PowerShell 5.1 及更高版本
# 2. 纯静默无界面运行 (WindowStyle Hidden)
# 3. 单向拉取与加锁：只有“拉取并锁定白名单”功能，无任何“解除/解锁”代码，防学生逆向与破坏
# 4. 离线/故障自动降级：网络异常时保留本地缓存，不影响正常使用
# ==============================================================================

$ErrorActionPreference = 'SilentlyContinue'

$RemoteUrl = "https://xbkjz.cn/edu/whitelist.txt"
$LocalFallbackPath = "C:\\Users\\A3\\Desktop\\Website\\xiaobao-tech\\edu\\whitelist.txt"
$CacheDir = "C:\\ProgramData\\XiaobaoTools"
$CachePath = "C:\\ProgramData\\XiaobaoTools\\whitelist_cache.txt"

$rawText = $null

# 1. 尝试从云端拉取
try {
    $wc = New-Object System.Net.WebClient
    $wc.Encoding = [System.Text.Encoding]::UTF8
    $rawText = $wc.DownloadString($RemoteUrl)
    if ($rawText -and $rawText.Trim().Length -gt 0) {
        if (-not (Test-Path $CacheDir)) {
            New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
        }
        [System.IO.File]::WriteAllText($CachePath, $rawText, [System.Text.Encoding]::UTF8)
    }
} catch {
    $rawText = $null
}

# 2. 若云端不可达，尝试读取本地发布文件
if (-not $rawText) {
    if (Test-Path $LocalFallbackPath) {
        try {
            $rawText = [System.IO.File]::ReadAllText($LocalFallbackPath, [System.Text.Encoding]::UTF8)
        } catch {
            $rawText = $null
        }
    }
}

# 3. 若依然没有，尝试读取本地缓存文件
if (-not $rawText) {
    if (Test-Path $CachePath) {
        try {
            $rawText = [System.IO.File]::ReadAllText($CachePath, [System.Text.Encoding]::UTF8)
        } catch {
            $rawText = $null
        }
    }
}

# 如果没有获得任何有效内容，退出以避免破坏现有配置
if (-not $rawText) {
    exit 0
}

# 4. 解析白名单规则
$rules = New-Object System.Collections.Generic.List[string]
$lines = $rawText.Split(@("`r`n", "`r", "`n"), [System.StringSplitOptions]::None)
foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -gt 0 -and -not $trimmed.StartsWith("#")) {
        $rules.Add($trimmed)
    }
}

if ($rules.Count -eq 0) {
    exit 0
}

# 5. 写入 Edge 与 Chrome 策略 (涵盖 HKLM 与 HKCU)
$policyTargets = @(
    "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Edge",
    "HKLM:\\SOFTWARE\\Policies\\Google\\Chrome",
    "HKCU:\\SOFTWARE\\Policies\\Microsoft\\Edge",
    "HKCU:\\SOFTWARE\\Policies\\Google\\Chrome"
)

foreach ($baseKey in $policyTargets) {
    $blockKey = "$baseKey\\URLBlocklist"
    $allowKey = "$baseKey\\URLAllowlist"

    if (-not (Test-Path $baseKey)) {
        New-Item -Path $baseKey -Force | Out-Null
    }
    if (-not (Test-Path $blockKey)) {
        New-Item -Path $blockKey -Force | Out-Null
    }

    # 封禁非白名单网址
    Set-ItemProperty -Path $blockKey -Name "1" -Value "*" -Type String -Force

    # 清空并重新写入白名单列表
    if (Test-Path $allowKey) {
        Remove-Item -Path $allowKey -Recurse -Force
    }
    New-Item -Path $allowKey -Force | Out-Null

    for ($i = 0; $i -lt $rules.Count; $i++) {
        $idxName = ($i + 1).ToString()
        Set-ItemProperty -Path $allowKey -Name $idxName -Value $rules[$i] -Type String -Force
    }

    # 禁用浏览器后台常驻与启动加速，确保策略即时生效
    Set-ItemProperty -Path $baseKey -Name "StartupBoostEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $baseKey -Name "BackgroundModeEnabled" -Value 0 -Type DWord -Force
}

# 写入完成日志标记
try {
    $logMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Synced $($rules.Count) rules successfully. Last: $($rules[$rules.Count - 1])`r`n"
    [System.IO.File]::AppendAllText("C:\\ProgramData\\XiaobaoTools\\sync.log", $logMsg, [System.Text.Encoding]::UTF8)
} catch {
    $null
}
"""

def get_cloud_sync_installed():
    if not os.path.exists(CLOUD_SYNC_SCRIPT_PATH):
        return False
    try:
        res = subprocess.run(
            ["schtasks", "/query", "/tn", CLOUD_SYNC_TASK_NAME],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return res.returncode == 0
    except Exception:
        return False

def deploy_sync_script():
    try:
        os.makedirs(CLOUD_SYNC_DEPLOY_DIR, exist_ok=True)
        src = os.path.join(RESOURCE_DIR, CLOUD_SYNC_SCRIPT_FILENAME)
        content = ""
        if os.path.exists(src):
            try:
                with open(src, "r", encoding="utf-8-sig") as f:
                    content = f.read()
            except Exception:
                pass
        if not content:
            content = SYNC_SCRIPT_CONTENT
        with open(CLOUD_SYNC_SCRIPT_PATH, "w", encoding="utf-8-sig") as f:
            f.write(content)
        return True
    except Exception:
        return False

def install_cloud_sync_task():
    if not deploy_sync_script():
        return False, "部署同步脚本到系统目录失败。"
    cmd = [
        "schtasks", "/create",
        "/tn", CLOUD_SYNC_TASK_NAME,
        "/tr", f'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "{CLOUD_SYNC_SCRIPT_PATH}"',
        "/sc", "onstart",
        "/ru", "SYSTEM",
        "/f"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode == 0:
            run_cloud_sync_now()
            return True, "开机静默云端同步任务已成功部署！\\n\\n- 运行机制：开机自动以最高 SYSTEM 权限在后台静默运行\\n- 权限特性：彻底免 UAC 弹窗、无黑框界面、普通学生无权修改\\n- 同步源：https://xbkjz.cn/edu/whitelist.txt\\n\\n学生机每次开机将自动静默同步最新白名单，无需插 U 盘！"
        else:
            err = res.stderr.strip() or res.stdout.strip()
            return False, f"创建计划任务失败：{err}"
    except Exception as e:
        return False, f"执行异常：{e}"

def uninstall_cloud_sync_task():
    try:
        res = subprocess.run(
            ["schtasks", "/delete", "/tn", CLOUD_SYNC_TASK_NAME, "/f"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if res.returncode == 0:
            return True, "已成功移除开机云端同步任务。"
        else:
            return False, f"移除任务失败：{res.stderr.strip() or res.stdout.strip()}"
    except Exception as e:
        return False, f"执行异常：{e}"

def run_cloud_sync_now():
    if not os.path.exists(CLOUD_SYNC_SCRIPT_PATH):
        deploy_sync_script()
    try:
        subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", CLOUD_SYNC_SCRIPT_PATH],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, "云端同步执行完成，白名单已刷新。"
    except Exception as e:
        return False, f"同步执行失败：{e}"



# --- 桌面与系统常规策略 ---
def get_wallpaper_locked():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)
    return val == 1

def set_wallpaper_locked(locked):
    if locked:
        return reg_write_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)

def get_spotlight_hidden():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)
    return val == 1

def set_spotlight_hidden(hidden):
    if hidden:
        return reg_write_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)

def get_file_ext_visible():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_EXPLORER_ADVANCED_PATH, REG_HIDE_FILE_EXT_VALUE)
    return val == 0

def set_file_ext_visible(visible):
    val = 0 if visible else 1
    return reg_write_dword(HKEY_CURRENT_USER, REG_EXPLORER_ADVANCED_PATH, REG_HIDE_FILE_EXT_VALUE, val)

def get_longpaths_status():
    val = reg_read_dword(HKEY_LOCAL_MACHINE, REG_LONGPATHS_PATH, REG_LONGPATHS_VALUE)
    return val == 1

def set_longpaths_enabled(enabled):
    val = 1 if enabled else 0
    return reg_write_dword(HKEY_LOCAL_MACHINE, REG_LONGPATHS_PATH, REG_LONGPATHS_VALUE, val)


# --- pip 镜像源管理 (支持官方、清华、阿里) ---
def get_pip_config_file_path():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            appdata = os.path.join(userprofile, "AppData", "Roaming")
        else:
            return None
    return os.path.join(appdata, "pip", "pip.ini")

def get_pip_mirror_type():
    """返回当前 pip 镜像源类型: 'tuna', 'aliyun', 'other', 'default'"""
    paths = []
    pdata = os.environ.get("PROGRAMDATA")
    if pdata:
        paths.append(os.path.join(pdata, "pip", "pip.ini"))
    uprofile = os.environ.get("USERPROFILE")
    if uprofile:
        paths.append(os.path.join(uprofile, "pip", "pip.ini"))
    appdata = os.environ.get("APPDATA")
    if appdata:
        paths.append(os.path.join(appdata, "pip", "pip.ini"))

    current_url = ""
    for path in paths:
        if os.path.exists(path):
            try:
                config = configparser.ConfigParser()
                config.read(path, encoding="utf-8")
                if "global" in config and "index-url" in config["global"]:
                    current_url = config["global"]["index-url"].strip()
            except Exception:
                pass

    if not current_url:
        return "default", ""
    if "tuna" in current_url:
        return "tuna", current_url
    if "aliyun" in current_url:
        return "aliyun", current_url
    return "other", current_url

def set_pip_mirror_source(source_type):
    """设置 pip 镜像源: 'tuna', 'aliyun', 'default'"""
    path = get_pip_config_file_path()
    if not path:
        return False, "未能定位 pip 配置文件路径。"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        config = configparser.ConfigParser()
        if os.path.exists(path):
            config.read(path, encoding="utf-8")
        if "global" not in config:
            config["global"] = {}

        if source_type == "tuna":
            config["global"]["index-url"] = PYPI_TUNA_URL
            msg = "pip 镜像源已配置为清华源"
        elif source_type == "aliyun":
            config["global"]["index-url"] = PYPI_ALIYUN_URL
            msg = "pip 镜像源已配置为阿里源"
        else:
            if "index-url" in config["global"]:
                del config["global"]["index-url"]
            if not config["global"]:
                del config["global"]
            msg = "pip 镜像源已恢复官方默认"

        with open(path, "w", encoding="utf-8") as f:
            config.write(f)
        return True, msg
    except Exception as e:
        return False, f"写入 pip 配置失败: {e}"


# --- 极简现代 GUI 实现 (三色设计：中性灰白底 #F8FAFC + 主文字/按钮 #0F172A + 边框中灰 #E2E8F0) ---
class CodingLabAssistantGUI:
    def __init__(self, root):
        self.root = root
        设置窗口图标(self.root)
        self.root.title("机房教学策略配置工具")
        self.root.resizable(False, False)

        self.root.configure(bg="#F8FAFC")
        self.auto_restart_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_status()

        # 根据内容真实高度精确自适应收紧，消除多余空白并居中
        self.root.update_idletasks()
        w = 530
        h = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ── 底部操作栏与状态条 ──────────────────────────────────────────
        status_bar = tk.Frame(self.root, bg="#F1F5F9", height=24)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_lbl = tk.Label(
            status_bar,
            text="运行环境：管理员权限已就绪",
            font=("Microsoft YaHei UI", 8),
            bg="#F1F5F9",
            fg="#475569",
            anchor="w",
            padx=12,
            pady=3
        )
        self.status_lbl.pack(side=tk.LEFT)

        author_lbl = tk.Label(
            status_bar,
            text="小宝科技站 xbkjz.cn",
            font=("Microsoft YaHei UI", 8),
            bg="#F1F5F9",
            fg="#64748B",
            cursor="hand2",
            padx=12
        )
        author_lbl.pack(side=tk.RIGHT)
        author_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))

        footer_panel = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=4)
        footer_panel.pack(fill=tk.X, side=tk.BOTTOM)

        self.chk = tk.Checkbutton(
            footer_panel,
            text="修改策略后自动重启资源管理器",
            variable=self.auto_restart_var,
            font=("Microsoft YaHei UI", 9),
            bg="#F8FAFC",
            activebackground="#F8FAFC",
            fg="#334155"
        )
        self.chk.pack(side=tk.LEFT)

        btn_kill_chrome = tk.Button(
            footer_panel,
            text="重启 Chrome",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_chrome
        )
        btn_kill_chrome.pack(side=tk.RIGHT, padx=(4, 0))

        btn_kill_edge = tk.Button(
            footer_panel,
            text="重启 Edge",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_edge
        )
        btn_kill_edge.pack(side=tk.RIGHT, padx=(4, 0))

        btn_restart_exp = tk.Button(
            footer_panel,
            text="重启资源管理器",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_explorer
        )
        btn_restart_exp.pack(side=tk.RIGHT)

        # ── 顶部头部区域 ──────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=8)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="机房教学策略配置工具",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#F8FAFC",
            fg="#0F172A"
        ).pack(anchor="w")

        hostname, ip = get_device_info()
        info_bar = tk.Frame(header, bg="#FFFFFF", padx=10, pady=5, relief=tk.SOLID, bd=1)
        info_bar.pack(fill=tk.X, pady=(6, 0))

        tk.Label(
            info_bar,
            text=f"计算机名称: {hostname}    |    局域网 IP: {ip}",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#475569"
        ).pack(side=tk.LEFT)

        # ── 功能卡片容器 ──────────────────────────────────────────────
        main_content = tk.Frame(self.root, bg="#F8FAFC", padx=16)
        main_content.pack(fill=tk.X, pady=(0, 4))

        # 1 & 2. 浏览器访问管控 (Edge 与 Chrome 统一结构)
        self.browser_widgets = {}
        for b_key in ("Edge", "Chrome"):
            self._build_browser_card(main_content, b_key)

        # 3. 云端白名单开机自动同步
        card_sync = tk.LabelFrame(
            main_content,
            text=" 云端白名单开机自动同步 (推荐) ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_sync.pack(fill=tk.X, pady=(0, 5))

        row_sync1 = tk.Frame(card_sync, bg="#FFFFFF")
        row_sync1.pack(fill=tk.X, pady=2)
        self.sync_lbl = tk.Label(row_sync1, text="开机静默同步任务：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.sync_lbl.pack(side=tk.LEFT)

        self.sync_now_btn = tk.Button(
            row_sync1, text="立即从云端拉取", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=12, cursor="hand2",
            command=self.manual_sync_now
        )
        self.sync_now_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.sync_btn = tk.Button(
            row_sync1, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=12, cursor="hand2",
            command=self.toggle_cloud_sync
        )
        self.sync_btn.pack(side=tk.RIGHT)

        row_sync2 = tk.Frame(card_sync, bg="#FFFFFF")
        row_sync2.pack(fill=tk.X, pady=(2, 1))
        tk.Label(
            row_sync2,
            text="同步源：https://xbkjz.cn/edu/whitelist.txt (开机免 UAC 静默更新，学生机无需留 exe)",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#64748B"
        ).pack(side=tk.LEFT)


        # 3. 桌面与系统规范
        card_desk = tk.LabelFrame(
            main_content,
            text=" 桌面与文件系统规范 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_desk.pack(fill=tk.X, pady=(0, 5))

        # 3.1 壁纸与锁屏
        row_wp = tk.Frame(card_desk, bg="#FFFFFF")
        row_wp.pack(fill=tk.X, pady=2)
        self.wp_lbl = tk.Label(row_wp, text="机构壁纸与锁屏：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.wp_lbl.pack(side=tk.LEFT)
        self.wp_btn = tk.Button(
            row_wp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_wallpaper
        )
        self.wp_btn.pack(side=tk.RIGHT)

        # 3.2 文件扩展名
        row_ext = tk.Frame(card_desk, bg="#FFFFFF")
        row_ext.pack(fill=tk.X, pady=2)
        self.ext_lbl = tk.Label(row_ext, text="文件扩展名 (后缀名)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.ext_lbl.pack(side=tk.LEFT)
        self.ext_btn = tk.Button(
            row_ext, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_file_ext
        )
        self.ext_btn.pack(side=tk.RIGHT)

        # 3.3 聚焦图标
        row_sp = tk.Frame(card_desk, bg="#FFFFFF")
        row_sp.pack(fill=tk.X, pady=2)
        self.sp_lbl = tk.Label(row_sp, text='桌面"了解此图片"图标：读取中', font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.sp_lbl.pack(side=tk.LEFT)
        self.sp_btn = tk.Button(
            row_sp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_spotlight
        )
        self.sp_btn.pack(side=tk.RIGHT)

        # 4. 编程环境优化
        card_dev = tk.LabelFrame(
            main_content,
            text=" 编程环境优化 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_dev.pack(fill=tk.X, pady=(0, 4))

        # 4.1 pip 镜像多源配置
        row_pip = tk.Frame(card_dev, bg="#FFFFFF")
        row_pip.pack(fill=tk.X, pady=2)
        self.pip_lbl = tk.Label(row_pip, text="Python pip 镜像源：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.pip_lbl.pack(side=tk.LEFT)

        btn_pip_default = tk.Button(
            row_pip, text="恢复默认", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("default")
        )
        btn_pip_default.pack(side=tk.RIGHT, padx=(4, 0))

        btn_pip_ali = tk.Button(
            row_pip, text="阿里源", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("aliyun")
        )
        btn_pip_ali.pack(side=tk.RIGHT, padx=(4, 0))

        btn_pip_tuna = tk.Button(
            row_pip, text="清华源", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("tuna")
        )
        btn_pip_tuna.pack(side=tk.RIGHT)

        # 4.2 Windows 长路径
        row_lp = tk.Frame(card_dev, bg="#FFFFFF")
        row_lp.pack(fill=tk.X, pady=2)
        self.lp_lbl = tk.Label(row_lp, text="Windows 长路径支持 (LongPaths)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.lp_lbl.pack(side=tk.LEFT)
        self.lp_btn = tk.Button(
            row_lp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_longpaths
        )
        self.lp_btn.pack(side=tk.RIGHT)

    def _build_browser_card(self, parent, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        card = tk.LabelFrame(
            parent,
            text=f" {name} 浏览器访问策略 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card.pack(fill=tk.X, pady=(0, 5))

        widgets = {}

        # 1. 白名单
        row_wl = tk.Frame(card, bg="#FFFFFF")
        row_wl.pack(fill=tk.X, pady=2)
        widgets["wl_lbl"] = tk.Label(row_wl, text="网址白名单锁定：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["wl_lbl"].pack(side=tk.LEFT)

        widgets["wl_cfg_btn"] = tk.Button(
            row_wl, text="管理白名单", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.open_whitelist_manager
        )
        widgets["wl_cfg_btn"].pack(side=tk.RIGHT, padx=(4, 0))

        widgets["wl_btn"] = tk.Button(
            row_wl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_whitelist(b_key)
        )
        widgets["wl_btn"].pack(side=tk.RIGHT)

        # 2. 桌面直达启动图标
        row_pt = tk.Frame(card, bg="#FFFFFF")
        row_pt.pack(fill=tk.X, pady=2)
        widgets["portal_lbl"] = tk.Label(row_pt, text="桌面直达启动图标：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["portal_lbl"].pack(side=tk.LEFT)

        widgets["test_btn"] = tk.Button(
            row_pt, text="测试打开", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._test_open_browser(b_key)
        )
        widgets["test_btn"].pack(side=tk.RIGHT, padx=(4, 0))

        widgets["portal_btn"] = tk.Button(
            row_pt, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_startup(b_key)
        )
        widgets["portal_btn"].pack(side=tk.RIGHT)

        # 3. 离线游戏
        row_gm = tk.Frame(card, bg="#FFFFFF")
        row_gm.pack(fill=tk.X, pady=2)
        widgets["game_lbl"] = tk.Label(row_gm, text=f"{cfg['game_label']}：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["game_lbl"].pack(side=tk.LEFT)
        widgets["game_btn"] = tk.Button(
            row_gm, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_game(b_key)
        )
        widgets["game_btn"].pack(side=tk.RIGHT)

        # 4. 下载限制
        row_dl = tk.Frame(card, bg="#FFFFFF")
        row_dl.pack(fill=tk.X, pady=2)
        widgets["dl_lbl"] = tk.Label(row_dl, text="文件下载限制：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["dl_lbl"].pack(side=tk.LEFT)
        widgets["dl_btn"] = tk.Button(
            row_dl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_downloads(b_key)
        )
        widgets["dl_btn"].pack(side=tk.RIGHT)

        self.browser_widgets[b_key] = widgets

    def _refresh_browser_status(self, b_key):
        cfg = BROWSERS[b_key]
        w = self.browser_widgets[b_key]

        wl_locked = cfg["get_wl"]()
        if wl_locked:
            w["wl_lbl"].configure(text="网址白名单锁定：已开启限制 (仅允许白名单网站)")
            w["wl_btn"].configure(text="解除限制", bg="#FFFFFF", fg="#0F172A")
        else:
            w["wl_lbl"].configure(text="网址白名单锁定：未锁定 (允许自由访问全网)")
            w["wl_btn"].configure(text="开启限制", bg="#0F172A", fg="#FFFFFF")

        pt_on = cfg["get_startup"]()
        if pt_on:
            w["portal_lbl"].configure(text="桌面直达启动图标：已配置直达 (双击直达目标主页)")
            w["portal_btn"].configure(text="恢复默认", bg="#FFFFFF", fg="#0F172A")
        else:
            w["portal_lbl"].configure(text="桌面直达启动图标：默认启动图标 (未绑定直达参数)")
            w["portal_btn"].configure(text="配置直达", bg="#0F172A", fg="#FFFFFF")

        gm_off = cfg["get_game"]()
        if gm_off:
            w["game_lbl"].configure(text=f"{cfg['game_label']}：已禁用")
            w["game_btn"].configure(text="允许游戏")
        else:
            w["game_lbl"].configure(text=f"{cfg['game_label']}：未禁用")
            w["game_btn"].configure(text="禁用游戏")

        dl_off = cfg["get_dl"]()
        if dl_off:
            w["dl_lbl"].configure(text="文件下载限制：已禁止所有文件下载")
            w["dl_btn"].configure(text="允许下载")
        else:
            w["dl_lbl"].configure(text="文件下载限制：允许下载")
            w["dl_btn"].configure(text="禁止下载")

    # ── 状态读取与刷新 ────────────────────────────────────────────────
    def refresh_status(self):
        # 1 & 2. 浏览器策略刷新 (Edge 与 Chrome 统一处理)
        for b_key in ("Edge", "Chrome"):
            self._refresh_browser_status(b_key)

        # 3. 云端白名单自动同步
        sync_installed = get_cloud_sync_installed()
        if sync_installed:
            self.sync_lbl.configure(text="开机静默同步任务：已就绪 (开机自动拉取更新)")
            self.sync_btn.configure(text="移除开机任务", bg="#FFFFFF", fg="#0F172A")
        else:
            self.sync_lbl.configure(text="开机静默同步任务：未部署 (需手动插 U 盘更新)")
            self.sync_btn.configure(text="部署开机同步", bg="#0F172A", fg="#FFFFFF")


        # 3. 桌面与系统规范
        wp_locked = get_wallpaper_locked()
        if wp_locked:
            self.wp_lbl.configure(text="机构壁纸与锁屏：已统一并锁定修改")
            self.wp_btn.configure(text="允许修改")
        else:
            self.wp_lbl.configure(text="机构壁纸与锁屏：未锁定 (允许自由修改)")
            self.wp_btn.configure(text="部署并锁定")

        ext_visible = get_file_ext_visible()
        if ext_visible:
            self.ext_lbl.configure(text="文件扩展名 (后缀名)：始终显示 (格式清晰可见)")
            self.ext_btn.configure(text="隐藏后缀")
        else:
            self.ext_lbl.configure(text="文件扩展名 (后缀名)：系统默认隐藏 (易引起混淆)")
            self.ext_btn.configure(text="显示后缀")

        sp_hidden = get_spotlight_hidden()
        if sp_hidden:
            self.sp_lbl.configure(text='桌面"了解此图片"图标：已隐藏')
            self.sp_btn.configure(text="恢复显示")
        else:
            self.sp_lbl.configure(text='桌面"了解此图片"图标：正常显示')
            self.sp_btn.configure(text="隐藏图标")

        # 4. 编程环境优化
        m_type, _ = get_pip_mirror_type()
        if m_type == "tuna":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 清华源")
        elif m_type == "aliyun":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 阿里源")
        elif m_type == "other":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 自定义源")
        else:
            self.pip_lbl.configure(text="Python pip 镜像源：官方默认源")

        lp_on = get_longpaths_status()
        if lp_on:
            self.lp_lbl.configure(text="Windows 长路径支持：已启用 (解除 260 字符限制)")
            self.lp_btn.configure(text="恢复默认")
        else:
            self.lp_lbl.configure(text="Windows 长路径支持：未启用 (限制 260 字符)")
            self.lp_btn.configure(text="启用长路径")

    # ── 交互事件处理 ──────────────────────────────────────────────────
    def trigger_explorer_update(self, action_name):
        if self.auto_restart_var.get():
            self.status_lbl.configure(text="正在重启资源管理器...")
            self.root.update()
            if restart_explorer():
                self.status_lbl.configure(text="设置已保存，资源管理器已成功重启。")
            else:
                self.status_lbl.configure(text="设置已保存，资源管理器重启失败。")
        else:
            messagebox.showinfo("操作成功", "设置已保存。\n\n请点击右下角“重启资源管理器”使更改生效。")
            self.status_lbl.configure(text="设置已保存，等待重启资源管理器...")

    def open_whitelist_manager(self):
        """打开通用白名单管理窗口"""
        win = tk.Toplevel(self.root)
        设置窗口图标(win)
        win.title("管理浏览器允许访问的网址白名单")
        win.geometry("480x420")
        win.resizable(False, False)
        win.configure(bg="#F8FAFC")
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win,
            text="浏览器允许访问的网址白名单清单",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#F8FAFC",
            fg="#0F172A"
        ).pack(pady=(12, 2))

        tk.Label(
            win,
            text="每行一条规则，支持通配符（Edge 与 Chrome 同步生效）\n保存后若白名单处于开启状态将立即同步到系统注册表。",
            font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC",
            fg="#64748B"
        ).pack(pady=(0, 8))

        text_area = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=("Consolas", 9), height=14,
            relief=tk.SOLID, bd=1
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        current_rules = load_whitelist()
        text_area.insert(tk.END, "\n".join(current_rules))

        btn_box = tk.Frame(win, bg="#F8FAFC")
        btn_box.pack(fill=tk.X, padx=16, pady=10)

        def save_and_close():
            raw = text_area.get("1.0", tk.END).strip().splitlines()
            cleaned = [line.strip() for line in raw if line.strip() and not line.strip().startswith("#")]
            if save_whitelist(cleaned):
                active_browsers = [cfg for cfg in BROWSERS.values() if cfg["get_wl"]()]
                for b_cfg in active_browsers:
                    b_cfg["set_wl"](True, cleaned)
                win.destroy()
                self.refresh_status()
                if active_browsers:
                    if messagebox.askyesno("保存成功", f"白名单规则已更新并同步写入注册表（共 {len(cleaned)} 条）。\n\n新策略需要重启浏览器生效，是否立即关闭并重启浏览器？"):
                        for b_cfg in active_browsers:
                            kill_browser_process(b_cfg["proc"])
                            subprocess.Popen(["cmd", "/c", "start", b_cfg["cmd"]], shell=True)
                else:
                    messagebox.showinfo("成功", f"白名单清单已保存（共 {len(cleaned)} 条）。\n当前白名单处于未开启状态，点击主界面的【开启限制】即可应用。")
            else:
                messagebox.showerror("错误", "保存白名单文件失败。")

        def reset_defaults():
            if messagebox.askyesno("恢复默认", "是否清空当前内容并恢复推荐的默认白名单？"):
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, "\n".join(DEFAULT_ALLOWLIST))

        tk.Button(
            btn_box, text="保存并生效", font=("Microsoft YaHei UI", 8, "bold"),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, padx=10, pady=2,
            command=save_and_close
        ).pack(side=tk.RIGHT, padx=(6, 0))

        tk.Button(
            btn_box, text="恢复默认清单", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, padx=8, pady=2,
            command=reset_defaults
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_box, text="取消", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#64748B", relief=tk.SOLID, bd=1, padx=8, pady=2,
            command=win.destroy
        ).pack(side=tk.LEFT)

    # ── 浏览器通用动作 ──
    def _toggle_browser_whitelist(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_wl"]()
        nxt = not curr
        if nxt and not messagebox.askyesno("确认", f"开启后 {name} 将阻断所有非白名单网站，是否继续？"):
            return
        if cfg["set_wl"](nxt):
            self.refresh_status()
            tip = f"{name} 白名单限制已开启。" if nxt else f"{name} 白名单限制已解除。"
            self.status_lbl.configure(text=tip)
            if messagebox.askyesno("提示", f"{tip}\n\n是否立即重启 {name} 浏览器生效？"):
                kill_browser_process(cfg["proc"])
                subprocess.Popen(["cmd", "/c", "start", cfg["cmd"]], shell=True)
        else:
            messagebox.showerror("错误", f"修改 {name} 白名单策略失败。")

    def _toggle_browser_startup(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_startup"]()
        nxt = not curr
        if cfg["set_startup"](nxt):
            self.refresh_status()
            tip = f"{name} 桌面图标已配置直达：{DEFAULT_STARTUP_URL}" if nxt else f"{name} 桌面图标已恢复为默认启动。"
            self.status_lbl.configure(text=tip)
            if nxt:
                if messagebox.askyesno("配置成功", f"{tip}\n\n是否立即通过直达参数启动 {name} 验证效果？"):
                    self._test_open_browser(b_key)
            else:
                messagebox.showinfo("提示", tip)
        else:
            messagebox.showerror("错误", f"修改 {name} 桌面快捷方式失败，未找到 {name} 安装路径。")

    def _test_open_browser(self, b_key):
        cmd = BROWSERS[b_key]["cmd"]
        try:
            subprocess.Popen(["cmd", "/c", "start", cmd, DEFAULT_STARTUP_URL], shell=True)
        except Exception:
            webbrowser.open(DEFAULT_STARTUP_URL)

    def _toggle_browser_game(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_game"]()
        nxt = not curr
        if cfg["set_game"](nxt):
            self.refresh_status()
            messagebox.showinfo("提示", f"{name} {cfg['game_short_name']}策略已保存，重启浏览器后生效。")
        else:
            messagebox.showerror("错误", f"修改 {name} 游戏策略失败。")

    def _toggle_browser_downloads(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_dl"]()
        nxt = not curr
        if cfg["set_dl"](nxt):
            self.refresh_status()
            act = f"已禁止 {name} 下载文件。" if nxt else f"已允许 {name} 下载文件。"
            if messagebox.askyesno("提示", f"{act}\n\n是否立即关闭 {name} 浏览器？"):
                kill_browser_process(cfg["proc"])
        else:
            messagebox.showerror("错误", f"修改 {name} 下载策略失败。")

    def _manual_restart_browser(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        kill_browser_process(cfg["proc"])
        self.status_lbl.configure(text=f"{name} 浏览器已关闭。")
        messagebox.showinfo("提示", f"{name} 浏览器已关闭，请重新启动以应用新策略。")

    # 快捷委托方法（保留方法接口兼容）
    def toggle_edge_whitelist(self): self._toggle_browser_whitelist("Edge")
    def toggle_edge_startup(self): self._toggle_browser_startup("Edge")
    def test_open_edge(self): self._test_open_browser("Edge")
    def toggle_edge_game(self): self._toggle_browser_game("Edge")
    def toggle_edge_downloads(self): self._toggle_browser_downloads("Edge")
    def manual_restart_edge(self): self._manual_restart_browser("Edge")

    def toggle_chrome_whitelist(self): self._toggle_browser_whitelist("Chrome")
    def toggle_chrome_startup(self): self._toggle_browser_startup("Chrome")
    def test_open_chrome(self): self._test_open_browser("Chrome")
    def toggle_chrome_game(self): self._toggle_browser_game("Chrome")
    def toggle_chrome_downloads(self): self._toggle_browser_downloads("Chrome")
    def manual_restart_chrome(self): self._manual_restart_browser("Chrome")

    # ── 云端同步动作 ──
    def toggle_cloud_sync(self):
        curr = get_cloud_sync_installed()
        if not curr:
            self.status_lbl.configure(text="正在向系统注册开机静默同步计划任务...")
            self.root.update()
            ok, msg = install_cloud_sync_task()
            self.refresh_status()
            if ok:
                self.status_lbl.configure(text="开机静默云端同步任务已部署完成。")
                messagebox.showinfo("部署成功", msg)
            else:
                self.status_lbl.configure(text="开机同步任务部署失败。")
                messagebox.showerror("部署失败", msg)
        else:
            if messagebox.askyesno("移除确认", "是否移除本机的开机云端同步任务？\\n\\n移除后，学生机将不再自动从云端更新白名单。"):
                self.status_lbl.configure(text="正在移除开机同步任务...")
                self.root.update()
                ok, msg = uninstall_cloud_sync_task()
                self.refresh_status()
                if ok:
                    self.status_lbl.configure(text="开机同步任务已移除。")
                    messagebox.showinfo("提示", msg)
                else:
                    self.status_lbl.configure(text="移除开机同步任务失败。")
                    messagebox.showerror("错误", msg)

    def manual_sync_now(self):
        self.status_lbl.configure(text="正在从云端拉取白名单并注入系统注册表...")
        self.root.update()
        ok, msg = run_cloud_sync_now()
        self.refresh_status()
        if ok:
            active_browsers = [cfg for cfg in BROWSERS.values() if cfg["get_wl"]()]
            self.status_lbl.configure(text="云端白名单同步已完成。")
            if messagebox.askyesno("同步完成", "云端白名单已成功拉取并写入系统注册表！\\n\\n是否立即重启浏览器以使新策略生效？"):
                for b_cfg in active_browsers:
                    kill_browser_process(b_cfg["proc"])
                    subprocess.Popen(["cmd", "/c", "start", b_cfg["cmd"]], shell=True)
        else:
            self.status_lbl.configure(text="云端同步执行失败。")
            messagebox.showerror("同步失败", msg)

    # ── 桌面与系统动作 ──
    def toggle_wallpaper(self):
        curr = get_wallpaper_locked()
        nxt = not curr
        if nxt:
            self.status_lbl.configure(text="正在部署机构壁纸和锁屏...")
            self.root.update()
            ok, msg = apply_wallpaper_and_lockscreen()
            if not ok:
                messagebox.showerror("壁纸设置失败", msg)
                return

        if set_wallpaper_locked(nxt):
            self.refresh_status()
            self.trigger_explorer_update("壁纸限制")
        else:
            messagebox.showerror("错误", "修改壁纸锁定状态失败。")

    def toggle_file_ext(self):
        curr = get_file_ext_visible()
        nxt = not curr
        if set_file_ext_visible(nxt):
            self.refresh_status()
            self.trigger_explorer_update("文件扩展名设置")
        else:
            messagebox.showerror("错误", "修改文件扩展名设置失败。")

    def toggle_spotlight(self):
        curr = get_spotlight_hidden()
        nxt = not curr
        if set_spotlight_hidden(nxt):
            self.refresh_status()
            self.trigger_explorer_update("了解此图片")
        else:
            messagebox.showerror("错误", '修改"了解此图片"隐藏状态失败。')

    def apply_pip_source(self, source_type):
        ok, msg = set_pip_mirror_source(source_type)
        if ok:
            self.refresh_status()
            self.status_lbl.configure(text=msg)
            messagebox.showinfo("提示", msg)
        else:
            messagebox.showerror("错误", msg)

    def toggle_longpaths(self):
        curr = get_longpaths_status()
        nxt = not curr
        if set_longpaths_enabled(nxt):
            self.refresh_status()
            msg = "Windows 长路径已解除 260 字符限制。" if nxt else "Windows 长路径已恢复默认限制。"
            self.status_lbl.configure(text=msg)
            messagebox.showinfo("提示", msg)
        else:
            messagebox.showerror("错误", "修改长路径限制失败。")

    def manual_restart_explorer(self):
        self.status_lbl.configure(text="正在重启资源管理器...")
        self.root.update()
        if restart_explorer():
            self.status_lbl.configure(text="资源管理器重启成功。")
            messagebox.showinfo("提示", "资源管理器已成功重启，更改已生效。")
        else:
            self.status_lbl.configure(text="资源管理器重启失败。")
            messagebox.showerror("错误", "无法重启资源管理器。")


def _show_error_and_exit(title, message):
    root = tk.Tk()
    设置窗口图标(root)
    root.withdraw()
    messagebox.showerror(title, message)
    sys.exit(1)


def main():
    if sys.platform != "win32":
        _show_error_and_exit("系统不支持", "本工具仅支持 Windows 操作系统。")

    if not is_admin():
        if "--elevated" in sys.argv:
            _show_error_and_exit("权限不足", "本工具需要管理员权限才能运行。\n请右键点击程序并选择“以管理员身份运行”。")
        run_as_admin()
        return

    root = tk.Tk()
    设置窗口图标(root)
    app = CodingLabAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
