# INT-SG-029 - Superglue ArgoCD

## Ziel

Superglue in den bestehenden GitOps-Pfad aufnehmen.

## Umsetzung

- neue ArgoCD-Application unter `k8s/argocd/apps/superglue-platform.yaml`
- `apps/kustomization.yaml` erweitert
- Helm-Parameter aktivieren Superglue-, Secret-, Certificate-, Monitoring- und Dashboard-Pfade

## Ergebnis

Superglue ist jetzt nicht nur manuell deploybar, sondern als eigene GitOps-Anwendung modelliert.

