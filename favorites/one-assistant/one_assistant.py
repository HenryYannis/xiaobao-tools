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
def reg_read_dword(hkey, path, value_name):
    try:
        with OpenKey(hkey, path, 0, KEY_READ) as key:
            val, _ = QueryValueEx(key, value_name)
            return val
    except Exception:
        return None

def reg_write_dword(hkey, path, value_name, value):
    try:
        with CreateKey(hkey, path) as key:
            SetValueEx(key, value_name, 0, REG_DWORD, value)
        return True
    except Exception as e:
        print(f"[RegWriteDwordError] {path}\\{value_name}: {e}")
        return False

def reg_read_string(hkey, path, value_name):
    try:
        with OpenKey(hkey, path, 0, KEY_READ) as key:
            val, _ = QueryValueEx(key, value_name)
            return val
    except Exception:
        return None

def reg_write_string(hkey, path, value_name, value):
    try:
        with CreateKey(hkey, path) as key:
            SetValueEx(key, value_name, 0, REG_SZ, value)
        return True
    except Exception as e:
        print(f"[RegWriteStringError] {path}\\{value_name}: {e}")
        return False

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

def kill_edge_process():
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "msedge.exe"],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        import time
        time.sleep(0.5)
        return True
    except Exception:
        return False

def kill_chrome_process():
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "chrome.exe"],
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        import time
        time.sleep(0.5)
        return True
    except Exception:
        return False


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
    import tempfile
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
    hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_GAME_VALUE)
    hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_GAME_VALUE)
    return hklm == 0 or hkcu == 0

def set_edge_game_disabled(disabled):
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_GAME_VALUE, 0)
        s2 = reg_write_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_GAME_VALUE, 0)
        return s1 or s2
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_GAME_VALUE)
        s2 = reg_delete_value(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_GAME_VALUE)
        return s1 and s2

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

# 函数别名
get_edge_shortcut_status = get_edge_startup_status
set_edge_shortcut = set_edge_startup
get_chrome_shortcut_status = get_chrome_startup_status
set_chrome_shortcut = set_chrome_startup

def get_chrome_game_disabled():
    hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_GAME_VALUE)
    hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_GAME_VALUE)
    return hklm == 0 or hkcu == 0

def set_chrome_game_disabled(disabled):
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_GAME_VALUE, 0)
        s2 = reg_write_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_GAME_VALUE, 0)
        return s1 or s2
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_GAME_VALUE)
        s2 = reg_delete_value(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_GAME_VALUE)
        return s1 and s2

def get_chrome_downloads_disabled():
    return _get_browser_downloads_disabled(REG_CHROME_PATH)

