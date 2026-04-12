param(
    [string]$ContainerName = "valeo-first-install-smoke",
    [int]$HostPort = 55432
)

$ErrorActionPreference = "Stop"

try {
    docker rm -f $ContainerName 2>$null | Out-Null
} catch {
}

docker run --name $ContainerName `
    -e POSTGRES_PASSWORD=postgres `
    -e POSTGRES_USER=postgres `
    -e POSTGRES_DB=valeo_test `
    -p "${HostPort}:5432" `
    -d postgres:15 | Out-Null

try {
    function Invoke-Step([string]$Command, [string]$Label) {
        Write-Host $Label
        Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0) {
            throw "$Label failed with exit code $LASTEXITCODE"
        }
    }

    for ($i = 0; $i -lt 40; $i++) {
        docker exec $ContainerName pg_isready -U postgres -d valeo_test *> $null
        if ($LASTEXITCODE -eq 0) {
            break
        }
        Start-Sleep -Seconds 2
    }

    $env:DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:${HostPort}/valeo_test"
    Invoke-Step "python scripts/init_db.py" "Running init_db.py"
    Invoke-Step "python scripts/check_required_domain_schemas.py" "Checking required domain schemas"
    Invoke-Step "python scripts/check_domain_table_ownership.py" "Checking domain table ownership"
    Write-Host "First-install smoke passed." -ForegroundColor Green
}
finally {
    docker rm -f $ContainerName 2>$null | Out-Null
}
