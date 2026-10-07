#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - Edge 浏览器联网控制工具 (Edge Internet Control)

功能：
- 限制或解除 Edge 浏览器联网权限
- 通过 Windows 防火墙规则控制
- 支持 x86 和 x64 版本的 Edge

使用方法：
- 需要以管理员权限运行
- 点击按钮切换 Edge 的联网状态

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限才能修改防火墙规则
- 修改后需要重启 Edge 浏览器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox

# --- 配置与主程序一致的规则名称 ---
RULE_NAME_X86 = "Block Edge Outbound (x86)"
RULE_NAME_X64 = "Block Edge Outbound (x64)"

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """以管理员权限重新运行当前程序"""
    # 获取当前运行的可执行文件路径
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 .exe
        executable = sys.executable
        params = ""
    else:
        # 如果是 .py 脚本
        executable = sys.executable
        params = f'"{__file__}"'
    
    try:
        # ShellExecuteW 第一个参数为 None，第二个为 "runas" (请求管理员)，后面是程序路径和参数
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    except Exception as e:
        print(f"提权失败: {e}")

def 清理规则():
    """执行删除防火墙规则的命令"""
    print("正在清理防火墙规则...")
    
    # 隐藏执行删除命令
    ret1 = os.system(f'netsh advfirewall firewall delete rule name="{RULE_NAME_X86}" >nul 2>&1')
    ret2 = os.system(f'netsh advfirewall firewall delete rule name="{RULE_NAME_X64}" >nul 2>&1')
    
    # 无论之前有没有规则，只要命令执行过，就视为操作完成
    return True

def main():
    # 1. 创建一个隐藏的 Tk 根窗口（用于弹窗，不显示主界面）
    root = tk.Tk()
    root.withdraw() 

    # 2. 执行清理逻辑
    清理规则()
    
    # 3. 弹出成功提示
    messagebox.showinfo(
        "恢复成功", 
        "防火墙规则已清理！\n\n网络权限已释放。\n如果 Edge 仍无法上网，请尝试刷新网页或重启浏览器。"
    )
    
    root.destroy()

if __name__ == "__main__":
    # 程序入口：先判断权限
    if is_admin():
        # 已经是管理员，直接执行
        main()
    else:
        # 不是管理员，申请提权
        run_as_admin()