param(
    [string]$BackupDir = "runtime/superglue-backups"
)

New-Item -ItemType Directory -Force -Path (Join-Path $BackupDir "db") | Out-Null
$target = Join-Path $BackupDir ("db/superglue_{0}.dump" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$dbUser = if ($env:SUPERGLUE_DB_USER) { $env:SUPERGLUE_DB_USER } else { "superglue" }
$dbName = if ($env:SUPERGLUE_DB_NAME) { $env:SUPERGLUE_DB_NAME } else { "superglue" }
docker compose -f docker-compose.integration.yml exec -T superglue-db pg_dump -U $dbUser -d $dbName -Fc > $target
Write-Host "db backup written to $target"
