param(
    [string]$ApiUrl = "http://localhost:3011/v1/health",
    [string]$ToolsUrl = "http://localhost:3011/v1/tools",
    [int]$MaxAttempts = 20,
    [int]$DelaySeconds = 2
)

for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    try {
        Invoke-WebRequest -Uri $ApiUrl -UseBasicParsing | Out-Null
        if ($env:SUPERGLUE_AUTH_TOKEN) {
            Invoke-WebRequest -Uri $ToolsUrl -Headers @{ Authorization = "Bearer $($env:SUPERGLUE_AUTH_TOKEN)" } -UseBasicParsing | Out-Null
        }
        Write-Host "superglue smoke ok"
        exit 0
    } catch {
        if ($attempt -eq $MaxAttempts) {
            throw
        }
        Start-Sleep -Seconds $DelaySeconds
    }
}

