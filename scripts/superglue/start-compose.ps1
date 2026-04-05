param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

if (-not $env:SUPERGLUE_DB_PASSWORD) { throw "SUPERGLUE_DB_PASSWORD is required" }
if (-not $env:SUPERGLUE_AUTH_TOKEN) { throw "SUPERGLUE_AUTH_TOKEN is required" }
if (-not $env:SUPERGLUE_OPENAI_API_KEY) { throw "SUPERGLUE_OPENAI_API_KEY is required" }
if (-not $env:SUPERGLUE_MINIO_ROOT_PASSWORD) { throw "SUPERGLUE_MINIO_ROOT_PASSWORD is required" }
if (-not $env:SUPERGLUE_MASTER_ENCRYPTION_KEY) { throw "SUPERGLUE_MASTER_ENCRYPTION_KEY is required" }

docker compose -f docker-compose.integration.yml --profile superglue up -d @ComposeArgs

