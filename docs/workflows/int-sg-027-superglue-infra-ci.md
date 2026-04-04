# INT-SG-027 - Superglue Infra CI

## Ziel

Infra-Renderpfade fuer Superglue automatisiert pruefen.

## Umsetzung

- GitHub-Workflow `.github/workflows/superglue-infra.yml`
- Compose-Render fuer Basis und Edge-Overlay
- `kubectl kustomize` + Client-Dry-Run
- Helm-Render ueber `scripts/superglue/render-helm.sh`

## Ergebnis

Compose-, Kustomize- und Helm-Drift fuer den Superglue-Stack werden jetzt in einer eigenen CI-Lane geprueft.

