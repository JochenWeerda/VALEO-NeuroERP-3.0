# Wave 104 — Flow Spine Persistenz + PCN-Compliance + Systemanalyse

## Scope
GAP-104-A (Flow Spine DB-Persistenz), GAP-104-B (TS Typ-Mismatch), GAP-104-C/D (PCN-Meldungen Endpoint + DB), GAP-104-E (Paginierung), GAP-104-F (Tenant-Isolation), GAP-104-G (NATS Outbox), GAP-104-H (Agent-Action + RAG), GAP-104-I (Voice-Kanal).

## Zielbild
Flow Spine Instanzen DB-persistent, PCN-Endpoint vollständig, Memory-Layer via Outbox verdrahtet, Agent-Action-Endpoint mit RAG, Voice-Kanal UI produktiv.

## Lieferumfang
Siehe Detailabschnitte unten.

## Abnahmekriterien
- `ops_flow_spine_instances` und `ops_pcn_meldungen` Tabellen per Alembic-Migration angelegt
- 15/15 Tests in `test_flow_spines_api.py` grün
- `create_instance` und `transition_instance` publizieren Outbox-Events
- `POST /process/flow-spines/{key}/agent-action` erreichbar (RAG optional)
- `pages/admin/voice-channel.tsx` im Nav erreichbar

---

## Vorarbeiten (Wave 104 Basis — bereits committed)

### Commits `2a8be12` / `1a35c3a` / `10e5c74` (Perf + HMR-Fixes)
- `flow_spines.py`: HTTP-Cache-Header (`Cache-Control`, `ETag`) auf Catalog + statischem Workspace
- `flow_spine_registry.py`: `merge_instance_statuses()` deep-copy-sicher
- `FlowSpineWorkspace.tsx`: useMutation für Action-Buttons, "Neue Instanz"-Dialog
- `flow-spines.ts`: staleTime 30 s (Workspace) / 60 s (Catalog), vollständiger API-Client
- Frontend: `useMemo`-Merge gegen HMR Hook-Count-Mismatch, Wildcard-Route-Loader stabilisiert

---

## P0 — Flow Spine Instance Store: DB-Persistenz (Gap 104-A)

**Problem:** `_instances: dict` in `flow_spines.py` war ein prozessinterner In-Memory-Dict —
alle Instanzen gingen bei Neustart verloren.

**Lösung:**
- Neues SQLAlchemy-Modell `FlowSpineInstance` in `app/domains/operations/models.py`
  - Schema: `domain_ops`, Tabelle: `ops_flow_spine_instances`
  - Felder: `id`, `case_number`, `process_key`, `label`, `customer_id`, `customer_name`,
    `subject`, `entry_mode`, `linked_document_id`, `linked_document_type`,
    `node_statuses` (JSONB), `active_node_id`, `last_actor`, `last_action_label`,
    `tenant_id`, `created_at`, `updated_at`
- Alembic-Migration: `flow_spine_instances_20260326.py`
- `flow_spines.py`: CRUD-Endpoints auf DB umgestellt, `_instances`-Dict entfernt

**Betroffene Dateien:**
- `app/domains/operations/models.py` — Modell hinzugefügt
- `alembic/versions/flow_spine_instances_20260326.py` — Migration neu
- `app/api/v1/endpoints/flow_spines.py` — In-Memory-Dict durch DB-Zugriff ersetzt

---

## P1 — `useFlowSpineInstances` Typ-Mismatch (Bug 104-B)

**Problem:** Backend `GET /{process_key}/instances` gibt
`{ process_key, total, instances: FlowSpineInstance[] }` zurück.
Frontend-Hook `useFlowSpineInstances` behandelte `res.data` direkt als `FlowSpineInstance[]`
→ Komponenten erhielten ein Objekt statt ein Array.

**Lösung:**
- `flow-spines.ts`: Response-Typ auf `{ process_key: string; total: number; instances: FlowSpineInstance[] }`
  korrigiert, Hook gibt `res.data.instances` zurück.

**Betroffene Dateien:**
- `packages/frontend-web/src/lib/api/flow-spines.ts`

---

## P2 — `POST /compliance/pcn-meldungen` (Gap 104-C)

**Problem:** Frontend `pcn-ufi.tsx` rief `POST /api/v1/compliance/pcn-meldungen` auf,
Endpoint fehlte → HTTP 404, User erhielt Fehler-Toast.

**Lösung:**
- Neues In-Memory-Store-basiertes Endpoint in `compliance.py`
- PCN-Meldung: `produktname`, `ufi`, `cas_nummern`, `gefahrenklassen`,
  `verwendungskategorie`, `pcnStatus`
- UFI-Format-Validierung (XXXX-XXXX-XXXX-XXXX)
- Gibt `meldung_id`, `status`, `created_at`, `schema_version` zurück

