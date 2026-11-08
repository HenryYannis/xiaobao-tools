# -*- coding: utf-8 -*-
"""机房 Hosts 一键初始化工具"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")

DEFAULT_HOSTS = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost
"""


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate() -> None:
    params = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )


def read_hosts() -> str:
    if not HOSTS_PATH.exists():
        return ""
    data = HOSTS_PATH.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "gbk", "mbcs"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def write_hosts(content: str) -> None:
    HOSTS_PATH.write_text(content.rstrip() + "\n", encoding="utf-8")
    try:
        os.chmod(HOSTS_PATH, 0o666)
    except OSError:
        pass


def flush_dns() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True,
            text=True,
            encoding="mbcs",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, out.strip()
    except Exception as exc:
        return False, str(exc)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Hosts 一键初始化")
        self.geometry("720x520")
        self.minsize(640, 440)
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#1f6feb", height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="机房 Hosts 初始化工具",
            bg="#1f6feb",
            fg="white",
            font=("Microsoft YaHei UI", 14, "bold"),
        ).pack(side="left", padx=16)

        tip = tk.Label(
            self,
            text="直接恢复为系统默认 hosts，并刷新 DNS 缓存。",
            bg="#f5f5f5",
            fg="#333",
            font=("Microsoft YaHei UI", 10),
            anchor="w",
        )
        tip.pack(fill="x", padx=16, pady=(12, 6))

        btn_row = tk.Frame(self, bg="#f5f5f5")
        btn_row.pack(fill="x", padx=16, pady=6)

        self.btn_reset = tk.Button(
            btn_row,
            text="一键初始化 Hosts",
            command=self.on_reset,
            bg="#1f6feb",
            fg="white",
            activebackground="#1558c0",
            activeforeground="white",
            font=("Microsoft YaHei UI", 11, "bold"),
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.btn_reset.pack(side="left")

        tk.Button(
            btn_row,
            text="刷新预览",
            command=self.refresh_preview,
            bg="#e8e8e8",
            font=("Microsoft YaHei UI", 10),
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        tk.Label(
            self,
            text=f"当前文件：{HOSTS_PATH}",
            bg="#f5f5f5",
            fg="#666",
            font=("Consolas", 9),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(8, 4))

        self.preview = scrolledtext.ScrolledText(
            self,
            wrap="none",
            font=("Consolas", 10),
            bg="white",
            relief="solid",
            borderwidth=1,
        )
        self.preview.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.status = tk.StringVar(value="就绪")
        tk.Label(
            self,
            textvariable=self.status,
            bg="#eeeeee",
            fg="#333",
            font=("Microsoft YaHei UI", 9),
            anchor="w",
            padx=12,
            pady=6,
        ).pack(fill="x", side="bottom")

        self.refresh_preview()

    def refresh_preview(self) -> None:
        try:
            content = read_hosts()
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", content if content else "(文件为空或不存在)")
            self.status.set(f"已加载当前 hosts（{len(content.splitlines())} 行）")
        except Exception as exc:
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", f"读取失败：{exc}")
            self.status.set("读取失败")

    def on_reset(self) -> None:
        if not is_admin():
            messagebox.showwarning(
                "需要管理员权限",
                "修改 hosts 需要管理员权限。\n请右键以管理员身份运行本程序。",
            )
            return

        ok = messagebox.askyesno(
            "确认初始化",
            "将覆盖当前 hosts，恢复为 Windows 默认内容。\n是否继续？",
        )
        if not ok:
            return

        try:
            write_hosts(DEFAULT_HOSTS)
            dns_ok, dns_msg = flush_dns()
            self.refresh_preview()
            msg = "Hosts 已初始化。"
            if dns_ok:
                msg += "\n\nDNS 缓存已刷新。"
            else:
                msg += f"\n\nDNS 刷新失败：{dns_msg}"
            self.status.set("初始化成功")
            messagebox.showinfo("完成", msg)
        except PermissionError:
            messagebox.showerror(
                "权限不足",
                "无法写入 hosts。请确认以管理员身份运行，并检查文件是否被占用。",
            )
            self.status.set("写入失败：权限不足")
        except Exception as exc:
            messagebox.showerror("失败", f"初始化失败：\n{exc}")
            self.status.set("初始化失败")


def main() -> None:
    if not is_admin():
        try:
            elevate()
            return
        except Exception:
            pass

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
