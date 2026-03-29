# Neuro-Core Zielarchitektur -- Gap-Analyse und Umsetzungsplan

Stand: 2026-03-29
Quelle: Integrierte Zielarchitektur (Bild) + Architektur-Review (6 fehlende Layer)

## 1. Architektur-Uebersicht

Die Zielarchitektur definiert zwei Pfade:

- **Kognitiver Pfad** (via Neuro-Core AI Orchestrator): Intent -> Context -> State -> Plan -> Verify -> Execute
- **Deterministischer Pfad** (Direct Access): Fast Track fuer CRUD ohne AI-Overhead

Dazwischen: Guardrails, Audit, Policy, Human Oversight als Querschnittsschichten.

## 2. Gap-Matrix: Ist vs. Soll

| # | Komponente | Soll (Zielarchitektur) | Ist (Codebase) | Gap-Typ | Prio |
|---|-----------|----------------------|---------------|---------|------|
| NC-01 | Neuro Intent Engine | Intent-Klassifikation, Confidence, Risikoklasse | Stage-basiertes Routing in `neuroassist.py`, kein NLU | **Ausbau** | P1 |
| NC-02 | Neuro State Graph | Stateful Business Object Graph (Bestellung, Rechnung, Kunde, Freigabe) | **Umgesetzt** (Lane B, `neuro_state_graph.py`, 37 Tests gruen) | Fertig | -- |
| NC-03 | Neuro Context Resolver | Rolle, Berechtigung, Business Objects, Einwilligung, Historie, Kanal | `neuroassist_context.py` loest Prozess/Aggregat auf; Consent fehlt | **Ausbau** | P2 |
| NC-04 | Neuro Planner | Kontext-Pruefung, Schritte generieren, Aktions-Favorit, Validierungsvertrag | Role/PromptPack Contracts vorhanden; kein expliziter Planner | **Ausbau** | P1 |
| NC-05 | Confidence & Risk Engine | Append-Only Confidence Ledger | **Umgesetzt** (Lane B, `confidence_ledger.py`, SHA-256 Hash-Chain, 37 Tests gruen) | Fertig | -- |
| NC-06 | Rule & Knowledge Store | Versionierte Policy- und Prompt-Registrierung | **Teilweise** (Lane G, `policy_registry.py` mit Versionierung + Rollback, `be5b0ddf4`) | **Ausbau** | P2 |
| NC-07 | Action & Policy Layer | Definierte Aktionen und Risikosteuerung | `business_commands.py`, `command_dispatcher.py` -- **produktionsreif** | Fertig | -- |
| NC-08 | Human Oversight | Menschliche Freigabe | `human_approval_gate.py` mit 4 Risikostufen -- **vorhanden** | **Ausbau** (Case Mgmt) | P3 |
| NC-09 | Guardrails & Output-Validierung | PII/DLP-Schutz, Inhaltsfilterung | **Umgesetzt** (Lane C, `pii_detector.py`, `guardrails.py`, `be5b0ddf4`) | Fertig | -- |
| NC-10 | Fast Track | Umgehung Neuro-Core fuer deterministisches CRUD | **Umgesetzt** (Lane E, `fast_track.py`, `be5b0ddf4`) | Fertig | -- |
| NC-11 | VALEO Copilot UI | Konversationale AI-Oberflaeche | **Umgesetzt** (Lane F, `copilot_ws.py`, `useCopilotStream.ts`, `be5b0ddf4`) | Fertig | -- |
| NC-12 | Interaktions-Kanaele | WhatsApp, E-Mail, Live-Chat/Web-Chat | Slack/Teams-Framework in `channel_ingress.py`; WA/Email/Chat fehlen | **Neubau** | P3 |
| NC-13 | Audit & Trace Layer | Unveraenderlicher Audit-Trail, Neuro-Entscheidungs-Protokoll, SIEM | **Umgesetzt** (Lane D, `audit_hardening.py`, `neuro_decision_protocol.py`, `79267fb43`) | Fertig | -- |
| NC-14 | Event Bus (Kafka) | Kafka Event Bus | **Teilweise** (Lane G, Event Schema Registry + Policy Registry, NATS Consumer umgesetzt) | **Ausbau** | P2 |
| NC-15 | Identity & Access / Secrets | OIDC + Vault | OIDC/Keycloak + RBAC vorhanden; kein Vault | **Ausbau** | P3 |
| NC-16 | Load Balancer | Service-Routing | Traefik-Ingress in k8s; kein expliziter LB in Compose | Infra | P3 |
| NC-17 | Domain Services | Auftrags-Service, Einkauf, Finanzdienst, externe APIs | **Produktionsreif** | Fertig | -- |

