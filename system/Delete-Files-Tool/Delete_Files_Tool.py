#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 文件清理工具 (File Cleaner Tool)

功能：
- 扫描文件类型并进行分类统计
- 扫描大文件（默认大于 2MB 的 .sb3 文件）
- 扫描空文件夹
- 支持全选、反选以及批量删除选中项目

特点：
- 界面直观：配备简洁易用的列表与分类面板，支持多选
- 全局现代字体：全界面微软雅黑渲染，布局排版更加美观
- 零依赖：仅使用 Python 标准库开发，开箱即用

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox


if getattr(sys, 'frozen', False):
    RESOURCE_DIR = sys._MEIPASS
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
    FOLDER_PATH = os.path.dirname(SCRIPT_DIR)
else:
    RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
    SCRIPT_DIR = RESOURCE_DIR
    FOLDER_PATH = os.path.dirname(os.path.dirname(SCRIPT_DIR))
EXCLUDED_FOLDERS = [
    os.path.join(FOLDER_PATH, '.verysync'),
    os.path.join(FOLDER_PATH, 'Scratch 初始程序'),
    os.path.join(FOLDER_PATH, 'Scratch 素材'),
    os.path.join(FOLDER_PATH, '安装包'),
    os.path.join(FOLDER_PATH, '比赛'),
]


def is_excluded(path):
    path_norm = os.path.normpath(path)
    for exc in EXCLUDED_FOLDERS:
        if path_norm.startswith(os.path.normpath(exc)):
            return True
    return False


def scan_extensions(folder_path):
    ext_map = {}
    for root, dirs, files in os.walk(folder_path):
        if is_excluded(root):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext:
                ext_map.setdefault(ext, []).append(os.path.join(root, f))
    return ext_map


def scan_large_files(folder_path, ext='.sb3', min_size_mb=2):
    result = []
    threshold = min_size_mb * 1024 * 1024
    for root, dirs, files in os.walk(folder_path):
        if is_excluded(root):
            continue
        for f in files:
            if f.lower().endswith(ext):
                fp = os.path.join(root, f)
                if os.path.getsize(fp) > threshold:
                    result.append(fp)
    return result


def scan_empty_folders(folder_path):
    result = []
    for root, dirs, files in os.walk(folder_path):
        if is_excluded(root):
            continue
        if not dirs and not files:
            result.append(root)
    return result


class FileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件清理工具")
        self.root.geometry("850x600")
        self.root.minsize(700, 500)

        # 设置窗口图标
        icon_path = os.path.join(RESOURCE_DIR, "bin.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # 优化全局 UI 样式与字体排版
        self.style = ttk.Style()
        self.style.configure(".", font=("微软雅黑", 9))
        self.style.configure("Treeview", font=("微软雅黑", 9), rowheight=24)
        self.style.configure("Treeview.Heading", font=("微软雅黑", 9, "bold"))
        self.style.configure("TLabelframe.Label", font=("微软雅黑", 9, "bold"), foreground="#333333")

        self.current_files = []
        self.current_folders = []
        self.ext_map = {}
        self.is_folder_mode = False

        self._build_ui()
        self._scan()

    def _build_ui(self):
        # 底部状态栏与作者信息栏（在最底端 pack 优先占位）
        sep = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        sep.pack(side=tk.BOTTOM, fill=tk.X)

        footer = ttk.Frame(self.root, padding=(12, 4))
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(footer, text="就绪")
        self.status_label.pack(side=tk.LEFT)

        author_frame = ttk.Frame(footer)
        author_frame.pack(side=tk.RIGHT)

        ttk.Label(
            author_frame,
            text="作者：小宝科技站 (",
            foreground="gray"
        ).pack(side=tk.LEFT)

        link_lbl = tk.Label(
            author_frame,
            text="xbkjz.cn",
            font=("微软雅黑", 9, "underline"),
            fg="#0066CC",
            cursor="hand2"
        )
        link_lbl.pack(side=tk.LEFT)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))
        link_lbl.bind("<Enter>", lambda e: link_lbl.configure(fg="#0044AA"))
        link_lbl.bind("<Leave>", lambda e: link_lbl.configure(fg="#0066CC"))

        ttk.Label(
            author_frame,
            text=")",
            foreground="gray"
        ).pack(side=tk.LEFT)

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="扫描文件类型", command=self._scan).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="扫描大文件 (>2MB .sb3)", command=self._scan_large).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="扫描空文件夹", command=self._scan_empty).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="删除选中", command=self._delete_selected).pack(side=tk.RIGHT, padx=4)
        ttk.Button(toolbar, text="全选", command=self._select_all).pack(side=tk.RIGHT, padx=4)
        ttk.Button(toolbar, text="反选", command=self._invert_selection).pack(side=tk.RIGHT, padx=4)

        ext_frame = ttk.LabelFrame(self.root, text="文件类型", padding=6)
        ext_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 0), pady=8)

        self.ext_listbox = tk.Listbox(
            ext_frame, 
            width=20, 
            exportselection=False,
            font=("微软雅黑", 9),
            bd=1,
            relief=tk.SOLID,
            highlightthickness=0,
            selectbackground="#0078D7",
            selectforeground="white"
        )
        self.ext_listbox.pack(fill=tk.Y, expand=True)
        self.ext_listbox.bind("<<ListboxSelect>>", self._on_ext_select)

        list_frame = ttk.LabelFrame(self.root, text="文件列表", padding=6)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ("filename", "size", "path")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("filename", text="文件名")
        self.tree.heading("size", text="大小")
        self.tree.heading("path", text="路径")
        self.tree.column("filename", width=180)
        self.tree.column("size", width=80, anchor=tk.E)
        self.tree.column("path", width=400)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _scan(self):
        self.ext_map = scan_extensions(FOLDER_PATH)
        self.ext_listbox.delete(0, tk.END)
        for ext in sorted(self.ext_map.keys()):
            count = len(self.ext_map[ext])
            self.ext_listbox.insert(tk.END, f"{ext}  ({count})")
        self.current_files = []
        self._refresh_tree()
        self.status_label.config(text=f"扫描完成，共 {len(self.ext_map)} 种文件类型")

    def _scan_large(self):
        self.current_files = scan_large_files(FOLDER_PATH)
        self.is_folder_mode = False
        self._refresh_tree()
        self.status_label.config(text=f"找到 {len(self.current_files)} 个大文件 (>2MB)")

    def _scan_empty(self):
        self.current_folders = scan_empty_folders(FOLDER_PATH)
        self.is_folder_mode = True
        self._refresh_folder_tree()
        self.status_label.config(text=f"找到 {len(self.current_folders)} 个空文件夹")

    def _on_ext_select(self, event):
        sel = self.ext_listbox.curselection()
        if not sel:
            return
        ext_text = self.ext_listbox.get(sel[0])
        ext = ext_text.split("  ")[0]
        self.current_files = self.ext_map.get(ext, [])
        self._refresh_tree()
        self.status_label.config(text=f"{ext} 共 {len(self.current_files)} 个文件")

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for fp in self.current_files:
            try:
                size = os.path.getsize(fp)
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.2f} MB"
            except OSError:
                size_str = "无法读取"
            self.tree.insert("", tk.END, values=(os.path.basename(fp), size_str, fp))

    def _refresh_folder_tree(self):
        self.tree.delete(*self.tree.get_children())
        for fp in self.current_folders:
            self.tree.insert("", tk.END, values=(os.path.basename(fp), "空文件夹", fp))

    def _select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _invert_selection(self):
        selected = set(self.tree.selection())
        all_items = set(self.tree.get_children())
        self.tree.selection_set(all_items - selected)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的项目")
            return

        paths = [self.tree.item(s)["values"][2] for s in selected]
        names = "\n".join(os.path.basename(p) for p in paths[:20])
        if len(paths) > 20:
            names += f"\n... 等共 {len(paths)} 个"

        if not messagebox.askyesno("确认删除", f"确定要删除以下项目吗？\n\n{names}"):
            return

        deleted = 0
        errors = []
        for p in paths:
            try:
                if self.is_folder_mode:
                    os.rmdir(p)
                else:
                    os.remove(p)
                deleted += 1
            except Exception as e:
                errors.append(f"{p}\n  原因: {e}")

        msg = f"成功删除 {deleted} 个项目"
        if errors:
            msg += f"\n\n删除失败 {len(errors)} 个：\n" + "\n".join(errors[:10])
        messagebox.showinfo("完成", msg)
        if self.is_folder_mode:
            self.current_folders = scan_empty_folders(FOLDER_PATH)
            self._refresh_folder_tree()
        else:
            self._refresh_tree()
        self.status_label.config(text=f"已删除 {deleted} 个项目")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCleanerApp(root)
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"+{x}+{y}")
    root.mainloop()
