# Open Gaps and Known Issues

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Zuletzt vollstaendig auditiert: **2026-04-10** (automatisierter Code-Audit ueber Frontend, Backend, Architektur und Build-Health).

---

## Build-Health (Stand 2026-04-10)

- **TypeScript**: 0 Fehler (`tsc --noEmit`)
- **Backend-Tests**: 7.010 gesammelt, Gesamtabdeckung ~45%
- **Frontend-Imports**: 0 gebrochene Importe
- **Endpoints**: 1.836 registriert (916 GET, 666 POST, 121 PUT, 133 DELETE), 231+ Router in `api.py`

---

## P1 — Fachlich duenn / produktionsblockierend

### STUB-001: Mischfutter-Produktion hat keine echte Datenbasis

- **Dateien**: `app/api/v1/endpoints/produktion_mischfutter.py`
- **Problem**: `GET /verfuegbarkeit` (Zeile 58) liefert 7 hartcodierte Komponenten, `GET /rezepte` (Zeile 76) liefert 3 statische Rezepte, `POST /auftraege` (Zeile 131) persistiert nicht und zieht keinen Bestand ab.
- **TODO im Code**: "replace with real inventory query once Lager-Bestaende table is wired"
- **Auswirkung**: Produktionsplanung ist rein visuell, kein echter Materialfluss.

### STUB-002: Futtermittel-Stammdaten sind Demo-Seed

- **Dateien**: `app/api/v1/endpoints/futter_stamm.py`
- **Problem**: `GET /einzelfuttermittel` (Zeile 161), `GET /mischfuttermittel` (Zeile 169), `GET /rezepte/{id}` (Zeile 185) liefern inline Demo-Daten aus `_REZEPT_SEED`. Kommentar: "Demo-Seed-Daten werden inline bereitgestellt, bis persistente Modelle existieren."
- **Auswirkung**: Kein CRUD, keine Mandantentrennung, keine Migration.

### STUB-003: Liquiditaetsuebersicht ist Platzhalter

- **Dateien**: `app/api/v1/endpoints/liquidity.py`
- **Problem**: `GET /finance/liquidity/overview` (Zeile 11) liefert leere Struktur mit 0-Werten, keine echte Berechnung.
- **Auswirkung**: Finance-Cockpit zeigt keine reale Liquiditaetslage.

### STUB-004: Sortenregister ist statische Liste

- **Dateien**: `app/api/v1/endpoints/agrar_varieties.py`
- **Problem**: `GET /` (Zeile 31) liefert hartcodierte `STANDARD_VARIETIES`. Kommentar: "kann spaeter aus DB/Stammdaten geladen werden."
- **Auswirkung**: Keine mandantenspezifischen Sorten, kein Anlegen/Aendern.

### TENANT-001: Multi-Tenancy-Enforcement nur auf Endpoint-Ebene

- **Dateien**: `app/core/tenant_context.py`, `app/middleware/`
- **Problem**: `X-Tenant-ID` wird als Context-Variable durchgereicht, aber **nicht in der Middleware validiert oder erzwungen**. Tenant-Isolation passiert in den einzelnen Endpunkten, nicht zentral. `audit_middleware.py` liest `request.state.tenant_id`, prueft aber nicht.
- **Auswirkung**: Ein fehlerhafter Endpoint kann versehentlich Cross-Tenant-Daten liefern. Die SEC-Reihe hat viele Router gehaertet, aber es gibt keinen zentralen Guard.
- **Empfehlung**: Middleware-Level Query-Filter oder zumindest ein zentraler Assert fuer alle DB-Queries.

### VOICE-001: Voice-Kanal ist Stub

- **Dateien**: `app/services/voice_adapter.py`, `packages/frontend-web/src/pages/admin/voice-channel.tsx`
- **Problem**: In-Memory-Session-Store, kein STT/TTS-Provider angebunden. Expliziter Platzhalter: `"text": "[STT-Ergebnis — Provider-Integration ausstehend]"`, `"provider": "pending"`.
- **Auswirkung**: Voice-Feature existiert nur als Routing-Skelett, nicht als nutzbarer Kanal.

---

## P2 — Architektonisch offen / mittelfristig relevant

### NATS-001: Event-Bus ist disabled by default

- **Dateien**: `app/infrastructure/eventbus/nats_publisher.py`, `nats_consumer.py`
- **Problem**: `enabled: bool = False` (Zeile 23 Publisher). Consumer loggt: "NATS consumer disabled — using log-only fallback". Architektur steht (DLQ, Idempotenz, Flow-Spine-Handler, Observability), aber in Produktion laeuft nichts ueber NATS.
- **Auswirkung**: Alle Events sind synchron oder log-only. Kein echter Pub/Sub im Betrieb.

### RAG-001: ChromaDB befuellt, aber schmaler Inhaltsbestand

