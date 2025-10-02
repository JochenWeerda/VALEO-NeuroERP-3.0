param(
  [Parameter(Mandatory=$true)][string]$Component,
  [Parameter(Mandatory=$true)][string]$Action,
  [Parameter(Mandatory=$true)][string]$Status,
  [string]$Notes = ""
)

$ts = [DateTime]::UtcNow.ToString("o")
$entry = @{ ts = $ts; component = $Component; action = $Action; status = $Status; notes = $Notes } | ConvertTo-Json -Compress
$logDir = Join-Path -Path (Resolve-Path ".").Path -ChildPath "logs/ops"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path -Path $logDir -ChildPath "experiment_log.jsonl"
Add-Content -Path $logFile -Value $entry
