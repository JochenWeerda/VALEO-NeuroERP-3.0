param(
  [switch]$UseCache,
  [switch]$Prune
)

$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $true

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red }

# Repo-Root setzen
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $RepoRoot
Write-Info "RepoRoot: $RepoRoot"

# Optional: requirements.txt erzeugen aus venv
$venvActivate = Join-Path $RepoRoot 'venv\Scripts\Activate.ps1'
$reqPath = Join-Path $RepoRoot 'backend\requirements.txt'
if (Test-Path $venvActivate) {
  try {
    Write-Info 'Aktiviere venv und erzeuge backend/requirements.txt aus pip freeze'
    . $venvActivate
    $freeze = & python -m pip freeze 2>$null
    if ($LASTEXITCODE -eq 0 -and $freeze) {
      $freeze | Out-File -FilePath $reqPath -Encoding ascii -Force
      Write-Ok "requirements.txt aktualisiert: $reqPath"
    } else {
      Write-Warn 'pip freeze lieferte kein Ergebnis; requirements.txt wird nicht überschrieben'
    }
  } catch {
    Write-Warn "Konnte venv/pip freeze nicht ausführen: $_"
  }
} else {
  if (-not (Test-Path $reqPath)) {
    Write-Warn 'Keine venv gefunden und backend/requirements.txt fehlt. Der Backend-Build kann fehlschlagen.'
  } else {
    Write-Info 'Verwende bestehende backend/requirements.txt'
  }
}

# Optional: Builder-Cache leeren
if ($Prune) {
  Write-Info 'Leere Docker Builder Cache (docker builder prune -af)'
  try { docker builder prune -af } catch { Write-Warn $_ }
}

# Docker Compose Down und Konflikt-Container räumen
Write-Info 'Stoppe und entferne bestehende Compose-Services (inkl. Volumes)'
try { docker compose down -v } catch { Write-Warn $_ }
foreach ($c in @('valeo-neuroerp-backend','valeo-neuroerp-frontend','valeo-neuroerp-postgres','valeo-neuroerp-redis','valeo-neuroerp-nginx','valeo-neuroerp-prometheus','valeo-neuroerp-grafana')) {
  try { docker rm -f $c 2>$null | Out-Null } catch { }
}

# Build
if ($UseCache) {
  Write-Info 'Baue Docker-Images (mit Cache)'
  docker compose build
} else {
  Write-Info 'Baue Docker-Images (ohne Cache)'
  docker compose build --no-cache
}
if ($LASTEXITCODE -ne 0) {
  Write-Warn 'Build fehlgeschlagen – versuche Frontend einzeln mit Prune'
  try {
    docker builder prune -af
    docker compose build --no-cache frontend
    docker compose build --no-cache backend
  } catch {
    Write-Err 'Erneuter Build fehlgeschlagen'; exit 1
  }
}

# Up
Write-Info 'Starte Services im Hintergrund'
 docker compose up -d
if ($LASTEXITCODE -ne 0) { Write-Err 'docker compose up -d fehlgeschlagen'; exit 1 }

# Übersicht
Write-Info 'Laufende Container:'
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health Checks
function Wait-Http($url, $timeoutSec = 60) {
  $stopAt = (Get-Date).AddSeconds($timeoutSec)
  while ((Get-Date) -lt $stopAt) {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5
      if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { return $true }
    } catch { }
    Start-Sleep -Seconds 2
  }
  return $false
}

if (Wait-Http 'http://localhost:8000/health' 60) {
  Write-Ok 'Backend erreichbar: http://localhost:8000'
} else {
  Write-Warn 'Backend Health nicht erreichbar (http://localhost:8000/health)'
}

if (Wait-Http 'http://localhost:3000' 60) {
  Write-Ok 'Frontend erreichbar: http://localhost:3000'
} else {
  Write-Warn 'Frontend (3000) nicht erreichbar; prüfe Container-Logs'
}

Write-Ok 'Rebuild/Restart abgeschlossen.'
