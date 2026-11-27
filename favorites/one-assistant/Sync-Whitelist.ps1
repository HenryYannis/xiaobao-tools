# ==============================================================================
# 机房教学策略 - 浏览器白名单静默同步与晚间关机管理 (PowerShell 原生版)
# 设计原则：
# 1. 兼容 Windows PowerShell 5.1 及更高版本
# 2. 纯静默无界面运行 (WindowStyle Hidden)
# 3. 单向拉取与加锁：只有“拉取并锁定白名单”功能，无任何“解除/解锁”代码，防学生逆向与破坏
# 4. 离线/故障自动降级：网络异常时保留本地缓存，不影响正常使用
# 5. 晚间纪律管控：自动部署每日 20:15 定时关机策略，并在开机超时时立即执行关机
# ==============================================================================

param(
    [int]$MaxRetries = 4,
    [int]$RetryDelaySeconds = 5
)

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
$CacheDir = "C:\ProgramData\XiaobaoTools"
$CachePath = "C:\ProgramData\XiaobaoTools\whitelist_cache.txt"

$SyncLog = "C:\ProgramData\XiaobaoTools\sync.log"
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
    # 兼容带 UTF-8 BOM 的白名单文件，避免首行被误判为非法字符
    $text = $text.TrimStart([char]0xFEFF)
    $list = New-Object System.Collections.Generic.List[string]
    # 用 -split 按行切分：PowerShell 7 下 .Split(@(...)) 可能被当成一个分隔符字符串，整份内容不被切开
    foreach ($line in ($text -split "\r\n|\r|\n")) {
        $t = $line.Trim()
        if ($t.Length -eq 0 -or $t.StartsWith("#")) { continue }
        if ($t.Length -gt 256 -or $t -notmatch '^[A-Za-z0-9*.\-:/_%?=&#~+]+$') {
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

function Get-RemoteWhitelistText([string]$url) {
    $ErrorActionPreference = 'Stop'
    # Windows PowerShell 5.1 默认可能只启用 TLS 1.0，必须显式开启 TLS 1.2 (3072) 及 TLS 1.3 (12288)
    try {
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072 -bor 12288
    } catch {
        try {
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        } catch { $null }
    }

    $req = [System.Net.HttpWebRequest]::Create($url)
    $req.Method = "GET"
    $req.Timeout = 8000
    $req.ReadWriteTimeout = 8000
    $req.CachePolicy = New-Object System.Net.Cache.RequestCachePolicy([System.Net.Cache.RequestCacheLevel]::BypassCache)
    $req.Headers.Add("Cache-Control", "no-cache")

    $resp = $null
    $reader = $null
    try {
        $resp = $req.GetResponse()
        $stream = $resp.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8, $true)
        return $reader.ReadToEnd()
    } finally {
        if ($reader) { $reader.Close() }
        if ($resp) { $resp.Close() }
    }
}

$rules = $null
$ruleSource = $null
if ($MaxRetries -lt 1) { $MaxRetries = 1 }

# 1. 尝试从云端拉取（含开机网络未就绪重试），校验通过才更新本地缓存
for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
    try {
        $remoteText = Get-RemoteWhitelistText $RemoteUrl
        $rules = Get-ValidRules $remoteText "remote"
        if ($rules) {
            $ruleSource = "remote"
            if (-not (Test-Path $CacheDir)) {
                New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
            }
            [System.IO.File]::WriteAllText($CachePath, $remoteText, [System.Text.Encoding]::UTF8)
            break
        }
        # 内容校验未通过（如被网关劫持返回登录页），无需重试
        break
    } catch {
        Write-SyncLog "Download failed (attempt $attempt/$MaxRetries): $($_.Exception.Message)"
        $rules = $null
        if ($attempt -lt $MaxRetries) {
            Start-Sleep -Seconds $RetryDelaySeconds
        }
    }
}

# 2. 若云端不可用，尝试读取上次校验通过的本地缓存
if (-not $rules -and (Test-Path $CachePath)) {
    try {
        $rules = Get-ValidRules ([System.IO.File]::ReadAllText($CachePath, [System.Text.Encoding]::UTF8)) "cache"
        if ($rules) { $ruleSource = "cache" }
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
Write-SyncLog "Synced $($rules.Count) rules from $ruleSource successfully. Last: $($rules[$rules.Count - 1])"
