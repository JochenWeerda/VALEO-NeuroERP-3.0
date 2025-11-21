# FiBu Shared Libraries – Integrationsstand (2025‑11‑14)

## 1. Aktuell umgesetzt
- `finance-shared` liefert wiederverwendbare Module für Auth/RBAC, Events sowie GoBD-Audit-Trails.
- `fibu-gateway`
  - nutzt `FiBuAccessPolicy` in allen Routen (`chart_of_accounts`, `journal_entries`, `op_management`).
  - erzeugt pro Journal-POST Audit-Trail-Einträge + Booking-Events via `FiBuEventPublisher`.
  - Event-Publisher hängt an NATS (konfigurierbar via `EVENT_BUS_*`) und fällt bei Fehlern auf strukturiertes Logging zurück.
  - Gateway-Clients besitzen vereinheitlichte Response-/Error-Verarbeitung (`GatewayServiceError`, Normalisierung von `{"data": ...}`).
  - Approval-Rules werden tenant-spezifisch aus SQLite-Store (`APPROVAL_RULES_DB_PATH`) gelesen und bei Bedarf per Default-Regel ergänzt.
  - Shared-Lib als Editable Install (`-e ../../packages/finance-shared`) in `requirements.txt`.
- `fibu-core`
  - `JournalService` erstellt GoBD-Audit-Log + Booking-Events mit validierten UUIDs.
  - Unit-Tests für Journal-Service vorhanden.

## 2. Offene Maßnahmen
1. **Event-Bus Hardening**
   - Kafka-Bridge für produktive Streams ergänzen.
   - Telemetrie & Alerting (Publish-Dauer, Fehlerrate) in Prometheus/Grafana aufnehmen.
   - Lifespan-Checks um `NATS`-Status erweitern (Ready-Endpoint).

2. **Gateway ↔ Core Contract Tests**
   - Sobald `fibu-core` echte REST-Routen besitzt:
     - CDC-/Schema-Tests (e.g. pytest + `respx`) automatisieren.
     - Mehrsprachige Fehler-Codes definieren und in `GatewayServiceError` mappen.
     - E2E-Testfall: Gateway POST → Core → Eventbus → Assertions.

3. **Approval-Rule Lifecycle**
   - Admin-API oder UI für Pflege (CRUD + Audit).
   - Optional: Cache-Layer (Redis) + Change-Events (`approval.rule.updated`).
   - Data-Migrationsskript, um bestehende Mandanten in SQLite bzw. spätere zentrale Config-DB zu übernehmen.

## 3. Nächste Schritte & Empfehlungen
- Priorität 1: Kafka-/Observability-Layer für Event-Publisher fertigstellen.
- Priorität 2: Contract-Tests mit `fibu-core` implementieren, sobald APIs stehen.
- Priorität 3: Approval-Rules-Admin-Flow (API, UI, Audit) etablieren.

## 4. Testing & Observability
- Bestehende pytest-Suites:
  - `packages/finance-shared/tests`
  - `services/finance/fibu-gateway/tests/unit`
  - `services/finance/fibu-core/tests`
- Nach Bus-Integration: zusätzliche Integrationstests mit lokalem NATS/Kafka + Prometheus-Metriken für Publishing-Erfolg/Fehler.


