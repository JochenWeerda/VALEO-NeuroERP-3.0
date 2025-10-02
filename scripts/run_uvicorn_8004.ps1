Param(
  [string]$Port = '8004'
)

$ErrorActionPreference = 'Stop'

try {
  if (-not (Test-Path 'logs')) { New-Item -ItemType Directory -Path 'logs' | Out-Null }
} catch {}

$env:PYTHONPATH = (Get-Location).Path
$env:USE_CHROMA = '0'

python -m uvicorn backend.main:app --host 0.0.0.0 --port $Port --reload --log-level debug


