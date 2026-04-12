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

## P1 — Verbleibende offene Punkte

### COVERAGE-001: Backend-Testabdeckung bei 45%

- Gesamtabdeckung ist fuer ein ERP-System niedrig. Kritische Pfade (Finance-Posting, Bestandsfuehrung, Tenant-Isolation) sollten >80% haben.

---

## P2 — Architektonisch offen / mittelfristig relevant

### NATS-001: Event-Bus disabled by default — aber jetzt config-aktivierbar

- **Dateien**: `app/infrastructure/eventbus/nats_publisher.py`, `nats_consumer.py`
- **Aenderung**: Publisher liest jetzt `EVENT_BUS_ENABLED` + `EVENT_BUS_PROVIDER=nats` aus Config. Aktivierung: `EVENT_BUS_ENABLED=true EVENT_BUS_PROVIDER=nats` in `.env`.
- **Verbleibend**: Architektur steht (DLQ, Idempotenz, Flow-Spine-Handler, Observability, Health-Check), aber im Dev-Betrieb laeuft NATS nicht mit.

### RAG-002: Obsidian als ergaenzende Knowledge-Quelle

**Abwaegung (2026-04-10):**

- **Pro Obsidian**: Kostenlos, keine laufenden DB-Kosten, Markdown-basiert, Git-versionierbar, starkes Plugin-Oekosystem, ideal fuer strukturiertes Prozesswissen (SOPs, Checklisten, Fachbegriffe). Kann als lokaler Markdown-Vault neben ChromaDB stehen.
- **Contra**: Kein nativer Multi-Tenant-Support, kein Server-Modus (Obsidian ist Desktop-App), fuer API-Zugriff braeuchte es einen File-Watcher oder Sync-Job der Markdown-Dateien in ChromaDB indiziert.
- **Empfehlung**: Obsidian als **redaktionelle Pflegeflaeche** fuer Wissensbasis-Eintraege nutzen. Ein einfacher Sync-Job (`scripts/obsidian_to_rag.py`) liest `.md`-Dateien aus einem konfigurierbaren Vault-Verzeichnis und fuettert sie ueber `indexer.index_knowledge()` in ChromaDB. Keine zusaetzlichen DB-Kosten, keine neue Infrastruktur, nur ein Dateipfad in der Config.
- **Konfiguration**: `OBSIDIAN_VAULT_PATH` in `.env` (optional, default: leer = deaktiviert).

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
| NATS JetStream | config-aktivierbar | `EVENT_BUS_ENABLED=true EVENT_BUS_PROVIDER=nats` |
| Keycloak/OIDC | produktiv | RS256/JWKS, dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB/RAG | produktiv (erweitert) | Artikel + Kunden + Kontrakte + Futtermittel + Knowledge |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools provisioniert |
| Voice-Kanal | Provider-ready | Whisper/Azure/OpenAI TTS konfigurierbar, Web Speech Fallback |
| Tenant-Enforcement | Middleware | `TenantEnforcementMiddleware` validiert X-Tenant-ID zentral |

---

## Zuletzt geschlossene Punkte (2026-04-10)

