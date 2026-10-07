# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - GUI 界面与交互层
三色设计规范：中性灰白底 #F8FAFC + 主文字/按钮 #0F172A + 边框中灰 #E2E8F0
"""

import os
import sys
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox, scrolledtext

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from config import DEFAULT_STARTUP_URL, DEFAULT_ALLOWLIST, 设置窗口图标
from reg_utils import (
    restart_explorer,
    kill_browser_process
)
from whitelist_manager import load_whitelist, save_whitelist
from browser_policy import BROWSERS
from system_policy import (
    apply_wallpaper_and_lockscreen,
    get_wallpaper_locked, set_wallpaper_locked,
    get_spotlight_hidden, set_spotlight_hidden,
    get_file_ext_visible, set_file_ext_visible,
    get_longpaths_status, set_longpaths_enabled,
    get_ms_store_status, uninstall_ms_store,
    get_pip_mirror_type, set_pip_mirror_source
)
from cloud_sync import (
    get_cloud_sync_installed,
    install_cloud_sync_task,
    uninstall_cloud_sync_task,
    run_cloud_sync_now
)

class CodingLabAssistantGUI:
    def __init__(self, root):
        self.root = root
        设置窗口图标(self.root)
        self.root.title("机房教学策略配置工具")
        self.root.resizable(False, False)

        self.root.configure(bg="#F8FAFC")
        self.auto_restart_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_status()

        # 根据内容真实高度精确自适应收紧，消除多余空白并居中
        self.root.update_idletasks()
        w = 530
        h = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ── 底部操作栏与状态条 ──────────────────────────────────────────
        status_bar = tk.Frame(self.root, bg="#F1F5F9", height=24)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_lbl = tk.Label(
            status_bar,
            text="运行环境：管理员权限已就绪",
            font=("Microsoft YaHei UI", 8),
            bg="#F1F5F9",
            fg="#475569",
            anchor="w",
            padx=12,
            pady=3
        )
        self.status_lbl.pack(side=tk.LEFT)

        author_lbl = tk.Label(
            status_bar,
            text="小宝科技站 xbkjz.cn",
            font=("Microsoft YaHei UI", 8),
            bg="#F1F5F9",
            fg="#64748B",
            cursor="hand2",
            padx=12
        )
        author_lbl.pack(side=tk.RIGHT)
        author_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))

        footer_panel = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=4)
        footer_panel.pack(fill=tk.X, side=tk.BOTTOM)

        self.chk = tk.Checkbutton(
            footer_panel,
            text="修改策略后自动重启资源管理器",
            variable=self.auto_restart_var,
            font=("Microsoft YaHei UI", 9),
            bg="#F8FAFC",
            activebackground="#F8FAFC",
            fg="#334155"
        )
        self.chk.pack(side=tk.LEFT)

        btn_kill_chrome = tk.Button(
            footer_panel,
            text="重启 Chrome",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_chrome
        )
        btn_kill_chrome.pack(side=tk.RIGHT, padx=(4, 0))

        btn_kill_edge = tk.Button(
            footer_panel,
            text="重启 Edge",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_edge
        )
        btn_kill_edge.pack(side=tk.RIGHT, padx=(4, 0))

        btn_restart_exp = tk.Button(
            footer_panel,
            text="重启资源管理器",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.manual_restart_explorer
        )
        btn_restart_exp.pack(side=tk.RIGHT)

        # ── 顶部标题区域 ──────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=8)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="机房教学策略配置工具",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#F8FAFC",
            fg="#0F172A"
        ).pack(anchor="w")

        # ── 功能卡片容器 ──────────────────────────────────────────────
        main_content = tk.Frame(self.root, bg="#F8FAFC", padx=16)
        main_content.pack(fill=tk.X, pady=(0, 4))

        # 1 & 2. 浏览器访问管控 (Edge 与 Chrome 统一结构)
        self.browser_widgets = {}
        for b_key in ("Edge", "Chrome"):
            self._build_browser_card(main_content, b_key)

        # 3. 云端白名单开机自动同步
        card_sync = tk.LabelFrame(
            main_content,
            text=" 云端白名单开机自动同步 (推荐) ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_sync.pack(fill=tk.X, pady=(0, 5))

        row_sync1 = tk.Frame(card_sync, bg="#FFFFFF")
        row_sync1.pack(fill=tk.X, pady=2)
        self.sync_lbl = tk.Label(row_sync1, text="开机静默同步任务：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.sync_lbl.pack(side=tk.LEFT)

        self.sync_now_btn = tk.Button(
            row_sync1, text="立即从云端拉取", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=12, cursor="hand2",
            command=self.manual_sync_now
        )
        self.sync_now_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self.sync_btn = tk.Button(
            row_sync1, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=12, cursor="hand2",
            command=self.toggle_cloud_sync
        )
        self.sync_btn.pack(side=tk.RIGHT)

        row_sync2 = tk.Frame(card_sync, bg="#FFFFFF")
        row_sync2.pack(fill=tk.X, pady=(2, 1))
        tk.Label(
            row_sync2,
            text="同步源：https://xbkjz.cn/edu/whitelist.txt (开机免 UAC 静默更新，学生机无需留 exe)",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#64748B"
        ).pack(side=tk.LEFT)

        # 3. 桌面与系统规范
        card_desk = tk.LabelFrame(
            main_content,
            text=" 桌面与系统规范 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_desk.pack(fill=tk.X, pady=(0, 5))

        # 3.1 壁纸与锁屏
        row_wp = tk.Frame(card_desk, bg="#FFFFFF")
        row_wp.pack(fill=tk.X, pady=2)
        self.wp_lbl = tk.Label(row_wp, text="机构壁纸与锁屏：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.wp_lbl.pack(side=tk.LEFT)
        self.wp_btn = tk.Button(
            row_wp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_wallpaper
        )
        self.wp_btn.pack(side=tk.RIGHT)

        # 3.2 文件扩展名
        row_ext = tk.Frame(card_desk, bg="#FFFFFF")
        row_ext.pack(fill=tk.X, pady=2)
        self.ext_lbl = tk.Label(row_ext, text="文件扩展名 (后缀名)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.ext_lbl.pack(side=tk.LEFT)
        self.ext_btn = tk.Button(
            row_ext, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_file_ext
        )
        self.ext_btn.pack(side=tk.RIGHT)

        # 3.3 聚焦图标
        row_sp = tk.Frame(card_desk, bg="#FFFFFF")
        row_sp.pack(fill=tk.X, pady=2)
        self.sp_lbl = tk.Label(row_sp, text='桌面"了解此图片"图标：读取中', font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.sp_lbl.pack(side=tk.LEFT)
        self.sp_btn = tk.Button(
            row_sp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_spotlight
        )
        self.sp_btn.pack(side=tk.RIGHT)

        # 3.4 Microsoft Store (应用商店)
        row_store = tk.Frame(card_desk, bg="#FFFFFF")
        row_store.pack(fill=tk.X, pady=2)
        self.store_lbl = tk.Label(row_store, text="Microsoft Store (应用商店)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.store_lbl.pack(side=tk.LEFT)
        self.store_btn = tk.Button(
            row_store, text="一键卸载", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.action_uninstall_store
        )
        self.store_btn.pack(side=tk.RIGHT)

        # 4. 编程环境优化
        card_dev = tk.LabelFrame(
            main_content,
            text=" 编程环境优化 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card_dev.pack(fill=tk.X, pady=(0, 4))

        # 4.1 pip 镜像多源配置
        row_pip = tk.Frame(card_dev, bg="#FFFFFF")
        row_pip.pack(fill=tk.X, pady=2)
        self.pip_lbl = tk.Label(row_pip, text="Python pip 镜像源：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.pip_lbl.pack(side=tk.LEFT)

        btn_pip_default = tk.Button(
            row_pip, text="恢复默认", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("default")
        )
        btn_pip_default.pack(side=tk.RIGHT, padx=(4, 0))

        btn_pip_ali = tk.Button(
            row_pip, text="阿里源", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("aliyun")
        )
        btn_pip_ali.pack(side=tk.RIGHT, padx=(4, 0))

        btn_pip_tuna = tk.Button(
            row_pip, text="清华源", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=8, cursor="hand2",
            command=lambda: self.apply_pip_source("tuna")
        )
        btn_pip_tuna.pack(side=tk.RIGHT)

        # 4.2 Windows 长路径
        row_lp = tk.Frame(card_dev, bg="#FFFFFF")
        row_lp.pack(fill=tk.X, pady=2)
        self.lp_lbl = tk.Label(row_lp, text="Windows 长路径支持 (LongPaths)：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        self.lp_lbl.pack(side=tk.LEFT)
        self.lp_btn = tk.Button(
            row_lp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_longpaths
        )
        self.lp_btn.pack(side=tk.RIGHT)

    def _build_browser_card(self, parent, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        card = tk.LabelFrame(
            parent,
            text=f" {name} 浏览器访问策略 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=5,
            relief=tk.SOLID,
            bd=1
        )
        card.pack(fill=tk.X, pady=(0, 5))

        widgets = {}

        # 1. 白名单
        row_wl = tk.Frame(card, bg="#FFFFFF")
        row_wl.pack(fill=tk.X, pady=2)
        widgets["wl_lbl"] = tk.Label(row_wl, text="网址白名单锁定：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["wl_lbl"].pack(side=tk.LEFT)

        widgets["wl_cfg_btn"] = tk.Button(
            row_wl, text="管理白名单", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.open_whitelist_manager
        )
        widgets["wl_cfg_btn"].pack(side=tk.RIGHT, padx=(4, 0))

        widgets["wl_btn"] = tk.Button(
            row_wl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_whitelist(b_key)
        )
        widgets["wl_btn"].pack(side=tk.RIGHT)

        # 2. 桌面直达启动图标
        row_pt = tk.Frame(card, bg="#FFFFFF")
        row_pt.pack(fill=tk.X, pady=2)
        widgets["portal_lbl"] = tk.Label(row_pt, text="桌面直达启动图标：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["portal_lbl"].pack(side=tk.LEFT)

        widgets["test_btn"] = tk.Button(
            row_pt, text="测试打开", font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._test_open_browser(b_key)
        )
        widgets["test_btn"].pack(side=tk.RIGHT, padx=(4, 0))

        widgets["portal_btn"] = tk.Button(
            row_pt, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_startup(b_key)
        )
        widgets["portal_btn"].pack(side=tk.RIGHT)

        # 3. 离线游戏
        row_gm = tk.Frame(card, bg="#FFFFFF")
        row_gm.pack(fill=tk.X, pady=2)
        widgets["game_lbl"] = tk.Label(row_gm, text=f"{cfg['game_label']}：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["game_lbl"].pack(side=tk.LEFT)
        widgets["game_btn"] = tk.Button(
            row_gm, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_game(b_key)
        )
        widgets["game_btn"].pack(side=tk.RIGHT)

        # 4. 下载限制
        row_dl = tk.Frame(card, bg="#FFFFFF")
        row_dl.pack(fill=tk.X, pady=2)
        widgets["dl_lbl"] = tk.Label(row_dl, text="文件下载限制：读取中", font=("Microsoft YaHei UI", 9), bg="#FFFFFF", fg="#334155")
        widgets["dl_lbl"].pack(side=tk.LEFT)
        widgets["dl_btn"] = tk.Button(
            row_dl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_downloads(b_key)
        )
        widgets["dl_btn"].pack(side=tk.RIGHT)

        self.browser_widgets[b_key] = widgets

    def _refresh_browser_status(self, b_key):
        cfg = BROWSERS[b_key]
        w = self.browser_widgets[b_key]

        wl_locked = cfg["get_wl"]()
        if wl_locked:
            w["wl_lbl"].configure(text="网址白名单锁定：已开启限制 (仅允许白名单网站)")
            w["wl_btn"].configure(text="解除限制", bg="#FFFFFF", fg="#0F172A")
        else:
            w["wl_lbl"].configure(text="网址白名单锁定：未锁定 (允许自由访问全网)")
            w["wl_btn"].configure(text="开启限制", bg="#0F172A", fg="#FFFFFF")

        pt_on = cfg["get_startup"]()
        if pt_on:
            w["portal_lbl"].configure(text="桌面直达启动图标：已配置直达 (双击直达目标主页)")
            w["portal_btn"].configure(text="恢复默认", bg="#FFFFFF", fg="#0F172A")
        else:
            w["portal_lbl"].configure(text="桌面直达启动图标：默认启动图标 (未绑定直达参数)")
            w["portal_btn"].configure(text="配置直达", bg="#0F172A", fg="#FFFFFF")

        gm_off = cfg["get_game"]()
        if gm_off:
            w["game_lbl"].configure(text=f"{cfg['game_label']}：已禁用")
            w["game_btn"].configure(text="允许游戏")
        else:
            w["game_lbl"].configure(text=f"{cfg['game_label']}：未禁用")
            w["game_btn"].configure(text="禁用游戏")

        dl_off = cfg["get_dl"]()
        if dl_off:
            w["dl_lbl"].configure(text="文件下载限制：已禁止所有文件下载")
            w["dl_btn"].configure(text="允许下载")
        else:
            w["dl_lbl"].configure(text="文件下载限制：允许下载")
            w["dl_btn"].configure(text="禁止下载")

    # ── 状态读取与刷新 ────────────────────────────────────────────────
    def refresh_status(self):
        # 1 & 2. 浏览器策略刷新 (Edge 与 Chrome 统一处理)
        for b_key in ("Edge", "Chrome"):
            self._refresh_browser_status(b_key)

        # 3. 云端白名单自动同步
        sync_installed = get_cloud_sync_installed()
        if sync_installed:
            self.sync_lbl.configure(text="开机静默同步任务：已就绪 (开机自动拉取更新)")
            self.sync_btn.configure(text="移除开机任务", bg="#FFFFFF", fg="#0F172A")
        else:
            self.sync_lbl.configure(text="开机静默同步任务：未部署 (需手动插 U 盘更新)")
            self.sync_btn.configure(text="部署开机同步", bg="#0F172A", fg="#FFFFFF")

        # 3. 桌面与系统规范
        wp_locked = get_wallpaper_locked()
        if wp_locked:
            self.wp_lbl.configure(text="机构壁纸与锁屏：已统一并锁定修改")
            self.wp_btn.configure(text="允许修改")
        else:
            self.wp_lbl.configure(text="机构壁纸与锁屏：未锁定 (允许自由修改)")
            self.wp_btn.configure(text="部署并锁定")

        ext_visible = get_file_ext_visible()
        if ext_visible:
            self.ext_lbl.configure(text="文件扩展名 (后缀名)：始终显示 (格式清晰可见)")
            self.ext_btn.configure(text="隐藏后缀")
        else:
            self.ext_lbl.configure(text="文件扩展名 (后缀名)：系统默认隐藏 (易引起混淆)")
            self.ext_btn.configure(text="显示后缀")

        sp_hidden = get_spotlight_hidden()
        if sp_hidden:
            self.sp_lbl.configure(text='桌面"了解此图片"图标：已隐藏')
            self.sp_btn.configure(text="恢复显示")
        else:
            self.sp_lbl.configure(text='桌面"了解此图片"图标：正常显示')
            self.sp_btn.configure(text="隐藏图标")

        store_installed = get_ms_store_status()
        if store_installed:
            self.store_lbl.configure(text="Microsoft Store (应用商店)：已安装 (允许下载软件)")
            self.store_btn.configure(text="一键卸载", bg="#0F172A", fg="#FFFFFF")
        else:
            self.store_lbl.configure(text="Microsoft Store (应用商店)：已卸载 (禁止学生下载软件)")
            self.store_btn.configure(text="重新卸载", bg="#FFFFFF", fg="#64748B")

        # 4. 编程环境优化
        m_type, _ = get_pip_mirror_type()
        if m_type == "tuna":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 清华源")
        elif m_type == "aliyun":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 阿里源")
        elif m_type == "other":
            self.pip_lbl.configure(text="Python pip 镜像源：当前使用 自定义源")
        else:
            self.pip_lbl.configure(text="Python pip 镜像源：官方默认源")

        lp_on = get_longpaths_status()
        if lp_on:
            self.lp_lbl.configure(text="Windows 长路径支持：已启用 (解除 260 字符限制)")
            self.lp_btn.configure(text="恢复默认")
        else:
            self.lp_lbl.configure(text="Windows 长路径支持：未启用 (限制 260 字符)")
            self.lp_btn.configure(text="启用长路径")

    # ── 交互事件处理 ──────────────────────────────────────────────────
    def trigger_explorer_update(self, action_name):
        if self.auto_restart_var.get():
            self.status_lbl.configure(text="正在重启资源管理器...")
            self.root.update()
            if restart_explorer():
                self.status_lbl.configure(text="设置已保存，资源管理器已成功重启。")
            else:
                self.status_lbl.configure(text="设置已保存，资源管理器重启失败。")
        else:
            messagebox.showinfo("操作成功", "设置已保存。\n\n请点击右下角“重启资源管理器”使更改生效。")
            self.status_lbl.configure(text="设置已保存，等待重启资源管理器...")

    def open_whitelist_manager(self):
        """打开通用白名单管理窗口"""
        win = tk.Toplevel(self.root)
        设置窗口图标(win)
        win.title("管理浏览器允许访问的网址白名单")
        win.geometry("480x420")
        win.resizable(False, False)
        win.configure(bg="#F8FAFC")
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win,
            text="浏览器允许访问的网址白名单清单",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#F8FAFC",
            fg="#0F172A"
        ).pack(pady=(12, 2))

        tk.Label(
            win,
            text="每行一条规则，支持通配符（Edge 与 Chrome 同步生效）\n保存后若白名单处于开启状态将立即同步到系统注册表。",
            font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC",
            fg="#64748B"
        ).pack(pady=(0, 8))

        text_area = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=("Consolas", 9), height=14,
            relief=tk.SOLID, bd=1
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        current_rules = load_whitelist()
        text_area.insert(tk.END, "\n".join(current_rules))

        btn_box = tk.Frame(win, bg="#F8FAFC")
        btn_box.pack(fill=tk.X, padx=16, pady=10)

        def save_and_close():
            raw = text_area.get("1.0", tk.END).strip().splitlines()
            cleaned = [line.strip() for line in raw if line.strip() and not line.strip().startswith("#")]
            if save_whitelist(cleaned):
                active_browsers = [cfg for cfg in BROWSERS.values() if cfg["get_wl"]()]
                for b_cfg in active_browsers:
                    b_cfg["set_wl"](True, cleaned)
                win.destroy()
                self.refresh_status()
                if active_browsers:
                    if messagebox.askyesno("保存成功", f"白名单规则已更新并同步写入注册表（共 {len(cleaned)} 条）。\n\n新策略需要重启浏览器生效，是否立即关闭并重启浏览器？"):
                        for b_cfg in active_browsers:
                            kill_browser_process(b_cfg["proc"])
                            subprocess.Popen(["cmd", "/c", "start", b_cfg["cmd"]], shell=True)
                else:
                    messagebox.showinfo("成功", f"白名单清单已保存（共 {len(cleaned)} 条）。\n当前白名单处于未开启状态，点击主界面的【开启限制】即可应用。")
            else:
                messagebox.showerror("错误", "保存白名单文件失败。")

        def reset_defaults():
            if messagebox.askyesno("恢复默认", "是否清空当前内容并恢复推荐的默认白名单？"):
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, "\n".join(DEFAULT_ALLOWLIST))

        tk.Button(
            btn_box, text="保存并生效", font=("Microsoft YaHei UI", 8, "bold"),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, padx=10, pady=2,
            command=save_and_close
        ).pack(side=tk.RIGHT, padx=(6, 0))

        tk.Button(
            btn_box, text="恢复默认清单", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, padx=8, pady=2,
            command=reset_defaults
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_box, text="取消", font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF", fg="#64748B", relief=tk.SOLID, bd=1, padx=8, pady=2,
            command=win.destroy
        ).pack(side=tk.LEFT)

    # ── 浏览器通用动作 ──
    def _toggle_browser_whitelist(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_wl"]()
        nxt = not curr
        if nxt and not messagebox.askyesno("确认", f"开启后 {name} 将阻断所有非白名单网站，是否继续？"):
            return
        if cfg["set_wl"](nxt):
            self.refresh_status()
            tip = f"{name} 白名单限制已开启。" if nxt else f"{name} 白名单限制已解除。"
            self.status_lbl.configure(text=tip)
            if messagebox.askyesno("提示", f"{tip}\n\n是否立即重启 {name} 浏览器生效？"):
                kill_browser_process(cfg["proc"])
                subprocess.Popen(["cmd", "/c", "start", cfg["cmd"]], shell=True)
        else:
            messagebox.showerror("错误", f"修改 {name} 白名单策略失败。")

    def _toggle_browser_startup(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_startup"]()
        nxt = not curr
        if cfg["set_startup"](nxt):
            self.refresh_status()
            tip = f"{name} 桌面图标已配置直达：{DEFAULT_STARTUP_URL}" if nxt else f"{name} 桌面图标已恢复为默认启动。"
            self.status_lbl.configure(text=tip)
            if nxt:
                if messagebox.askyesno("配置成功", f"{tip}\n\n是否立即通过直达参数启动 {name} 验证效果？"):
                    self._test_open_browser(b_key)
            else:
                messagebox.showinfo("提示", tip)
        else:
            messagebox.showerror("错误", f"修改 {name} 桌面快捷方式失败，未找到 {name} 安装路径。")

    def _test_open_browser(self, b_key):
        cmd = BROWSERS[b_key]["cmd"]
        try:
            subprocess.Popen(["cmd", "/c", "start", cmd, DEFAULT_STARTUP_URL], shell=True)
        except Exception:
            webbrowser.open(DEFAULT_STARTUP_URL)

    def _toggle_browser_game(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_game"]()
        nxt = not curr
        if cfg["set_game"](nxt):
            self.refresh_status()
            messagebox.showinfo("提示", f"{name} {cfg['game_short_name']}策略已保存，重启浏览器后生效。")
        else:
            messagebox.showerror("错误", f"修改 {name} 游戏策略失败。")

    def _toggle_browser_downloads(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        curr = cfg["get_dl"]()
        nxt = not curr
        if cfg["set_dl"](nxt):
            self.refresh_status()
            act = f"已禁止 {name} 下载文件。" if nxt else f"已允许 {name} 下载文件。"
            if messagebox.askyesno("提示", f"{act}\n\n是否立即关闭 {name} 浏览器？"):
                kill_browser_process(cfg["proc"])
        else:
            messagebox.showerror("错误", f"修改 {name} 下载策略失败。")

    def _manual_restart_browser(self, b_key):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        kill_browser_process(cfg["proc"])
        self.status_lbl.configure(text=f"{name} 浏览器已关闭。")
        messagebox.showinfo("提示", f"{name} 浏览器已关闭，请重新启动以应用新策略。")

    # 快捷委托方法
    def toggle_edge_whitelist(self): self._toggle_browser_whitelist("Edge")
    def toggle_edge_startup(self): self._toggle_browser_startup("Edge")
    def test_open_edge(self): self._test_open_browser("Edge")
    def toggle_edge_game(self): self._toggle_browser_game("Edge")
    def toggle_edge_downloads(self): self._toggle_browser_downloads("Edge")
    def manual_restart_edge(self): self._manual_restart_browser("Edge")

    def toggle_chrome_whitelist(self): self._toggle_browser_whitelist("Chrome")
    def toggle_chrome_startup(self): self._toggle_browser_startup("Chrome")
    def test_open_chrome(self): self._test_open_browser("Chrome")
    def toggle_chrome_game(self): self._toggle_browser_game("Chrome")
    def toggle_chrome_downloads(self): self._toggle_browser_downloads("Chrome")
    def manual_restart_chrome(self): self._manual_restart_browser("Chrome")

    # ── 云端同步动作 ──
    def toggle_cloud_sync(self):
        curr = get_cloud_sync_installed()
        if not curr:
            self.status_lbl.configure(text="正在向系统注册开机静默同步计划任务...")
            self.root.update()
            ok, msg = install_cloud_sync_task()
            self.refresh_status()
            if ok:
                self.status_lbl.configure(text="开机静默云端同步任务已部署完成。")
                messagebox.showinfo("部署成功", msg)
            else:
                self.status_lbl.configure(text="开机同步任务部署失败。")
                messagebox.showerror("部署失败", msg)
        else:
            if messagebox.askyesno("移除确认", "是否移除本机的开机云端同步任务？\n\n移除后，学生机将不再自动从云端更新白名单。"):
                self.status_lbl.configure(text="正在移除开机同步任务...")
                self.root.update()
                ok, msg = uninstall_cloud_sync_task()
                self.refresh_status()
                if ok:
                    self.status_lbl.configure(text="开机同步任务已移除。")
                    messagebox.showinfo("提示", msg)
                else:
                    self.status_lbl.configure(text="移除开机同步任务失败。")
                    messagebox.showerror("错误", msg)

    def manual_sync_now(self):
        self.status_lbl.configure(text="正在从云端拉取白名单并注入系统注册表...")
        self.root.update()
        ok, msg = run_cloud_sync_now()
        self.refresh_status()
        if ok:
            active_browsers = [cfg for cfg in BROWSERS.values() if cfg["get_wl"]()]
            self.status_lbl.configure(text="云端白名单同步已完成。")
            if messagebox.askyesno("同步完成", "云端白名单已成功拉取并写入系统注册表！\n\n是否立即重启浏览器以使新策略生效？"):
                for b_cfg in active_browsers:
                    kill_browser_process(b_cfg["proc"])
                    subprocess.Popen(["cmd", "/c", "start", b_cfg["cmd"]], shell=True)
        else:
            self.status_lbl.configure(text="云端同步执行失败。")
            messagebox.showerror("同步失败", msg)

    # ── 桌面与系统动作 ──
    def toggle_wallpaper(self):
        curr = get_wallpaper_locked()
        nxt = not curr
        if nxt:
            self.status_lbl.configure(text="正在部署机构壁纸和锁屏...")
            self.root.update()
            ok, msg = apply_wallpaper_and_lockscreen()
            if not ok:
                messagebox.showerror("壁纸设置失败", msg)
                return

        if set_wallpaper_locked(nxt):
            self.refresh_status()
            self.trigger_explorer_update("壁纸限制")
        else:
            messagebox.showerror("错误", "修改壁纸锁定状态失败。")

    def toggle_file_ext(self):
        curr = get_file_ext_visible()
        nxt = not curr
        if set_file_ext_visible(nxt):
            self.refresh_status()
            self.trigger_explorer_update("文件扩展名设置")
        else:
            messagebox.showerror("错误", "修改文件扩展名设置失败。")

    def toggle_spotlight(self):
        curr = get_spotlight_hidden()
        nxt = not curr
        if set_spotlight_hidden(nxt):
            self.refresh_status()
            self.trigger_explorer_update("了解此图片")
        else:
            messagebox.showerror("错误", '修改"了解此图片"隐藏状态失败。')

    def action_uninstall_store(self):
        curr_installed = get_ms_store_status()
        if not curr_installed:
            if not messagebox.askyesno(
                "卸载确认",
                "检测到当前系统可能已卸载 Microsoft Store。\n\n是否仍然强制执行一遍深度卸载清理（清除所有用户残留及系统预装包）？"
            ):
                return
        else:
            if not messagebox.askyesno(
                "卸载确认",
                "确定要在本机彻底卸载 Microsoft Store (Windows 应用商店) 吗？\n\n卸载后将移除所有用户的应用商店组件并清理预装包，学生将无法通过应用商店下载安装游戏或第三方软件。"
            ):
                return

        self.status_lbl.configure(text="正在彻底卸载 Microsoft Store，请稍候...")
        self.root.update()
        ok, msg = uninstall_ms_store()
        self.refresh_status()
        if ok:
            self.status_lbl.configure(text="Microsoft Store 已成功卸载。")
            messagebox.showinfo("卸载完成", "Microsoft Store (Windows 应用商店) 已成功卸载！\n\n已清除当前用户、所有账户及系统预装包。")
        else:
            self.status_lbl.configure(text="Microsoft Store 卸载失败。")
            messagebox.showerror("错误", msg)

    def apply_pip_source(self, source_type):
        ok, msg = set_pip_mirror_source(source_type)
        if ok:
            self.refresh_status()
            self.status_lbl.configure(text=msg)
            messagebox.showinfo("提示", msg)
        else:
            messagebox.showerror("错误", msg)

    def toggle_longpaths(self):
        curr = get_longpaths_status()
        nxt = not curr
        if set_longpaths_enabled(nxt):
            self.refresh_status()
            msg = "Windows 长路径已解除 260 字符限制。" if nxt else "Windows 长路径已恢复默认限制。"
            self.status_lbl.configure(text=msg)
            messagebox.showinfo("提示", msg)
        else:
            messagebox.showerror("错误", "修改长路径限制失败。")

    def manual_restart_explorer(self):
        self.status_lbl.configure(text="正在重启资源管理器...")
        self.root.update()
        if restart_explorer():
            self.status_lbl.configure(text="资源管理器重启成功。")
            messagebox.showinfo("提示", "资源管理器已成功重启，更改已生效。")
        else:
            self.status_lbl.configure(text="资源管理器重启失败。")
            messagebox.showerror("错误", "无法重启资源管理器。")
