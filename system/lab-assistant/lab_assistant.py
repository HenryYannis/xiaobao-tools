#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 系统权限限制工具 (System Restrictions Controller)

功能：
- 禁止/允许修改桌面壁纸
- 移除/恢复桌面"了解此图片"聚焦图标
- 禁用/启用 Chrome 和 Edge 离线游戏
- 注入/撤销系统 Hosts 屏蔽规则（拦截娱乐网站）
- 配置/恢复 pip 国内镜像源（清华 TUNA）

特点：
- 传统古早UI：使用 Windows 原生灰/白默认界面风格，布局简单直观，非花哨设计
- 零依赖：纯标准库（tkinter, winreg, ctypes）开发，开箱即用
- 提权检测：自动检测并请求管理员权限以修改系统策略
- 实时同步：启动时自动读取注册表，真实反映系统当前状态
- 智能交互：修改壁纸或图标后支持一键/自动重启资源管理器

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import sys
import ctypes
import shutil
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox
from winreg import (
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    OpenKey, CreateKey, SetValueEx, DeleteValue, QueryValueEx,
    CloseKey, REG_DWORD, REG_SZ, KEY_READ, KEY_ALL_ACCESS
)

# --- Paths ---
# 系统 Hosts 文件路径
SYSTEM_HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
# 本工具自带的 Hosts 屏蔽规则文件（与本脚本同目录）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
LOCAL_HOSTS_PATH = os.path.join(_SCRIPT_DIR, "hosts")
# Hosts 注入块标记
_HOSTS_BLOCK_BEGIN = "# ===== XIAOBAO-TOOLS HOSTS BEGIN ====="
_HOSTS_BLOCK_END   = "# ===== XIAOBAO-TOOLS HOSTS END ====="

# pip 国内镜像（清华 TUNA）
PYPI_MIRROR_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"

# 壁纸图片文件名（与脚本同目录，打包进 EXE 时从 _MEIPASS 提取）
WALLPAPER_FILENAME = "bizhi.jpg"
# 锁屏注册表策略路径
_LOCKSCREEN_REG_PATH = r"SOFTWARE\Policies\Microsoft\Windows\Personalization"
_LOCKSCREEN_REG_VALUE = "LockScreenImage"
# 图片部署到系统固定目录（锁屏策略需要一个持久路径）
_WALLPAPER_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
_WALLPAPER_DEPLOY_PATH = os.path.join(_WALLPAPER_DEPLOY_DIR, WALLPAPER_FILENAME)

