# INT-SG-056 - Superglue CI Smoke

## Ziel

Einen reproduzierbaren Dev-Connector-Smoke fuer CI und Staging bereitstellen.

## Umgesetzt

- `scripts/superglue/ci-smoke.sh` und `.ps1` pruefen Health und Tool-Listing.
- `.github/workflows/superglue-dev-connector-smoke.yml` fuehrt den Smoke per `workflow_dispatch` und Nightly aus.
- Secrets und Zielumgebungen bleiben bewusst extern konfigurierbar.

## Verifikation

- `bash scripts/superglue/ci-smoke.sh` bzw. `powershell -File scripts/superglue/ci-smoke.ps1`

