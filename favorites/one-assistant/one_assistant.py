#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 (Lab Policy Configurator) - 程序主入口

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import tkinter as tk
from tkinter import messagebox

from config import 设置窗口图标
from reg_utils import is_admin, run_as_admin
from ui import CodingLabAssistantGUI

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