### Review-Erweiterungen (6 fehlende Layer)

| # | Komponente | Beschreibung | Gap-Typ | Prio |
|---|-----------|-------------|---------|------|
| EXT-01 | Neuro Verification Engine | Formale Pruefung JEDES Plans VOR Ausfuehrung (Vorbedingungen, Policy, Datenintegritaet, Zustandsuebergaenge) | **Umgesetzt** (NC-001, `c6e82411`) | P1 |
| EXT-02 | Interaction State Manager | Kanal-/Dialogzustand (new -> engaged -> qualified -> intent_detected -> conversion_ready -> escalated -> closed) | **Umgesetzt** (NC-002, `c6e82411`) | P2 |
| EXT-03 | Voice Adapter Layer | STT/TTS, Turn Manager, Latency Control -- Voice ist Echtzeit, kein Chat | **Umgesetzt** (NC-003, `c6e82411`) | P3 |
| EXT-04 | Consent Engine | Opt-in/Opt-out, Kanalberechtigungen, Zeitstempel, Zweckbindung (DSGVO) | **Umgesetzt** (NC-004, `c6e82411`) | P2 |
| EXT-05 | Neuro Simulation Engine | Dry-Run fuer Entscheidungen, Regelvalidierung, Edge-Case-Simulation | **Umgesetzt** (NC-005, `c6e82411`) | P2 |
| EXT-06 | Compensation Engine | Rollback, Retry, Alternative Pfade, Eskalation bei Teilprozess-Abbruch | **Umgesetzt** (NC-006, `c6e82411`) | P1 |

## 3. Parallelisierbare Lanes

Die Umsetzung ist in **8 unabhaengige Lanes** geschnitten. Jeder Agent bearbeitet genau eine Lane.
Abhaengigkeiten zwischen Lanes sind explizit markiert.

---

### Lane A: Neuro-Core Kernel (NC-01, NC-04, EXT-01)

**Scope:** Intent Engine + Planner + Verification Engine
**Dateibesitz:**

