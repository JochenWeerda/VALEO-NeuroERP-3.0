# INT-SG-023 - Superglue K8s Basis

## Ziel

Superglue neben dem Compose-Pfad auch als klaren Kubernetes-Basisstack modellieren.

## Umsetzung

- `k8s/superglue/` mit `kustomization.yaml`
- Namespace, ServiceAccount und ConfigMap
- Services fuer App, Postgres und MinIO
- StatefulSets fuer Postgres und MinIO
- PVC fuer Runtime-Daten
- Deployment fuer Superglue selbst

## Ergebnis

Der Cluster-Pfad ist jetzt als eigenstaendiger, kustomize-faehiger Stack vorhanden und nutzt dieselben `SUPERGLUE_*`-Bezeichner wie der Compose-Pfad.

