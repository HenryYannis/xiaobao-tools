#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 命令行进度条 (Progress Bar)

功能：
- 在命令行显示动态进度条
- 支持自定义进度条长度
- 实时更新进度百分比

使用方法：
- 直接运行即可看到进度条效果
- 可作为模块导入使用

注意事项：
- 需要在命令行环境中运行
- 使用 time.sleep 模拟进度，实际使用时可替换为真实任务

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import time


def show_progress_bar(total=10):
    """显示进度条"""
    print("---------开始执行---------")
    for i in range(total + 1):
        a = "**" * i
        b = ".." * (total - i)
        c = (i / total) * 100
        print(f"\r{c}%：[{a}->{b}]", end="", flush=True)
        time.sleep(1)
    print("\n---------结束执行---------")


if __name__ == "__main__":
    show_progress_bar()