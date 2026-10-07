# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 全局配置与常量
"""

import os
import sys

# --- 路径与资源配置 ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
if getattr(sys, 'frozen', False):
    RESOURCE_DIR = sys._MEIPASS
else:
    RESOURCE_DIR = _SCRIPT_DIR

# pip 镜像源地址
PYPI_TUNA_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
PYPI_ALIYUN_URL = "https://mirrors.aliyun.com/pypi/simple/"

# 浏览器默认启动直达地址
DEFAULT_STARTUP_URL = "https://xbkjz.cn/edu"

# 壁纸图片文件名与锁屏路径
WALLPAPER_FILENAME = "bizhi.jpg"
_LOCKSCREEN_REG_PATH = r"SOFTWARE\Policies\Microsoft\Windows\Personalization"
_LOCKSCREEN_REG_VALUE = "LockScreenImage"
_WALLPAPER_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
_WALLPAPER_DEPLOY_PATH = os.path.join(_WALLPAPER_DEPLOY_DIR, WALLPAPER_FILENAME)

# 白名单配置文件与默认规则
WHITELIST_FILENAME = "whitelist.txt"
DEFAULT_ALLOWLIST = [
    # 本地与浏览器内部协议
    "localhost",
    "127.0.0.1",
    "file://*",
    "edge://*",
    "chrome://*",
    # 必应、MSN 与微软底层服务 (保障新标签页与系统弹窗畅通)
    "bing.com",
    "bing.net",
    "bingapis.com",
    "msn.cn",
    "msn.com",
    "microsoft.com",
    "live.com",
    "azureedge.net",
    "aka.ms",
    # 小宝科技站 & xbyxz.cn
    "xbkjz.cn",
    "xbyxz.cn",
    # 中国电子学会
    "qceit.org.cn",
    # Tinkercad 建模与电路
    "tinkercad.com",
    # 信息学奥赛一本通
    "ybt.ssoier.cn",
]

# --- 注册表路径常量 ---
# 桌面个性化
REG_WALLPAPER_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
REG_WALLPAPER_VALUE = "NoChangingWallPaper"
REG_SPOTLIGHT_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
REG_SPOTLIGHT_VALUE = "{2cc5ca98-6485-489a-920e-b3e88a6ccce3}"

# 浏览器基础键路径
REG_EDGE_PATH = r"SOFTWARE\Policies\Microsoft\Edge"
REG_CHROME_PATH = r"SOFTWARE\Policies\Google\Chrome"

# 浏览器通用子键与值名
REG_BROWSER_BLOCKLIST_SUBKEY = "URLBlocklist"
REG_BROWSER_ALLOWLIST_SUBKEY = "URLAllowlist"
REG_BROWSER_DOWNLOAD_VALUE = "DownloadRestrictions"

# 离线游戏值名
REG_EDGE_GAME_VALUE = "AllowSurfGame"
REG_CHROME_GAME_VALUE = "AllowDinosaurEasterEgg"

# 系统与文件配置
REG_LONGPATHS_PATH = r"SYSTEM\CurrentControlSet\Control\FileSystem"
REG_LONGPATHS_VALUE = "LongPathsEnabled"
REG_EXPLORER_ADVANCED_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
REG_HIDE_FILE_EXT_VALUE = "HideFileExt"

# --- 云端白名单静默同步配置 ---
CLOUD_WHITELIST_URL = "https://xbkjz.cn/edu/whitelist.txt"
CLOUD_SYNC_TASK_NAME = "XiaobaoPolicySync"
CLOUD_SYNC_SCRIPT_FILENAME = "Sync-Whitelist.ps1"
CLOUD_SYNC_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
CLOUD_SYNC_SCRIPT_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, CLOUD_SYNC_SCRIPT_FILENAME)
CLOUD_SYNC_LOG_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, "sync.log")

SYNC_SCRIPT_CONTENT = """# ==============================================================================
# 机房教学策略 - 浏览器白名单静默同步脚本 (PowerShell 原生版)
# 设计原则：
# 1. 兼容 Windows PowerShell 5.1 及更高版本
# 2. 纯静默无界面运行 (WindowStyle Hidden)
# 3. 单向拉取与加锁：只有“拉取并锁定白名单”功能，无任何“解除/解锁”代码，防学生逆向与破坏
# 4. 离线/故障自动降级：网络异常时保留本地缓存，不影响正常使用
# ==============================================================================

