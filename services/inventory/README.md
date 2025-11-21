# Inventory Service

Mehrlager- und Chargenverwaltung als eigenständiger FastAPI-Microservice.

## Features
- Verwaltung von Lagerhäusern, Lagerorten & Artikeln
- Chargen/Lot-Verwaltung (SKU + Lot-Nummer) inkl. Traceability
- Wareneingänge, Umlagerungen, Auslagerungen & Korrekturen
- Reporting-API für Dashboard/Stock-Alerts/Replenishment
- Frontend-Hooks (`/api/v1/inventory/articles`, `/stock-movements`, `/reports/*`)
- Event-Publishing **und** Subscription auf bestehende Domain-Events (`purchase.receipt.posted`, `sales.shipment.confirmed`)
- Workflow-Registrierung (`inventory_inbound_flow`) + Weiterleitung sämtlicher Events an den Workflow-Service
- EPCIS-Persistenz (Object/Aggregation/Transformation/Transaction) inkl. REST-API, NATS-Publish und Prometheus-Metriken

## Lokal starten
```bash
uvicorn main:app --reload --port 5400
```

## Konfiguration
### Betriebsprofile
| Variable | Werte | Wirkung |
| --- | --- | --- |
| `INVENTORY_GLOBAL_OPERATION_MODE` | `test` (Default) \| `real` | Legt den Standardmodus für alle Module fest. `real` aktiviert automatisch produktive Integrationen (z. B. EventBus). |
| `INVENTORY_MODULE_MODE_OVERRIDES` | Komma-separierte Liste (`event_bus=real,database=test`) | Überschreibt den Modus einzelner Module. Derzeit wird `event_bus` ausgewertet; weitere Module können sukzessive angebunden werden. |

Die aktiven Werte können zur Laufzeit über `settings.get_module_mode("<modul>")` bzw. `settings.is_real_mode("<modul>")` abgefragt werden.

### Beispielprofile
- Testbetrieb (lokal, ohne NATS/Produktivabhängigkeiten): `env/test.env.example` kopieren und als `.env` im Service-Verzeichnis ablegen.
- Produktivbetrieb (mit NATS & Postgres): `env/production.env.example` nutzen und Secrets ergänzen. EventBus wird automatisch aktiv.
- Selektive Umschaltung: z. B. global `test`, aber `INVENTORY_MODULE_MODE_OVERRIDES=event_bus=real`, falls nur Event-Publishing echt laufen soll.

## Tests
```bash
pytest services/inventory/tests
```

## Migrationen (Alembic)

- Konfiguration: `services/inventory/alembic.ini`
- DB-URL via `INVENTORY_DATABASE_URL`

Migration ausführen:
```bash
alembic -c services/inventory/alembic.ini upgrade head
```

Neue Migration erzeugen:
```bash
alembic -c services/inventory/alembic.ini revision --autogenerate -m "epcis indices"
```

## EPCIS – API & Betriebsleitfaden

- Basis-URL: `/api/v1/inventory/epcis`
- Mandant: per Header `X-Tenant-Id` (Fallback: `default`)
- Idempotenz: `idempotency_key` im Request (optional). Falls nicht gesetzt, wird ein stabiler Hash aus Eventdaten erzeugt. Server speichert einen eindeutigen `event_key` und gibt bei Duplikaten das bestehende Event zurück.
- Rate-Limit: globaler Token-Bucket (konfigurierbar über `RATE_LIMIT_PER_MINUTE`)
- Circuit Breaker: für NATS-Publish (`NATS_FAILURE_THRESHOLD`, `NATS_CIRCUIT_BREAKER_OPEN_SECONDS`)

### Endpunkte
- `POST /api/v1/inventory/epcis/events`
  - Request-Body:
    ```json
    {
      "event_type": "ObjectEvent|AggregationEvent|TransformationEvent|TransactionEvent",
      "event_time": "ISO-8601 optional",
      "biz_step": "optional",
      "read_point": "optional",
      "lot_id": "UUID optional",
      "sku": "optional",
      "quantity": 10.0,
      "extensions": { "foo": "bar" },
      "idempotency_key": "optional"
    }
    ```
  - Header: `X-Tenant-Id: <tenant>`
  - Antwort: `EpcisEventRead` (inkl. `tenant_id`, `created_at`)
- `GET /api/v1/inventory/epcis/events?limit=200`
  - Header: `X-Tenant-Id: <tenant>`
  - Antwort: `{ "items": EpcisEventRead[], "total": number }` – nur Events des Tenants
- `POST /api/v1/inventory/epcis/maintenance/retention`
  - Erzwingt Aufbewahrung (Löschen älterer Events) und Pseudonymisierung sensibler Extension-Felder gem. Einstellungen
  - Header: `X-Tenant-Id: <tenant>`
  - Antwort: `{ "deleted": number, "anonymized": number }`

### Einstellungen (Auszug)
- `EPCIS_RETENTION_DAYS` (Standard 365)
- `EPCIS_ANONYMIZE_KEYS` (Default: `["userName","email","phone","address","personalId"]`)
- `RATE_LIMIT_PER_MINUTE` (z. B. 600)
- `NATS_FAILURE_THRESHOLD`, `NATS_CIRCUIT_BREAKER_OPEN_SECONDS`
- `TEAMS_WEBHOOK_URL`, `ESCALATION_EMAIL` (für Eskalation)

