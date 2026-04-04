param(
    [string]$Namespace = $(if ($env:SUPERGLUE_NAMESPACE) { $env:SUPERGLUE_NAMESPACE } else { "valeo-integrations" }),
    [string]$SecretStoreKind = $(if ($env:SUPERGLUE_SECRET_STORE_KIND) { $env:SUPERGLUE_SECRET_STORE_KIND } else { "ClusterSecretStore" }),
    [string]$SecretStoreName = $(if ($env:SUPERGLUE_SECRET_STORE_NAME) { $env:SUPERGLUE_SECRET_STORE_NAME } else { "valeo-vault" }),
    [string]$VaultPrefix = $(if ($env:SUPERGLUE_VAULT_PREFIX) { $env:SUPERGLUE_VAULT_PREFIX } else { "secret/data/valeo/superglue" })
)

@"
Superglue bootstrap mapping
namespace=$Namespace
secretStoreRef.kind=$SecretStoreKind
secretStoreRef.name=$SecretStoreName
app=$VaultPrefix/app
db=$VaultPrefix/db
minio=$VaultPrefix/minio
hosts.api=$(if ($env:SUPERGLUE_HOST_API) { $env:SUPERGLUE_HOST_API } else { "superglue.example.test" })
hosts.minio=$(if ($env:SUPERGLUE_HOST_MINIO) { $env:SUPERGLUE_HOST_MINIO } else { "superglue-minio.example.test" })
"@