- **Dateien**: `app/services/vector_store.py`, `app/services/indexer.py`
- **Problem**: Indexer laeuft alle 5 Minuten und indexiert Artikel + Kunden pro Tenant. ChromaDB ist funktional, aber nur zwei Entity-Typen sind indiziert. Kein Prozesswissen, keine Dokumente, keine Wissensbasis-Eintraege.
- **Auswirkung**: RAG-Antworten sind auf Artikel-/Kundenstamm beschraenkt.

### CRUD-001: GET-only-Endpoints ohne Mutation

Folgende Ressourcen haben nur Lesezugriff, obwohl CRUD fachlich sinnvoll waere:

| Endpoint-Datei | Routen | Fehlend |
|----------------|--------|---------|
| `config_service.py` | GET | POST/PUT fuer Konfigurationsaenderungen |
| `disposition.py` | 2 GET | POST/PUT fuer Dispositionsentscheidungen |
| `dms_images.py` | 2 GET | POST fuer Bild-Upload |
| `direct_debits.py` | 2 GET | POST/DELETE fuer Lastschrift-Management |
| `foerderung.py` | 2 GET | POST fuer Foerderantraege |
| `marketing.py` | 3 GET | POST fuer Kampagnen |
| `zertifikate.py` | 2 GET | POST fuer Zertifikatsanlage |

### COVERAGE-001: Backend-Testabdeckung bei 45%

- Gesamtabdeckung ist fuer ein ERP-System niedrig. Kritische Pfade (Finance-Posting, Bestandsfuehrung, Tenant-Isolation) sollten >80% haben.

---

## P3 — Frontend-Restarbeiten (niedrig)

### FE-001: `downloadComingSoon`-Rest in Lieferanten-Stamm

- **Datei**: `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx` (Zeile ~400)
- **Problem**: Dokument-Download zeigt `t('crud.messages.downloadComingSoon')` statt echtem Download.

### FE-002: Toast-only Bulk-Aktionen in 3 Dateien

Buttons zeigen Erfolgs-Toast ohne echte API-Mutation:

| Datei | Aktion | Problem |
|-------|--------|---------|
| `futtermittel/charge-verfolgung.tsx` | Export/Recall/Trace (Zeilen 145-163) | Static Config liefert Toast-only; wird in `useMemo` ueberschrieben — fragiles Pattern |
| `fibu/kreditoren.tsx` | DATEV-Export-Button | Zeigt Info-Toast, triggert keinen echten Export |
| `fuhrpark/fahrzeug-stamm.tsx` | Drucker-Setup / Akte drucken | `await` + Toast ohne Fehlerbehandlung |

---

## P4 — Externe Abhaengigkeiten (nicht repo-seitig loesbar)

### EXT-001: Live-Credentials und Zielsystem-URLs

- Superglue-Connectors, L3-Import, Erstinstallation und Finance-Export brauchen produktive Tenant-Secrets, Zielsystem-URLs und Ops-Alerting-Werte, die ausserhalb des Repos gepflegt werden.

### EXT-002: FIBU-Mappings fuer Cutover

- Fachlich freigegebene Konten-/Steuer-/Kostenstellen-Mappings fuer die L3-Migration stehen noch aus.

### EXT-003: Externes Monitoring/Alerting

- Prometheus-Metriken (`valeo_event_bus_*`) werden exportiert, aber Grafana-Dashboards und Alerting-Regeln sind nicht im Repo und muessen ops-seitig aufgesetzt werden.

---

## Infrastruktur-Status (Kurzreferenz)

| Komponente | Status | Bemerkung |
|------------|--------|-----------|
| PostgreSQL 15 | produktiv | Multi-Schema, Alembic-Migrationen |
| Redis 7 | produktiv | Session/Cache |
| NATS JetStream | architekturbereit, disabled | Log-only Fallback |
| Keycloak/OIDC | produktiv | RS256/JWKS, dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB/RAG | produktiv (schmal) | Nur Artikel + Kunden indiziert |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools provisioniert |
| Voice-Kanal | Stub | Kein STT/TTS-Provider |

---

## Zuletzt geschlossene Punkte (2026-04-10)

- ~~`POST /api/v1/compliance/pcn-meldungen` fehlte~~ -> jetzt vollstaendig implementiert in `compliance.py:818` mit UFI-Validierung und Tenant-Isolation
- ~~OP-ROLL-007 bis OP-ROLL-012 (Fallkopf-Rollout) waren reserviert~~ -> alle 6 Slices abgeschlossen, 8 Kernmasken mit operativem Vorgangskopf, Register bewusst schlank gelassen und dokumentiert in `operational-rollout-scope-2026-04-09.md`
- ~~Frontend-Typecheck war fragil~~ -> 0 Fehler, `tsc --noEmit` ist gruen
- ~~Mock-Seiten-Inventur war nur geschaetzt~~ -> vollstaendiger Audit: 0 rein unverbundene Pages, 479 Seiten nutzen Hook-basierte API-Anbindung

---

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen Doku, Implementierung, Fachlogik oder Benutzerfuehrung auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`
- `docs/project-context/operational-rollout-scope-2026-04-09.md`
- `docs/roadmap/status/2026-04-03-security-hardening-phase-2.md`
