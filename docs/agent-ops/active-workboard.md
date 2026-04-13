# Active Workboard

Stand: `2026-04-10`

Dieses Board ist bewusst schlank gehalten, damit Session-Starts und Agent-Handoffs weniger Kontext verbrauchen.

Archiv des vorherigen Boards:
- [active-workboard-2026-04-10-pre-slim.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/archive/active-workboard-2026-04-10-pre-slim.md)

## Arbeitsregel

- Nur aktive oder frisch abgeschlossene Slices bleiben hier sichtbar.
- Historische Serien wandern ins Archiv.
- Claim-Pflicht bleibt unveraendert:
  1. Slice auf `reserviert`
  2. Workboard committen
  3. erst dann implementieren

## Kurzstand

- Das gemeinsame operative Arbeitsmodell ist bereits in den priorisierten Kernmasken ausgerollt.
- Der Rollout-Scope ist dokumentiert in:
  - [operational-rollout-scope-2026-04-09.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/operational-rollout-scope-2026-04-09.md)
- Der naechste Block betrifft Sammel- und Follow-up-Masken mit echtem operativem Mehrwert.

## DOC-REF-002

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe ERP-Referenzdoku neutralisieren, Lizenz-/Referenzlage scharfziehen und direkte Nennungen des angefragten Systems aus den aktiven Repo-Dokumenten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Die Referenzanalyse bleibt fachlich brauchbar, benennt aber nur noch neutrale Vergleichsklassen bzw. permissive/kommerzielle Lizenzrisiken; direkte Nennungen des angefragten Systems sind aus den aktiven Projektkontext-Dateien entfernt.
**Erledigt:** Die aktive Referenzdatei wurde auf `docs/project-context/erp-reference-gap-analysis-amic-community-erp-fiori-2026-04-08.md` umgestellt; Tail-Plan, i18n-, Setup-, Roadmap- und Archivdoku nutzen jetzt neutrale Bezeichnungen; ein repo-weiter Textscan auf die direkte Nennung liefert keine Treffer mehr.
**Checks:** `rg -n -i "\\bodoo\\b" . --glob '!node_modules/**' --glob '!.git/**' --glob '!packages/frontend-web/node_modules/**' --glob '!venv/**' --glob '!coverage_html/**'`, `node scripts/docs-governance-check.cjs`

## DOC-REF-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Eine neutrale ERP-Referenzmatrix im Repo festhalten und daraus die naechsten sechs fachlichen Vertiefungs-Slices fuer VALEO ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Es gibt eine eigenstaendige Matrix mit Referenzmustern, Lizenz-/Uebernahmeregeln und VALEO-Istbild; daraus sind sechs konkrete Slices mit Zielbild und Prioritaet im Workboard abgeleitet.
**Erledigt:** `docs/project-context/erp-reference-matrix-2026-04-12.md` verdichtet jetzt fachliches Tiefenbild, Community-ERP-Referenzmuster, Fiori-/OpenUI5-UIX-Muster, Lizenzregeln und konkrete Slice-Ableitung; die naechsten sechs fachlichen Vertiefungs-Slices sind daraus direkt abgeleitet.
**Checks:** `node scripts/docs-governance-check.cjs`

## DOM-FIN-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** FIBU-Operatorpfade fuer Abschluss, Reorganisator, Zinswesen und Revisionssicht semantisch verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/finance/*`, `packages/frontend-web/src/pages/fibu/*`, relevante Finance-/FIBU-Read-Models und Endpunkte
**Abnahmekriterien:** Abschluss- und FIBU-Operatorraeume tragen denselben klaren Status-, Fristen-, Revisions- und Folgeaktionsrahmen.
**Fortschritt:** Die erste Codewelle zieht den Operatorrahmen auf `fibu/abschluss-cockpit.tsx`; die zweite Welle verdichtet jetzt `fibu/schnittstellen-center.tsx` mit Connector-Readiness, Perioden-/Profilrisiko und klarer Folgeaktion ohne neue Requests.

## DOM-SUPPLY-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** Die physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` fachlich und statusseitig durchgaengig harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/annahme/*`, `packages/frontend-web/src/pages/waage/*`, `packages/frontend-web/src/pages/charge/*`, `packages/frontend-web/src/pages/logistik/*`
**Abnahmekriterien:** Jeder Uebergabepunkt zeigt Objektbezug, Abweichung, naechste Aktion und Folgeobjekt konsistent.
**Fortschritt:** Die erste Codewelle verdichtet Uebergaberisiken in `waage/liste.tsx` und `logistik/tourenplanung.tsx`; die zweite Welle zieht `charge/wareneingang.tsx` mit Scan-Assist, Kettenrisiko und Operator-Schritt in denselben physischen Rahmen.

## DOM-PROC-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation auf echte Folgefaelle heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/einkauf/*`, relevante Beschaffungsendpunkte, Dokument- und Kommunikationspfade
**Abnahmekriterien:** Beschaffungsfaelle bilden Matching-Ausnahmen, Nachforderung und Folgekommunikation als echte Arbeitsobjekte ab.
**Fortschritt:** Die erste Codewelle hebt `einkauf/rechnung-abgleich.tsx` auf einen echten Ausnahme- und Folgefallrahmen; die zweite Welle zieht `einkauf/rechnungseingang.tsx` mit Abweichungsdruck, Wareneingangsbezug und naechster Freigabeaktion nach.