- `app/agents/neuro_intent_engine.py` (NEU)
- `app/agents/neuro_planner.py` (NEU)
- `app/agents/neuro_verification_engine.py` (NEU)
- `app/agents/neuroassist_contracts.py` (EDIT -- IntentResult, PlanStep, VerificationResult Contracts)
- `tests/test_neuro_intent_engine.py` (NEU)
- `tests/test_neuro_planner.py` (NEU)
- `tests/test_neuro_verification_engine.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-A1 | `IntentResult` Contract: intent, confidence_score (0-1), risk_class, explanation, requested_action | Unit-Test |
| NC-A2 | `IntentEngine.classify(user_input, context) -> IntentResult` mit Capability-Matching | Unit-Test + Integration mit bestehenden 5 Capabilities |
| NC-A3 | `PlanStep` Contract + `Planner.generate_plan(intent, context) -> list[PlanStep]` | Unit-Test |
| NC-A4 | `VerificationResult` Contract + `VerificationEngine.verify(plan, state) -> VerificationResult` mit Policy-Check, Precondition-Check, State-Transition-Check | Unit-Test |
| NC-A5 | Integration: Intent -> Context -> Plan -> Verify -> Execute Pipeline im `neuroassist_runtime.py` | E2E-Test |

**Abhaengigkeiten:** Keine (nutzt bestehende Contracts aus `neuroassist_contracts.py`)

---

### Lane B: State Graph + Confidence Ledger (NC-02, NC-05) -- ABGESCHLOSSEN

**Status:** Umgesetzt am 2026-03-29, 37 Tests gruen
**Scope:** Expliziter Business State Graph + Append-Only Confidence Ledger

**Erstellte Dateien:**

- `app/core/neuro_state_graph.py` -- StateNode, StateEdge, StateTransition, StateGraphSnapshot, StateGraphService mit Transitions-Matrix fuer 8 Business-Object-Typen
- `app/core/confidence_ledger.py` -- Append-Only Ledger mit SHA-256 Hash-Chain, Reproducibility (model_id, model_version, input_hash), ConfidenceLedgerService
- `app/infrastructure/models/neuro_state_models.py` -- SQLAlchemy ORM (4 Tabellen in domain_shared)
- `alembic/versions/neuroassist_state_graph_confidence_ledger_20260329.py` -- Migration (4 Tabellen, 13 Indices)
- `app/api/v1/endpoints/neuro_state_graph_api.py` -- REST API unter `/api/v1/neuro/` (State Graph CRUD + Transitions + Confidence Ledger + Chain Verification)
- `tests/test_neuro_state_graph.py` -- 37 Tests (Unit + API)

**Slices (alle abgeschlossen):**

| Slice | Inhalt | Status |
|-------|--------|--------|
| NC-B1 | StateNode + StateEdge + StateTransition Modelle, Graph-Operationen, Transitions-Matrix | Gruen (8 Tests) |
| NC-B2 | 8 Node-Typen: Bestellung, Rechnung, Lagerbestand, Kunde, Freigabe, Lieferschein, Kontrakt, Gutschrift | Gruen |
| NC-B3 | ConfidenceLedgerEntry Append-Only mit SHA-256 Hash-Chain, model_version, input_hash | Gruen (5 Tests) |
| NC-B4 | Chain Verification, Tamper Detection, Risk Summary, Latest Confidence | Gruen (10 Tests) |
| NC-B5 | REST API: 12 Endpoints, Chain Verify Endpoint, Summary Endpoint | Gruen (14 Tests) |

**Abhaengigkeiten:** B5 (Integration mit Planner/Approval Gate) kann spaeter nachgezogen werden.

---

### Lane C: Guardrails + DLP + Consent (NC-09, EXT-04)

**Scope:** PII-Erkennung/Maskierung, DLP-Regeln, Consent-Lifecycle
**Dateibesitz:**

- `app/core/guardrails.py` (NEU)
- `app/core/pii_detector.py` (NEU)
- `app/core/consent_engine.py` (NEU)
- `app/infrastructure/models/consent_models.py` (NEU)
- `alembic/versions/consent_engine_*.py` (NEU)
- `app/middleware/guardrail_middleware.py` (NEU)
- `tests/test_guardrails.py` (NEU)
- `tests/test_pii_detector.py` (NEU)
- `tests/test_consent_engine.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-C1 | `PIIDetector` -- Regex + Pattern-basierte Erkennung (IBAN, Telefon, E-Mail, Steuernummer, Personalausweis) | Unit-Test mit DE-Testdaten |
| NC-C2 | `PIIMasker.mask(text) -> MaskedText` -- reversibel fuer berechtigte Nutzer, irreversibel fuer Logs | Unit-Test |
| NC-C3 | `GuardrailMiddleware` -- Input-Filterung (Prompt Injection Detection), Output-Filterung (PII in AI-Antworten) | Unit-Test + Integration |
| NC-C4 | `ConsentRecord` Modell (person_id, channel, purpose, granted_at, revoked_at, legal_basis) | Migration |
| NC-C5 | `ConsentEngine.check(person_id, channel, purpose) -> ConsentStatus` + `grant/revoke` API | Unit-Test + REST-Endpoint |

**Abhaengigkeiten:** Keine

---

### Lane D: Audit Hardening + Decision Protocol (NC-13, NC-05 teilweise)

**Scope:** Persistentes Append-Only Audit-Schema, Neuro-Entscheidungs-Protokoll, SIEM-Vorbereitung
**Dateibesitz:**

- `app/infrastructure/models/audit_models.py` (NEU)
- `app/core/neuro_decision_protocol.py` (NEU)
- `alembic/versions/audit_append_only_*.py` (NEU)
- `app/middleware/audit_middleware.py` (EDIT -- DB-Write statt nur Logging)
- `app/api/v1/endpoints/audit_evidence.py` (EDIT -- Query-API)
- `tests/test_audit_append_only.py` (NEU)
- `tests/test_neuro_decision_protocol.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-D1 | `AuditEntry` Append-Only-Tabelle (kein UPDATE/DELETE, DB-Trigger/Policy) mit Hash-Chain (previous_hash + SHA-256) | Migration + Constraint-Test |
| NC-D2 | `AuditMiddleware` schreibt Mutationen in `AuditEntry`-Tabelle (nicht nur Structured Log) | Integration-Test |
| NC-D3 | `NeuroDecisionProtocol` Tabelle (decision_id, intent, plan_steps, verification_result, confidence_score, human_approval, execution_result, explanation) | Migration |
| NC-D4 | `DecisionProtocol.record(decision)` -- automatisch aus Neuro-Core Pipeline befuellt | Integration-Test |
| NC-D5 | Audit-Query-API: `GET /api/v1/audit/trail?aggregate_id=X&from=&to=` + Hash-Chain-Validierung | REST-Test |

**Abhaengigkeiten:** D4 braucht Lane A (Pipeline) -- kann aber parallel bis D3 laufen.

---

### Lane E: Fast Track + Compensation (NC-10, EXT-06)

**Scope:** Deterministischer Bypass fuer CRUD + Fehlerbehandlung/Rollback
**Dateibesitz:**

- `app/core/fast_track.py` (NEU)
- `app/core/compensation_engine.py` (NEU)
- `app/middleware/fast_track_middleware.py` (NEU)
- `tests/test_fast_track.py` (NEU)
- `tests/test_compensation_engine.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-E1 | `FastTrackClassifier.is_fast_track(request) -> bool` -- Regelwerk: reine GET-Requests, Standard-CRUD ohne Business-Logik, konfigurierbare Whitelist | Unit-Test |
| NC-E2 | `FastTrackMiddleware` -- leitet Fast-Track-Requests direkt an Domain Services, umgeht Neuro-Core | Integration-Test |
| NC-E3 | `CompensationStep` Contract (action, rollback_action, status, retry_count, max_retries) | Unit-Test |
| NC-E4 | `CompensationEngine.execute_with_compensation(steps) -> CompensationResult` -- Saga-Pattern mit Rollback | Unit-Test mit Fehler-Szenario |
| NC-E5 | Integration in Action Layer: `CommandDispatcher` nutzt CompensationEngine fuer Multi-Step-Commands | Integration-Test |

