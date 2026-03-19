param(
    [Parameter(Mandatory = $true)]
    [string]$BaseUrl,

    [string]$AppName = "VALEO NeuroERP",

    [string]$BotDisplayName = "VALEO NeuroERP",

    [string]$OutputPath = "dist/slack-app-manifest.generated.yaml"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $repoRoot "config/slack/slack-app-manifest.template.yaml"
$targetPath = Join-Path $repoRoot $OutputPath
$requestUrl = ($BaseUrl.TrimEnd("/")) + "/api/v1/channels/slack/events"

if (-not (Test-Path $templatePath)) {
    throw "Template nicht gefunden: $templatePath"
}

$content = Get-Content -Path $templatePath -Raw
$content = $content.Replace("__APP_NAME__", $AppName)
$content = $content.Replace("__BOT_DISPLAY_NAME__", $BotDisplayName)
$content = $content.Replace("__REQUEST_URL__", $requestUrl)

$targetDir = Split-Path -Parent $targetPath
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Set-Content -Path $targetPath -Value $content -Encoding utf8

Write-Host "Slack-Manifest erzeugt:" -ForegroundColor Green
Write-Host "  $targetPath"
Write-Host ""
Write-Host "Request URL:" -ForegroundColor Cyan
Write-Host "  $requestUrl"
Write-Host ""
Write-Host "Naechste Schritte:" -ForegroundColor Yellow
Write-Host "  1. Slack -> api.slack.com/apps -> Create New App -> From an app manifest"
Write-Host "  2. Inhalt aus $targetPath einfuegen"
Write-Host "  3. App installieren"
Write-Host "  4. Signing Secret nach CHANNEL_SLACK_SIGNING_SECRET uebernehmen"
Write-Host "  5. Bot Token nach CHANNEL_SLACK_BOT_TOKEN uebernehmen"