## DOM-CON-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** Kontraktfixierung, Marktbewertung, Mahnung und Engagement als vollwertige Operatorraeume ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/kontrakte/*`, `packages/frontend-web/src/pages/contracts-v2.tsx`, relevante Kontraktendpunkte
**Abnahmekriterien:** Fixierungs-, Markt- und Mahnlogik ist nicht nur sichtbar, sondern als klarer Operatorpfad bedienbar.
**Fortschritt:** Die erste Codewelle zieht Operator-Druck, ungesicherte Mengen und naechsten Pfad in `contracts-v2.tsx` hoch; die zweite Welle verdichtet `kontrakte/KontraktPositionsmonitor.tsx` zum echten Exposure-, Fixierungs- und Mahnoperatorraum.

## DOM-CRM-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** CRM-/Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/crm/*`, `packages/frontend-web/src/pages/service/*`, zugehoerige APIs und Agent-Ops-Verknuepfung
**Abnahmekriterien:** CRM und Service tragen denselben Fallbezug, Ownership-Rahmen und Abschlusspfad.
**Fortschritt:** Die erste Codewelle verdichtet Ownership-/Folgeobjektlogik in `crm/kunden-stamm-modern/LegacyKundenStammModern.tsx` und `service/anfrage-detail.tsx`; die zweite Welle zieht `crm/opportunity-detail.tsx` mit Deal-Risiko, Angebotspfad und naechster Folgeaktion nach.

