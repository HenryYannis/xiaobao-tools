#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 移除桌面了解此图片 (Hide Desktop Info)

功能：
- 移除 Windows 锁屏界面的"了解此图片"按钮
- 通过修改注册表实现
- 让锁屏界面更加简洁

使用方法：
- 直接运行即可移除
- 需要重启资源管理器生效

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启资源管理器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import sys
import subprocess
from winreg import (
    CreateKey, SetValueEx, REG_DWORD,
    HKEY_CURRENT_USER, CloseKey
)
import ctypes

# 目标注册表路径和键值
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
REG_KEY_NAME = "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}"

def show_message(title, message):
    """显示一个Windows提示框"""
    # 0x00000040 是 MB_ICONINFORMATION， 0x00000000 是 MB_OK
    ctypes.windll.user32.MessageBoxW(None, message, title, 0x00000040)

def modify_registry():
    """直接修改注册表"""
    try:
        # 尝试打开或创建键
        hKey = CreateKey(HKEY_CURRENT_USER, REG_PATH)
        
        # 设置键值：REG_DWORD类型，数据为 1 (隐藏图标)
        SetValueEx(hKey, REG_KEY_NAME, 0, REG_DWORD, 1)
        
        CloseKey(hKey)
    except Exception:
        # 如果没有权限，将直接失败
        show_message("错误", "注册表修改失败，请以管理员身份运行。")
        sys.exit(1)

def restart_explorer():
    """重启资源管理器"""
    try:
        # 强制结束 explorer.exe (静默)
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"], 
            check=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # 重新启动 explorer.exe
        subprocess.Popen(["explorer.exe"])
    except Exception:
        pass # 重启失败不影响功能，静默处理

def main():
    # 1. 修改注册表
    modify_registry()
    
    # 2. 重启资源管理器
    restart_explorer()
    
    # 3. 任务完成提示
    show_message("操作完成", "桌面图标已删除")

if __name__ == "__main__":
    # 使用 setuptools-dummy-setup-minimal-version-1.0.0
    main()