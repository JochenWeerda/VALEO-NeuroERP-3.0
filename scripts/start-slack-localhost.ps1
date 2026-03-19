param(
    [int]$Port = 8000,
    [string]$AppName = "VALEO NeuroERP",
    [string]$BotDisplayName = "VALEO NeuroERP",
    [string]$Subdomain = "",
    [ValidateSet("auto", "ngrok", "localtunnel", "cloudflared")]
    [string]$Provider = "auto"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$logsDir = Join-Path $repoRoot "logs"
$distDir = Join-Path $repoRoot "dist"
$logPath = Join-Path $logsDir "slack-localtunnel.log"
$errLogPath = Join-Path $logsDir "slack-localtunnel.err.log"
$pidPath = Join-Path $distDir "slack-localtunnel.pid"

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

$existingPid = $null
if (Test-Path $pidPath) {
    $existingPid = (Get-Content -Path $pidPath -Raw).Trim()
    if ($existingPid) {
        try {
            $existingProcess = Get-Process -Id ([int]$existingPid) -ErrorAction Stop
            Write-Host "Localtunnel laeuft bereits mit PID $existingPid." -ForegroundColor Yellow
            Write-Host "Stoppe ihn zuerst oder loesche dist\\slack-localtunnel.pid." -ForegroundColor Yellow
            exit 1
        } catch {
        }
    }
}

function Get-PublicUrlFromNgrok {
    try {
        $response = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5
        foreach ($tunnel in ($response.tunnels | Where-Object { $_.proto -eq "https" })) {
            if ($tunnel.public_url) {
                return [string]$tunnel.public_url
            }
        }
    } catch {
    }
    return $null
}

function Get-PublicUrlFromCloudflared {
    if (-not (Test-Path $logPath)) {
        return $null
    }
    $lines = Get-Content -Path $logPath -ErrorAction SilentlyContinue
    foreach ($line in $lines) {
        if ($line -match "https://[a-zA-Z0-9.-]+\\.trycloudflare\\.com") {
            return ($Matches[0]).Trim()
        }
    }
    return $null
}

function Start-NgrokProcess {
    param([int]$Port)
    return Start-Process -FilePath "ngrok.exe" -ArgumentList @("http", "$Port", "--log=stdout") -RedirectStandardOutput $logPath -RedirectStandardError $errLogPath -PassThru -WindowStyle Hidden
}

function Start-CloudflaredProcess {
    param([int]$Port)
    return Start-Process -FilePath "cloudflared.exe" -ArgumentList @("tunnel", "--url", "http://localhost:$Port", "--no-autoupdate", "--logfile", $logPath) -RedirectStandardError $errLogPath -PassThru -WindowStyle Hidden
}

function Start-LocaltunnelProcess {
    param([int]$Port, [string]$Subdomain)
    $args = @("--yes", "localtunnel", "--port", "$Port")
    if ($Subdomain.Trim()) {
        $args += @("--subdomain", $Subdomain.Trim())
    }
    return Start-Process -FilePath "npx.cmd" -ArgumentList $args -RedirectStandardOutput $logPath -RedirectStandardError $errLogPath -PassThru -WindowStyle Hidden
}

function Resolve-Provider {
    param([string]$Requested)
    if ($Requested -ne "auto") {
        return $Requested
    }
    if (Get-Command cloudflared.exe -ErrorAction SilentlyContinue) {
        return "cloudflared"
    }
    if (Get-Command ngrok.exe -ErrorAction SilentlyContinue) {
        return "ngrok"
    }
    return "localtunnel"
}

if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}
if (Test-Path $errLogPath) {
    Remove-Item $errLogPath -Force
}

$resolvedProvider = Resolve-Provider -Requested $Provider
if ($resolvedProvider -eq "ngrok") {
    $process = Start-NgrokProcess -Port $Port
} elseif ($resolvedProvider -eq "cloudflared") {
    $process = Start-CloudflaredProcess -Port $Port
} else {
    $process = Start-LocaltunnelProcess -Port $Port -Subdomain $Subdomain
}
Set-Content -Path $pidPath -Value $process.Id -Encoding ascii

$publicUrl = $null
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 1
    if ($resolvedProvider -eq "ngrok") {
        $publicUrl = Get-PublicUrlFromNgrok
    } elseif ($resolvedProvider -eq "cloudflared") {
        $publicUrl = Get-PublicUrlFromCloudflared
    } elseif (Test-Path $logPath) {
        $lines = Get-Content -Path $logPath -ErrorAction SilentlyContinue
        foreach ($line in $lines) {
            if ($line -match "your url is:\s+(https://\S+)") {
                $publicUrl = $Matches[1]
                break
            }
        }
    }
    if ($publicUrl) {
        break
    }
    if ($process.HasExited) {
        break
    }
}

if (-not $publicUrl) {
    Write-Host "Konnte keine Tunnel-URL ermitteln." -ForegroundColor Red
    if (Test-Path $logPath) {
        Get-Content -Path $logPath -Tail 50
    }
    if (Test-Path $errLogPath) {
        Get-Content -Path $errLogPath -Tail 50
    }
    exit 1
}

powershell -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts/render-slack-manifest.ps1") `
    -BaseUrl $publicUrl `
    -AppName $AppName `
    -BotDisplayName $BotDisplayName | Out-Host

Write-Host ""
Write-Host "Localhost-Slack-Setup bereit." -ForegroundColor Green
Write-Host "Provider:" -ForegroundColor Cyan
Write-Host "  $resolvedProvider"
Write-Host ""
Write-Host "Tunnel URL:" -ForegroundColor Cyan
Write-Host "  $publicUrl"
Write-Host ""
Write-Host "Tunnel Prozess:" -ForegroundColor Cyan
Write-Host "  PID $($process.Id)"
Write-Host ""
Write-Host "Zum Stoppen:" -ForegroundColor Yellow
Write-Host "  Stop-Process -Id $($process.Id)"