**Abhaengigkeiten:** E5 haengt von bestehender `command_dispatcher.py` ab (Edit, nicht Neubau).

---

### Lane F: Copilot Backend + Interaction State (NC-11, EXT-02)

**Scope:** WebSocket-Streaming fuer Copilot, Interaction State Machine
**Dateibesitz:**

- `app/api/v1/endpoints/copilot_ws.py` (NEU)
- `app/core/interaction_state.py` (NEU)
- `app/infrastructure/models/interaction_state_models.py` (NEU)
- `alembic/versions/interaction_state_*.py` (NEU)
- `packages/frontend-web/src/features/copilot/useCopilotChat.ts` (EDIT -- WebSocket statt Mock)
- `packages/frontend-web/src/features/copilot/useCopilotStream.ts` (NEU)
- `tests/test_copilot_ws.py` (NEU)
- `tests/test_interaction_state.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-F1 | `InteractionState` FSM (new -> engaged -> qualified -> intent_detected -> conversion_ready -> escalated -> closed) + SQLAlchemy-Modell | Unit-Test + Migration |
| NC-F2 | `InteractionStateManager.transition(session_id, event) -> InteractionState` mit Guards und Audit | Unit-Test |
| NC-F3 | WebSocket-Endpoint `ws://host/api/v1/copilot/chat` mit Token-Auth, SSE-Fallback | Integration-Test |
| NC-F4 | Frontend `useCopilotStream` Hook -- WebSocket-Client mit Reconnect und Message-Queue | Vitest |
| NC-F5 | Copilot -> Neuro-Core Pipeline: Chat-Nachricht -> IntentEngine -> Planner -> Response-Stream | E2E-Test |

**Abhaengigkeiten:** F5 haengt von Lane A (IntentEngine/Planner) ab.

---

### Lane G: Event Bus Hardening + Knowledge Store (NC-14, NC-06)

**Scope:** NATS-Consumer aktivieren, Event-Schemas, Knowledge/Policy Versionierung
**Dateibesitz:**

