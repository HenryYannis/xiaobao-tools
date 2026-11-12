# -*- coding: utf-8 -*-
"""
Win 服务优化工具 —— 一键禁用 7 个占内存的 Windows 服务
对应文章: https://zhuanlan.zhihu.com/p/2082535069646959544

用法：双击运行（需管理员权限），或 python win_service_optimizer.py
依赖：仅标准库（tkinter / ctypes / winreg），Windows 自带 Python 均含
"""

import ctypes
import os
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ------------------------------------------------------------------
# 服务定义：(服务名, 显示名称, 中文说明, 默认推荐)
# ------------------------------------------------------------------
SERVICES = [
    ("SysMain", "SysMain (Superfetch)",
     "预加载加速，SSD 上无用，可吃近 1G 内存。机械硬盘请勿关闭！", False),
    ("DiagTrack", "连接用户体验和遥测",
     "微软收集使用数据上传，空闲时占 CPU 10-20%。可放心关。", True),
    ("DoSvc", "Delivery Optimization 传递优化",
     "P2P 上传更新包给其他电脑，有内存泄漏 bug。强烈建议关。", True),
    ("WSearch", "Windows Search 搜索索引",
     "后台建索引占 CPU/磁盘。不用自带搜索可关（开始菜单搜索会变慢）。", False),
    ("Spooler", "Print Spooler 打印服务",
     "打印队列服务。没打印机可关；用 PDF 虚拟打印的请保留。", False),
    ("WbioSrvc", "Windows 生物识别",
     "指纹/人脸登录。没有指纹识别器才关，关后只能密码登录。", False),
    ("RemoteRegistry", "Remote Registry 远程注册表",
     "允许远程修改注册表，纯安全隐患。所有人都建议关。", True),
]

IS_ADMIN_HINT = "此操作需要管理员权限，请右键以管理员身份运行本脚本。"

SC_MANAGER_CONNECT = 0x0001
SERVICE_QUERY_STATUS = 0x0004
SERVICE_RUNNING = 0x4  # SERVICE_STATUS.dwCurrentState

# sc.exe 用全路径，避免 PATH 劫持
SC_EXE = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                      "System32", "sc.exe")

# SCM API：显式声明 64 位安全的参数/返回类型
_advapi = None


def _adv():
    global _advapi
    if _advapi is None:
        from ctypes import wintypes
        adv = ctypes.windll.advapi32
        adv.OpenSCManagerW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        adv.OpenSCManagerW.restype = ctypes.c_void_p
        adv.OpenServiceW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, wintypes.DWORD]
        adv.OpenServiceW.restype = ctypes.c_void_p
        adv.QueryServiceStatus.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        adv.QueryServiceStatus.restype = wintypes.BOOL
        adv.CloseServiceHandle.argtypes = [ctypes.c_void_p]
        adv.CloseServiceHandle.restype = wintypes.BOOL
        _advapi = adv
    return _advapi

_START_MAP = {0: "驱动(引导)", 1: "驱动(系统)", 2: "自动", 3: "手动", 4: "已禁用"}
_MODE_LABEL = {"disabled": "禁用", "auto": "自动", "demand": "手动"}
_MODE_REG_VALUE = {"disabled": 4, "auto": 2, "demand": 3}


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _decode_output(data: bytes) -> str:
    if not data:
        return ""
    encodings = ("utf-8", "oem", "mbcs") if os.name == "nt" else ("utf-8",)
    for enc in encodings:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            pass
    return data.decode("utf-8", errors="replace")


def run_sc(*args):
    """调用 sc 命令，返回 (返回码, 输出)。"""
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        p = subprocess.run([SC_EXE, *args], capture_output=True,
                           timeout=15, creationflags=flags)
        out = _decode_output(p.stdout) + _decode_output(p.stderr)
        return p.returncode, out.strip()
    except FileNotFoundError:
        return 1, "sc 命令不可用（非 Windows 环境？）"
    except Exception as e:
        return 1, str(e)


def query_start_type(name: str) -> str:
    """从注册表读服务启动类型（与系统语言无关）。失败返回 '未知'。"""
    if os.name != "nt":
        return "未知"
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\%s" % name)
        try:
            start, _ = winreg.QueryValueEx(key, "Start")
        finally:
            winreg.CloseKey(key)
        return _START_MAP.get(start, "未知(%d)" % start)
    except FileNotFoundError:
        return "不存在"
    except Exception:
        return "未知"