- ~~DB-BOOT-001: Erstinstallation ueber Docker/Alembic war nicht deterministisch abgesichert~~ -> `python scripts/init_db.py` laeuft jetzt auf leerer Postgres-DB bis `head`; `add_business_partners_tenant_id_20260219.py` und `perf_indexes_multitenant_20260408.py` sind fuer Neuinstallationen idempotent; `docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.dev.yml`, `Dockerfile`, `Dockerfile.backend` und `entrypoint.sh` starten den Backend-Prozess nicht mehr mit still verschluckten Migrationsfehlern oder Legacy-SQL-Tabellenpfaden; `scripts/check_required_domain_schemas.py` prueft im CI die zentrale Mehr-Domaenen-Struktur des ERP; `scripts/smoke_first_install_docker.ps1` und `scripts/smoke_first_install_docker.sh` liefern den reproduzierbaren Docker-Smoke fuer frische GitHub-Spiegel.
- ~~STUB-001: Mischfutter-Produktion war hartcodiert~~ -> `produktion_mischfutter.py` liest jetzt Verfuegbarkeit aus `futtermittel_einzelfutter`, Rezepte aus `futtermittel_rezepte`, persistiert Auftraege in `futtermittel_produktionsauftraege` mit echtem Bestandsabzug bei Freigabe und Rueckbuchung bei Storno.
- ~~STUB-002: Futtermittel-Stamm war Demo-Seed~~ -> Neues Domainmodell `app/infrastructure/models/futtermittel_models.py` mit 6 Tabellen (Einzelfutter, Mischfutter, Rezepte, Komponenten, Produktionsauftraege, Sorten). Vollstaendiges CRUD in `futter_stamm.py`. Migration: `futtermittel_sorten_produktion_20260410`.
- ~~STUB-003: Liquiditaetsuebersicht war Platzhalter~~ -> `liquidity.py` berechnet jetzt Liquiditaet aus OP-Debitoren/Kreditoren, Journal-Salden (Kontenklasse 1xxx) und 30-Tage-Prognose-Buckets.
- ~~STUB-004: Sortenregister war statische Liste~~ -> `agrar_varieties.py` hat jetzt volles CRUD gegen `domain_shared.agrar_sorten` mit Auto-Seed pro Tenant.
- ~~TENANT-001: Multi-Tenancy nur auf Endpoint-Ebene~~ -> Neue `TenantEnforcementMiddleware` in `app/middleware/tenant_enforcement.py` validiert X-Tenant-ID zentral auf allen API-Pfaden, setzt ContextVar pro Request und rejected fehlende/ungueltige Tenant-IDs.
- ~~VOICE-001: Voice-Kanal war Stub~~ -> `voice_adapter.py` unterstuetzt jetzt Whisper API (STT), OpenAI TTS, Azure Cognitive Speech und Web Speech API Fallback. Konfiguration ueber `VOICE_STT_PROVIDER` / `VOICE_TTS_PROVIDER`.
- ~~NATS-001: Event-Bus war hardcoded disabled~~ -> Publisher liest jetzt `EVENT_BUS_ENABLED` + `EVENT_BUS_PROVIDER` aus Config; Aktivierung per Env-Variable.
- ~~RAG-001: ChromaDB nur Artikel + Kunden~~ -> Indexer erweitert um `index_contracts()`, `index_feed()`, `index_knowledge()`, `index_all()`.
- ~~CRUD-001: 7 GET-only Endpoints~~ -> POST/PUT/DELETE fuer Disposition, Foerderung, Marketing, Zertifikate, Direct Debits und DMS-Images ergaenzt. Nur `config_service.py` verbleibt GET-only.
- ~~FE-001: downloadComingSoon~~ -> Durch echte DMS-Fehlermeldung ersetzt in `lieferanten-stamm.tsx`.
- ~~FE-002: Toast-only Actions~~ -> Audit-Korrektur: `charge-verfolgung.tsx` nutzt echte API via `useMemo`-Override; `kreditoren.tsx` navigiert bereits korrekt; `fahrzeug-stamm.tsx` hat echte API-Calls mit Error-Handling. Keine echten Toast-only-Bugs.
- ~~`POST /api/v1/compliance/pcn-meldungen` fehlte~~ -> jetzt vollstaendig implementiert in `compliance.py:818` mit UFI-Validierung und Tenant-Isolation
- ~~CRUD-002: config_service.py hat nur GET~~ -> `config_service.py` hat bereits vollstaendiges CRUD (GET/PUT/PATCH/DELETE) fuer Connectors, Reporting Units und Schedules. War faelschlich als offen dokumentiert.
- ~~OP-ROLL-007 bis OP-ROLL-012 (Fallkopf-Rollout) waren reserviert~~ -> alle 6 Slices abgeschlossen, 8 Kernmasken mit operativem Vorgangskopf, Register bewusst schlank gelassen und dokumentiert in `operational-rollout-scope-2026-04-09.md`
- ~~Settlement-, Mahn-, OP- und liefernahe Follow-up-Masken fielen noch aus dem gemeinsamen Arbeitsmodell heraus~~ -> `packages/frontend-web/src/pages/{annahme/abrechnung,einkauf/rechnungseingaenge-liste,einkauf/anlieferavis,einkauf/auftragsbestaetigung,finance/mahnwesen,finance/op-debitoren,finance/op-kreditoren}.tsx` tragen jetzt denselben leichten Vorgangskopf fuer Rueckstand, Freigabe-/Verbuchungsdruck, Blocker und naechste Aktion, weiterhin ausschliesslich aus bereits geladenen Daten.
- ~~Sammel- und Meldearbeitsplaetze in Einkauf, FIBU, Annahme und Labor liefen noch ohne einheitlichen leichten Operationsrahmen~~ -> `packages/frontend-web/src/pages/{einkauf/anlieferavis-liste,einkauf/auftragsbestaetigungen-liste,fibu/zahlungslaeufe,finance/ustva,fibu/elster-online,fibu/schnittstellen-center,annahme/warteschlange,labor/proben-liste,qualitaet/labor-liste}.tsx` fuehren jetzt denselben kompakten Fallkopf, Kontext und Timeline ausschliesslich aus bereits geladenen Daten und ohne zusaetzliche API-Last.
- ~~L3/FIBU-Operatorraeume waren noch uneinheitlich zwischen Journal, Checklisten, Zahlungslaeufen und physischem Waagenknoten~~ -> `packages/frontend-web/src/pages/{fibu/buchungsjournal,fibu/abschluss-checklist-detail,finance/zahlungslauf-kreditoren,finance/lastschriften-debitoren,fibu/buchhaltungsuebersicht,waage/liste}.tsx` nutzen jetzt denselben leichten Vorgangsrahmen fuer Revisionsdruck, Pflicht-/Mandatslage, Periodenkontext und physische Bottlenecks, weiterhin ohne Zusatz-Requests.
- ~~Bankabgleich, Payment-Matching, AP-Invoices sowie weitere FIBU-/Charge-/Logistik-Folgeraume liefen noch ohne konsistenten leichten Operationsrahmen~~ -> `packages/frontend-web/src/pages/{finance/bank-abgleich,finance/payment-matching,finance/ap-invoices-list,finance/ap-invoice-form,fibu/offene-posten,fibu/zahlungseingaenge,fibu/zahlungsvorschlaege,fibu/bwa,fibu/bilanz,charge/rueckverfolgung,charge/wareneingang,logistik/tourenplanung}.tsx` tragen jetzt denselben kompakten Fallkopf, Kontext und die kurze Timeline ausschliesslich aus bereits geladenen Daten und ohne zusaetzliche API-Last.
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
