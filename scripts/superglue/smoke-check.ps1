param(
    [string]$ApiUrl = "http://localhost:3010/health"
)

Invoke-WebRequest -Uri $ApiUrl -UseBasicParsing | Out-Null
Write-Host "superglue smoke ok"

