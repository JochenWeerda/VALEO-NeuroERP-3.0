param(
  [Parameter(Mandatory = $true)]
  [int]$Port
)

$connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $connections) {
  Write-Output "No listener on port $Port"
  exit 0
}

$pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $pids) {
  try {
    Stop-Process -Id $pid -Force -ErrorAction Stop
    Write-Output "Stopped PID $pid on port $Port"
  } catch {
    Write-Output "Failed to stop PID $pid: $($_.Exception.Message)"
  }
}


