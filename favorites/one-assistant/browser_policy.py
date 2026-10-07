# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - Edge 与 Chrome 浏览器访问策略与快捷方式管理
"""

import os
import sys
import subprocess
import tempfile

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from winreg import (
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    CreateKey, SetValueEx, REG_SZ
)
from config import (
    DEFAULT_STARTUP_URL,
    REG_EDGE_PATH, REG_CHROME_PATH,
    REG_BROWSER_BLOCKLIST_SUBKEY, REG_BROWSER_ALLOWLIST_SUBKEY,
    REG_BROWSER_DOWNLOAD_VALUE,
    REG_EDGE_GAME_VALUE, REG_CHROME_GAME_VALUE
)
from reg_utils import (
    reg_read_value, reg_read_dword, reg_read_string,
    reg_write_dword, reg_write_string,
    reg_delete_value, reg_delete_key_tree
)
from whitelist_manager import load_whitelist

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
