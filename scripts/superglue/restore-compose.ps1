param(
    [Parameter(Mandatory = $true)]
    [string]$DumpFile
)

$dbUser = if ($env:SUPERGLUE_DB_USER) { $env:SUPERGLUE_DB_USER } else { "superglue" }
$dbName = if ($env:SUPERGLUE_DB_NAME) { $env:SUPERGLUE_DB_NAME } else { "superglue" }
Get-Content -Path $DumpFile -Encoding Byte -ReadCount 0 | docker compose -f docker-compose.integration.yml exec -T superglue-db pg_restore -U $dbUser -d $dbName --clean --if-exists
Write-Host "db restore completed"
