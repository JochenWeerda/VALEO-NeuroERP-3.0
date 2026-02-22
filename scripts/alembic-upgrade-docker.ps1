param(
    [string]$BackendContainer = "valeo-neuro-erp-backend",
    [string]$Workdir = "/app"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking backend container '$BackendContainer'..." -ForegroundColor Cyan
$running = docker ps --filter "name=^${BackendContainer}$" --format "{{.Names}}"
if (-not $running) {
    Write-Host "Container '$BackendContainer' is not running." -ForegroundColor Red
    Write-Host "Start stack first: docker compose up -d backend postgres" -ForegroundColor Yellow
    exit 1
}

Write-Host "Running Alembic inside Docker container..." -ForegroundColor Cyan
docker exec $BackendContainer sh -lc "cd $Workdir && alembic current"
docker exec $BackendContainer sh -lc "cd $Workdir && alembic heads"
docker exec $BackendContainer sh -lc "cd $Workdir && alembic upgrade head"
docker exec $BackendContainer sh -lc "cd $Workdir && alembic current"

Write-Host "Alembic upgrade in Docker finished." -ForegroundColor Green