## DOM-DOC-003

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/pages/dokumente/*`, `packages/frontend-web/src/pages/compliance/*`, `packages/frontend-web/src/pages/fibu/atlas.tsx`, `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx`
**Abnahmekriterien:** Dokumente und Meldungen zeigen revisionsrelevanten Nachweisstatus, Rueckmeldungspfad und Wiedervorlage konsistent.
**Fortschritt:** Die erste Codewelle fuehrt Nachweisrisiko in `dokumente/ablage.tsx` und Rueckmeldungsrisiko in `compliance/meldewesen-konsole.tsx` zusammen; die zweite Welle verdichtet `fibu/atlas.tsx` mit Artefakt-, Rueckmelde- und Objektkettenkontext zum revisionsnahen Nachweisfall.

## COV-FIN-002

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Coverage-Tiefe fuer FIBU-Kernpfade aufbauen: Journal, Zahlungslaeufe, DATEV/ELSTER-nahe Follow-up-Logik und Abschlusskontext.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, relevante Finance-/FIBU-Services und Endpunkte
**Abnahmekriterien:** Kritische FIBU-Kernpfade besitzen gezielte Tests statt nur allgemeiner Gesamtquote; Ratchet kann fuer Finance spaeter angehoben werden.

## COV-INV-002

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Coverage fuer Bestandsfuehrung, Lagerbewegung, Inventur und physische Objektkette erweitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, Inventory-/Ops-/Logistik-Endpunkte und Services
**Abnahmekriterien:** Stock-Movements, Inventur und kritische Lagerpfade sind ueber gezielte Tests gegen Regressionen abgesichert.

## COV-INT-002

**Von:** Codex
**Stand:** reserviert
**Ziel des Slices:** Integrations-Governance tiefer testen: Superglue, Secrets, Outbound-Gates, Bootstrap und Tenant-Schutz.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, `app/services/**`, `app/integrations/**`
**Abnahmekriterien:** Integrationsnahe Kernpfade werden nicht nur konfiguriert, sondern auch testseitig breiter abgesichert.

## DOM-FIN-002

**Von:** Codex
**Stand:** offen
**Ziel des Slices:** FIBU-/L3-Parity fachlich weiter vertiefen, insbesondere Abschluss-, Revisions- und Operator-Pfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante FIBU-/Finance-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Finance/FIBU ist nicht nur breit, sondern in den priorisierten Operatorpfaden semantisch konsistenter und tiefer.

## DOM-INV-002

**Von:** Codex
**Stand:** offen
**Ziel des Slices:** Inventory-/Ops-/Logistik-Parity weiterziehen, insbesondere physische Objektkette, Queue, Wiegung, Fracht und Charge.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante Inventory-/Ops-/Logistik-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Die physische Kette ist fachlich tiefer und konsistenter ueber mehrere Kernmasken und Backend-Pfade hinweg.

## DOM-CRM-002

**Von:** Codex
**Stand:** offen
**Ziel des Slices:** CRM-/Sales-/Service-Parity angleichen, insbesondere Vorgangsbezug, Folgeobjekte und echte Arbeitsobjekte statt Listenbreite.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante CRM-/Sales-/Service-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** CRM-/Sales-/Service-Raeume besitzen vergleichbare fachliche Tiefe in den priorisierten Kernobjekten.

## ARCH-DOM-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fachliche Schema-Zuordnung der Tabellen nicht nur behaupten, sondern mit einem expliziten Audit- und Guardrail-Pfad pruefbar machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `scripts/check_required_domain_schemas.py`, neues Domain-Mapping-Audit unter `scripts/`
**Abnahmekriterien:** Es gibt einen automatisierten Check fuer Kern-Schemaanker plus fachlich schiefe bzw. bewusst tolerierte Cross-Domain-Zuordnungen.
**Erledigt:** `scripts/check_domain_table_ownership.py` prueft jetzt representative Exact-Ownership-Regeln, Prefix-Regeln und dokumentierte Legacy-Placements; `scripts/smoke_first_install_docker.ps1/.sh` fuehren den Ownership-Check nach frischer Migration mit aus.
**Checks:** `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55437`, `python scripts/check_domain_table_ownership.py` (gegen frische Smoke-DB)

## COVERAGE-ERP-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Coverage fuer ERP-Kernpfade auf einen belastbaren Ratchet-Pfad bringen statt pauschal 100% zu behaupten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.github/workflows/quality-gate.yml`, `pytest.ini`, neue Coverage-Guard-Skripte/Tests unter `scripts/` und `tests/`
**Abnahmekriterien:** CI prueft einen expliziten Mindeststandard fuer kritische Pfade; die Doku benennt ehrlich, was repo-seitig erreichbar ist und was nicht.
**Erledigt:** `.github/workflows/quality-gate.yml` fuehrt jetzt `scripts/check_critical_backend_coverage.py` nach pytest aus; neue Tests fuer Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement stabilisieren die Kernpfade; die Doku benennt `100%` repo-weit explizit nicht als kurzfristig belastbares Ziel.
**Checks:** `pytest tests/test_event_bus_runtime.py tests/test_integration_bootstrap.py tests/test_secrets_vault.py tests/test_security_startup_guards.py tests/test_nats_event_handlers.py tests/test_tenant_enforcement.py -q`, `python scripts/check_critical_backend_coverage.py`

## NATS-DEV-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Event-Bus/NATS im Dev-Betrieb automatisch mit Docker laufen lassen, statt nur config-aktivierbar zu sein.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docker-compose*.yml`, `.env.example`, ggf. `app/core/config.py`, Event-Bus-Tests
**Abnahmekriterien:** Standard-Dev-Compose bringt NATS mit hoch und Backend laeuft dabei automatisch auf NATS statt Memory-Fallback.
**Erledigt:** `docker-compose.yml` und `docker-compose.dev.yml` starten NATS jetzt mit JetStream-Healthcheck; die jeweiligen Backend-Services laufen dort automatisch mit `EVENT_BUS_ENABLED=true`, `EVENT_BUS_PROVIDER=nats`, `EVENT_BUS_NATS_URL=nats://nats:4222`; `.env.example` spiegelt denselben Dev-Pfad.
**Checks:** `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`

## INT-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe Integrationen soweit repo-seitig vorbereiten, dass lokale oder frische Installationen nicht an fehlenden Bootstrap-Hinweisen fuer Secrets, Zielsysteme und Ops-Parameter scheitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.env.example`, `scripts/`, ggf. Integrations-README unter `docs/`
**Abnahmekriterien:** Es gibt einen reproduzierbaren Readiness-/Bootstrap-Check fuer Live-Integrationen und klare env-/secret-Vorlagen fuer lokale bzw. ops-seitige Aktivierung.
**Erledigt:** `app/services/integration_bootstrap.py` verdichtet OIDC-, NATS-, Superglue-, Voice- und CRM-Downstream-Readiness; `scripts/check_integration_bootstrap.py` reportet bzw. failt optional strikt; `.env.example` fuehrt die zentralen Bootstrap-Variablen; `docs/project-context/integration-bootstrap-readiness-2026-04-12.md` dokumentiert die repo-seitig vorbereiteten und die ops-seitig verbleibenden Themen.
**Checks:** `python scripts/check_integration_bootstrap.py`, `pytest tests/test_integration_bootstrap.py -q`

## DOCS-README-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Root-README gegen den aktuellen Repo-, Delivery- und Bootstrap-Stand aufraeumen und wieder als belastbaren Einstiegspunkt ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `README.md`
**Abnahmekriterien:** README ist encoding-sauber, verweist auf die echten Source-of-Truth-Dokumente, ueberzeichnet den Produktreifegrad nicht und bildet den aktuellen Docker-/Bootstrap-Pfad korrekt ab.
**Erledigt:** `README.md` ist von veralteter Langform und Mojibake auf einen knappen, ehrlichen Einstiegspunkt umgestellt; der aktuelle Reifegrad, der Alembic-/Docker-Erstinstallationspfad, die Mehr-Domaenen-Struktur, lokale Prüfkommandos sowie die maßgeblichen Source-of-Truth-Dokumente sind jetzt korrekt referenziert; ueberspannte Vollstaendigkeits- und Production-Claims wurden entfernt.
**Checks:** `node scripts/docs-governance-check.cjs`, `rg -n "ð|â|Ã|�" README.md`

## DB-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Erstinstallation ueber Alembic und Docker auf leerer Postgres-DB deterministisch machen und die Mehr-Domaenen-Struktur automatisiert pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/env.py`, `alembic/versions/*`, `scripts/init_db.py`, `scripts/check_required_domain_schemas.py`, `docker-compose*.yml`, `Dockerfile*`, `.github/workflows/quality-gate.yml`
**Abnahmekriterien:** `python scripts/init_db.py` laeuft auf leerer DB bis `head`; der Compose-/Docker-Pfad verschluckt keine Migrationsfehler; eine Strukturpruefung bestaetigt zentrale ERP-Domaenen und Kernobjekte.
**Erledigt:** `add_business_partners_tenant_id_20260219.py` ist jetzt neuinstallationssicher und ersetzt den falschen globalen Business-Partner-Unique-Pfad; `perf_indexes_multitenant_20260408.py` legt optionale Indexe nur noch fehlertolerant an; `docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.dev.yml`, `entrypoint.sh`, `Dockerfile` und `Dockerfile.backend` starten Backend-Prozesse erst nach erfolgreichem `python scripts/init_db.py`; Legacy-SQL-Tabellenpfade sind aus dem Dev-Erststart entfernt; `scripts/check_required_domain_schemas.py` verifiziert die zentrale Mehr-Domaenen-Struktur im CI und `scripts/smoke_first_install_docker.ps1/.sh` liefern einen reproduzierbaren First-Install-Smoke fuer frische GitHub-Spiegel.
**Checks:** frische Postgres-Container-DB via `python scripts/init_db.py`, `python scripts/check_required_domain_schemas.py`, `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434`, `python -m py_compile scripts/init_db.py scripts/check_required_domain_schemas.py alembic/env.py alembic/versions/add_business_partners_tenant_id_20260219.py alembic/versions/perf_indexes_multitenant_20260408.py`, `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.staging.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-013

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme-Abrechnung als echten Settlement-Fall mit Ressourcen-, Preis- und Freigabekontext surfacen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
**Abnahmekriterien:** Abrechnung zeigt Fallkopf, knappen Kontext und Timeline ueber dem Settlement-Arbeitsplatz, ohne neue API-Last.
**Erledigt:** `annahme/abrechnung.tsx` zeigt jetzt Settlement-Fallkopf, Abrechnungskontext und Verlauf aus bereits vorhandenen Preview-/Campaign-/Settlement-Daten direkt ueber dem Self-Billing-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-014

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rechnungseingaenge-Liste als operativen Sammelarbeitsplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
**Abnahmekriterien:** Die Liste zeigt klaren Freigabe-/Verbuchungsdruck und die naechste Bulk-Aktion, ohne den Listenraum zu ueberladen.
**Erledigt:** `rechnungseingaenge-liste.tsx` verdichtet jetzt Freigabe-/Verbuchungsstau, Summenlage und die naechste Bulk-Aktion ueber der bestehenden Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-015

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Mahnwesen als echten Follow-up-Fall mit Owner-, Risiko- und Governance-Sicht verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
**Abnahmekriterien:** Mahnwesen zeigt Mahndruck, Zins-/Connector-Lage und naechste FIBU-Aktion direkt vor dem Objektarbeitsplatz.
**Erledigt:** `finance/mahnwesen.tsx` fuehrt jetzt Mahndruck, Zins-/Connector-Kontext und naechste FIBU-Massnahme als kompakten Follow-up-Kopf ueber dem Objektarbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-016

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Offene-Posten-Raeume fuer Debitoren und Kreditoren auf eine gemeinsame operative Sicht ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/{op-debitoren,op-kreditoren}.tsx`
**Abnahmekriterien:** Beide OP-Raeume zeigen Rueckstand, Risiko und naechste Massnahme konsistent und schlank.
**Erledigt:** `op-debitoren.tsx` und `op-kreditoren.tsx` nutzen jetzt dasselbe leichte OP-Modell fuer Rueckstand, Mahn-/Ueberfaelligkeitsdruck, Kontext und Folgeaktion, ohne die Facharbeit in Tabellen und Dialogen zu verdoppeln.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-017

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufsnahe Dokumenten-/Lieferobjekte mit leichtem Vorgangsbild harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis,auftragsbestaetigung}.tsx`
**Abnahmekriterien:** Beide Objektmasken gewinnen Blocker-, Kontext- und naechste-Aktion-Sicht ohne Doppelung zur Fachmaske.
**Erledigt:** `anlieferavis.tsx` und `auftragsbestaetigung.tsx` haben jetzt einen kompakten Logistik-/Pruefkopf ueber der ObjectPage und bleiben darunter fachlich unveraendert tief.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-018

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und offene Restgrenzen fuer den naechsten Operativ-Rollout dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Es ist dokumentiert, welche Sammel- und Follow-up-Masken jetzt unter dem Zielbild laufen und welche bewusst weiterhin schlank bleiben.
**Erledigt:** Das schlanke Workboard und die Scope-Doku decken jetzt auch Sammel- und Follow-up-Masken fuer Settlement, Rechnungseingaenge, Mahnwesen, OP-Raeume sowie einkaufsnahe Lieferobjekte ab.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-019

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufslisten fuer Avis und Auftragsbestaetigungen als operative Sammelarbeitsplaetze verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis-liste,auftragsbestaetigungen-liste}.tsx`
**Abnahmekriterien:** Beide Listen zeigen Stau, Blocker und naechste Bulk-Aktion ueber der Liste, ohne den Tabellenraum zu ueberfrachten.
**Erledigt:** `anlieferavis-liste.tsx` und `auftragsbestaetigungen-liste.tsx` fuehren jetzt denselben leichten Sammelvorgangskopf fuer Liefer- und Freigabestau ueber der bestehenden ListReport-Facharbeit.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-020

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungslaeufe und UStVA/ELSTER als echte Finance-Follow-up-Raeume verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{fibu/zahlungslaeufe,finance/ustva,fibu/elster-online}.tsx`
**Abnahmekriterien:** Die Seiten zeigen FIBU-Druck, Fristen und naechste Massnahme ueber dem Arbeitsraum.
**Erledigt:** `zahlungslaeufe.tsx`, `finance/ustva.tsx` und `fibu/elster-online.tsx` zeigen jetzt Fristen, Freigabedruck und Einreichungs-/Exportpfad als leichten Finance-Follow-up-Rahmen ueber Wizard bzw. Fachformular.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-021

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Schnittstellen- und Meldefolgearbeitsplatz mit demselben schlanken Fallmodell harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx`, ggf. angrenzende FIBU-Follow-up-Seiten.
**Abnahmekriterien:** Schnittstellen-Center zeigt operativen Druck, Risiken und naechste Aktion ohne KPI-Dopplung.
**Erledigt:** `fibu/schnittstellen-center.tsx` fuehrt Connector-, Revisions- und Periodenlage jetzt als technischen FIBU-Fallkopf mit kurzer Timeline und Masterdatenkontext.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-022

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme- und Queue-Sammelraum mit derselben Leitlogik weiterziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:** Warteschlange zeigt operativen Stau, aktuelle Prioritaet und naechste Massnahme ueber der Liste.
**Erledigt:** `annahme/warteschlange.tsx` verdichtet Queue-Druck, Objektkettenlage und Bottleneck-Hinweis jetzt als operativen Annahmekopf ueber der bestehenden Operator-Oberflaeche.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-023

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-/Qualitaets-Sammelarbeitsplaetze auf den leichten Operationsrahmen heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{labor/proben-liste,qualitaet/labor-liste}.tsx`
**Abnahmekriterien:** Laborlisten zeigen Probenstau, kritische Faelle und naechste Folgeaktion ueber der Liste.
**Erledigt:** `labor/proben-liste.tsx` und `qualitaet/labor-liste.tsx` zeigen jetzt offenen Analyse- und Probenstau, Labor-/Chargekontext und die naechste Folgeaktion ueber den Tabellen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-024

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und Restgrenzen nach der dritten Rollout-Welle erneut komprimiert dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Der Rollout bleibt nachvollziehbar und weiterhin bewusst schlank.
**Erledigt:** Scope und Open-Gaps dokumentieren jetzt die dritte Welle fuer Einkaufslisten, FIBU-Follow-up, Schnittstellen, Queue und Laborraeume weiterhin als leichten Rollout ohne Zusatz-Requests.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-025

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditorenraum als FIBU-Profiarbeitsplatz mit echter Folgeaktion statt Info-Toast vertiefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/kreditoren.tsx`
**Abnahmekriterien:** `fibu/kreditoren.tsx` fuehrt DATEV-/Exportpfade als belastbare Folgeaktion ohne lokale Quittungs-Toastlogik.
**Erledigt:** `fibu/kreditoren.tsx` ist jetzt als echter Follow-up-Arbeitsraum mit Fallkopf, Kontext und Timeline verdichtet; DATEV-Export fuehrt direkt in den Buchungsuebergabe-Raum statt lokaler Info-Toast.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-026

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lieferanten-Dokumentraum mit realem Downloadverhalten statt TXT-Fallback professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`
**Abnahmekriterien:** Dokumentdownload in `lieferanten-stamm.tsx` nutzt nur echte Artefaktpfade und zeigt klare Fehlerfuehrung ohne pseudo-download.
**Erledigt:** `lieferanten-stamm.tsx` nutzt jetzt nur noch den echten Downloadpfad; pseudo-TXT-Fallback ist entfernt und Fehlersituationen zeigen klaren DMS-/Artefakt-Hinweis.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-027

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fuhrpark-Funktionsaktionen robust und revisionssicher machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fuhrpark/fahrzeug-stamm.tsx`
**Abnahmekriterien:** Drucker-/Druck-/Unfall-/Loesch-Aktionen behandeln Fehler sauber und quittieren nicht mehr blind.
**Erledigt:** `fuhrpark/fahrzeug-stamm.tsx` fuehrt Setup-, Druck-, Unfall- und Loesch-Aktionen jetzt mit try/catch, klaren Fehlertoasts und Loeschbestaetigung aus.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-028

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Charge-Verfolgung von fragiler Static-Toast-Konfiguration auf belastbaren Runtime-Aktionspfad ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/futtermittel/charge-verfolgung.tsx`
**Abnahmekriterien:** Bulk-Aktionen in der Charge-Verfolgung sind eindeutig runtime-gebunden und enthalten keine toten Static-Action-Reste.
**Erledigt:** `futtermittel/charge-verfolgung.tsx` fuehrt keine static Toast-BulkActions mehr; alle Massenaktionen laufen nur noch ueber den runtime-verdrahteten Aktionspfad.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-029

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/FIBU-Monatswerte als Fiori-artigen Operatorraum mit klaren Folgeaktionen und Kontrolldichte veredeln.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/monatswerte.tsx`
**Abnahmekriterien:** Monatswerte liefern klaren Fallkopf, Risiken und naechste Aktion ohne Zusatz-Requests, konsistent zum Operational-Modell.
**Erledigt:** `fibu/monatswerte.tsx` hat jetzt denselben leichten Fallrahmen fuer L3/FIBU-Auswertung (Status, Risiken, naechste Aktion) ohne neue Datenabfragen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-030

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/Cutover-nahe Buchungsuebergabe als FIBU-Leitstand mit Governance- und Revisionskontext vervollstaendigen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/schnittstelle-fibu.tsx`
**Abnahmekriterien:** Schnittstelle-FIBU zeigt operativen Druck, Revisions-/Cutover-Kontext und belastbare Folgewege ohne Platzhalteraktionen.
**Erledigt:** `fibu/schnittstelle-fibu.tsx` zeigt jetzt Fallkopf, Timeline und Revisions-/Cutover-Kontext fuer den Buchungsuebergabeprozess, inklusive klarer Folgefuehrung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-031

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsjournal als FIBU-Operatorraum mit Revisionsdruck, Periode und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchungsjournal.tsx`
**Abnahmekriterien:** `fibu/buchungsjournal.tsx` zeigt Fallkopf, Kontext und Timeline aus bereits geladenen Journaldaten und fuehrt DATEV-/Stornofolge ohne Blindflug.
**Erledigt:** `fibu/buchungsjournal.tsx` fuehrt Journalbuchungen jetzt als Revisionsfall mit Fallkopf, Referenzkontext, Timeline und direktem Exportpfad in die Buchungsuebergabe.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-032

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Abschluss-Checkliste als echter Close-Fall mit Pflichtdruck, Owner und Flow-Spine-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/abschluss-checklist-detail.tsx`
**Abnahmekriterien:** `abschluss-checklist-detail.tsx` verdichtet Pflichtquote, Blocker und naechste Abschlussaktion oberhalb der Checkliste.
**Erledigt:** `abschluss-checklist-detail.tsx` zeigt jetzt den Close-Fall mit Pflichtdruck, Flow-Spine-Bezug, Blockern und kompakter Vorgangssicht ueber der Checkliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-033

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditoren-Zahlungslauf als Fiori-artigen Zahlungsoperatorraum mit Governance- und Freigabedruck heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
**Abnahmekriterien:** `zahlungslauf-kreditoren.tsx` zeigt kompakten Zahlungsfallkopf, Kontext und Timeline ohne Zusatz-Requests.
**Erledigt:** `zahlungslauf-kreditoren.tsx` fuehrt den Kreditorenlauf jetzt mit Freigabe-, Skonto- und Ausfuehrungsdruck ueber dem bestehenden SEPA-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-034

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lastschriftlauf als Debitoren-Follow-up mit Mandats-, Frist- und Ausfuehrungsdruck darstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
**Abnahmekriterien:** `lastschriften-debitoren.tsx` bekommt denselben leichten Vorgangsrahmen fuer Mandatslage, Freigabe und Export.
**Erledigt:** `lastschriften-debitoren.tsx` surfact Mandatsluecken, Debitorenlauf und Freigabestatus jetzt als kompakten Follow-up-Rahmen ueber dem ObjectPage-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-035

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchhaltungsuebersicht als L3/FIBU-Cockpit mit Perioden- und Schnittstellenlage professionell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchhaltungsuebersicht.tsx`
**Abnahmekriterien:** `buchhaltungsuebersicht.tsx` zeigt kompakten Operatorrahmen fuer Periodenlage, Exportpfad und Revisionskontext.
**Erledigt:** `fibu/buchhaltungsuebersicht.tsx` verdichtet Periodenlage, Revisionskontext und Folgepfade jetzt als L3/FIBU-Cockpit ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-036

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Waagenliste als physischer Leitknoten auf das einheitliche Fallmodell ziehen, ohne die bestehende Uebersicht zu ueberladen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/liste.tsx`
**Abnahmekriterien:** `waage/liste.tsx` fuehrt kompakten Fallkopf, Kontext und Timeline fuer den physischen Kettenzustand aus vorhandenen Daten.
**Erledigt:** `waage/liste.tsx` nutzt jetzt denselben leichten Fallrahmen fuer Bottleneck, Eichlage und die physische Kette direkt ueber der Operatorliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-037

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bankabgleich als echter Klaerungs- und Ausgleichsfall mit Owner, Matching-Druck und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
**Abnahmekriterien:** `bank-abgleich.tsx` nutzt den leichten Fallrahmen ohne neue Requests und macht offene Matching-Lage sofort lesbar.
**Erledigt:** `finance/bank-abgleich.tsx` verdichtet Importstand, Abgleichsdifferenz, Zuordnungsdruck und naechste Aktion jetzt direkt ueber dem Object-Page-Arbeitsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-038

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Payment-Matching als FIBU-Klaerungsarbeitsplatz mit Kontext, Timeline und Folgepfad professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/payment-matching.tsx`
**Abnahmekriterien:** `payment-matching.tsx` fuehrt Rueckstand, Matching-Risiko und naechste Aktion komprimiert ueber dem Arbeitsraum.
**Erledigt:** `finance/payment-matching.tsx` surfact Matching-Stau, manuellen Klaerungsbedarf und Importkontext als kompakten Vorgangsrahmen ohne Zusatz-Last.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-039

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoices-Liste als operativer Pruef- und Freigabestauplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx`
**Abnahmekriterien:** `ap-invoices-list.tsx` zeigt Stau, Blocker und naechste Sammelaktion aus vorhandenen Listen-/Statusdaten.
**Erledigt:** `finance/ap-invoices-list.tsx` zeigt jetzt Freigabestau, buchbare Rechnungen und die naechste Sammelaktion direkt ueber der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-040

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoice-Form als echter Pruef- und Buchungsfall mit Governance- und Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx`
**Abnahmekriterien:** `ap-invoice-form.tsx` erhaelt den leichten Fallrahmen fuer Freigabe, Blocker und naechste Massnahme ohne neue API-Last.
**Erledigt:** `finance/ap-invoice-form.tsx` fuehrt Freigabestatus, Buchbarkeit und Summenlage jetzt als kompakten Pruef- und Buchungsfall.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-041

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Offene-Posten-Gesamtraum als operatorischer Sammelfall zwischen Debitoren und Kreditoren verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/offene-posten.tsx`
**Abnahmekriterien:** `fibu/offene-posten.tsx` zeigt OP-Druck, Ausgleichslage und Folgeweg ueber dem Arbeitsraum.
**Erledigt:** `fibu/offene-posten.tsx` verdichtet OP-Druck, Ueberfaelligkeit und Mahnfolge als klares Arbeitsbild vor der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-042

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungseingaenge als echter Clearing- und Rueckstandsraum mit kompaktem Vorgangsbild heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungseingaenge.tsx`
**Abnahmekriterien:** `zahlungseingaenge.tsx` surfact Rueckstand, Abgleichslage und naechste Aktion oberhalb der Facharbeit.
**Erledigt:** `fibu/zahlungseingaenge.tsx` fuehrt Rueckstand, Trefferquote und Import-/Klaerungskontext jetzt als einheitlichen Clearing-Rahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-043

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungsvorschlaege als FIBU-Entscheidungsraum mit Priorisierung und Governance-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungsvorschlaege.tsx`
**Abnahmekriterien:** `zahlungsvorschlaege.tsx` zeigt Prioritaet, Liquiditaetsdruck und naechste Folgeaktion ohne neue Requests.
**Erledigt:** `fibu/zahlungsvorschlaege.tsx` zeigt jetzt Prioritaet, Skonto-Potenzial und Zahlungsfreigabe als kompakten Entscheidungsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-044

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** BWA als Fiori-artigen Analysearbeitsplatz mit Perioden-, Abweichungs- und Folgekontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bwa.tsx`
**Abnahmekriterien:** `bwa.tsx` fuehrt Fallkopf, Kontext und Timeline aus bereits geladenen Auswertungsdaten.
**Erledigt:** `fibu/bwa.tsx` verdichtet Periodenlage, Ergebnisabweichung und Folgeaktion als leichten Analysearbeitsplatz ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-045

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bilanz als L3/FIBU-Abschlussraum mit Risiko- und Folgepfad konsistent zum neuen Arbeitsmodell ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bilanz.tsx`
**Abnahmekriterien:** `bilanz.tsx` liefert kompakten Operatorrahmen fuer Abschlusslage, Revisionskontext und Drilldown-Folgewege.
**Erledigt:** `fibu/bilanz.tsx` fuehrt Bilanzsumme, EK-Quote, Ausgleichslage und Abschlussfolge nun als kompakten Abschlussrahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-046

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rueckverfolgung als physischer Ausnahme- und Nachweisfall mit Charge-/Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/rueckverfolgung.tsx`
**Abnahmekriterien:** `charge/rueckverfolgung.tsx` zeigt Status, Blocker und Folgewege fuer Charge-/Nachweisfaelle ohne neuen Datenpfad.
**Erledigt:** `charge/rueckverfolgung.tsx` verdichtet Spurpfad, Lieferkettenblocker und Nachweisfolge ueber der eigentlichen Timeline.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-047

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wareneingang als physischer Fall zwischen Annahme, Charge und Lager deutlich mit dem Zielbild verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/wareneingang.tsx`
**Abnahmekriterien:** `charge/wareneingang.tsx` fuehrt den leichten Fallrahmen fuer Ressource, Blocker und naechste Aktion aus vorhandenen Daten.
**Erledigt:** `charge/wareneingang.tsx` fuehrt Lieferant, Charge, Lagerort und QS-Lage nun als kompakten Eingangsvorgang vor dem Wizard.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-048

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Tourenplanung als Logistik-Leitraum mit Folgecharakter, Bottleneck und Aktionspriorisierung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`
**Abnahmekriterien:** `tourenplanung.tsx` bekommt den kompakten Vorgangsrahmen fuer Druck, Blocker und naechste Massnahme ohne Zusatz-Requests.
**Erledigt:** `logistik/tourenplanung.tsx` zeigt Dispositionslage, Ressourcenengpaesse und die naechste Aktionsprioritaet jetzt direkt ueber den Touren.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-049

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Debitorische Ausgangsrechnungen als echter Freigabe-, Druck- und Forderungsfall statt reine Listenmaske fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoices-list.tsx`
**Abnahmekriterien:** `invoices-list.tsx` zeigt Rueckstand, Druck-/Versanddruck und naechste Sammelaktion aus bestehender Listenlage.

## OP-ROLL-050

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Ausgangsrechnungsformular als echter Faktura-, Freigabe- und Folgebelegfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoice-form.tsx`
**Abnahmekriterien:** `invoice-form.tsx` fuehrt Status, Blocker und naechste Aktion oberhalb der Fachbearbeitung.

## OP-ROLL-051

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Dunning-Editor als echter Mahn- und Eskalationsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/dunning-editor.tsx`
**Abnahmekriterien:** `dunning-editor.tsx` surfact Mahnstufe, Eskalationspfad und naechste Aktion ohne neue Requests.

## OP-ROLL-052

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsimport als echter Import-, Pruef- und Verbuchungsfall aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/buchungsimport.tsx`
**Abnahmekriterien:** `buchungsimport.tsx` zeigt Importdruck, Fehlerlage und Folgepfad aus bereits vorhandenen Daten.

## OP-ROLL-053

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Audit-Trail als FIBU-Revisionsraum mit Follow-up und Ausnahmebild fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/audit-trail.tsx`
**Abnahmekriterien:** `audit-trail.tsx` fuehrt Revisionslage, offene Auffaelligkeiten und naechste Pruefaktion kompakt.

## OP-ROLL-054

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Nebenbuch-Abstimmung als echter Clearing- und Differenzraum verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx`
**Abnahmekriterien:** `nebenbuch-abstimmung.tsx` zeigt Differenzen, Blocker und naechste Klaerungsschritte im leichten Fallmodell.

## OP-ROLL-055

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Hauptbuch als echter Abschluss- und Revisionsraum aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/hauptbuch.tsx`
**Abnahmekriterien:** `hauptbuch.tsx` fuehrt Abschlusslage, Journaldruck und naechste Aktion oberhalb der Sachkontensicht.

## OP-ROLL-056

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** GuV als FIBU-Abweichungs- und Ergebnisraum konsistent zum Operationsmodell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/guv.tsx`
**Abnahmekriterien:** `guv.tsx` zeigt Ergebnisdruck, Ausreisser und Folgeweg ohne Zusatz-Requests.

## OP-ROLL-057

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kontenplan als professionellen Steuerungsraum mit Revisions- und Nutzungskontext ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kontenplan.tsx`
**Abnahmekriterien:** `kontenplan.tsx` surfact Kontenlogik, Sperr-/Nutzungslage und naechste Verwaltungsaktion ohne Ueberladung.

## OP-ROLL-058

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OP-Verwaltung als querliegender FIBU-Klaerungsraum zwischen Debitoren und Kreditoren fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/op-verwaltung.tsx`
**Abnahmekriterien:** `op-verwaltung.tsx` zeigt Blocker, Rueckstand und Eskalationspfad ueber der Sammelmaske.

## OP-ROLL-059

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Anlagen-Suite als echter Revisions-, Abschreibungs- und Abschlussfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/anlagen-suite.tsx`
**Abnahmekriterien:** `anlagen-suite.tsx` fuehrt Abschreibungsdruck, Revisionslage und naechste Periode kompakt.

## OP-ROLL-060

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditlinien als Risiko- und Freigaberaum fuer Finanzierung und Forderungsschutz aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kreditlinien.tsx`
**Abnahmekriterien:** `kreditlinien.tsx` zeigt Auslastung, Grenzverletzungen und naechste Massnahme im einheitlichen Arbeitsmodell.

## OP-ROLL-061

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandsuebersicht als echter Lager- und Reservierungsraum mit Folgepfad verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** `bestandsuebersicht.tsx` zeigt Verfuegbarkeit, Engpaesse und naechste Lageraktion ohne neue API-Last.

## OP-ROLL-062

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandskorrektur als echter Pruef-, Freigabe- und Auditfall fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandskorrektur.tsx`
**Abnahmekriterien:** `bestandskorrektur.tsx` surfact Differenz, Begruendung und Folgeaktion oberhalb der Erfassung.

## OP-ROLL-063

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einlagerung als physischer Vorgang zwischen Bestand, Charge und Lagerplatz klar verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/einlagerung.tsx`
**Abnahmekriterien:** `einlagerung.tsx` fuehrt Ressourcenlage, Blocker und naechste Massnahme ohne neue Requests.

## OP-ROLL-064

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Auslagerung als echter Liefer- und Verfuegbarkeitsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/auslagerung.tsx`
**Abnahmekriterien:** `auslagerung.tsx` zeigt Verfuegbarkeit, Reservierungsdruck und Folgeweg oberhalb der Facharbeit.

## OP-ROLL-065

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerbewegungen als Revisions- und Rueckverfolgungsraum einheitlich aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/lagerbewegungen.tsx`
**Abnahmekriterien:** `lagerbewegungen.tsx` verdichtet Bewegungsdruck, Audit-Lage und Folgepfad ohne zusaetzliche Datenlast.

## OP-ROLL-066

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Inventur als echter Klaerungs- und Differenzraum zwischen Lager und FIBU fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/inventur.tsx`
**Abnahmekriterien:** `inventur.tsx` zeigt Differenzdruck, Owner und naechste Inventuraktion im leichten Fallmodell.

## OP-ROLL-067

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerterminal als physischer Arbeitsraum fuer schnelle Entscheidungen mit kompaktem Kontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/terminal.tsx`
**Abnahmekriterien:** `terminal.tsx` fuehrt Status, Blocker und naechste Aktion ohne die Touch-Bedienung zu ueberfrachten.

## OP-ROLL-068

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Qualitaetsausnahmen als echter Eskalations- und Freigaberaum fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx`
**Abnahmekriterien:** `ausnahmen.tsx` zeigt Risiko, Owner, naechste Massnahme und Eskalationsdruck ueber dem Arbeitsraum.

## OP-ROLL-069

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Reklamationsliste als Sammelraum fuer Eskalationen, Wiedervorlagen und Folgewege verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/reklamationen.tsx`
**Abnahmekriterien:** `reklamationen.tsx` surfact Rueckstand, Risikobild und naechste Sammelaktion kompakt aus vorhandenen Daten.

## OP-ROLL-070

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-Detail als echter Pruef- und Freigabefall zwischen Probe, Charge und QS fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/labor-detail.tsx`
**Abnahmekriterien:** `labor-detail.tsx` fuehrt Befundlage, Blocker und naechste Aktion konsistent ueber der Fachmaske.

## OP-ROLL-071

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Frachtbriefe als echter Logistik- und Nachweisraum zwischen Tour, Charge und Dokument professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`
**Abnahmekriterien:** `frachtbriefe.tsx` zeigt Blocker, Dokumentdruck und naechste Aktion ohne neue Requests.

## OP-ROLL-072

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wiegungen als operative Sammelmaske zwischen Waage, Annahme und Abrechnung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/wiegungen.tsx`
**Abnahmekriterien:** `wiegungen.tsx` surfact Rueckstand, Blocker und Folgepfad im leichten Fallmodell aus bereits geladenen Daten.
