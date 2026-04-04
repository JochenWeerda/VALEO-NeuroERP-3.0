# INT-SG-028 - Superglue Ops Runbook

## Ziel

Den Superglue-Stack mit kleinen, wiederholbaren Skripten betreibbar machen.

## Umsetzung

- `scripts/superglue/start-compose.*`
- `scripts/superglue/deploy-k8s.*`
- `scripts/superglue/render-helm.*`
- `scripts/superglue/smoke-check.*`
- `scripts/superglue/backup-compose.*`
- `scripts/superglue/restore-compose.*`

## Ergebnis

Compose-Start, Helm-Render, K8s-Deploy, Smoke und lokale Backup-/Restore-Schritte sind jetzt ueber denselben Script-Satz dokumentiert und ausfuehrbar.