**Betroffene Dateien:**
- `app/api/v1/endpoints/compliance.py`

---

## Tests

| Test | Ergebnis |
|------|----------|
| `test_flow_spines_api.py` (7 Tests) | 7/7 PASSED |
| Neue Tests: Instance CRUD via DB | PASSED |
| Neuer Test: PCN-Meldung POST | PASSED |

---

## Nachlieferung: Alle geschlossenen Gaps (Wave 104 komplett)

### GAP-104-D: PCN-Meldungen DB-Persistenz ✅
- `PCNMeldung`-Modell in `operations/models.py` (Schema `domain_ops`, `ops_pcn_meldungen`)
- Migration `pcn_meldungen_20260326.py` (chain: `flow_spine_instances_20260326` → `pcn_meldungen_20260326`)
- `compliance.py`: `POST/GET /compliance/pcn-meldungen` auf DB umgestellt, `_PCN_STORE` entfernt, Paginierung + Tenant-Isolation

### GAP-104-E: Flow Spine Paginierung ✅
- `GET /{process_key}/instances`: `?skip=0&limit=50` (max 200), Envelope enthält `skip`, `limit`, `total`

### GAP-104-F: Tenant-Isolation ✅
- `create_instance`: setzt `tenant_id = get_current_tenant_id()`
- `list_instances`: filtert auf `FlowSpineInstance.tenant_id == tenant_id`

### Sonstige Fixes ✅
- `compliance.py:_pdf_escape` Docstring: raw-string `r"""..."""` → DeprecationWarning beseitigt
- `flow_spines.py` linter-change (`partner_name`): übernommen, TS-Typen bereits korrekt

## P3-Gaps (Wave 104 Nachlieferung — vollständig geschlossen)

### GAP-104-G: NATS Outbox-Events für Flow Spine ✅
- `create_instance` und `transition_instance` sind jetzt `async def`
- `OutboxPublisher(db, get_event_publisher()).store_event(event, tenant_id)` in-transaction
- Events: `FlowSpineInstanceCreated`, `FlowSpineTransitionOccurred` (in `process_events.py`)
- Graceful Degradation: Outbox-Fehler werden geloggt, blockieren die HTTP-Response nicht

### GAP-104-H: Agent-Action Endpoint mit RAG ✅
- `POST /process/flow-spines/{process_key}/agent-action`
- Request: `{ action, node_id?, instance_id?, context? }`
- RAG: ChromaDB-Suche (top-3, gefiltert auf `process_key`) — graceful degradation wenn ChromaDB fehlt
- Response: `{ status, executed_at, rag_hits, workspace_title, instance? }`

### GAP-104-I: Voice-Kanal Admin-Seite ✅
- `packages/frontend-web/src/pages/admin/voice-channel.tsx`
- Nutzt `useVoiceIntent` aus `@/features/ki-usability/hooks/useVoiceIntent`
- Konfidenz-Slider (50–100 %), Sprachtest-Button, Erkennungsverlauf (letzte 20 Einträge)
- Nav-Eintrag in `core.tsx`: Administration → Voice-Kanal (Mic-Icon), Pfad `admin/voice-channel`

---

## Systemanalyse-Abgleich mit Zielarchitektur (Stand 2026-03-26)

```
Zielarchitektur-Schicht              Implementierungsstand
─────────────────────────────────────────────────────────────────
VALEO UI (Klassisch)                 ✅ React 18/TS, Vite, Mask-Builder (~450 Seiten)
VALEO Copilot UI (Chat/Voice)        ⚠️  ki-usability Feature-Flag; Voice partiell
API Gateway                          ✅ FastAPI + Middleware-Stack
AI Agent Orchestrator (Neuro-Core)   ✅ Flow Spine Registry (9 Prozesse)
LLM / KI-Modelle                     ⚠️  services/ai/ vorhanden, Agent-Integration partiell
Tool Layer (Function Calling)        ✅ Flow Spine Actions + Agent-Action-Endpoint
Memory Layer (Kafka/NATS)            ⚠️  NATS JetStream vorhanden, Agent-Kontext fehlt
Flow Spine Instance Persistenz       ✅ DB-backed (Wave 104)
Redis — Kurzzeit-Cache               ✅ konfiguriert; HTTP-Cache-Header auf Catalog/Workspace
Vector DB (RAG)                      ⚠️  knowledge_api.py vorhanden, RAG-Infra partiell
ERP Services (Domänen)               ✅ Sales, Einkauf, Lager, Finanzen, CRM, DMS
PostgreSQL (Multi-Schema)            ✅ Alembic, SQLAlchemy 2.0
Externe APIs                         ✅ BrightSky/DWD, Open-Meteo, Twilio, EDIFACT
Compliance-Abdeckung                 ✅ PCN-Meldungen Endpoint ergänzt (Wave 104)
```

## Status
`abgeschlossen` — 2026-03-26