### Auto-Remediation & Eskalation
- Automatischer Retry (exponentielles Backoff) für NATS/DB-Fehler bis zur definierten Grenze
- Bei Erreichen der Grenze: Teams/E-Mail Eskalation inkl. Eventdetails
- Details und Playbooks: `docs/deployment/runbook/inventory/epcis-auto-remediation.md`

### Frontend (EPCIS-Ansicht)
- Seite: `packages/frontend-web/src/pages/inventory/epcis/index.tsx`
- Funktionen:
  - Tabelle mit Filtern (`biz_step`, `sku`)
  - KPIs: Gesamtanzahl, Top-`biz_step`
  - Tenant-Feld (`X-Tenant-Id`) und Limit-Auswahl
- API-Client: `packages/frontend-web/src/lib/services/inventory-service.ts`

## API-Überblick

| Endpoint | Beschreibung |
| --- | --- |
| `GET /api/v1/inventory/articles` | Aggregierte Artikelübersicht für das Frontend |
| `GET /api/v1/inventory/stock-movements` | Letzte Bewegungen (Belege) |
| `POST /api/v1/inventory/stock-movements` | Generischer Bewegungs-Endpunkt (`in`, `out`, `transfer`, `adjustment`) |
| `GET /api/v1/inventory/reports/stock-levels` | KPI-Feed für Dashboard |
| `GET /api/v1/inventory/reports/stock-alerts` | Low-Stock-Warnungen |
| `GET /api/v1/inventory/warehouses/{id}` / `PUT` / `DELETE` | CRUD für Lagerhäuser inkl. `is_active` |
| Bestehende Endpoints | `/receipts`, `/transfers`, `/lots`, `/lots/{id}` |
| `POST /api/v1/inventory/epcis/events` | EPCIS-Event erfassen (Body: `event_type`, `biz_step`, `read_point`, `sku`, `quantity`, optional `lot_id`, `extensions`) |
| `GET /api/v1/inventory/epcis/events` | Letzte EPCIS-Events (max. 200) |

## Domain-Events

### Publizierte Events
- `inventory.warehouse.created`
- `inventory.location.created`
- `inventory.goods.received`
- `inventory.stock.transferred`
- `inventory.stock.issued`
- `inventory.stock.adjusted`
- `inventory.lot.trace.requested`

Payload (vereinfacht):

```json
{
  "eventId": "uuid",
  "eventType": "inventory.goods.received",
  "aggregateId": "stock-item-uuid",
  "aggregateType": "inventory.stock_item",
  "eventVersion": 1,
  "occurredOn": "2025-11-14T08:00:00Z",
  "tenantId": "default",
  "data": {
    "stockItemId": "...",
    "warehouseId": "...",
    "quantity": 10,
    "sku": "SKU-1"
  }
}
```

### Konsumierte Events
- `purchase.receipt.posted` → erzeugt automatisch Wareneingänge
- `sales.shipment.confirmed` → löst Auslagerung / Bestandsreduzierung aus

Subscriptions laufen über `InventoryEventSubscribers` (NATS). Falls `INVENTORY_EVENT_BUS_ENABLED` deaktiviert ist, werden weder Events publiziert noch konsumiert.

## Workflow-Integration

Beim Service-Start wird automatisch die Definition `inventory_inbound_flow` im Workflow-Service registriert. Dabei werden folgende Events gemappt:

| Workflow-Zustand | Event |
| --- | --- |
| receiving → stored | `inventory.goods.received` |
| stored → allocated | `inventory.stock.reserved` (zukünftig) |
| allocated → shipped | `inventory.stock.issued` |
| * → exception | `inventory.receiving.mismatch` |

## Frontend-Kompatibilität

- React Query Hooks (`packages/frontend-web/src/lib/api/inventory.ts`) greifen nun auf die neuen REST-Routen zu (inkl. Filterparametern `is_active`).
- `StockManagement` nutzt `/articles` & `/stock-movements` direkt.
- Dashboard-/Berichtsseiten konsumieren `/reports/*`.
- Die Chargen-Rückverfolgung (`pages/charge/rueckverfolgung.tsx`) ruft `GET /api/v1/inventory/lots/{id}` mittels `useLotTrace` auf.

## Monitoring & Alerts

- Prometheus-Metriken:
  - `inventory_epcis_events_total{type,biz_step}`
  - `inventory_epcis_event_failures_total`
- Alerts (Helm `prometheus-alerts.yaml`):
  - `InventoryEpcisEventFailures` (Fehler > 0 in 10m)
  - `InventoryEpcisNoEvents` (keine Events in 30m über 1h)

## Runbook – EPCIS Smoke-Test

1) Lokaler Start:
```bash
uvicorn services.inventory.main:app --reload --port 5400
```
2) Event anlegen:
```bash
curl -X POST http://localhost:5400/api/v1/inventory/epcis/events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"ObjectEvent","biz_step":"receiving","read_point":"WH1/DOCK-1","sku":"SKU-TEST","quantity":5,"extensions":{"poNumber":"PO-123"}}'
```
3) Listing prüfen:
```bash
curl http://localhost:5400/api/v1/inventory/epcis/events
```
4) Metriken prüfen:
```bash
curl http://localhost:5400/metrics | rg inventory_epcis
```

Mock-/Sampledaten entstehen direkt aus den tatsächlichen Lagerbeständen; zusätzliche Fixtures sind nicht nötig.
