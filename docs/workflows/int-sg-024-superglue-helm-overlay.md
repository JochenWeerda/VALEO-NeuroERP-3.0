# INT-SG-024 - Superglue Helm Overlay

## Ziel

Superglue als optionale Komponente im bestehenden `valeo-erp`-Chart renderbar machen.

## Umsetzung

- `superglue:`-Block in `k8s/helm/valeo-erp/values.yaml`
- Templates fuer ServiceAccount, ConfigMap, Services, StatefulSets, PVC und Deployment
- Nutzung der bestehenden Chart-Labels und Secret-Patterns

## Ergebnis

Superglue kann jetzt ohne zweiten Chart ueber Helm mit denselben Release-/Label-Konventionen wie der Rest der Plattform ausgerollt werden.

