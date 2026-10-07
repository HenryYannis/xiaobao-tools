# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 桌面规范、环境优化与应用商店管理
"""

import os
import sys
import shutil
import ctypes
import configparser
import subprocess

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from winreg import (
    HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    CreateKey, OpenKey, SetValueEx, QueryInfoKey, EnumKey,
    REG_SZ, KEY_READ
)
from config import (
    RESOURCE_DIR, WALLPAPER_FILENAME,
    _LOCKSCREEN_REG_PATH, _LOCKSCREEN_REG_VALUE,
    _WALLPAPER_DEPLOY_DIR, _WALLPAPER_DEPLOY_PATH,
    REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE,
    REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE,
    REG_EXPLORER_ADVANCED_PATH, REG_HIDE_FILE_EXT_VALUE,
    REG_LONGPATHS_PATH, REG_LONGPATHS_VALUE,
    PYPI_TUNA_URL, PYPI_ALIYUN_URL
)
from reg_utils import (
    reg_read_dword, reg_write_dword, reg_delete_value
)

# --- 壁纸与锁屏 ---
def get_wallpaper_source_path():
    return os.path.join(RESOURCE_DIR, WALLPAPER_FILENAME)

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

def get_wallpaper_locked():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)
    return val == 1

def set_wallpaper_locked(locked):
    if locked:
        return reg_write_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)

# --- 桌面聚焦图标 ---
def get_spotlight_hidden():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)
    return val == 1

def set_spotlight_hidden(hidden):
    if hidden:
        return reg_write_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)

# --- 文件扩展名 ---
def get_file_ext_visible():
    val = reg_read_dword(HKEY_CURRENT_USER, REG_EXPLORER_ADVANCED_PATH, REG_HIDE_FILE_EXT_VALUE)
    return val == 0

def set_file_ext_visible(visible):
    val = 0 if visible else 1
    return reg_write_dword(HKEY_CURRENT_USER, REG_EXPLORER_ADVANCED_PATH, REG_HIDE_FILE_EXT_VALUE, val)

# --- Windows 长路径 ---
def get_longpaths_status():
    val = reg_read_dword(HKEY_LOCAL_MACHINE, REG_LONGPATHS_PATH, REG_LONGPATHS_VALUE)
    return val == 1

def set_longpaths_enabled(enabled):
    val = 1 if enabled else 0
    return reg_write_dword(HKEY_LOCAL_MACHINE, REG_LONGPATHS_PATH, REG_LONGPATHS_VALUE, val)

# --- Microsoft Store 应用商店管理 ---
def get_ms_store_status():
    """检查系统是否安装了 Microsoft Store (返回 True 表示已安装，False 表示未安装/已卸载)"""
    # 1. 快速检查协议关联 (HKEY_CLASSES_ROOT\ms-windows-store)
    for root in (HKEY_CLASSES_ROOT, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER):
        try:
            path = r"ms-windows-store" if root == HKEY_CLASSES_ROOT else r"Software\Classes\ms-windows-store"
            with OpenKey(root, path, 0, KEY_READ):
                return True
        except Exception:
            pass
    # 2. 检查注册表 AppModel Packages
    try:
        with OpenKey(HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages", 0, KEY_READ) as k:
            count = QueryInfoKey(k)[0]
            for i in range(count):
                if "Microsoft.WindowsStore" in EnumKey(k, i):
                    return True
    except Exception:
        pass
    # 3. 检查系统目录 WindowsApps 中是否存在商店激活包
    try:
        winapps = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "WindowsApps")
        if os.path.exists(winapps):
            for entry in os.listdir(winapps):
                if "Microsoft.WindowsStore" in entry:
                    return True
    except Exception:
        pass
    return False

def uninstall_ms_store():
    """彻底卸载 Microsoft Store (当前用户、所有用户及预装包)"""
    ps_cmd = (
        "Get-AppxPackage -AllUsers *WindowsStore* | Remove-AppxPackage -ErrorAction SilentlyContinue; "
        "Get-AppxPackage *WindowsStore* | Remove-AppxPackage -ErrorAction SilentlyContinue; "
        "Get-AppxProvisionedPackage -Online | Where-Object { $_.PackageName -like '*WindowsStore*' } | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, "Microsoft Store (应用商店) 已执行卸载清理。"
    except Exception as e:
        return False, f"卸载执行失败: {e}"

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
                    break
            except Exception:
                pass

    if not current_url:
        return "default", ""

    if PYPI_TUNA_URL.lower() in current_url.lower():
        return "tuna", current_url
    elif PYPI_ALIYUN_URL.lower() in current_url.lower():
        return "aliyun", current_url
    else:
        return "other", current_url

def set_pip_mirror_source(source_type):
    """设置 pip 镜像源: 'tuna', 'aliyun', 'default'"""
    path = get_pip_config_file_path()
    if not path:
        return False, "未能识别用户 AppData 目录"

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