# --- Wallpaper & Lock Screen Helper Functions ---
def get_wallpaper_source_path():
    """获取壁纸源文件路径（开发模式取脚本目录，PyInstaller 取 _MEIPASS）"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = _SCRIPT_DIR
    return os.path.join(base, WALLPAPER_FILENAME)


def _deploy_wallpaper():
    """
    将壁纸图片复制到持久路径供锁屏策略使用。
    返回 (deployed_path: str | None, error: str)
    """
    src = get_wallpaper_source_path()
    if not os.path.exists(src):
        return None, f"未找到壁纸文件：{src}"
    try:
        os.makedirs(_WALLPAPER_DEPLOY_DIR, exist_ok=True)
        shutil.copy2(src, _WALLPAPER_DEPLOY_PATH)
        return _WALLPAPER_DEPLOY_PATH, ""
    except Exception as e:
        # 复制失败时降级为直接使用源路径（非打包场景可行）
        return src, str(e)


def set_desktop_wallpaper(image_path):
    """通过 Win32 API 设置桌面壁纸，返回是否成功"""
    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return bool(result)


def set_lockscreen_image(image_path):
    """通过注册表组策略设置锁屏壁纸，返回是否成功"""
    try:
        with CreateKey(HKEY_LOCAL_MACHINE, _LOCKSCREEN_REG_PATH) as key:
            SetValueEx(key, _LOCKSCREEN_REG_VALUE, 0, REG_SZ, image_path)
        return True
    except Exception as e:
        print(f"[LockScreenError] {e}")
        return False


def apply_wallpaper_and_lockscreen():
    """
    部署图片并同时设置桌面壁纸与锁屏。
    返回 (success: bool, message: str)
    """
    path, err = _deploy_wallpaper()
    if path is None:
        return False, f"壁纸文件无法访问：{err}"

    wp_ok = set_desktop_wallpaper(path)
    ls_ok = set_lockscreen_image(path)

    if wp_ok and ls_ok:
        return True, "桌面壁纸和锁屏已设置完成。"
    elif wp_ok:
        return True, "桌面壁纸已设置，锁屏设置失败（请确认管理员权限）。"
    elif ls_ok:
        return True, "锁屏已设置，桌面壁纸 API 调用失败。"
    else:
        return False, "桌面壁纸和锁屏均设置失败，请确认管理员权限。"


# --- Registry Keys ---
# 1. Wallpaper restriction
REG_WALLPAPER_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
REG_WALLPAPER_VALUE = "NoChangingWallPaper"

# 2. Spotlight "Learn about this picture" desktop icon restriction
REG_SPOTLIGHT_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
REG_SPOTLIGHT_VALUE = "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}"

# 3. Chrome Dino Game restriction
REG_CHROME_PATH = r"SOFTWARE\Policies\Google\Chrome"
REG_CHROME_VALUE = "AllowDinosaurEasterEgg"

# 4. Edge Surf Game restriction
REG_EDGE_PATH = r"SOFTWARE\Policies\Microsoft\Edge"
REG_EDGE_VALUE = "AllowSurfGame"


# --- Registry Helper Functions ---
def reg_read_dword(hkey, path, value_name):
    """读取注册表 DWORD 值，如果键或值不存在返回 None"""
    try:
        with OpenKey(hkey, path, 0, KEY_READ) as key:
            val, _ = QueryValueEx(key, value_name)
            return val
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[RegReadError] {path}\\{value_name}: {e}")
        return None


def reg_write_dword(hkey, path, value_name, value):
    """向注册表写入 DWORD 值，返回是否成功"""
    try:
        with CreateKey(hkey, path) as key:
            SetValueEx(key, value_name, 0, REG_DWORD, value)
        return True
    except PermissionError:
        print(f"[RegWritePermissionError] {path}\\{value_name}: Requires administrator privileges.")
        return False
    except Exception as e:
        print(f"[RegWriteError] {path}\\{value_name}: {e}")
        return False


def reg_delete_value(hkey, path, value_name):
    """从注册表删除特定值，如果不存在也视为成功，返回是否成功"""
    try:
        with OpenKey(hkey, path, 0, KEY_ALL_ACCESS) as key:
            DeleteValue(key, value_name)
        return True
    except FileNotFoundError:
        return True
    except PermissionError:
        print(f"[RegDeletePermissionError] {path}\\{value_name}: Requires administrator privileges.")
        return False
    except Exception as e:
        print(f"[RegDeleteError] {path}\\{value_name}: {e}")
        return False


# --- Core Logic Functions ---
def is_admin():
    """判断是否具备管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """以管理员身份重新运行程序"""
    if getattr(sys, 'frozen', False):
        executable = sys.executable
        params = ""
    else:
        executable = sys.executable
        params = f'"{__file__}"'
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        sys.exit(0)
    except Exception as e:
        print(f"提权失败: {e}")
        sys.exit(1)


def restart_explorer():
    """重启 Windows 资源管理器进程以应用桌面和壁纸配置"""
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        subprocess.Popen(["explorer.exe"])
        return True
    except Exception as e:
        print(f"资源管理器重启出错: {e}")
        try:
            subprocess.Popen(["explorer.exe"])
        except Exception:
            pass
        return False


# --- Policy Management Functions ---
def get_wallpaper_locked():
    """获取壁纸锁定的真实状态。1 表示锁定 (True)"""
    val = reg_read_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)
    return val == 1


