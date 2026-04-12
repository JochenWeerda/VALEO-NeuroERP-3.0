# Open Gaps and Known Issues

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Zuletzt vollstaendig auditiert: **2026-04-12**.

---

## Build-Health (Stand 2026-04-12)

- **TypeScript**: 0 Fehler (`tsc --noEmit`)
- **Backend-Tests**: repo-weit weiterhin deutlich zu niedrig fuer ein ERP, zuletzt grob bei ~45%
- **Frontend-Imports**: 0 gebrochene Importe
- **Alembic**: 1 Head
- **Docker-Erstinstallation**: Alembic-Bootstrap und Mehr-Domaenen-Struktur auf leerer DB abgesichert

---

## P1 - Verbleibende offene Punkte

### COVERAGE-001: Backend-Testabdeckung repo-weit weiter zu niedrig

- Gesamtabdeckung ist fuer ein ERP-System weiterhin zu niedrig. `100%` repo-weit ist kurzfristig kein belastbares Ziel.
- Neu ist ein Ratchet fuer kritische Kernpfade ueber `scripts/check_critical_backend_coverage.py` und `.github/workflows/quality-gate.yml`.
- Der naechste sinnvolle Schritt ist systematischer Ausbau der Testtiefe fuer Finance-Posting, Bestandsfuehrung, Tenant-Isolation und Integrations-Governance.

### DOMAIN-PARITY-001: Fachliche Tiefe der Domains ist weiterhin ungleich

- Der Repo-Schnitt ist breit, aber nicht alle Domaenen haben dieselbe fachliche Tiefe, denselben Testgrad oder dieselbe Integrationshaerte.
- Das ist ein laufendes Ausbauprogramm, kein einzelner Bugfix.

---

## P2 - Architektonisch offen / mittelfristig relevant

### NATS-001: Event-Bus jetzt im Docker-Dev-Stack automatisch aktiv

- **Dateien**: `docker-compose.yml`, `docker-compose.dev.yml`, `.env.example`, `app/infrastructure/eventbus/nats_publisher.py`, `app/infrastructure/eventbus/nats_consumer.py`
- **Aenderung**: Root- und Dev-Compose bringen NATS jetzt standardmaessig mit hoch; Backend laeuft dort automatisch mit `EVENT_BUS_ENABLED=true`, `EVENT_BUS_PROVIDER=nats`.
- **Verbleibend**: Nicht-Docker-Entwicklung kann weiterhin bewusst ohne NATS laufen; fachliche Last- und Betriebsprofile muessen ops-seitig abgestimmt bleiben.

### RAG-002: Obsidian als ergaenzende Knowledge-Quelle

**Abwaegung (2026-04-10):**

- **Pro Obsidian**: Kostenlos, keine laufenden DB-Kosten, Markdown-basiert, Git-versionierbar, starkes Plugin-Oekosystem, ideal fuer strukturiertes Prozesswissen (SOPs, Checklisten, Fachbegriffe).
- **Contra**: Kein nativer Multi-Tenant-Support, kein Server-Modus, fuer API-Zugriff braeuchte es einen File-Watcher oder Sync-Job.
- **Empfehlung**: Obsidian als redaktionelle Pflegeflaeche fuer Wissensbasis-Eintraege nutzen; Sync-Job spaeter nachziehen.

### ARCH-DOM-001: Domain-Ownership ist jetzt pruefbar, aber nicht fachlich „fertig“

- `scripts/check_domain_table_ownership.py` prueft jetzt representative Tabellenbesitzregeln.
- Historisch gewachsene Legacy-Placements sind dokumentiert und bewusst toleriert, z. B.:
  - `domain_crm.sales_*`
  - `domain_inventory.agrar_*`
  - `domain_shared.agrar_sorten`
  - `domain_einkauf.kontrakte`
- Diese Placements sind damit transparent, aber nicht automatisch fachlich final.

---

## P4 - Externe Abhaengigkeiten (nicht repo-seitig loesbar)

### EXT-001: Live-Credentials und Zielsystem-URLs

- Superglue-Connectors, L3-Import, Erstinstallation und Finance-Export brauchen produktive Tenant-Secrets, Zielsystem-URLs und Ops-Alerting-Werte, die ausserhalb des Repos gepflegt werden.
- Repo-seitig ist die Bootstrap-Reife jetzt besser vorbereitet ueber `.env.example`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md).

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
| NATS JetStream | Dev-auto / ops-konfigurierbar | Docker-Dev startet NATS automatisch |
| Keycloak/OIDC | produktiv | RS256/JWKS, dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB/RAG | produktiv (erweitert) | Artikel + Kunden + Kontrakte + Futtermittel + Knowledge |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools provisioniert |
| Voice-Kanal | provider-ready | Whisper/Azure/OpenAI TTS konfigurierbar, Browser-Fallback |
| Tenant-Enforcement | Middleware | `TenantEnforcementMiddleware` validiert `X-Tenant-ID` zentral |

---

## Zuletzt geschlossene Punkte (2026-04-12)

- ~~DB-BOOT-001: Erstinstallation ueber Docker/Alembic war nicht deterministisch abgesichert~~ -> `python scripts/init_db.py` laeuft jetzt auf leerer Postgres-DB bis `head`; `scripts/check_required_domain_schemas.py` prueft die Mehr-Domaenen-Struktur; `scripts/smoke_first_install_docker.ps1/.sh` liefern den reproduzierbaren Docker-Smoke.
- ~~ARCH-DOM-001 war offen~~ -> `scripts/check_domain_table_ownership.py` prueft jetzt fachliche Tabellen-Zuordnung inklusive dokumentierter Legacy-Placements.
- ~~COVERAGE-ERP-001 war offen~~ -> `scripts/check_critical_backend_coverage.py` fuehrt einen CI-Ratchet fuer kritische Kernpfade ein; neue Tests decken Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement ab.
- ~~NATS-DEV-001 war offen~~ -> `docker-compose.yml`, `docker-compose.dev.yml` und `.env.example` starten und konfigurieren NATS im Dev-Betrieb automatisch.
- ~~INT-BOOT-001 war offen~~ -> `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md) liefern den repo-seitigen Bootstrap- und Readiness-Pfad fuer OIDC, NATS, Superglue, Voice und CRM-Downstream.
- ~~OP-ROLL-049 bis OP-ROLL-072 (Fallkopf-Rollout Welle 3) waren reserviert~~ -> alle 24 Slices abgeschlossen: Dunning-Editor, 6 Lager-Masken (Bestandsuebersicht, Korrektur, Ein-/Auslagerung, Bewegungen, Inventur), Terminal, 3 Qualitaet-Masken (Ausnahmen, Reklamationen, Labor-Detail), Frachtbriefe und Wiegungen tragen jetzt denselben leichten operativen Fallkopf. 11 weitere Finance/FIBU-Masken hatten den Header bereits aus frueheren Sessions.

---

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen Doku, Implementierung, Fachlogik oder Benutzerfuehrung auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`
- `docs/project-context/operational-rollout-scope-2026-04-09.md`
- `docs/roadmap/status/2026-04-03-security-hardening-phase-2.md`
