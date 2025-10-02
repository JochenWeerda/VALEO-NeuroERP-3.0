param(
  [switch]$NoCacheClear
)

$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $true

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red }

# Repo-Root ermitteln
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $RepoRoot
Write-Info "RepoRoot: $RepoRoot"

# Virtuelle Umgebung aktivieren (optional, wenn vorhanden)
$venvActivate = Join-Path $RepoRoot 'venv\Scripts\Activate.ps1'
if (Test-Path $venvActivate) {
  Write-Info "Aktiviere venv"
  . $venvActivate
} else {
  Write-Warn "Keine venv gefunden unter $venvActivate (fahre ohne fort)"
}

# PYTHONPATH setzen für diesen Prozess und Child-Prozesse
$env:PYTHONPATH = "$RepoRoot"
Write-Info "PYTHONPATH: $env:PYTHONPATH"

# Frontend API-Basis setzen
$FrontendDir = Join-Path $RepoRoot 'frontend'
$EnvLocal = Join-Path $FrontendDir '.env.local'
$apiLine = 'VITE_API_BASE=http://127.0.0.1:8001/api'
if (Test-Path $EnvLocal) {
  $content = Get-Content $EnvLocal -Raw
  if ($content -match '^VITE_API_BASE=') {
    $new = ($content -replace '^VITE_API_BASE=.*', $apiLine)
    if ($new -ne $content) {
      $new | Set-Content -NoNewline $EnvLocal -Encoding UTF8
      Write-Ok "VITE_API_BASE aktualisiert in .env.local"
    } else {
      Write-Info ".env.local bereits korrekt"
    }
  } else {
    Add-Content -Path $EnvLocal -Value ("`n" + $apiLine)
    Write-Ok "VITE_API_BASE an .env.local angehängt"
  }
} else {
  $apiLine | Set-Content $EnvLocal -Encoding UTF8
  Write-Ok ".env.local erstellt mit VITE_API_BASE"
}

# Alte Prozesse ggf. beenden
Write-Info "Beende alte node/uvicorn Prozesse (falls vorhanden)"
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name uvicorn,python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*uvicorn*' -or $_.StartInfo -ne $null } | Stop-Process -Force -ErrorAction SilentlyContinue

# Vite-Caches leeren (optional)
if (-not $NoCacheClear) {
  Write-Info "Leere Vite-Caches"
  $viteA = Join-Path $FrontendDir '.vite'
  $viteB = Join-Path $FrontendDir 'node_modules\.vite'
  foreach ($p in @($viteA, $viteB)) {
    if (Test-Path $p) {
      try { Remove-Item -Recurse -Force $p; Write-Ok "Gelöscht: $p" } catch { Write-Warn "Konnte $p nicht löschen: $_" }
    }
  }
} else {
  Write-Info "Vite-Caches werden behalten (NoCacheClear)"
}

# Backend starten (Uvicorn 127.0.0.1:8001)
Write-Info "Starte Backend (Uvicorn) auf 127.0.0.1:8001"
$backendCmd = "python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --app-dir `"$RepoRoot`""
$backend = Start-Process -PassThru -WindowStyle Minimized powershell -ArgumentList @('-NoProfile','-Command',"cd `"$RepoRoot`"; `$env:PYTHONPATH=`"$RepoRoot`"; $backendCmd")
Write-Ok "Backend PID: $($backend.Id)"

# Frontend starten (Vite auf 3004)
Write-Info "Starte Frontend (Vite) auf Port 3004"
$frontendCmd = "npm run dev -- --port 3004"
$frontend = Start-Process -PassThru -WorkingDirectory $FrontendDir -WindowStyle Minimized powershell -ArgumentList @('-NoProfile','-Command',$frontendCmd)
Write-Ok "Frontend PID: $($frontend.Id)"

function Wait-Http($url, $timeoutSec = 60) {
  $stopAt = (Get-Date).AddSeconds($timeoutSec)
  while ((Get-Date) -lt $stopAt) {
    try {
      $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
        return $true
      }
    } catch { }
    Start-Sleep -Seconds 1
  }
  return $false
}

# Health-Checks
if (Wait-Http 'http://127.0.0.1:8001/openapi.json' 60) {
  Write-Ok "Backend erreichbar: http://127.0.0.1:8001"
} else {
  Write-Err "Backend nicht erreichbar (Timeout)"
}

# Vite-Standardport 3004 checken (optional)
if (Wait-Http 'http://localhost:3004' 60) {
  Write-Ok "Frontend erreichbar: http://localhost:3004"
  try { Start-Process 'http://localhost:3004' | Out-Null } catch { }
} else {
  Write-Warn "Frontend auf 3004 nicht erreichbar (ggf. anderer Port). Bitte Konsole prüfen."
}

Write-Ok "Start abgeschlossen. Logs laufen in den minimierten Fenstern."
