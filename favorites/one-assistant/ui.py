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
from tkinter import messagebox

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from config import DEFAULT_STARTUP_URL, 设置窗口图标
from reg_utils import (
    restart_explorer,
    kill_browser_process
)
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
    uninstall_cloud_sync_task
)

def launch_browser(cmd, *args):
    """用 Windows 的 start 命令启动浏览器（start 能通过 App Paths 找到 msedge / chrome）。

    - 不用 shell=True：列表参数再加 shell=True 会变成 cmd /c cmd /c start ...，套了两层 shell。
    - start 后面先给一个空标题 ""，否则 start 会把第一个带引号的参数当成窗口标题。
    - 每个参数都加引号，网址里的 & 之类字符不会被 cmd 当成命令分隔符。
    """
    quoted = " ".join('"%s"' % str(a).replace('"', '') for a in (cmd, *args))
    return subprocess.Popen(
        'cmd /c start "" ' + quoted,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


class CodingLabAssistantGUI:
    def __init__(self, root):
        self.root = root
        设置窗口图标(self.root)
        self.root.title("机房教学策略配置工具")
        self.root.resizable(True, True)
        self.root.minsize(680, 380)

        self.root.configure(bg="#F8FAFC")
        self.auto_restart_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_status()

        # 宽屏双栏自适应：优先一屏完整展示，小屏幕/高缩放下自动限制高度并启用滚动
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w = min(940, max(680, screen_w - 40))
        req_h = (
            self._header.winfo_reqheight()
            + self._main_content.winfo_reqheight()
            + self._footer_panel.winfo_reqheight()
            + self._status_bar.winfo_reqheight()
            + 4
        )
        h = min(req_h, max(380, screen_h - 80))
        x = max(0, (screen_w - w) // 2)
        y = max(0, (screen_h - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _create_card(self, parent, title, pady_bottom=6, expand=False):
        card = tk.LabelFrame(
            parent,
            text=f" {title} ",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=12,
            pady=6,
            relief=tk.SOLID,
            bd=1
        )
        card.pack(fill=tk.BOTH if expand else tk.X, expand=expand, pady=(0, pady_bottom))
        return card

    def _create_status_row(self, parent, title_text):
        """创建统一格式的状态行：左侧 [状态徽章 + 项目名称]，右侧放置操作按钮"""
        row = tk.Frame(parent, bg="#FFFFFF")
        row.pack(fill=tk.X, pady=3)

        badge = tk.Label(
            row,
            text="读取中",
            font=("Microsoft YaHei UI", 8, "bold"),
            bg="#F1F5F9",
            fg="#64748B",
            padx=6,
            pady=1,
            width=7
        )
        badge.pack(side=tk.LEFT, padx=(0, 6))

        lbl = tk.Label(
            row,
            text=title_text,
            font=("Microsoft YaHei UI", 9),
            bg="#FFFFFF",
            fg="#1E293B",
            anchor="w"
        )
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return row, badge, lbl

    def _set_toggle_row(self, badge, btn, active, on_badge, off_badge, on_btn, off_btn):
        """统一直观状态：已开启=绿色徽章+浅色关闭按钮；未开启=浅灰徽章+深色开启按钮"""
        if active:
            badge.configure(text=on_badge, bg="#DCFCE7", fg="#15803D")
            btn.configure(text=on_btn, bg="#F8FAFC", fg="#334155")
        else:
            badge.configure(text=off_badge, bg="#F1F5F9", fg="#64748B")
            btn.configure(text=off_btn, bg="#0F172A", fg="#FFFFFF")

    def _build_ui(self):
        # ── 底部操作栏与状态条 ──────────────────────────────────────────
        self._status_bar = status_bar = tk.Frame(self.root, bg="#F1F5F9", height=24)
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

        self._footer_panel = footer_panel = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=6)
        footer_panel.pack(fill=tk.X, side=tk.BOTTOM)

        self.chk = tk.Checkbutton(
            footer_panel,
            text="修改桌面/系统策略后自动重启资源管理器",
            variable=self.auto_restart_var,
            font=("Microsoft YaHei UI", 9),
            bg="#F8FAFC",
            activebackground="#F8FAFC",
            fg="#334155"
        )
        self.chk.pack(side=tk.LEFT)

        # ── 顶部标题区域 ──────────────────────────────────────────────
        self._header = header = tk.Frame(self.root, bg="#F8FAFC", padx=16, pady=8)
        header.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            header,
            text="机房教学策略配置工具",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#F8FAFC",
            fg="#0F172A"
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="核心：白名单开机静默同步 + 浏览器管控",
            font=("Microsoft YaHei UI", 8),
            bg="#F8FAFC",
            fg="#64748B"
        ).pack(side=tk.RIGHT, pady=(4, 0))

        # ── 中间可滚动双栏容器 ────────────────────────────────────────
        scroll_wrap = tk.Frame(self.root, bg="#F8FAFC")
        scroll_wrap.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scroll_wrap, bg="#F8FAFC", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(scroll_wrap, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._main_content = main_content = tk.Frame(canvas, bg="#F8FAFC", padx=16, pady=2)
        win_id = canvas.create_window((0, 0), window=main_content, anchor="nw")

        def _sync_scroll(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            need_scroll = main_content.winfo_reqheight() > canvas.winfo_height()
            if need_scroll and not scrollbar.winfo_ismapped():
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            elif not need_scroll and scrollbar.winfo_ismapped():
                scrollbar.pack_forget()

        main_content.bind("<Configure>", _sync_scroll)
        canvas.bind("<Configure>", lambda e: (canvas.itemconfigure(win_id, width=e.width), _sync_scroll()))
        self.root.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            if main_content.winfo_reqheight() > canvas.winfo_height() else None
        )

        main_content.columnconfigure(0, weight=1, uniform="col")
        main_content.columnconfigure(1, weight=1, uniform="col")

        left_col = tk.Frame(main_content, bg="#F8FAFC")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        right_col = tk.Frame(main_content, bg="#F8FAFC")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # 左栏：Edge 与 Chrome 浏览器访问管控（均分高度，与右栏底部对齐）
        self.browser_widgets = {}
        self._build_browser_card(left_col, "Edge", pady_bottom=8, expand=True)
        self._build_browser_card(left_col, "Chrome", pady_bottom=0, expand=True)

        # 右栏 1：开机教学策略与晚间纪律（核心功能置顶）
        card_sync = self._create_card(right_col, "开机教学策略与晚间纪律 (核心)", pady_bottom=8)

        row_sync1, self.sync_badge, _ = self._create_status_row(card_sync, "开机静默同步")
        self.sync_btn = tk.Button(
            row_sync1, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_cloud_sync
        )
        self.sync_btn.pack(side=tk.RIGHT)

        row_sync2 = tk.Frame(card_sync, bg="#FFFFFF")
        row_sync2.pack(fill=tk.X, pady=(2, 1))
        tk.Label(
            row_sync2,
            text="开机免 UAC 自动拉取云端 whitelist.txt | 每日 20:15 自动关机",
            font=("Microsoft YaHei UI", 8),
            bg="#FFFFFF",
            fg="#64748B"
        ).pack(side=tk.LEFT)

        # 右栏 2：桌面与系统规范
        card_desk = self._create_card(right_col, "桌面与系统规范", pady_bottom=8, expand=True)

        row_wp, self.wp_badge, _ = self._create_status_row(card_desk, "机构壁纸与锁屏")
        self.wp_btn = tk.Button(
            row_wp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_wallpaper
        )
        self.wp_btn.pack(side=tk.RIGHT)

        row_ext, self.ext_badge, _ = self._create_status_row(card_desk, "显示文件扩展名")
        self.ext_btn = tk.Button(
            row_ext, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_file_ext
        )
        self.ext_btn.pack(side=tk.RIGHT)

        row_sp, self.sp_badge, _ = self._create_status_row(card_desk, '隐藏"了解此图片"')
        self.sp_btn = tk.Button(
            row_sp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_spotlight
        )
        self.sp_btn.pack(side=tk.RIGHT)

        row_store, self.store_badge, _ = self._create_status_row(card_desk, "Microsoft Store")
        self.store_btn = tk.Button(
            row_store, text="一键卸载", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.action_uninstall_store
        )
        self.store_btn.pack(side=tk.RIGHT)

        # 右栏 3：编程环境优化
        card_dev = self._create_card(right_col, "编程环境优化", pady_bottom=0, expand=True)

        row_pip, self.pip_badge, _ = self._create_status_row(card_dev, "pip 镜像源")
        self.pip_btns = {}
        for label, src_type in (("默认", "default"), ("阿里", "aliyun"), ("清华", "tuna")):
            btn = tk.Button(
                row_pip, text=label, font=("Microsoft YaHei UI", 8),
                bg="#FFFFFF", fg="#0F172A", relief=tk.SOLID, bd=1, width=5, cursor="hand2",
                command=lambda s=src_type: self.apply_pip_source(s)
            )
            btn.pack(side=tk.RIGHT, padx=(3, 0))
            self.pip_btns[src_type] = btn

        row_lp, self.lp_badge, _ = self._create_status_row(card_dev, "Windows 长路径")
        self.lp_btn = tk.Button(
            row_lp, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=self.toggle_longpaths
        )
        self.lp_btn.pack(side=tk.RIGHT)

    def _build_browser_card(self, parent, b_key, pady_bottom=6, expand=False):
        cfg = BROWSERS[b_key]
        name = cfg["name"]
        card = self._create_card(parent, f"{name} 浏览器访问策略", pady_bottom=pady_bottom, expand=expand)

        widgets = {}

        # 1. 白名单（直接由 whitelist.txt / 云端同步控制，不再提供弹窗管理）
        row_wl, widgets["wl_badge"], _ = self._create_status_row(card, "网址白名单锁定")
        widgets["wl_btn"] = tk.Button(
            row_wl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_whitelist(b_key)
        )
        widgets["wl_btn"].pack(side=tk.RIGHT)

        # 2. 桌面直达启动图标
        row_pt, widgets["portal_badge"], _ = self._create_status_row(card, "桌面直达主页")
        widgets["portal_btn"] = tk.Button(
            row_pt, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_startup(b_key)
        )
        widgets["portal_btn"].pack(side=tk.RIGHT)

        # 3. 离线游戏
        row_gm, widgets["game_badge"], _ = self._create_status_row(card, cfg["game_label"])
        widgets["game_btn"] = tk.Button(
            row_gm, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_game(b_key)
        )
        widgets["game_btn"].pack(side=tk.RIGHT)

        # 4. 下载限制
        row_dl, widgets["dl_badge"], _ = self._create_status_row(card, "禁止文件下载")
        widgets["dl_btn"] = tk.Button(
            row_dl, text="...", font=("Microsoft YaHei UI", 8),
            bg="#0F172A", fg="#FFFFFF", relief=tk.SOLID, bd=1, width=10, cursor="hand2",
            command=lambda: self._toggle_browser_downloads(b_key)
        )
        widgets["dl_btn"].pack(side=tk.RIGHT)

        self.browser_widgets[b_key] = widgets

    def _refresh_browser_status(self, b_key):
        cfg = BROWSERS[b_key]
        w = self.browser_widgets[b_key]

        self._set_toggle_row(
            w["wl_badge"], w["wl_btn"], cfg["get_wl"](),
            "已锁定", "未锁定", "解除限制", "开启限制"
        )
        self._set_toggle_row(
            w["portal_badge"], w["portal_btn"], cfg["get_startup"](),
            "已开启", "未开启", "恢复默认", "开启直达"
        )
        self._set_toggle_row(
            w["game_badge"], w["game_btn"], cfg["get_game"](),
            "已禁用", "未禁用", "允许游戏", "禁用游戏"
        )
        self._set_toggle_row(
            w["dl_badge"], w["dl_btn"], cfg["get_dl"](),
            "已禁止", "未禁止", "允许下载", "禁止下载"
        )

    # ── 状态读取与刷新 ────────────────────────────────────────────────
    def refresh_status(self):
        for b_key in ("Edge", "Chrome"):
            self._refresh_browser_status(b_key)

        self._set_toggle_row(
            self.sync_badge, self.sync_btn, get_cloud_sync_installed(),
            "已部署", "未部署", "移除任务", "部署任务"
        )
        self._set_toggle_row(
            self.wp_badge, self.wp_btn, get_wallpaper_locked(),
            "已锁定", "未锁定", "允许修改", "部署锁定"
        )
        self._set_toggle_row(
            self.ext_badge, self.ext_btn, get_file_ext_visible(),
            "已显示", "未显示", "隐藏后缀", "显示后缀"
        )
        self._set_toggle_row(
            self.sp_badge, self.sp_btn, get_spotlight_hidden(),
            "已隐藏", "未隐藏", "恢复显示", "隐藏图标"
        )

        store_installed = get_ms_store_status()
        self._set_toggle_row(
            self.store_badge, self.store_btn, not store_installed,
            "已卸载", "未卸载", "重新清理", "一键卸载"
        )

        m_type, _ = get_pip_mirror_type()
        pip_badges = {
            "tuna": ("清华源", "#DCFCE7", "#15803D"),
            "aliyun": ("阿里源", "#DCFCE7", "#15803D"),
            "other": ("自定义", "#FEF3C7", "#B45309"),
            "default": ("官方源", "#F1F5F9", "#64748B"),
        }
        b_text, b_bg, b_fg = pip_badges.get(m_type, pip_badges["default"])
        self.pip_badge.configure(text=b_text, bg=b_bg, fg=b_fg)
        for src_type, btn in self.pip_btns.items():
            is_cur = (src_type == m_type)
            btn.configure(
                bg="#15803D" if is_cur and src_type != "default" else ("#0F172A" if is_cur else "#FFFFFF"),
                fg="#FFFFFF" if is_cur else "#0F172A"
            )

        self._set_toggle_row(
            self.lp_badge, self.lp_btn, get_longpaths_status(),
            "已启用", "未启用", "恢复默认", "启用长路径"
        )

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
            messagebox.showinfo("操作成功", "设置已保存，重启资源管理器或注销后生效。")
            self.status_lbl.configure(text="设置已保存，等待资源管理器刷新...")

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
                launch_browser(cfg["cmd"])
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
            launch_browser(cmd, DEFAULT_STARTUP_URL)
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
            if messagebox.askyesno("移除确认", "是否移除本机的开机静默教学策略？\n\n移除后，学生机将不再自动同步白名单，且晚间自动关机任务将被清理。"):
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
            self.status_lbl.configure(text="Windows 长路径恢复失败。")
            messagebox.showerror("错误", "修改长路径限制失败。")
