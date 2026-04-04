#!/usr/bin/env bash
set -euo pipefail

tmp_chart_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_chart_dir}"' EXIT

cp -R k8s/helm/valeo-erp/. "${tmp_chart_dir}/"
if command -v helm >/dev/null 2>&1; then
  helm dependency build "${tmp_chart_dir}" >/dev/null
  helm template superglue "${tmp_chart_dir}" \
    --set superglue.enabled=true \
    --set superglue.ingress.enabled=true \
    --set superglue.backup.enabled=true >/tmp/superglue-helm-render.yaml
else
  docker run --rm \
    -v "${tmp_chart_dir}:/chart" \
    -v "/tmp:/tmp" \
    alpine/helm:3.17.2 \
    sh -lc "helm dependency build /chart >/dev/null && helm template superglue /chart --set superglue.enabled=true --set superglue.ingress.enabled=true --set superglue.backup.enabled=true >/tmp/superglue-helm-render.yaml"
fi

test -s /tmp/superglue-helm-render.yaml
echo "helm render ok"
