# EPCIS Event Pipeline – Auto-Remediation & Eskalation (Inventory)

## 1. Konfiguration

### Helm Values (values-inventory.yaml)
```yaml
inventory:
  enabled: true
  image:
    repository: ghcr.io/valeo-neuroerp/inventory
    tag: latest
  env:
    # Auto-Remediation
    EPCIS_MAX_RETRIES: "3"
    EPCIS_RETRY_BACKOFF_BASE: "2"
    # Eskalation (optional)
    TEAMS_WEBHOOK_URL: "https://outlook.office.com/webhook/..."
    ESCALATION_EMAIL: "compliance-oncall@valeo.com"
  secretRefs: []
```

### Secrets (optional)
```bash
kubectl create secret generic inventory-teams-webhook \
  -n <namespace> \
  --from-literal=url='<TEAMS_WEBHOOK_URL>'
```

## 2. Auto-Remediation Playbooks

### EPCIS Event Processing Failures
- Symptom: `inventory_epcis_event_failures_total` > 0
- Quelle: API `POST /api/v1/inventory/epcis/events` oder Subscriber

Aktionen (automatisiert):
1. NATS Connection Error
   - Retries: max 3 (Backoff: 2s, 4s, 8s)
   - Aktion: NATS-Verbindung neu aufbauen
   - Erfolg: Publish erfolgreich
2. Database Timeout
   - Retries: max 3 (Backoff: 1s, 2s, 4s)
   - Aktion: DB-Connection Pool refreshen
   - Erfolg: Persistenz erfolgreich
3. Validation Error
   - Keine Retries
   - Sofortige Eskalation

### Eskalationsmatrix
| Fehlertyp            | Retries | Auto-Remediation | Eskalation       |
|----------------------|---------|------------------|------------------|
| NATS Error           | 3       | ✓                | Nach 3 Fehlern   |
| DB Timeout           | 3       | ✓                | Nach 3 Fehlern   |
| Validation           | 0       | ✗                | Sofort           |
| Unknown              | 1       | ✗                | Nach 1 Fehler    |

## 3. Teams/E-Mail Eskalation

### Teams Webhook Format (Adaptive Card)
```json
{
  "type": "message",
  "attachments": [{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
      "type": "AdaptiveCard",
      "version": "1.4",
      "body": [
        {"type": "TextBlock", "text": "VALEO Inventory - Auto-Remediation", "weight": "bolder"},
        {"type": "TextBlock", "text": "EPCIS-Event Eskalation: {error}", "wrap": true},
        {"type": "FactSet", "facts": [
          {"title": "event_id", "value": "{event_id}"},
          {"title": "error", "value": "{error}"},
          {"title": "retry_count", "value": "{retry_count}"},
          {"title": "status", "value": "eskalation_erforderlich"}
        ]}
      ]
    }
  }]
}
```

### E-Mail (Fallback)
- Empfänger: `ESCALATION_EMAIL`
- Betreff: `[CRITICAL] EPCIS Event Processing Failure - {event_id}`
- Inhalt: Event-Details, Fehler, Retry-History, nächste Schritte

## 4. Monitoring & Alerts

Prometheus Alerts (Beispiele):
```yaml
- alert: InventoryEpcisEventFailures
  expr: sum(rate(inventory_epcis_event_failures_total[10m])) > 0
  for: 10m
  labels: { severity: critical, component: inventory }
  annotations:
    summary: "EPCIS Event Processing Failures"
    description: "Fehler beim Verarbeiten von EPCIS Events - Auto-Remediation aktiv"

- alert: InventoryEpcisAutoRemediationFailed
  expr: inventory_epcis_event_failures_total > 3
  for: 5m
  labels: { severity: warning, component: inventory }
  annotations:
    summary: "Auto-Remediation für EPCIS Events fehlgeschlagen"
    description: "Maximale Retries erreicht - manuelle Eskalation erforderlich"
```

Metriken:
- `inventory_epcis_events_total`
- `inventory_epcis_event_failures_total`
- `inventory_epcis_event_processing_duration_seconds`
- `inventory_epcis_retry_attempts_total` (optional erweitern)

## 5. Manuelle Intervention (Runbook)

1) Event-Status prüfen (Datenbank):
```bash
kubectl exec -it deploy/valeo-erp-inventory -- \
  psql \"$INVENTORY_DATABASE_URL\" -c \"SELECT COUNT(*), MAX(event_time) FROM inventory_epcis_events;\"
```

2) NATS-Verbindung testen:
```bash
kubectl exec -it deploy/valeo-erp-inventory -- \
  python -c \"import asyncio; from nats.aio.client import Client; \
async def t(): nc=Client(); await nc.connect('nats://nats:4222'); print('NATS OK'); await nc.close(); \
asyncio.run(t())\"
```

3) Force Retry (nur Notfall):
```bash
curl -X POST http://inventory-service:5400/api/v1/inventory/epcis/events \
  -H \"Content-Type: application/json\" \
  -d '{\"event_type\":\"ObjectEvent\",\"biz_step\":\"receiving\",\"epc_list\":[\"urn:epc:id:sgtin:test.001.1\"]}'
```

## 6. Rollback

1) Auto-Remediation deaktivieren
```yaml
env:
  EPCIS_MAX_RETRIES: \"0\"
```

2) Event-Publishing pausieren
```yaml
env:
  EVENT_BUS_ENABLED: \"false\"
```

3) Manuelle Verarbeitung
- Events zwischenpuffern und nach Problembehebung batchweise verarbeiten
*** End Patch***}>>();