def query_running(name: str):
    """用 SCM API 查询运行状态（与系统语言无关）。True/False/None(未知)。"""
    if os.name != "nt":
        return None
    try:
        adv = _adv()
        h_mgr = adv.OpenSCManagerW(None, None, SC_MANAGER_CONNECT)
        if not h_mgr:
            return None
        try:
            h_svc = adv.OpenServiceW(h_mgr, name, SERVICE_QUERY_STATUS)
            if not h_svc:
                return None
            try:
                buf = ctypes.create_string_buffer(36)  # SERVICE_STATUS
                if not adv.QueryServiceStatus(h_svc, buf):
                    return None
                # SERVICE_STATUS 结构: (DWORD dwType, DWORD dwCurrentState, ...)
                state = int.from_bytes(buf.raw[4:8], "little")
                return state == SERVICE_RUNNING
            finally:
                adv.CloseServiceHandle(h_svc)
        finally:
            adv.CloseServiceHandle(h_mgr)
    except Exception:
        return None


def _is_access_denied(code: int, out: str) -> bool:
    return code == 5 or "拒绝访问" in out or "access is denied" in out.lower()


def _set_start_in_registry(name: str, mode: str):
    """直接写入注册表 Start 值，用于处理 sc config 被保护的服务（如 DoSvc）。"""
    if os.name != "nt":
        raise OSError("非 Windows 环境")
    import winreg
    key_path = r"SYSTEM\CurrentControlSet\Services\%s" % name
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                         winreg.KEY_SET_VALUE)
    try:
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, _MODE_REG_VALUE[mode])
    finally:
        winreg.CloseKey(key)


def _try_stop_service(name: str) -> bool:
    stop_code, stop_out = run_sc("stop", name)
    return stop_code == 0 or "1062" in stop_out


