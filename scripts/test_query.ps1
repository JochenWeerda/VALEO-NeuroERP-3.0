Param(
  [string]$BaseUrl = 'http://127.0.0.1:8004',
  [string]$Q = 'LangGraph Workflow',
  [int]$N = 3,
  [string]$PersistDir = 'output/ai-workflow/chroma_store',
  [string]$Collection = 'valero_code'
)

$ErrorActionPreference = 'Stop'

try {
  $url = "$BaseUrl/api/ai-workflow/query?q=$([System.Uri]::EscapeDataString($Q))&n=$N&persist_dir=$([System.Uri]::EscapeDataString($PersistDir))&collection=$([System.Uri]::EscapeDataString($Collection))"
  Write-Output ("QUERY: " + $url)
  $resp = Invoke-WebRequest -Uri $url -UseBasicParsing
  $resp.Content | Out-String
} catch {
  Write-Output $_
  exit 1
}


