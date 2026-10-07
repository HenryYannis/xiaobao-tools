# ==============================================================================
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
$LocalFallbackPath = "C:\Users\A3\Desktop\Website\xiaobao-tech\edu\whitelist.txt"
$CacheDir = "C:\ProgramData\XiaobaoTools"
$CachePath = "C:\ProgramData\XiaobaoTools\whitelist_cache.txt"

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
    "HKLM:\SOFTWARE\Policies\Microsoft\Edge",
    "HKLM:\SOFTWARE\Policies\Google\Chrome",
    "HKCU:\SOFTWARE\Policies\Microsoft\Edge",
    "HKCU:\SOFTWARE\Policies\Google\Chrome"
)

foreach ($baseKey in $policyTargets) {
    $blockKey = "$baseKey\URLBlocklist"
    $allowKey = "$baseKey\URLAllowlist"

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
    [System.IO.File]::AppendAllText("C:\ProgramData\XiaobaoTools\sync.log", $logMsg, [System.Text.Encoding]::UTF8)
} catch {
    $null
}
