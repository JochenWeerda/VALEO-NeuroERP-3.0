Param(
  [string]$BaseUrl = "http://127.0.0.1:8002",
  [string]$RepoRoot = (Get-Location).Path,
  [string]$ApiToken = "dev",
  [int]$PollSeconds = 2,
  [int]$MaxPolls = 180
)

$ErrorActionPreference = "Stop"

try {
  $encodedRepo = [System.Uri]::EscapeDataString($RepoRoot)
  $startUrl = "$BaseUrl/api/ai-workflow/start?repo_root=$encodedRepo&api_token=$ApiToken"
  Write-Output ("STARTE: " + $startUrl)

  $resp = Invoke-WebRequest -Uri $startUrl -UseBasicParsing -Method POST
  $job = $resp.Content | ConvertFrom-Json
  $job_id = $job.job_id

  if (-not $job_id) {
    Write-Error "Keine job_id erhalten"
    exit 1
  }

  Write-Output ("JOB_ID=" + $job_id)

  for ($i = 0; $i -lt $MaxPolls; $i++) {
    Start-Sleep -Seconds $PollSeconds
    try {
      $statusUrl = "$BaseUrl/api/ai-workflow/status/$job_id"
      $s = Invoke-WebRequest -Uri $statusUrl -UseBasicParsing -Method GET
      $js = $s.Content | ConvertFrom-Json
      $st = $js.status
      Write-Output ("STATUS=" + $st)
      if ($st -in @("done", "completed", "failed", "error")) {
        $js | ConvertTo-Json -Depth 8
        break
      }
    } catch {
      Write-Output "Status fetch failed"
    }
  }
}
catch {
  Write-Output $_
  exit 1
}