$ErrorActionPreference = 'SilentlyContinue'

$RemoteUrl = "https://xbkjz.cn/edu/whitelist.txt"
$LocalFallbackPath = "C:\\Users\\A3\\Desktop\\Website\\xiaobao-tech\\edu\\whitelist.txt"
$CacheDir = "C:\\ProgramData\\XiaobaoTools"
$CachePath = "C:\\ProgramData\\XiaobaoTools\\whitelist_cache.txt"

$rawText = $null

# 1. 尝试从云端拉取
try {
    $wc = New-Object System.Net.WebClient
    $wc.Encoding = [System.Text.Encoding]::UTF8
    $rawText = $wc.DownloadString($RemoteUrl)
    if ($rawText -and $rawText.Trim().Length -gt 0) {
        if (-not (Test-Path $CacheDir)) {
            New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
        }
        [System.IO.File]::WriteAllText($CachePath, $rawText, [System.Text.Encoding]::UTF8)
    }
} catch {
    $rawText = $null
}

# 2. 若云端不可达，尝试读取本地发布文件
if (-not $rawText) {
    if (Test-Path $LocalFallbackPath) {
        try {
            $rawText = [System.IO.File]::ReadAllText($LocalFallbackPath, [System.Text.Encoding]::UTF8)
        } catch {
            $rawText = $null
        }
    }
}

# 3. 若依然没有，尝试读取本地缓存文件
if (-not $rawText) {
    if (Test-Path $CachePath) {
        try {
            $rawText = [System.IO.File]::ReadAllText($CachePath, [System.Text.Encoding]::UTF8)
        } catch {
            $rawText = $null
        }
    }
}

# 如果没有获得任何有效内容，退出以避免破坏现有配置
if (-not $rawText) {
    exit 0
}

# 4. 解析白名单规则
$rules = New-Object System.Collections.Generic.List[string]
$lines = $rawText.Split(@("`r`n", "`r", "`n"), [System.StringSplitOptions]::None)
foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -gt 0 -and -not $trimmed.StartsWith("#")) {
        $rules.Add($trimmed)
    }
}

if ($rules.Count -eq 0) {
    exit 0
}

# 5. 写入 Edge 与 Chrome 策略 (涵盖 HKLM 与 HKCU)
$policyTargets = @(
    "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Edge",
    "HKLM:\\SOFTWARE\\Policies\\Google\\Chrome",
    "HKCU:\\SOFTWARE\\Policies\\Microsoft\\Edge",
    "HKCU:\\SOFTWARE\\Policies\\Google\\Chrome"
)

foreach ($baseKey in $policyTargets) {
    $blockKey = "$baseKey\\URLBlocklist"
    $allowKey = "$baseKey\\URLAllowlist"

    if (-not (Test-Path $baseKey)) {
        New-Item -Path $baseKey -Force | Out-Null
    }
    if (-not (Test-Path $blockKey)) {
        New-Item -Path $blockKey -Force | Out-Null
    }

    # 封禁非白名单网址
    Set-ItemProperty -Path $blockKey -Name "1" -Value "*" -Type String -Force

    # 清空并重新写入白名单列表
    if (Test-Path $allowKey) {
        Remove-Item -Path $allowKey -Recurse -Force
    }
    New-Item -Path $allowKey -Force | Out-Null

    for ($i = 0; $i -lt $rules.Count; $i++) {
        $idxName = ($i + 1).ToString()
        Set-ItemProperty -Path $allowKey -Name $idxName -Value $rules[$i] -Type String -Force
    }

    # 禁用浏览器后台常驻与启动加速，确保策略即时生效
    Set-ItemProperty -Path $baseKey -Name "StartupBoostEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $baseKey -Name "BackgroundModeEnabled" -Value 0 -Type DWord -Force
}

# 写入完成日志标记
try {
    $logMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Synced $($rules.Count) rules successfully. Last: $($rules[$rules.Count - 1])`r`n"
    [System.IO.File]::AppendAllText("C:\\ProgramData\\XiaobaoTools\\sync.log", $logMsg, [System.Text.Encoding]::UTF8)
} catch {
    $null
}
"""

def 设置窗口图标(window):
    icon_path = os.path.join(RESOURCE_DIR, "system.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception:
            pass