- `app/infrastructure/eventbus/nats_consumer.py` (NEU)
- `app/infrastructure/eventbus/event_schemas.py` (NEU)
- `app/core/knowledge_store.py` (NEU -- oder EDIT `knowledge_core_contracts.py`)
- `app/core/policy_registry.py` (NEU)
- `tests/test_nats_consumer.py` (NEU)
- `tests/test_policy_registry.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-G1 | Event-Schema-Registry: Pydantic-Modelle fuer Domain-Events mit Version-Header | Unit-Test |
| NC-G2 | `NATSConsumer` -- generischer Consumer mit Retry, DLQ, Idempotenz-Pruefung | Unit-Test (umgesetzt) |
| NC-G3 | Mindestens 3 Consumer aktivieren: Audit-Event, Inventory-Movement, Settlement-Created | Integration-Test |
| NC-G4 | `PolicyRegistry` -- YAML/JSON-backed Policy-Speicher mit Versionierung + Rollback | Unit-Test |
| NC-G5 | `PromptPackRegistry` -- versionierte Prompt-Packs mit A/B-Testing-Faehigkeit | Unit-Test |

**Abhaengigkeiten:** Keine

---

### Lane H: Channels + Voice (NC-12, EXT-03)

**Scope:** WhatsApp-Adapter, E-Mail-Kanal, Voice-Layer, Simulation Engine
**Dateibesitz:**

- `app/channels/whatsapp_adapter.py` (NEU)
- `app/channels/email_channel.py` (NEU)
- `app/channels/voice_adapter.py` (NEU)
- `app/core/simulation_engine.py` (NEU -- EXT-05)
- `tests/test_whatsapp_adapter.py` (NEU)
- `tests/test_simulation_engine.py` (NEU)

**Slices:**

| Slice | Inhalt | Abnahme |
|-------|--------|---------|
| NC-H1 | `WhatsAppAdapter` -- WhatsApp Business API Webhook-Empfang, Message-Parsing, Reply | Unit-Test mit Mock-Webhook |
| NC-H2 | `EmailChannel` -- IMAP-Polling/Webhook fuer eingehende E-Mails, Response via SMTP | Unit-Test |
| NC-H3 | `VoiceAdapter` -- STT/TTS-Integration (Whisper/Azure), Turn-Manager, Latency-Budget | Unit-Test mit Mock-Audio |
| NC-H4 | Channel -> ChannelIngress -> Neuro-Core Routing fuer alle 3 neuen Kanaele | Integration-Test |
| NC-H5 | `SimulationEngine.dry_run(plan, state) -> SimulationResult` -- testet Entscheidungen ohne Ausfuehrung | Unit-Test |

**Abhaengigkeiten:** H4 haengt von bestehender `channel_ingress.py` ab. H5 haengt von Lane A (Planner) ab.

## 4. Abhaengigkeitsgraph

```text
Lane A (Neuro-Core Kernel) -----> keine Abhaengigkeit
Lane B (State Graph)       -----> B5 wartet auf A
Lane C (Guardrails)        -----> keine Abhaengigkeit
Lane D (Audit Hardening)   -----> D4 wartet auf A
Lane E (Fast Track)        -----> keine Abhaengigkeit
Lane F (Copilot)           -----> F5 wartet auf A
Lane G (Event Bus)         -----> keine Abhaengigkeit
Lane H (Channels)          -----> H4/H5 warten auf A
```

**Parallelisierung:** Alle 8 Lanes koennen sofort starten. Nur der jeweils letzte Slice (Integration) wartet auf Lane A.

## 5. Prioritaetsreihenfolge

### P1 -- Sofort (Kern-Differenzierung)

1. **Lane A** -- Neuro-Core Kernel (Intent + Planner + Verification)
2. **Lane B** -- State Graph + Confidence Ledger
3. **Lane C** -- Guardrails + Consent
4. **Lane D** -- Audit Hardening

### P2 -- Danach (Produktionsreife)

5. **Lane E** -- Fast Track + Compensation
6. **Lane F** -- Copilot Backend
7. **Lane G** -- Event Bus + Knowledge Store

### P3 -- Dann (Channel-Erweiterung)

8. **Lane H** -- Channels + Voice + Simulation

## 6. Agent-Zuweisungsregeln

- Pro Lane ein Agent.
- Dateibesitz ist exklusiv -- kein Agent darf Dateien einer anderen Lane bearbeiten.
- Jeder Agent committet nach jedem abgeschlossenen Slice.
- Commit-Convention: `feat(nc-XX): <beschreibung>` (z.B. `feat(nc-a1): intent result contract`)
- Integration-Slices (A5, B5, D4, E5, F5, H4, H5) erst nach Abhaengigkeits-Lane.
- Bei Ueberschneidung mit bestehenden Dateien: Edit-Scope klar dokumentieren, kein Full-Rewrite.

## 7. Workboard-Eintrag (Template)

Jede Lane wird als eigener Slice im `active-workboard.md` eingetragen:

```
| NC-A | Neuro-Core Kernel (Intent + Planner + Verification) | offen | -- | app/agents/neuro_*.py, tests/test_neuro_*.py | NC-A1 starten | keine |
```

## 8. Erfolgskriterien (Definition of Done)

- Alle Unit-Tests gruen
- Alle Integration-Tests gruen
- Keine Regressionen in bestehenden 900+ Tests
- Audit-Trail fuer jede AI-Entscheidung nachweisbar
- Confidence Ledger append-only (DB-Constraint verifiziert)
- PII-Masking aktiv auf allen AI-Ein-/Ausgaben
- Fast Track messbar schneller als Neuro-Core-Pfad
- Jeder Slice hat Workflow-Doku + Card nach bestehendem Template
