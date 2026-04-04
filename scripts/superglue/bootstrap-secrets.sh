#!/usr/bin/env bash
set -euo pipefail

: "${SUPERGLUE_NAMESPACE:=valeo-integrations}"
: "${SUPERGLUE_SECRET_STORE_KIND:=ClusterSecretStore}"
: "${SUPERGLUE_SECRET_STORE_NAME:=valeo-vault}"
: "${SUPERGLUE_VAULT_PREFIX:=secret/data/valeo/superglue}"

cat <<EOF
Superglue bootstrap mapping
namespace=${SUPERGLUE_NAMESPACE}
secretStoreRef.kind=${SUPERGLUE_SECRET_STORE_KIND}
secretStoreRef.name=${SUPERGLUE_SECRET_STORE_NAME}
app=${SUPERGLUE_VAULT_PREFIX}/app
db=${SUPERGLUE_VAULT_PREFIX}/db
minio=${SUPERGLUE_VAULT_PREFIX}/minio
hosts.api=${SUPERGLUE_HOST_API:-superglue.example.test}
hosts.minio=${SUPERGLUE_HOST_MINIO:-superglue-minio.example.test}
EOF

