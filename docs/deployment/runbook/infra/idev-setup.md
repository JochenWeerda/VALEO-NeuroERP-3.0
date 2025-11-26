# InfraStat IDEV Produktiv-Setup

## 1. Secrets erstellen
```bash
kubectl create secret generic infrastat-idev \
  --from-literal=username='<IDEV_USER>' \
  --from-literal=password='<IDEV_PASS>' \
  --from-file=clientCert=path/to/cert.pem \
  --from-file=clientKey=path/to/key.pem \
  -n <namespace>
```

## 2. Helm Overrides anwenden
- `docs/deployment/helm/infra/values-infrastat.yaml` anpassen (Image-Tag, Retry-Parameter).
```bash
helm upgrade --install valeo-erp ./k8s/helm/valeo-erp \
  -n <namespace> \
  -f docs/deployment/helm/infra/values-infrastat.yaml \
  --set infrastat.image.tag=<release-tag> \
  --set alerts.infrastatEnabled=true
```

## 3. Workflow-Definition finalisieren
- Stelle sicher, dass alle Events (`intrastat.validation.*`, `intrastat.submission.*`) im Workflow-Service definiert sind.
- Optional: Workflow-Definition in `services/compliance/infrastat/app/workflow/registration.py` ausrollen (`helm upgrade` löst Registrierung beim Start aus).

## 4. Alerts/Monitoring
- Prometheus-ConfigMap (`prometheus-alerts.yaml`) aktivieren (`alerts.infrastatEnabled=true`).
- Alertmanager-Routing für `component=infrastat` konfigurieren.
- Smoke-Test: `kubectl port-forward svc/valeo-erp-infrastat 5200` → `curl /metrics` und Alerts mithilfe von `promtool test rules`. 

## 5. Smoke-Test (IDEV)
1. Port-Forward:
   ```bash
   kubectl -n <namespace> port-forward svc/valeo-app-infrastat 5200:5200
   ```
2. Batch anlegen & validieren:
   ```bash
   curl -X POST http://localhost:5200/api/v1/ingestion/batch -H "Content-Type: application/json" -d @sample_batch.json
   curl -X POST http://localhost:5200/api/v1/batches/<BATCH_ID>/validate
   ```
3. Submission simulieren:
   ```bash
   curl -X POST http://localhost:5200/api/v1/batches/<BATCH_ID>/submit
   ```
4. IDEV-Server prüfen (`Upload-Log` sollte neuen Datensatz zeigen).

## 6. Prometheus/Alertmanager Smoke-Test
- `kubectl port-forward svc/prometheus 9090` und Query `infrastat_submission_failure_ratio`.
- `promtool test rules prometheus-alerts.yaml`.
- Alertmanager-Routing prüfen (`component=infrastat` -> Compliance OnCall).