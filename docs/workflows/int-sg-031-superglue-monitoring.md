# INT-SG-031 - Superglue Monitoring

## Ziel

Superglue an die bestehende Prometheus- und Alerting-Struktur anbinden.

## Umsetzung

- `ServiceMonitor` fuer den K8s-Pfad
- Helm-Template fuer `ServiceMonitor`
- neue Superglue-Alertregeln in `prometheus-alerts.yaml`

## Ergebnis

Health-, Sync- und Quarantaene-Signale sind jetzt als explizite Ops-Metriken und Alerts modelliert.

