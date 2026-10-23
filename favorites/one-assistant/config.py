# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 全局配置与常量
"""

import os
import sys

# --- 路径与资源配置 ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
if getattr(sys, 'frozen', False):
    RESOURCE_DIR = getattr(sys, '_MEIPASS', _SCRIPT_DIR)
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
AUTO_SHUTDOWN_TASK_NAME = "XiaobaoAutoShutdown"
CLOUD_SYNC_SCRIPT_FILENAME = "Sync-Whitelist.ps1"
CLOUD_SYNC_DEPLOY_DIR = r"C:\ProgramData\XiaobaoTools"
CLOUD_SYNC_SCRIPT_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, CLOUD_SYNC_SCRIPT_FILENAME)
CLOUD_SYNC_LOG_PATH = os.path.join(CLOUD_SYNC_DEPLOY_DIR, "sync.log")

SYNC_SCRIPT_CONTENT = """# ==============================================================================
# 机房教学策略 - 浏览器白名单静默同步与晚间关机管理 (PowerShell 原生版)
# 设计原则：
# 1. 兼容 Windows PowerShell 5.1 及更高版本
# 2. 纯静默无界面运行 (WindowStyle Hidden)
# 3. 单向拉取与加锁：只有“拉取并锁定白名单”功能，无任何“解除/解锁”代码，防学生逆向与破坏
# 4. 离线/故障自动降级：网络异常时保留本地缓存，不影响正常使用
# 5. 晚间纪律管控：自动部署每日 20:15 定时关机策略，并在开机超时时立即执行关机
# ==============================================================================

$ErrorActionPreference = 'SilentlyContinue'

# ==============================================================================
# 0. 晚间自动关机策略 (默认每天 20:15 自动关机)
# ==============================================================================
$ShutdownHour = 20
$ShutdownMinute = 15
$ShutdownTimeStr = "{0:D2}:{1:D2}" -f $ShutdownHour, $ShutdownMinute

try {
    # (1) 注册/更新每日定时关机计划任务 (以 SYSTEM 最高权限运行，普通学生无法撤销)
    schtasks /create /tn "XiaobaoAutoShutdown" /tr "shutdown.exe /s /t 60" /sc daily /st $ShutdownTimeStr /ru "SYSTEM" /f | Out-Null

    # (2) 漏洞弥补：若开机时已超过设定的关机时间，立即触发 60 秒关机倒计时
    $now = Get-Date
    if ($now.Hour -gt $ShutdownHour -or ($now.Hour -eq $ShutdownHour -and $now.Minute -ge $ShutdownMinute)) {
        shutdown.exe /s /t 60
    }
} catch {
    $null
}

# ==============================================================================
# 1. 云端白名单拉取与加锁
# ==============================================================================

$RemoteUrl = "https://xbkjz.cn/edu/whitelist.txt"
$LocalFallbackPath = "C:\\Users\\A3\\Desktop\\Website\\xiaobao-tech\\edu\\whitelist.txt"
$CacheDir = "C:\\ProgramData\\XiaobaoTools"
$CachePath = "C:\\ProgramData\\XiaobaoTools\\whitelist_cache.txt"

$SyncLog = "C:\\ProgramData\\XiaobaoTools\\sync.log"
function Write-SyncLog([string]$msg) {
    try {
        if (-not (Test-Path $CacheDir)) { New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null }
        [System.IO.File]::AppendAllText($SyncLog, "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg`r`n", [System.Text.Encoding]::UTF8)
    } catch { $null }
}

# 校验白名单内容：每行只能是网址规则（字母、数字和 * . - : / _ % ? = & # ~ +），最多 1000 条。
# 拉到的是网页（比如被劫持、被机房网关重定向到登录页）或格式不对时整份丢弃，不写入浏览器策略。
function Get-ValidRules([string]$text, [string]$source) {
    if (-not $text) { return $null }
    $list = New-Object System.Collections.Generic.List[string]
    foreach ($line in $text.Split(@("`r`n", "`r", "`n"), [System.StringSplitOptions]::None)) {
        $t = $line.Trim()
        if ($t.Length -eq 0 -or $t.StartsWith("#")) { continue }
        if ($t.Length -gt 256 -or $t -notmatch '^[A-Za-z0-9*.\\-:/_%?=&#~+]+$') {
            Write-SyncLog "Rejected $source : invalid line '$($t.Substring(0, [Math]::Min(60, $t.Length)))'"
            return $null
        }
        $list.Add($t)
    }
    if ($list.Count -eq 0 -or $list.Count -gt 1000) {
        Write-SyncLog "Rejected $source : $($list.Count) rules"
        return $null
    }
    return ,$list
}

$rules = $null

# 1. 尝试从云端拉取，校验通过才更新本地缓存
try {
    $wc = New-Object System.Net.WebClient
    $wc.Encoding = [System.Text.Encoding]::UTF8
    $remoteText = $wc.DownloadString($RemoteUrl)
    $rules = Get-ValidRules $remoteText "remote"
    if ($rules) {
        if (-not (Test-Path $CacheDir)) {
            New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
        }
        [System.IO.File]::WriteAllText($CachePath, $remoteText, [System.Text.Encoding]::UTF8)
    }
} catch {
    Write-SyncLog "Download failed: $($_.Exception.Message)"
    $rules = $null
}

# 2. 若云端不可用，尝试读取本地发布文件（教师机上的网站目录，学生机上不存在会自动跳过）
if (-not $rules -and (Test-Path $LocalFallbackPath)) {
    try {
        $rules = Get-ValidRules ([System.IO.File]::ReadAllText($LocalFallbackPath, [System.Text.Encoding]::UTF8)) "local"
    } catch {
        $rules = $null
    }
}

# 3. 若依然没有，尝试读取上次校验通过的本地缓存
if (-not $rules -and (Test-Path $CachePath)) {
    try {
        $rules = Get-ValidRules ([System.IO.File]::ReadAllText($CachePath, [System.Text.Encoding]::UTF8)) "cache"
    } catch {
        $rules = $null
    }
}

# 如果没有获得任何有效规则，退出以避免破坏现有配置
if (-not $rules) {
    Write-SyncLog "No valid whitelist, keep current browser policy"
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
Write-SyncLog "Synced $($rules.Count) rules successfully. Last: $($rules[$rules.Count - 1])"
"""

def 设置窗口图标(window):
    icon_path = os.path.join(RESOURCE_DIR, "system.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception:
            pass