def set_wallpaper_locked(locked):
    """设置壁纸锁定状态"""
    if locked:
        return reg_write_dword(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_WALLPAPER_PATH, REG_WALLPAPER_VALUE)


def get_spotlight_hidden():
    """获取桌面"了解此图片"隐藏状态。1 表示隐藏 (True)"""
    val = reg_read_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)
    return val == 1


def set_spotlight_hidden(hidden):
    """设置桌面"了解此图片"隐藏状态"""
    if hidden:
        return reg_write_dword(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE, 1)
    else:
        return reg_delete_value(HKEY_CURRENT_USER, REG_SPOTLIGHT_PATH, REG_SPOTLIGHT_VALUE)


def get_browser_games_disabled():
    """
    检查离线游戏禁用状态。
    Chrome: AllowDinosaurEasterEgg = 0 表示禁用
    Edge: AllowSurfGame = 0 表示禁用
    """
    chrome_hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE)
    chrome_hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE)
    edge_hklm = reg_read_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE)
    edge_hkcu = reg_read_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE)

    is_dino_disabled = (chrome_hklm == 0 or chrome_hkcu == 0)
    is_surf_disabled = (edge_hklm == 0 or edge_hkcu == 0)

    return is_dino_disabled or is_surf_disabled


def set_browser_games_disabled(disabled):
    """设置浏览器离线游戏禁用状态"""
    success = True
    if disabled:
        s1 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE, 0)
        s2 = reg_write_dword(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE, 0)
        s3 = reg_write_dword(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE, 0)
        s4 = reg_write_dword(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE, 0)
        success = s1 or s2 or s3 or s4
    else:
        s1 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_CHROME_PATH, REG_CHROME_VALUE)
        s2 = reg_delete_value(HKEY_CURRENT_USER, REG_CHROME_PATH, REG_CHROME_VALUE)
        s3 = reg_delete_value(HKEY_LOCAL_MACHINE, REG_EDGE_PATH, REG_EDGE_VALUE)
        s4 = reg_delete_value(HKEY_CURRENT_USER, REG_EDGE_PATH, REG_EDGE_VALUE)
        success = s1 and s2 and s3 and s4

    return success