def set_chrome_downloads_disabled(disabled):
    return _set_browser_downloads_disabled(REG_CHROME_PATH, disabled)


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

        # 1. Edge 浏览器访问管控
        card_edge = tk.LabelFrame(
            main_content,
            text=" Edge 浏览器访问策略 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_edge.pack(fill=tk.X, pady=(0, 5))

        # 1.1 Edge 白名单
        row_ewl = tk.Frame(card_edge, bg="#FFFFFF")
        row_ewl.pack(fill=tk.X, pady=2)
        self.edge_wl_lbl = tk.Label(row_ewl, text="网址白名单锁定：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.edge_wl_lbl.pack(side=tk.LEFT)

        self.edge_wl_cfg_btn = tk.Button(
            row_ewl, text="管理白名单", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.open_whitelist_manager
        )
        self.edge_wl_cfg_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.edge_wl_btn = tk.Button(
            row_ewl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_edge_whitelist
        )
        self.edge_wl_btn.pack(side=tk.RIGHT)

        # 1.2 Edge 桌面直达启动图标
        row_ept = tk.Frame(card_edge, bg="#FFFFFF")
        row_ept.pack(fill=tk.X, pady=2)
        self.edge_portal_lbl = tk.Label(row_ept, text="桌面直达启动图标：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.edge_portal_lbl.pack(side=tk.LEFT)

        self.edge_test_btn = tk.Button(
            row_ept, text="测试打开", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.test_open_edge
        )
        self.edge_test_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.edge_portal_btn = tk.Button(
            row_ept, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_edge_startup
        )
        self.edge_portal_btn.pack(side=tk.RIGHT)

        # 1.3 Edge 离线游戏
        row_egm = tk.Frame(card_edge, bg="#FFFFFF")
        row_egm.pack(fill=tk.X, pady=2)
        self.edge_game_lbl = tk.Label(row_egm, text="离线冲浪游戏 (Surf)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.edge_game_lbl.pack(side=tk.LEFT)
        self.edge_game_btn = tk.Button(
            row_egm, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_edge_game
        )
        self.edge_game_btn.pack(side=tk.RIGHT)

        # 1.4 Edge 下载限制
        row_edl = tk.Frame(card_edge, bg="#FFFFFF")
        row_edl.pack(fill=tk.X, pady=2)
        self.edge_dl_lbl = tk.Label(row_edl, text="文件下载限制：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.edge_dl_lbl.pack(side=tk.LEFT)
        self.edge_dl_btn = tk.Button(
            row_edl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_edge_downloads
        )
        self.edge_dl_btn.pack(side=tk.RIGHT)

        # 2. Chrome 浏览器访问管控 (1:1 对照)
        card_chrome = tk.LabelFrame(
            main_content,
            text=" Chrome 浏览器访问策略 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_chrome.pack(fill=tk.X, pady=(0, 5))

        # 2.1 Chrome 白名单
        row_cwl = tk.Frame(card_chrome, bg="#FFFFFF")
        row_cwl.pack(fill=tk.X, pady=2)
        self.chrome_wl_lbl = tk.Label(row_cwl, text="网址白名单锁定：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.chrome_wl_lbl.pack(side=tk.LEFT)

        self.chrome_wl_cfg_btn = tk.Button(
            row_cwl, text="管理白名单", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.open_whitelist_manager
        )
        self.chrome_wl_cfg_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.chrome_wl_btn = tk.Button(
            row_cwl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_chrome_whitelist
        )
        self.chrome_wl_btn.pack(side=tk.RIGHT)

        # 2.2 Chrome 桌面直达启动图标
        row_cpt = tk.Frame(card_chrome, bg="#FFFFFF")
        row_cpt.pack(fill=tk.X, pady=2)
        self.chrome_portal_lbl = tk.Label(row_cpt, text="桌面直达启动图标：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.chrome_portal_lbl.pack(side=tk.LEFT)

        self.chrome_test_btn = tk.Button(
            row_cpt, text="测试打开", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.test_open_chrome
        )
        self.chrome_test_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.chrome_portal_btn = tk.Button(
            row_cpt, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_chrome_startup
        )
        self.chrome_portal_btn.pack(side=tk.RIGHT)

        # 2.3 Chrome 离线游戏
        row_cgm = tk.Frame(card_chrome, bg="#FFFFFF")
        row_cgm.pack(fill=tk.X, pady=2)
        self.chrome_game_lbl = tk.Label(row_cgm, text="离线恐龙游戏 (Dino)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.chrome_game_lbl.pack(side=tk.LEFT)
        self.chrome_game_btn = tk.Button(
            row_cgm, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_chrome_game
        )
        self.chrome_game_btn.pack(side=tk.RIGHT)

        # 2.4 Chrome 下载限制
        row_cdl = tk.Frame(card_chrome, bg="#FFFFFF")
        row_cdl.pack(fill=tk.X, pady=2)
        self.chrome_dl_lbl = tk.Label(row_cdl, text="文件下载限制：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.chrome_dl_lbl.pack(side=tk.LEFT)
        self.chrome_dl_btn = tk.Button(
            row_cdl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_chrome_downloads
        )
        self.chrome_dl_btn.pack(side=tk.RIGHT)

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

    # ── 状态读取与刷新 ────────────────────────────────────────────────
    def refresh_status(self):
        # 1. Edge 策略刷新
        edge_wl_locked = get_edge_whitelist_locked()
        if edge_wl_locked:
            self.edge_wl_lbl.configure(text="网址白名单锁定：已开启限制 (仅允许白名单网站)")
            self.edge_wl_btn.configure(text="解除限制", bg="#FFFFFF", fg="#0F172A")
        else:
            self.edge_wl_lbl.configure(text="网址白名单锁定：未锁定 (允许自由访问全网)")
            self.edge_wl_btn.configure(text="开启限制", bg="#0F172A", fg="#FFFFFF")

        edge_pt_on = get_edge_startup_status()
        if edge_pt_on:
            self.edge_portal_lbl.configure(text="桌面直达启动图标：已配置直达 (双击直达目标主页)")
            self.edge_portal_btn.configure(text="恢复默认", bg="#FFFFFF", fg="#0F172A")
        else:
            self.edge_portal_lbl.configure(text="桌面直达启动图标：默认启动图标 (未绑定直达参数)")
            self.edge_portal_btn.configure(text="配置直达", bg="#0F172A", fg="#FFFFFF")

        edge_gm_off = get_edge_game_disabled()
        if edge_gm_off:
            self.edge_game_lbl.configure(text="离线冲浪游戏 (Surf)：已禁用")
            self.edge_game_btn.configure(text="允许游戏")
        else:
            self.edge_game_lbl.configure(text="离线冲浪游戏 (Surf)：未禁用")
            self.edge_game_btn.configure(text="禁用游戏")

        edge_dl_off = get_edge_downloads_disabled()
        if edge_dl_off:
            self.edge_dl_lbl.configure(text="文件下载限制：已禁止所有文件下载")
            self.edge_dl_btn.configure(text="允许下载")
        else:
            self.edge_dl_lbl.configure(text="文件下载限制：允许下载")
            self.edge_dl_btn.configure(text="禁止下载")

        # 2. Chrome 策略刷新
        chrome_wl_locked = get_chrome_whitelist_locked()
        if chrome_wl_locked:
            self.chrome_wl_lbl.configure(text="网址白名单锁定：已开启限制 (仅允许白名单网站)")
            self.chrome_wl_btn.configure(text="解除限制", bg="#FFFFFF", fg="#0F172A")
        else:
            self.chrome_wl_lbl.configure(text="网址白名单锁定：未锁定 (允许自由访问全网)")
            self.chrome_wl_btn.configure(text="开启限制", bg="#0F172A", fg="#FFFFFF")

        chrome_pt_on = get_chrome_startup_status()
        if chrome_pt_on:
            self.chrome_portal_lbl.configure(text="桌面直达启动图标：已配置直达 (双击直达目标主页)")
            self.chrome_portal_btn.configure(text="恢复默认", bg="#FFFFFF", fg="#0F172A")
        else:
            self.chrome_portal_lbl.configure(text="桌面直达启动图标：默认启动图标 (未绑定直达参数)")
            self.chrome_portal_btn.configure(text="配置直达", bg="#0F172A", fg="#FFFFFF")

        chrome_gm_off = get_chrome_game_disabled()
        if chrome_gm_off:
            self.chrome_game_lbl.configure(text="离线恐龙游戏 (Dino)：已禁用")
            self.chrome_game_btn.configure(text="允许游戏")
        else:
            self.chrome_game_lbl.configure(text="离线恐龙游戏 (Dino)：未禁用")
            self.chrome_game_btn.configure(text="禁用游戏")

        chrome_dl_off = get_chrome_downloads_disabled()
        if chrome_dl_off:
            self.chrome_dl_lbl.configure(text="文件下载限制：已禁止所有文件下载")
            self.chrome_dl_btn.configure(text="允许下载")
        else:
            self.chrome_dl_lbl.configure(text="文件下载限制：允许下载")
            self.chrome_dl_btn.configure(text="禁止下载")

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
                edge_on = get_edge_whitelist_locked()
                chrome_on = get_chrome_whitelist_locked()
                if edge_on:
                    set_edge_whitelist_locked(True, cleaned)
                if chrome_on:
                    set_chrome_whitelist_locked(True, cleaned)
                win.destroy()
                self.refresh_status()
                if edge_on or chrome_on:
                    if messagebox.askyesno("保存成功", f"白名单规则已更新并同步写入注册表（共 {len(cleaned)} 条）。\n\n新策略需要重启浏览器生效，是否立即关闭并重启浏览器？"):
                        if edge_on:
                            kill_edge_process()
                            subprocess.Popen(["cmd", "/c", "start", "msedge"], shell=True)
                        if chrome_on:
                            kill_chrome_process()
                            subprocess.Popen(["cmd", "/c", "start", "chrome"], shell=True)
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

    # ── Edge 动作 ──
    def toggle_edge_whitelist(self):
        curr = get_edge_whitelist_locked()
        nxt = not curr
        if nxt and not messagebox.askyesno("确认", "开启后 Edge 将阻断所有非白名单网站，是否继续？"):
            return
        if set_edge_whitelist_locked(nxt):
            self.refresh_status()
            tip = "Edge 白名单限制已开启。" if nxt else "Edge 白名单限制已解除。"
            self.status_lbl.configure(text=tip)
            if messagebox.askyesno("提示", f"{tip}\n\n是否立即重启 Edge 浏览器生效？"):
                kill_edge_process()
                subprocess.Popen(["cmd", "/c", "start", "msedge"], shell=True)
        else:
            messagebox.showerror("错误", "修改 Edge 白名单策略失败。")

    def toggle_edge_startup(self):
        curr = get_edge_startup_status()
        nxt = not curr
        if set_edge_startup(nxt):
            self.refresh_status()
            tip = f"Edge 桌面图标已配置直达：{DEFAULT_STARTUP_URL}" if nxt else "Edge 桌面图标已恢复为默认启动。"
            self.status_lbl.configure(text=tip)
            if nxt:
                if messagebox.askyesno("配置成功", f"{tip}\n\n是否立即通过直达参数启动 Edge 验证效果？"):
                    self.test_open_edge()
            else:
                messagebox.showinfo("提示", tip)
        else:
            messagebox.showerror("错误", "修改 Edge 桌面快捷方式失败，未找到 Edge 安装路径。")

    def test_open_edge(self):
        try:
            subprocess.Popen(["cmd", "/c", "start", "msedge", DEFAULT_STARTUP_URL], shell=True)
        except Exception:
            webbrowser.open(DEFAULT_STARTUP_URL)

    def toggle_edge_game(self):
        curr = get_edge_game_disabled()
        nxt = not curr
        if set_edge_game_disabled(nxt):
            self.refresh_status()
            messagebox.showinfo("提示", "Edge 冲浪游戏策略已保存，重启浏览器后生效。")
        else:
            messagebox.showerror("错误", "修改 Edge 游戏策略失败。")

    def toggle_edge_downloads(self):
        curr = get_edge_downloads_disabled()
        nxt = not curr
        if set_edge_downloads_disabled(nxt):
            self.refresh_status()
            act = "已禁止 Edge 下载文件。" if nxt else "已允许 Edge 下载文件。"
            if messagebox.askyesno("提示", f"{act}\n\n是否立即关闭 Edge 浏览器？"):
                kill_edge_process()
        else:
            messagebox.showerror("错误", "修改 Edge 下载策略失败。")

    # ── Chrome 动作 ──
    def toggle_chrome_whitelist(self):
        curr = get_chrome_whitelist_locked()
        nxt = not curr
        if nxt and not messagebox.askyesno("确认", "开启后 Chrome 将阻断所有非白名单网站，是否继续？"):
            return
        if set_chrome_whitelist_locked(nxt):
            self.refresh_status()
            tip = "Chrome 白名单限制已开启。" if nxt else "Chrome 白名单限制已解除。"
            self.status_lbl.configure(text=tip)
            if messagebox.askyesno("提示", f"{tip}\n\n是否立即重启 Chrome 浏览器生效？"):
                kill_chrome_process()
                subprocess.Popen(["cmd", "/c", "start", "chrome"], shell=True)
        else:
            messagebox.showerror("错误", "修改 Chrome 白名单策略失败。")

    def toggle_chrome_startup(self):
        curr = get_chrome_startup_status()
        nxt = not curr
        if set_chrome_startup(nxt):
            self.refresh_status()
            tip = f"Chrome 桌面图标已配置直达：{DEFAULT_STARTUP_URL}" if nxt else "Chrome 桌面图标已恢复为默认启动。"
            self.status_lbl.configure(text=tip)
            if nxt:
                if messagebox.askyesno("配置成功", f"{tip}\n\n是否立即通过直达参数启动 Chrome 验证效果？"):
                    self.test_open_chrome()
            else:
                messagebox.showinfo("提示", tip)
        else:
            messagebox.showerror("错误", "修改 Chrome 桌面快捷方式失败，未找到 Chrome 安装路径。")

    def test_open_chrome(self):
        try:
            subprocess.Popen(["cmd", "/c", "start", "chrome", DEFAULT_STARTUP_URL], shell=True)
        except Exception:
            webbrowser.open(DEFAULT_STARTUP_URL)

    def toggle_chrome_game(self):
        curr = get_chrome_game_disabled()
        nxt = not curr
        if set_chrome_game_disabled(nxt):
            self.refresh_status()
            messagebox.showinfo("提示", "Chrome 恐龙游戏策略已保存，重启浏览器后生效。")
        else:
            messagebox.showerror("错误", "修改 Chrome 游戏策略失败。")

    def toggle_chrome_downloads(self):
        curr = get_chrome_downloads_disabled()
        nxt = not curr
        if set_chrome_downloads_disabled(nxt):
            self.refresh_status()
            act = "已禁止 Chrome 下载文件。" if nxt else "已允许 Chrome 下载文件。"
            if messagebox.askyesno("提示", f"{act}\n\n是否立即关闭 Chrome 浏览器？"):
                kill_chrome_process()
        else:
            messagebox.showerror("错误", "修改 Chrome 下载策略失败。")

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

    def manual_restart_edge(self):
        kill_edge_process()
        self.status_lbl.configure(text="Edge 浏览器已关闭。")
        messagebox.showinfo("提示", "Edge 浏览器已关闭，请重新启动以应用新策略。")

    def manual_restart_chrome(self):
        kill_chrome_process()
        self.status_lbl.configure(text="Chrome 浏览器已关闭。")
        messagebox.showinfo("提示", "Chrome 浏览器已关闭，请重新启动以应用新策略。")


def main():
    if sys.platform != "win32":
        root = tk.Tk()
        设置窗口图标(root)
        root.withdraw()
        messagebox.showerror("系统不支持", "本工具仅支持 Windows 操作系统。")
        sys.exit(1)

    if not is_admin():
        if "--elevated" in sys.argv:
            root = tk.Tk()
            设置窗口图标(root)
            root.withdraw()
            messagebox.showerror("权限不足", "本工具需要管理员权限才能运行。\n请右键点击程序并选择“以管理员身份运行”。")
            sys.exit(1)
        run_as_admin()
        return

    root = tk.Tk()
    设置窗口图标(root)
    app = CodingLabAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
