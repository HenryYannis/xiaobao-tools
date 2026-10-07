# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 注册表底层读写与系统进程工具
"""

import os
import sys
import time
import ctypes
import subprocess
from winreg import (
    HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    OpenKey, CreateKey, SetValueEx, DeleteValue, DeleteKey,
    EnumKey, QueryValueEx, QueryInfoKey, REG_DWORD, REG_SZ, KEY_READ, KEY_ALL_ACCESS
)

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

# --- 系统基础操作 ---
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
