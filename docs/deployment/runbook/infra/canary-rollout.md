# Canary-Rollout Leitfaden (Staging → Prod 10% → 100%)

## Voraussetzungen
- Staging erfolgreich (Smoke-Tests grün)
- Monitoring aktiv (Prometheus/Alertmanager)

## 1. Canary aktivieren (10%)

### Istio VirtualService (Beispiel)
```yaml
http:
  - match:
      - uri:
          prefix: /api/v1
    route:
      - destination:
          host: inventory-service
          port:
            number: 5400
        weight: 90
      - destination:
          host: inventory-service-canary
          port:
            number: 5400
        weight: 10
```

Apply:
```bash
kubectl -n production apply -f k8s/istio/virtual-service.yaml
```

## 2. Beobachten (15–30 Minuten)
- Fehler-Rate: `sum(rate(inventory_epcis_event_failures_total[10m]))`
- Latenz: `histogram_quantile(0.95, rate(inventory_epcis_event_processing_seconds_bucket[5m]))`
- Business-Health: EPCIS Events Rate `sum(rate(inventory_epcis_events_total[10m]))`

## 3. Erhöhen auf 50%
Passen Sie `weight` 50/50 an, erneut beobachten.

## 4. Erhöhen auf 100%
Wenn Metriken grün: 100% auf neues Ziel, altes Ziel entfernen.

## 5. Rollback
- Bei Problemen Gewichte sofort zurücksetzen (90/10 auf alt), Incident eröffnen.

## 6. Automatisierung (optional)
- GitOps: Gewichte in kustomize/values, PR-gesteuert.
- Alerts binden Eskalation (Teams/E-Mail) an Rollout-Phasen.


