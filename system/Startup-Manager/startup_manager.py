#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开机启动项管理工具 (Startup Manager)

功能：
- 查看所有开机启动项
- 启用/禁用启动项
- 添加新的启动项
- 删除启动项
- 查看启动项详情

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import os
import winreg
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class StartupManager:
    """开机启动项管理器"""

    def __init__(self, root):
        self.root = root
        self.root.title("开机启动项管理工具")
        self.root.resizable(False, False)

        # 启动项注册表路径
        self.startup_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "用户启动项"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "系统启动项"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "用户启动项(一次性)"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "系统启动项(一次性)"),
        ]

        # 启动文件夹路径
        self.startup_folders = [
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
            os.path.join(os.environ.get('ALLUSERSPROFILE', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        ]

        # 创建界面
        self.create_widgets()

        # 加载启动项
        self.load_startup_items()

        # 窗口居中
        self.root.update_idletasks()
        w, h = 900, 600
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="开机启动项管理", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 启动项列表
        list_frame = ttk.LabelFrame(main_frame, text="启动项列表", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        columns = ("name", "command", "location", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.tree.heading("name", text="名称")
        self.tree.heading("command", text="命令")
        self.tree.heading("location", text="位置")
        self.tree.heading("status", text="状态")
        self.tree.column("name", width=200)
        self.tree.column("command", width=350)
        self.tree.column("location", width=150)
        self.tree.column("status", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(btn_frame, text="刷新", command=self.load_startup_items).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="添加启动项", command=self.add_startup_item).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_selected).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="打开启动文件夹", command=self.open_startup_folder).grid(row=0, column=3, padx=5)

        # 详情
        detail_frame = ttk.LabelFrame(main_frame, text="启动项详情", padding="10")
        detail_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.detail_text = tk.Text(detail_frame, height=6, wrap=tk.WORD)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)

        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_startup_items(self):
        """加载启动项"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载注册表启动项
        for hive, key_path, location in self.startup_keys:
            try:
                key = winreg.OpenKey(hive, key_path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        self.tree.insert("", tk.END, values=(name, value, location, "启用"))
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except OSError:
                pass

        # 加载启动文件夹
        for folder in self.startup_folders:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    filepath = os.path.join(folder, file)
                    if os.path.isfile(filepath):
                        self.tree.insert("", tk.END, values=(
                            file, filepath, "启动文件夹", "启用"
                        ))

        self.status_var.set(f"已加载 {len(self.tree.get_children())} 个启动项")

    def on_select(self, event):
        """选择启动项"""
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item, "values")

        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, f"名称: {values[0]}\n")
        self.detail_text.insert(tk.END, f"命令: {values[1]}\n")
        self.detail_text.insert(tk.END, f"位置: {values[2]}\n")
        self.detail_text.insert(tk.END, f"状态: {values[3]}\n")

        command = values[1]
        if os.path.exists(command):
            self.detail_text.insert(tk.END, f"\n文件存在: 是\n")
            try:
                self.detail_text.insert(tk.END, f"文件大小: {os.path.getsize(command)} 字节\n")
            except OSError:
                pass
        else:
            self.detail_text.insert(tk.END, f"\n文件存在: 否\n")

    def add_startup_item(self):
        """添加启动项"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加启动项")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        dx = (dialog.winfo_screenwidth() - 500) // 2
        dy = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"500x200+{dx}+{dy}")

        ttk.Label(dialog, text="名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(dialog, text="命令:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        cmd_var = tk.StringVar()
        cmd_frame = ttk.Frame(dialog)
        cmd_frame.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))
        ttk.Entry(cmd_frame, textvariable=cmd_var, width=35).grid(row=0, column=0)
        ttk.Button(cmd_frame, text="浏览", command=lambda: self.browse_command(cmd_var)).grid(row=0, column=1, padx=(5, 0))

        ttk.Label(dialog, text="位置:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        location_var = tk.StringVar(value="用户启动项")
        ttk.Combobox(dialog, textvariable=location_var, values=["用户启动项", "系统启动项", "启动文件夹"],
                     state="readonly", width=20).grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="确定", command=lambda: self.confirm_add(
            name_var.get(), cmd_var.get(), location_var.get(), dialog
        )).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).grid(row=0, column=1, padx=10)

    def browse_command(self, cmd_var):
        """浏览命令"""
        filepath = filedialog.askopenfilename(
            title="选择程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filepath:
            cmd_var.set(filepath)

    def confirm_add(self, name, command, location, dialog):
        """确认添加"""
        if not name or not command:
            messagebox.showwarning("警告", "请填写名称和命令")
            return

        try:
            if location == "用户启动项":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                                    0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                winreg.CloseKey(key)
            elif location == "系统启动项":
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                                    0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                winreg.CloseKey(key)
            elif location == "启动文件夹":
                folder = self.startup_folders[0]
                shortcut_path = os.path.join(folder, name + ".lnk")
                subprocess.run(
                    f'powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\'{shortcut_path}\'); $s.TargetPath = \'{command}\'; $s.Save()"',
                    shell=True, timeout=30
                )

            dialog.destroy()
            self.load_startup_items()
            messagebox.showinfo("成功", "启动项已添加")

        except (OSError, subprocess.SubprocessError) as e:
            logging.error(f"添加启动项失败: {e}")
            messagebox.showerror("错误", f"添加失败: {e}")

    def delete_selected(self):
        """删除选中启动项"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的启动项")
            return

        if not messagebox.askyesno("确认", "确定要删除选中的启动项吗？"):
            return

        for item in selected:
            values = self.tree.item(item, "values")
            name = values[0]
            location = values[2]

            try:
                if location == "用户启动项":
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                        r"Software\Microsoft\Windows\CurrentVersion\Run",
                                        0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                elif location == "系统启动项":
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                        r"Software\Microsoft\Windows\CurrentVersion\Run",
                                        0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                elif location == "启动文件夹":
                    filepath = values[1]
                    if os.path.exists(filepath):
                        os.remove(filepath)

            except (OSError, PermissionError) as e:
                logging.error(f"删除启动项失败: {e}")
                messagebox.showerror("错误", f"删除失败: {e}")

        self.load_startup_items()
        messagebox.showinfo("成功", "启动项已删除")

    def open_startup_folder(self):
        """打开启动文件夹"""
        folder = self.startup_folders[0]
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("警告", "启动文件夹不存在")


if __name__ == "__main__":
    root = tk.Tk()
    app = StartupManager(root)
    root.mainloop()
