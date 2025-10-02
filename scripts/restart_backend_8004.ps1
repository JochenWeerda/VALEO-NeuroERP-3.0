$port = 8004
try {
  $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
  }
} catch {}

try {
  $python = Join-Path $PSScriptRoot '..' | Resolve-Path | ForEach-Object { Join-Path $_ 'venv\Scripts\python.exe' }
  if (-not (Test-Path $python)) { $python = 'python' }
  Start-Job -Name uv8004 -ScriptBlock { param($py)
    & $py -m uvicorn backend.main:app --host 0.0.0.0 --port 8004
  } -ArgumentList $python | Out-Null
  Start-Sleep -Seconds 3
  $health = (Invoke-WebRequest -Uri 'http://127.0.0.1:8004/health' -UseBasicParsing).Content
  Write-Output $health
  $openapi = (Invoke-WebRequest -Uri 'http://127.0.0.1:8004/openapi.json' -UseBasicParsing).Content
  $openapi | Out-File -FilePath (Join-Path $PSScriptRoot '..\.openapi_after_restart_8004.json') -Encoding utf8
  if ($openapi -match '/api/ai-workflow/query') { Write-Output 'QUERY_ROUTE=present' } else { Write-Output 'QUERY_ROUTE=absent' }
}
catch {
  Write-Output $_
  exit 1
}


