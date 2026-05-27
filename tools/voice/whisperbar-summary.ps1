#Requires -Version 5.1
<#
.SYNOPSIS
  WhisperBar Summary — Clipboard to Ollama summary via ki-usability-api.
.DESCRIPTION
  Strg+Shift+2 companion script for tools/voice/whisperbar.ahk
  Env: KI_USABILITY_URL (default http://localhost:5200)
#>
param(
    [string]$ApiBase = $(if ($env:KI_USABILITY_URL) { $env:KI_USABILITY_URL } else { "http://localhost:5200" })
)

$ErrorActionPreference = "Stop"

$text = Get-Clipboard -Raw
if ([string]::IsNullOrWhiteSpace($text)) {
    Write-Error "Zwischenablage ist leer."
    exit 1
}

$body = @{
    mode = "summary"
    text = $text.Trim()
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "$ApiBase/api/v1/voice/pipeline" -Method POST -Body $body -ContentType "application/json; charset=utf-8"
} catch {
    Write-Error "ki-usability-api nicht erreichbar unter $ApiBase — $_"
    exit 2
}

$summary = $response.summary_text
if ([string]::IsNullOrWhiteSpace($summary)) {
    Write-Error "Keine Zusammenfassung erhalten."
    exit 3
}

Set-Clipboard -Value $summary
$seconds = if ($response.estimated_seconds) { $response.estimated_seconds } else { "?" }
Write-Host "Zusammenfassung (~${seconds}s) in Zwischenablage kopiert."
Write-Host $summary