def set_service(name: str, mode: str) -> str:
    """mode: 'disabled' | 'auto' | 'demand'。返回结果消息。"""
    label = _MODE_LABEL[mode]
    code, out = run_sc("config", name, "start=", mode)
    via_reg = False
    if code != 0:
        if _is_access_denied(code, out) and is_admin():
            try:
                _set_start_in_registry(name, mode)
                via_reg = True
            except OSError as e:
                return f"❌ {name} 设置失败：{out or '拒绝访问'}；注册表写入也失败：{e}"
        else:
            return f"❌ {name} 设置失败：{out or '未知错误'}（是否管理员权限？）"

    prefix = "已通过注册表设为" if via_reg else "已设为"
    msg = f"✅ {name} {prefix}“{label}”"
    if mode == "disabled":
        if _try_stop_service(name):
            msg += "（服务已停止）"
        elif via_reg:
            msg += "（受系统保护无法立即停止，重启电脑后生效）"
        else:
            msg += "（服务未能停止，可能需重启生效）"
    elif via_reg:
        msg += "（重启电脑后生效）"
    return msg


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Win 服务优化工具 — 禁用 7 个占内存服务")
        self.geometry("860x560")
        self.minsize(760, 480)
        self._queue: "queue.Queue" = queue.Queue()
        self._busy = False
        self._build()
        self.after(100, self._poll_queue)
        self.refresh_all()

    # ---------- 线程安全：工作线程只往队列投递，主循环统一执行 ----------
    def _post(self, fn, *args):
        self._queue.put((fn, args))

    def _poll_queue(self):
        try:
            while True:
                fn, args = self._queue.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    # ---------------- 界面 ----------------
    def _build(self):
        admin = is_admin()
        banner = tk.Label(
            self,
            text=("✅ 已以管理员身份运行" if admin
                  else "⚠️ 未以管理员运行 —— 操作将失败，请右键“以管理员身份运行”"),
            fg="#0a7d32" if admin else "#c0392b",
            font=("Microsoft YaHei", 11, "bold"), anchor="w",
        )
        banner.pack(fill="x", padx=10, pady=(8, 2))

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=6)
        cols = ("name", "state", "desc")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 selectmode="browse")
        for cid, text, w, anchor in (
            ("name", "服务", 240, "w"),
            ("state", "当前状态", 110, "center"),
            ("desc", "说明", 420, "w"),
        ):
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, anchor=anchor)
        sb = ttk.Scrollbar(frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for name, disp, desc, _ in SERVICES:
            self.tree.insert("", "end", iid=name, values=(disp, "读取中…", desc))

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(2, 4))
        self._buttons = []
        for text, cmd in (
            ("刷新状态", self.refresh_all),
            ("禁用选中服务", lambda: self._set_selected("disabled")),
            ("设为手动", lambda: self._set_selected("demand")),
            ("恢复自动", lambda: self._set_selected("auto")),
        ):
            b = tk.Button(btns, text=text, width=14, command=cmd)
            b.pack(side="left", padx=2)
            self._buttons.append(b)

        quick = tk.LabelFrame(self, text="一键操作", font=("Microsoft YaHei", 10))
        quick.pack(fill="x", padx=10, pady=(2, 4))
        tk.Label(quick, text="按文章建议一键禁用：",
                 font=("Microsoft YaHei", 9)).pack(side="left", padx=6)
        b1 = tk.Button(quick, text="一键禁用推荐项 (DiagTrack/DoSvc/RemoteRegistry)",
                       command=self._disable_recommended)
        b1.pack(side="left", padx=6)
        b2 = tk.Button(quick, text="一键恢复全部为自动", command=self._restore_all)
        b2.pack(side="left", padx=6)
        self._buttons += [b1, b2]

        tip = tk.Label(
            self,
            text="提示：禁用 Spooler 会影响 PDF 虚拟打印；禁用 WbioSrvc 后无法指纹/人脸登录；机械硬盘勿禁 SysMain。",
            fg="#666", font=("Microsoft YaHei", 9), anchor="w",
        )
        tip.pack(fill="x", padx=10, pady=(0, 6))

    def _set_buttons_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for b in self._buttons:
            b.configure(state=state)

    # ---------------- 查询（后台线程，不阻塞界面） ----------------
    def refresh_all(self):
        def work():
            for name, *_ in SERVICES:
                cfg = query_start_type(name)
                running = query_running(name)
                if cfg == "不存在":
                    state = "不存在"
                elif running is True:
                    state = cfg + "/运行中"
                elif running is None:
                    state = cfg + "（状态未知）"
                else:
                    state = cfg
                self._post(self.tree.set, name, "state", state)
        threading.Thread(target=work, daemon=True).start()

    # ---------------- 操作 ----------------
    def _selected_name(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在列表中选择一个服务。")
            return None
        return sel[0]

    def _check_admin(self):
        if not is_admin():
            messagebox.showwarning("权限不足", IS_ADMIN_HINT)
            return False
        return True

    def _label(self, name):
        for n, disp, *_ in SERVICES:
            if n == name:
                return disp
        return name

    def _set_selected(self, mode):
        name = self._selected_name()
        if not name or not self._check_admin():
            return
        if not messagebox.askyesno(
                "确认", f"将把 {self._label(name)} 设为“{_MODE_LABEL[mode]}”，继续吗？"):
            return
        self._run_in_thread([name], mode)

    def _disable_recommended(self):
        if not self._check_admin():
            return
        names = [n for n, _, _, rec in SERVICES if rec]
        if not messagebox.askyesno("确认", "将禁用：" + "、".join(names) + "，继续吗？"):
            return
        self._run_in_thread(names, "disabled")

    def _restore_all(self):
        if not self._check_admin():
            return
        if not messagebox.askyesno("确认", "将把列表中全部服务恢复为“自动”启动，继续吗？"):
            return
        self._run_in_thread([n for n, *_ in SERVICES], "auto")

    def _run_in_thread(self, names, mode):
        if self._busy:
            return
        self._busy = True
        self._set_buttons_state(False)

        def work():
            results = [set_service(n, mode) for n in names]
            self._post(self._show_results, names, results)
        threading.Thread(target=work, daemon=True).start()

    def _show_results(self, names, results):
        self._busy = False
        self._set_buttons_state(True)
        messagebox.showinfo("结果", "\n".join(results))
        self.refresh_all()


def main():
    if os.name != "nt":
        print("警告：本工具用于 Windows，当前系统不是 Windows，仅可调试界面。")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
