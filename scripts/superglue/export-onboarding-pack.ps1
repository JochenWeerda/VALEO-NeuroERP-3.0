param(
    [string]$TenantId = "default",
    [ValidateSet("json", "env", "vault")]
    [string]$Format = "json",
    [string]$OutputPath = ""
)

$args = @("scripts/superglue/export-onboarding-pack.py", "--tenant", $TenantId, "--format", $Format)
if ($OutputPath) {
    $args += @("--output", $OutputPath)
}

python @args