# --- Hosts Injection Functions ---
def _read_system_hosts():
    """读取系统 hosts 文件内容，出错返回 None"""
    try:
        with open(SYSTEM_HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        print(f"[HostsReadError] {e}")
        return None


def _write_system_hosts(content):
    """写入系统 hosts 文件，返回是否成功"""
    try:
        with open(SYSTEM_HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except PermissionError:
        print("[HostsWritePermissionError] 需要管理员权限")
        return False
    except Exception as e:
        print(f"[HostsWriteError] {e}")
        return False


def get_hosts_injected():
    """判断系统 hosts 中是否已注入小宝工具箱屏蔽规则"""
    content = _read_system_hosts()
    if content is None:
        return False
    return _HOSTS_BLOCK_BEGIN in content


def _strip_injection(content):
    """从 hosts 内容中移除小宝工具箱注入块"""
    lines = content.splitlines(keepends=True)
    result = []
    inside = False
    for line in lines:
        if line.strip() == _HOSTS_BLOCK_BEGIN:
            inside = True
            continue
        if line.strip() == _HOSTS_BLOCK_END:
            inside = False
            continue
        if not inside:
            result.append(line)
    return "".join(result)


def inject_hosts():
    """将本地 hosts 屏蔽规则注入系统 hosts 文件，返回 (success, message)"""
    if not os.path.exists(LOCAL_HOSTS_PATH):
        return False, f"未找到规则文件：{LOCAL_HOSTS_PATH}"
    try:
        with open(LOCAL_HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            local_rules = f.read()
    except Exception as e:
        return False, f"读取规则文件失败：{e}"

    sys_content = _read_system_hosts()
    if sys_content is None:
        return False, "无法读取系统 hosts 文件。"

    if _HOSTS_BLOCK_BEGIN in sys_content:
        sys_content = _strip_injection(sys_content)

    block = (
        f"\n{_HOSTS_BLOCK_BEGIN}\n"
        f"{local_rules.strip()}\n"
        f"{_HOSTS_BLOCK_END}\n"
    )
    new_content = sys_content.rstrip("\n") + "\n" + block

    if not _write_system_hosts(new_content):
        return False, "写入系统 hosts 失败，请确认管理员权限。"

    try:
        subprocess.run(
            ["ipconfig", "/flushdns"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception:
        pass

    return True, "Hosts 屏蔽规则已成功注入，DNS 缓存已刷新。"


def remove_hosts():
    """从系统 hosts 中撤销注入的屏蔽规则，返回 (success, message)"""
    sys_content = _read_system_hosts()
    if sys_content is None:
        return False, "无法读取系统 hosts 文件。"

    if _HOSTS_BLOCK_BEGIN not in sys_content:
        return True, "系统 hosts 中未检测到注入规则，无需撤销。"

    new_content = _strip_injection(sys_content)
    if not _write_system_hosts(new_content):
        return False, "写入系统 hosts 失败，请确认管理员权限。"

    try:
        subprocess.run(
            ["ipconfig", "/flushdns"],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception:
        pass

    return True, "Hosts 屏蔽规则已成功撤销，DNS 缓存已刷新。"


# --- pip Mirror Functions ---
def _run_pip_config(args):
    """运行 pip config 命令，返回 (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "config"] + args,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def get_pip_mirror_status():
    """
    获取当前 pip 全局 index-url 配置。
    返回 (is_mirror_set: bool, current_url: str)
    """
    code, out, err = _run_pip_config(["get", "global.index-url"])
    if code == 0 and out:
        current = out.strip()
        is_mirror = (
            "tuna" in current or "aliyun" in current
            or "douban" in current or "163" in current
            or "tencent" in current or "huaweicloud" in current
        )
        return is_mirror, current
    return False, ""


def set_pip_mirror(use_mirror):
    """设置或取消 pip 国内镜像，返回 (success, message)"""
    if use_mirror:
        code, out, err = _run_pip_config(["set", "global.index-url", PYPI_MIRROR_URL])
        if code == 0:
            return True, f"pip 镜像已设置为清华 TUNA 源：{PYPI_MIRROR_URL}"
        return False, f"设置失败：{err or out}"
    else:
        code, out, err = _run_pip_config(["unset", "global.index-url"])
        if code == 0:
            return True, "pip 镜像已恢复为官方默认源。"
        # pip config unset 对不存在的键也可能返回非0，统一视为成功
        return True, "pip 镜像已恢复为官方默认源（原本未配置）。"


# --- Classic GUI Implementation ---
class RestrictionsToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("系统权限控制中心")
        self.root.resizable(False, False)

        # 居中窗口（高度足够容纳所有功能区域）
        w, h = 480, 480
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.auto_restart_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_status()

    def _build_ui(self):
        # ── 固定底部元素：必须先 pack(side=BOTTOM)，否则会被中间内容遮挡 ──────

        # 最底部状态栏（凹陷样式）
        self.status_lbl = tk.Label(
            self.root,
            text="系统权限：已获得管理员权限",
            font=("微软雅黑", 8),
            anchor="w",
            bd=1,
            relief=tk.SUNKEN,
            padx=5,
            pady=2
        )
        self.status_lbl.pack(fill=tk.X, side=tk.BOTTOM)

        # 底部操作栏
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=15, pady=(3, 4), side=tk.BOTTOM)

        self.restart_btn = tk.Button(
            footer_frame,
            text="重启资源管理器",
            font=("微软雅黑", 9),
            command=self.manual_restart_explorer
        )
        self.restart_btn.pack(side=tk.RIGHT)

        self.chk = tk.Checkbutton(
            footer_frame,
            text="修改后自动重启资源管理器",
            variable=self.auto_restart_var,
            font=("微软雅黑", 9)
        )
        self.chk.pack(side=tk.LEFT)

        # 作者信息 & 网站超链接
        author_frame = tk.Frame(self.root)
        author_frame.pack(fill=tk.X, padx=15, pady=(0, 2), side=tk.BOTTOM)

        tk.Label(
            author_frame,
            text="作者：小宝科技站 (xbkjz.cn)　",
            font=("微软雅黑", 8),
            fg="gray"
        ).pack(side=tk.LEFT)

        link_lbl = tk.Label(
            author_frame,
            text="xbkjz.cn",
            font=("微软雅黑", 8, "underline"),
            fg="#0066CC",
            cursor="hand2"
        )
        link_lbl.pack(side=tk.LEFT)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))
        link_lbl.bind("<Enter>", lambda e: link_lbl.configure(fg="#0044AA"))
        link_lbl.bind("<Leave>", lambda e: link_lbl.configure(fg="#0066CC"))

        # ── 主内容区（从上往下 pack）─────────────────────────────────────────

        # 头部标题
        tk.Label(
            self.root,
            text="系统限制与策略控制中心",
            font=("微软雅黑", 12, "bold")
        ).pack(pady=(10, 2))

        tk.Label(
            self.root,
            text="管理学校机房、演示环境或公共设备的安全策略",
            font=("微软雅黑", 9),
            fg="gray"
        ).pack(pady=(0, 5))

        # 策略设置 LabelFrame
        content_frame = tk.LabelFrame(
            self.root,
            text="策略设置",
            font=("微软雅黑", 9),
            padx=15,
            pady=8
        )
        content_frame.pack(fill=tk.X, padx=15, pady=(0, 5))

        # 1. 桌面壁纸限制
        wp_frame = tk.Frame(content_frame)
        wp_frame.pack(fill=tk.X, pady=3)
        self.wp_lbl = tk.Label(wp_frame, text="壁纸修改权限：读取中...", font=("微软雅黑", 9))
        self.wp_lbl.pack(side=tk.LEFT)
        self.wp_btn = tk.Button(
            wp_frame, text="读取中...", font=("微软雅黑", 9),
            width=10, command=self.toggle_wallpaper
        )
        self.wp_btn.pack(side=tk.RIGHT)

        # 2. 桌面"了解此图片"
        sp_frame = tk.Frame(content_frame)
        sp_frame.pack(fill=tk.X, pady=3)
        self.sp_lbl = tk.Label(sp_frame, text='桌面"了解此图片"：读取中...', font=("微软雅黑", 9))
        self.sp_lbl.pack(side=tk.LEFT)
        self.sp_btn = tk.Button(
            sp_frame, text="读取中...", font=("微软雅黑", 9),
            width=10, command=self.toggle_spotlight
        )
        self.sp_btn.pack(side=tk.RIGHT)

        # 3. 浏览器离线游戏限制
        bg_frame = tk.Frame(content_frame)
        bg_frame.pack(fill=tk.X, pady=3)
        self.bg_lbl = tk.Label(bg_frame, text="浏览器离线小游戏：读取中...", font=("微软雅黑", 9))
        self.bg_lbl.pack(side=tk.LEFT)
        self.bg_btn = tk.Button(
            bg_frame, text="读取中...", font=("微软雅黑", 9),
            width=10, command=self.toggle_browser_games
        )
        self.bg_btn.pack(side=tk.RIGHT)

        # 网站屏蔽（Hosts 注入）LabelFrame
        hosts_lf = tk.LabelFrame(
            self.root,
            text="网站屏蔽（Hosts 注入）",
            font=("微软雅黑", 9),
            padx=15,
            pady=8
        )
        hosts_lf.pack(fill=tk.X, padx=15, pady=(0, 5))

        hf_row = tk.Frame(hosts_lf)
        hf_row.pack(fill=tk.X)
        self.hosts_lbl = tk.Label(hf_row, text="屏蔽规则：读取中...", font=("微软雅黑", 9))
        self.hosts_lbl.pack(side=tk.LEFT)
        self.hosts_btn = tk.Button(
            hf_row, text="读取中...", font=("微软雅黑", 9),
            width=10, command=self.toggle_hosts
        )
        self.hosts_btn.pack(side=tk.RIGHT)

        # pip 软件源配置 LabelFrame
        pip_lf = tk.LabelFrame(
            self.root,
            text="pip 软件源配置",
            font=("微软雅黑", 9),
            padx=15,
            pady=8
        )
        pip_lf.pack(fill=tk.X, padx=15, pady=(0, 5))

        pf_row = tk.Frame(pip_lf)
        pf_row.pack(fill=tk.X)
        self.pip_lbl = tk.Label(pf_row, text="pip 镜像源：读取中...", font=("微软雅黑", 9))
        self.pip_lbl.pack(side=tk.LEFT)
        self.pip_btn = tk.Button(
            pf_row, text="读取中...", font=("微软雅黑", 9),
            width=10, command=self.toggle_pip_mirror
        )
        self.pip_btn.pack(side=tk.RIGHT)

    def refresh_status(self):
        """读取系统真实状态并更新UI文字"""
        # 1. 壁纸限制状态
        wp_locked = get_wallpaper_locked()
        if wp_locked:
            self.wp_lbl.configure(text="壁纸修改权限：已禁止")
            self.wp_btn.configure(text="允许修改")
        else:
            self.wp_lbl.configure(text="壁纸修改权限：正常")
            self.wp_btn.configure(text="禁止修改")

        # 2. 了解此图片状态
        sp_hidden = get_spotlight_hidden()
        if sp_hidden:
            self.sp_lbl.configure(text='桌面"了解此图片"：已隐藏')
            self.sp_btn.configure(text="恢复显示")
        else:
            self.sp_lbl.configure(text='桌面"了解此图片"：正常显示')
            self.sp_btn.configure(text="隐藏图标")

        # 3. 浏览器游戏状态
        bg_disabled = get_browser_games_disabled()
        if bg_disabled:
            self.bg_lbl.configure(text="浏览器离线小游戏：已禁用")
            self.bg_btn.configure(text="启用游戏")
        else:
            self.bg_lbl.configure(text="浏览器离线小游戏：正常启用")
            self.bg_btn.configure(text="禁用游戏")

        # 4. Hosts 注入状态
        hosts_injected = get_hosts_injected()
        if hosts_injected:
            self.hosts_lbl.configure(text="屏蔽规则：已注入系统 Hosts")
            self.hosts_btn.configure(text="撤销注入")
        else:
            self.hosts_lbl.configure(text="屏蔽规则：未注入")
            self.hosts_btn.configure(text="注入规则")

        # 5. pip 镜像状态
        pip_mirror, pip_url = get_pip_mirror_status()
        if pip_mirror:
            short = pip_url if len(pip_url) <= 38 else pip_url[:35] + "..."
            self.pip_lbl.configure(text=f"pip 镜像源：{short}")
            self.pip_btn.configure(text="恢复官方源")
        else:
            self.pip_lbl.configure(text="pip 镜像源：官方默认 / 未配置")
            self.pip_btn.configure(text="启用国内源")

    def trigger_explorer_update(self, action_name):
        """根据自动重启选项，自动或手动重启资源管理器"""
        if self.auto_restart_var.get():
            self.status_lbl.configure(text="正在重启资源管理器...")
            self.root.update()
            if restart_explorer():
                self.status_lbl.configure(text="设置已保存，资源管理器已成功重启。")
            else:
                self.status_lbl.configure(text="设置已保存，但资源管理器重启失败。")
        else:
            messagebox.showinfo(
                "操作成功",
                f'设置已修改。\n\n请点击右下角的"重启资源管理器"按钮以应用更改！'
            )
            self.status_lbl.configure(text="设置已保存，等待重启资源管理器...")

    def toggle_wallpaper(self):
        """切换壁纸锁状态。锁定时先强制设置指定壁纸和锁屏，再禁止用户修改。"""
        current_state = get_wallpaper_locked()
        next_state = not current_state

        if next_state:
            # ── 锁定前：先设置壁纸 & 锁屏 ──────────────────────────────────
            self.status_lbl.configure(text="正在设置壁纸和锁屏...")
            self.root.update()
            wp_ok, wp_msg = apply_wallpaper_and_lockscreen()
            if not wp_ok:
                messagebox.showerror("壁纸设置失败", wp_msg)
                self.status_lbl.configure(text="操作取消：壁纸设置失败。")
                return

        if set_wallpaper_locked(next_state):
            self.refresh_status()
            if next_state:
                self.status_lbl.configure(text="壁纸和锁屏已锁定，用户无法修改。")
                self.trigger_explorer_update("壁纸限制")
            else:
                self.trigger_explorer_update("壁纸限制")
        else:
            messagebox.showerror("错误", "修改壁纸锁定状态失败，请确认是否以管理员权限运行。")

    def toggle_spotlight(self):
        """切换桌面"了解此图片"隐藏状态"""
        current_state = get_spotlight_hidden()
        next_state = not current_state
        if set_spotlight_hidden(next_state):
            self.refresh_status()
            self.trigger_explorer_update("了解此图片")
        else:
            messagebox.showerror("错误", '修改"了解此图片"隐藏状态失败，请确认是否以管理员权限运行。')

    def toggle_browser_games(self):
        """切换浏览器游戏禁用状态"""
        current_state = get_browser_games_disabled()
        next_state = not current_state
        if set_browser_games_disabled(next_state):
            self.refresh_status()
            messagebox.showinfo(
                "操作成功",
                "离线小游戏设置已保存！\n\n请重新启动 Chrome 或 Edge 浏览器使策略生效。"
            )
            self.status_lbl.configure(text="设置已保存，需要重启浏览器生效。")
        else:
            messagebox.showerror("错误", "修改浏览器游戏限制失败，请检查管理员权限。")

    def toggle_hosts(self):
        """切换 Hosts 注入状态"""
        injected = get_hosts_injected()
        if injected:
            success, msg = remove_hosts()
        else:
            success, msg = inject_hosts()

        if success:
            self.refresh_status()
            self.status_lbl.configure(text=msg[:62] + ("..." if len(msg) > 62 else ""))
        else:
            messagebox.showerror("操作失败", msg)

    def toggle_pip_mirror(self):
        """切换 pip 镜像源"""
        is_mirror, _ = get_pip_mirror_status()
        self.status_lbl.configure(text="正在配置 pip 镜像源...")
        self.root.update()
        success, msg = set_pip_mirror(not is_mirror)
        if success:
            self.refresh_status()
            self.status_lbl.configure(text=msg[:62] + ("..." if len(msg) > 62 else ""))
        else:
            messagebox.showerror("操作失败", msg)

    def manual_restart_explorer(self):
        """手动重启资源管理器"""
        self.status_lbl.configure(text="正在手动重启资源管理器...")
        self.root.update()
        if restart_explorer():
            self.status_lbl.configure(text="资源管理器重启成功。")
            messagebox.showinfo("提示", "资源管理器已成功重启，更改已生效。")
        else:
            self.status_lbl.configure(text="资源管理器重启失败。")
            messagebox.showerror("错误", "无法重启资源管理器，请尝试手动重启。")


def main():
    if sys.platform != "win32":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("系统不支持", "本工具仅支持 Windows 操作系统。")
        sys.exit(1)

    if not is_admin():
        run_as_admin()
        return

    root = tk.Tk()
    app = RestrictionsToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
