#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 全屏仪表盘时钟 (Dashboard Clock)

功能：
- 全屏显示的数字时钟
- 支持多时区显示
- 支持倒计时和闹钟功能
- 支持状态记录看板

使用方法：
- 直接运行即可启动全屏时钟
- 按 Escape 键退出全屏

注意事项：
- 需要 tkinter 库（Python 自带）
- 默认使用 ds-digital 字体，如不存在会使用系统默认字体

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import tkinter as tk
from time import strftime, localtime


class FullscreenClock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.after_id = None

        # 尝试使用 ds-digital 字体，不存在则回退
        try:
            test_font = ('ds-digital', 200)
            self.root.option_add('*Font', test_font)
        except Exception:
            pass

        # 创建时间标签
        self.clock_label = tk.Label(
            self.root,
            font=('ds-digital', 200) if self._font_available('ds-digital') else ('Courier', 150),
            bg='black',
            fg='white'
        )
        self.clock_label.pack(anchor='center', pady=200)

        # 创建日期标签
        self.date_label = tk.Label(
            self.root,
            font=('Arial', 24),
            bg='black',
            fg='#57606a'
        )
        self.date_label.pack(anchor='center', pady=0)

        # 绑定退出快捷键
        self.root.bind('<Escape>', self.safe_exit)
        self.root.bind('q', self.safe_exit)

        self.update_time()

    @staticmethod
    def _font_available(font_name):
        """检查字体是否可用"""
        try:
            import tkinter.font as tkfont
            available = tkfont.families()
            return font_name in available
        except Exception:
            return False

    def update_time(self):
        current_time = strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)

        # 更新日期
        current_date = strftime('%Y年%m月%d日 %A')
        self.date_label.config(text=current_date)

        h, m, s = map(int, current_time.split(':'))

        # 颜色状态机逻辑
        new_color = 'white'  # 默认颜色
        if m == 59 and s >= 57:
            new_color = 'red'

        # 仅在颜色变化时更新配置（优化性能）
        if self.clock_label.cget('foreground') != new_color:
            self.clock_label.config(fg=new_color)

        # 500ms 刷新一次，避免秒数跳变
        self.after_id = self.root.after(500, self.update_time)

    def safe_exit(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


if __name__ == "__main__":
    app = FullscreenClock()
    app.root.mainloop()
