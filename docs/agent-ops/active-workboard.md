# Active Workboard

Stand: `2026-05-12`

## ERP-FINANZ-ORDERS-DOC-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Veraltete `packages/erp-domain`-Order-REST-Dokumentation auf die entschiedene Python-FastAPI-Zielroute ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ERP-FINANZ-ORDERS-DOC-001.yaml`, `packages/erp-domain/README.md`, `packages/erp-domain/src/bootstrap.ts`, `C:\Users\Jochen\.cursor\plans\erp-finanz_roadmap_9029845d.plan.md`
**Abnahmekriterien:** README nennt keine oeffentlichen Node-Order-Endpunkte mehr; Orders-REST verweist auf `/api/v1/sales/orders`; Roadmap-Phase 3 ist nicht mehr zweigeteilt, sondern Doku/Redirect-only.
**Erledigt:** `packages/erp-domain/README.md` beschreibt Orders-REST jetzt als Python-FastAPI-Vertrag unter `/api/v1/sales/orders`; die veralteten `/api/orders`-Beispiele sind entfernt. `packages/erp-domain/src/bootstrap.ts` enthaelt keinen irrefuehrenden Controller-TODO mehr. Die Cursor-Roadmap ist auf die entschiedene Doku/Redirect-only-Variante gezogen.
**Checks:** `pnpm test:erp-domain -- erp-bootstrap-orders.spec.ts`; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Historische Archive und generierte API-Dumps koennen weiterhin alte Order-Begriffe enthalten; dieser Slice betrifft nur aktive Roadmap-/Paketdoku.

## HRM-GERMANY-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Deutsche HRM-Gaps ueber Personalakte, eAU, Payroll/DATEV, ESS/MSS, Recruiting/Onboarding, Reporting, Datenschutz, kontrollierte KI und Office-Connectoren als pruefbaren Zielvertrag schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GERMANY-GAP-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_readiness_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Zielbild und Gap-Matrix decken die 15 Mindestpunkte ab; API liefert HRM-Readiness mit Status, Rechts-/Compliance-Referenzen, Integrationen, KI-Kontrollen und naechsten Slices; Tests sichern eAU, §26 BDSG, BAG-Arbeitszeitpflicht, EU-AI-Act-Hochrisiko und Office-/DATEV-Connectoren.
**Erledigt:** `GET /api/v1/personal/hrm-readiness` eingefuehrt; Zielvertrag deckt die 15 HRM-Mindestpunkte, eAU, Personalakte, DATEV/Payroll, ESS/MSS, Recruiting/Performance, Datenschutz, kontrollierte KI und Office-Connectoren ab. Frontend-API-Hook `useHrmReadiness` ergaenzt. Gap-Plan und Open-Gaps-Doku aktualisiert.
**Checks:** `pytest tests/test_personal_hrm_readiness_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rechtsfeinpruefung, Betriebsvereinbarungen, echte eAU-/DATEV-/Microsoft-/Google-Zugangsdaten und produktive AVV/DPA bleiben Folgeslices.

## HRM-AKTE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Ersten Vertrag fuer digitale Personalakte mit Dokumentklassen, DMS-Referenzen, Rollenfilter, Audit- und Retention-Sicht bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-AKTE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_employee_file_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Personalakte kann Dokumentmetadaten lesen und anlegen; Dokumentklassen weisen Rechtsgrundlage, Standard-Sichtbarkeit und Retention aus; Rollenfilter fuer Employee/Manager/HR/Payroll ist regressionsgesichert; Export-/Loeschkonzept ist im Contract sichtbar.
**Erledigt:** `GET /api/v1/personal/employee-files/{employee_ref}` und `POST /api/v1/personal/employee-files/{employee_ref}/documents` eingefuehrt. Dokumentklassen, Rollenfilter, Exportpaket, Retention-Sicht und Frontend-Hooks sind verfuegbar; Doku markiert produktive DB-/DMS-Anbindung als Folgeslice.
**Checks:** `pytest tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive DMS-Ablage, echte Signaturen, Rechtsfreigabe der Aufbewahrungsfristen und DB-Migration bleiben Folgeslices.

## HRM-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Alle verbleibenden HRM-Plan-Gaps repo-seitig als API-/Frontend-/Doku-Vertraege schliessen: eAU, DATEV/Payroll-Closeout, Vertragsvorlagen, ESS, MSS, Recruiting, Analytics, Privacy, AI-Governance und Office-Connectoren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GAP-CLOSURE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** HRM-Plan weist keine fachlichen Repo-Gaps mehr aus; jeder verbliebene Punkt hat einen API-Vertrag und Frontend-Hook; Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate und Office-Connector-Readiness.
**Erledigt:** `GET /api/v1/personal/hrm-operating-system` eingefuehrt; HRM-Plan weist keine fachlichen Repo-Gaps mehr aus. Frontend-Hook `useHrmOperatingSystem` ergaenzt. Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate, Office-Connector-Readiness und die kanonischen `time_entries`-Service-Regeln.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten, AVV/DPA, Betriebsvereinbarungen, DSFA und Rechtsfreigaben bleiben externe Betriebsfreigaben.

## HRM-OPERATIONS-GATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Externe HRM-Betriebsfreigaben fachlich sauber zum Abschluss fuehren: Evidenzanforderungen, Owner, Go-live-Blocker, Abnahme und Auditstatus fuer eAU, DATEV, Office/SSO, LibreOffice/E-Signatur, AVV/DPA, Betriebsrat, DSFA und Rechtsfreigaben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gates_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** `GET /api/v1/personal/hrm-operations-gates` liefert Gate-Status mit Evidenzpflichten und Go-live-Blockern; Doku unterscheidet fachlich abgeschlossen, repo-seitig umgesetzt und extern freizugeben; Tests sichern alle externen Gates und Professional-Practice-Kriterien.
**Erledigt:** `GET /api/v1/personal/hrm-operations-gates` eingefuehrt; alle verbleibenden HRM-Betriebsfreigaben sind als blockierende Gates mit Owner, Evidenzanforderungen, Abnahmekriterien, Auditspur und Professional-Practice-Regeln modelliert. Frontend-Hook `useHrmOperationsGates` ergaenzt. HRM-Plan und Open-Gaps-Doku fuehren keine unspezifizierten Restpunkte mehr, sondern nur noch evidenzbasierte Go-live-Gates.
**Checks:** `pytest tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gates_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Abschluss der Gates erfordert reale externe Nachweise; ohne diese Nachweise bleibt Go-live bewusst blockiert.

## HRM-OPERATIONS-GATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates technisch vollstaendig machen: persistente Gate-/Evidence-Daten, Approval-/Reject-Workflow, Connector-Probe-Status, Auditspur und Go-live-Policy.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-002.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/versions/hrm_operations_gates_20260513.py`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Gates werden aus DB-Zustand plus Default-Katalog gelesen; Evidence kann angelegt werden; Gate-Entscheidungen koennen approved/rejected werden; Connector-Probes aktualisieren Status; `goLiveAllowed` wird aus persistenten Status abgeleitet; API-/Frontend-Contracts und Tests sind vorhanden.
**Erledigt:** Persistente Gate-, Evidence-, Probe- und Audit-Tabellen per Alembic ergaenzt; `GET /hrm-operations-gates` liest Runtime-Status aus DB mit Katalog-Fallback; Evidence-, Probe- und Decision-Endpunkte sowie `GET /hrm-operations-gates/go-live-policy` umgesetzt; Frontend-Hooks fuer Lesen, Evidence, Probe, Entscheidung und Go-live-Policy ergaenzt; Tests sichern Seed, Evidence, Probe, Approval, Evidence-Pflicht und Blocker-Policy.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py alembic/versions/hrm_operations_gates_20260513.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Providerzugriffe benoetigen weiterhin produktive Credentials; dieser Slice implementiert die technische Workflow- und Persistenzschicht inklusive Probe-Status, nicht die Beschaffung externer Freigaben.

## HRM-OPERATIONS-GATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates als bedienbares Frontend-Cockpit verfuegbar machen: Go-live-Status, Gate-Liste, Evidence-Erfassung, Probe-Erfassung und Approval/Reject-Aktionen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-003.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/personal.ts`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/personal.ts`
**Abnahmekriterien:** Personal-Navigation enthaelt das HRM-Freigabe-Cockpit; Route ist aufloesbar; UI zeigt Go-live-Policy, Blocker und Gate-Details; pro Gate koennen Evidence, Probe und Entscheidung ausgelöst werden; Typecheck ist gruen.
**Erledigt:** `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx` als HR-Freigabe-Cockpit ergaenzt; Personal-Navigation und Route-Aliase zeigen `/personal/hrm-freigaben`; UI nutzt einfache Buero-Sprache fuer Produktivstart, Pruefpunkte, Nachweise, Tests, Freigaben und naechste Aktionen. HRM-Plan und Open-Gaps-Doku markieren den Bedienpfad als repo-seitig geschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Freigaben bleiben betriebliche Nachweise; UI stellt den technischen Bedienpfad bereit.

## HRM-OPERATIONS-GATES-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Freigabe-Cockpit fachlich als Admin-/Compliance-/Go-live-Readiness-Arbeitsflaeche schaerfen: Name, Risiko, Prioritaet, Faelligkeit, Rollenhinweis und letzte Aenderung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-004.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`
**Abnahmekriterien:** API liefert Readiness-Metadaten je Gate; UI heisst HRM-Betriebsfreigaben; UI zeigt Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollen-/Sichtbarkeitshinweis und Abnahmekriterien; Typecheck und fokussierte API-Tests sind gruen.
**Erledigt:** `HrmOperationsGateOut` liefert Prioritaet, Risiko-Level, Faelligkeit, letzte Aenderung, berechtigte Rollen und Read-only-Rollen. Das Frontend heisst jetzt `HRM-Betriebsfreigaben`, zeigt Admin-/Compliance-/Readiness-Kontext, Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollenhinweis und einfache Arbeitsbegriffe.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Rollen-/Rechtesteuerung haengt an der zentralen Auth-/Navigation-Enforcement; dieser Slice macht fachliche Sichtbarkeit und API-Metadaten explizit.

## HRM-OPERATIONS-GATES-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Google-Studio-Designentwurf fuer `HRM-Betriebsfreigaben` in die bestehende VALEO-React-Seite uebertragen: Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen und aufklappbare Arbeitsbereiche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-005.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`
**Abnahmekriterien:** Seite folgt dem Studio-Entwurf ohne neue Dependencies; bestehende React-Query-Hooks bleiben verdrahtet; sichtbare Sprache bleibt buerotauglich; Typecheck ist gruen.
**Erledigt:** Google-Studio-Entwurf in die echte VALEO-Seite uebertragen: sticky Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen, aufklappbare Details und Arbeitsaktionen. Keine neue `motion`-Dependency; alle bestehenden Runtime-Hooks bleiben verdrahtet.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Studio-Prototyp enthaelt Mockdaten und `motion`; Uebernahme erfolgt auf echte VALEO-Daten und ohne zusaetzliche Animationsdependency.

## HRM-GO-LIVE-TEMPLATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Evidenzpaket als operative Repo-Vorlagen unter `docs/hrm-go-live-templates/` bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-001.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Gesamtwerk enthaelt Gate-Matrix, Go-live-Protokoll, Betriebsratsstatus, Mitarbeiterinformation, VVT, AVV/DPA, DSFA, Rollen, TOM, Retention, eAU, DATEV/Payroll, Office/SSO, DMS/E-Signatur, KI/Analytics, Evidence/Audit, Geschaeftsfuehrungsfreigabe und optionale Betriebsvereinbarung; Doku verweist auf das Vorlagenpaket; rechtlicher Arbeitsvorlagen-Charakter ist klar markiert.
**Erledigt:** `docs/hrm-go-live-templates/README.md` und `00_hrm_go_live_gesamtwerk.md` ergaenzt. Das Gesamtwerk deckt alle sieben HRM-Betriebsfreigabe-Gates mit ausfuellbaren Arbeitsmustern, Mindest-Evidence, Freigaben und Auditspur ab. HRM-Plan und Open-Gaps-Doku verweisen auf das Vorlagenpaket.
**Checks:** `rg -n "HRM-GATE-001|Mindest-Evidence|BDSG Paragraf 26|DSFA-Vorpruefung|Geschaeftsfuehrungsfreigabe" docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktivnutzung erfordert reale Datenschutz-, Payroll-/Steuerberater-, IT-Sicherheits- und Rechtspruefung.

## HRM-GO-LIVE-TEMPLATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Formulare auf den tatsaechlichen VALEO-Funktionsumfang begrenzen und hypothetische, nicht vorgesehene KI-/Auswertungsbegriffe aus Mitarbeiter- und Freigabetexten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-002.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`
**Abnahmekriterien:** Formulare nennen keine nicht vorgesehenen Funktionen; Mitarbeiterinformation beschreibt nur real vorgesehene HRM-Funktionen; KI-Freigabe ist als optionale Assistenzfunktions-Pruefung formuliert; API-/Doku-Vertraege sind konsistent.
**Erledigt:** Formulare, HRM-Plan, Open-Gaps-Doku und Personal-API sind auf den realen Funktionsumfang gezogen. Mitarbeitertexte nennen Personalverwaltung, Arbeitszeit, Abwesenheiten, Dokumente, Payroll-Vorbereitung, freigegebenes HR-Reporting, Compliance und optional konkret freigegebene KI-Assistenz; hypothetische Sonderfunktionen wurden entfernt.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_readiness_api.py` (keine Treffer); `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Konkrete spaetere KI- oder Analytics-Erweiterungen brauchen erneut gesonderte Datenschutz-, Legal- und Betriebsratspruefung.

## HRM-GO-LIVE-TEMPLATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Gesamtwerk in einzelne, direkt auffindbare Formular-Dateien unter `docs/hrm-go-live-templates/` zerlegen, ohne den fachlichen Master zu duplizieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-003.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/01_hrm_go_live_freigabeprotokoll.md`, `docs/hrm-go-live-templates/02_betriebsratsstatus_kein_betriebsrat.md`, `docs/hrm-go-live-templates/03_mitarbeiterinformation_hrm.md`, `docs/hrm-go-live-templates/04_vvt_hrm_system.md`, `docs/hrm-go-live-templates/05_avv_dpa_pruefprotokoll.md`, `docs/hrm-go-live-templates/06_dsfa_vorpruefung.md`, `docs/hrm-go-live-templates/07_rollen_berechtigungskonzept.md`, `docs/hrm-go-live-templates/08_tom_it_sicherheitsfreigabe.md`, `docs/hrm-go-live-templates/09_retention_loeschkonzept.md`, `docs/hrm-go-live-templates/10_eau_freigabeprotokoll.md`, `docs/hrm-go-live-templates/11_datev_payroll_abnahme.md`, `docs/hrm-go-live-templates/12_office_sso_abnahme.md`, `docs/hrm-go-live-templates/13_dms_esignatur_rendering_abnahme.md`, `docs/hrm-go-live-templates/14_ki_assistenz_reporting_freigabe.md`, `docs/hrm-go-live-templates/15_evidence_auditprotokoll.md`, `docs/hrm-go-live-templates/16_geschaeftsfuehrungsfreigabe.md`, `docs/hrm-go-live-templates/17_betriebsvereinbarung_optional.md`
**Abnahmekriterien:** Alle im README genannten Einzelvorlagen existieren; jede Einzelvorlage ist als Auszug mit Zweck, Verwendung und Link zum Master auffindbar; keine Einzelvorlage nennt hypothetische, nicht vorgesehene HRM-Funktionen; Doku-Checks sind gruen.
**Erledigt:** Einzelvorlagen `01_...` bis `17_...` unter `docs/hrm-go-live-templates/` ergaenzt und im README verlinkt. Jede Vorlage ist als Arbeitsauszug aus dem Master gekennzeichnet und auf den realen HRM-Funktionsumfang begrenzt. HRM-Plan und Open-Gaps-Doku nennen die operativen Einzelvorlagen.
**Checks:** `Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates` (keine Treffer); `$files = (Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md | ForEach-Object { $_.FullName }); node scripts/docs-markdown-check.cjs @files`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Die Einzeldateien sind Arbeitskopien aus dem Master; bei inhaltlichen Aenderungen muss der Master als Source of Truth zuerst angepasst werden.

## HRM-GO-LIVE-UX-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigaben von Compliance-Cockpit zu gefuehrter Arbeitsflaeche ausbauen und daraus einen repo-weiten UX-Exzellenzstandard fuer alle Domaenen ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** HRM-Seite bietet Rollenfokus, Gate-Aufgabenplan, Vorlage-Link je Gate, gefuehrte Nachweis-/Test-/Freigabe-Schritte, Audit-Zeitleiste und Management-Entscheidungsbild; repo-weiter UX-Standard uebertraegt diese Muster auf alle Domaenen; Typecheck und Doku-Checks sind gruen.
**Erledigt:** HRM-Betriebsfreigaben bieten jetzt Rollenfokus, Management-Entscheidungsbild, Vorlage-Link je Gate, gefuehrte Auswahllisten fuer Nachweise und Tests, Aufgabenplan je Gate und Audit-Zeitleiste. Der neue UX-Exzellenzstandard uebertraegt Rollenfokus, Aufgabenplan, naechste Aktion, Vorlage-/Nachweislink, gefuehrte Eingabe, Audit-Zeitleiste und Management-Bild auf alle Domaenen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Vollstaendige Ueberarbeitung aller Domaenen bleibt ein Rollout-Programm; dieser Slice liefert Referenzumsetzung und verbindlichen Standard.

## UX-STANDARD-COMPONENTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Wiederverwendbare UX-Exzellenz-Komponenten fuer Rollenfokus, Aufgabenplan, naechste Aktion, Evidence-Link, Audit-Zeitleiste, Managemententscheidung und CRUD-Abdeckung bereitstellen und in HRM als Referenz nutzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`, `packages/frontend-web/src/components/workflow/ux-standard.tsx`, `packages/frontend-web/src/components/workflow/index.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Komponenten sind typisiert und domaenenneutral; HRM nutzt mindestens Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste und Managemententscheidung aus dem Baukasten; UX-Standard dokumentiert den Baukasten und CRUD-Matrix; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `ux-standard.tsx` stellt `RoleFocusBar`, `OperationalTaskPlan`, `NextActionPanel`, `EvidenceTemplateLink`, `AuditTimeline`, `ManagementDecisionPanel`, `CrudCapabilityChecklist` und `EmptyStateWithAction` bereit. HRM-Betriebsfreigaben nutzen den Baukasten fuer Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste, Next Action und Managemententscheidung. UX-Standard dokumentiert Komponenten und CRUD-Abdeckung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Domaenen muessen in Folgeslices migriert werden; dieser Slice schafft den gemeinsamen Baukasten und die HRM-Referenzverdrahtung.

## UX-FINANCE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Den UX-Exzellenzbaukasten auf Finance/FIBU anwenden, beginnend mit dem Kreditoren-Zahlungslauf als produktkritischer Zahlungsarbeitsflaeche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-001.yaml`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Kreditoren-Zahlungslauf zeigt Rollenfokus, Aufgabenplan, Managemententscheidung, Audit-/Zahlungspfad und CRUD-Abdeckung; naechste Aktion bleibt sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/zahlungslauf-kreditoren.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Aufgabenplan, Managemententscheidung, Next Action und CRUD-Abdeckung. Der bestehende Zahlungspfad und Kontext bleiben erhalten. UX-Standard dokumentiert den Finance-Rollout-Status und naechste Finance-Slices.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Finance-Seiten wie UStVA, Mahnwesen und Abschluss folgen in separaten Rollout-Slices.

## UX-FINANCE-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** UStVA als zweite Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-002.yaml`, `packages/frontend-web/src/pages/finance/ustva.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** UStVA zeigt Rollenfokus fuer FIBU, Steuerbuero, Controlling und Leitung; Melde-Aufgabenplan fuehrt Periode, Abweichungen, Freigabe und ELSTER; Managemententscheidung zeigt abgabefaehig/gestoppt; CRUD-/Meldeabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/ustva.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung. Bestehender Meldeverlauf, UStVA-Kontext, FIBU-KPIs und Submit-/Export-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Mahnwesen und Periodenabschluss folgen in separaten Finance-UX-Slices.

## UX-FINANCE-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Mahnwesen als dritte Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-003.yaml`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Mahnwesen zeigt Rollenfokus fuer FIBU, Forderungsmanagement, Vertrieb, Leitung und Steuerbuero; Aufgabenplan fuehrt OP-Auswahl, Parameter, Versand/Eskalation und Zahlungsklaerung; Managemententscheidung zeigt sendbar/gestoppt; CRUD-/Kommunikationsabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/mahnwesen.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung. Bestehende Mahnlage, Kontext, FIBU-KPIs, Versand-, Paid-, Export- und Inkasso-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Periodenabschluss folgt in separatem Finance-UX-Slice.

## TODO-SPRINT-001

**Von:** Cursor<br>
**Owner:** (Team)<br>
**Stand:** dokumentiert 2026-04-24<br>
**Ziel des Slices:** Die abgestimmte **TODO-Umsetzungs-Roadmap** (Meilensteine **M-01–M-12**) und die **Sprint-Zuordnung S1–S5** im Repo und hier im Workboard als **einzige Sprint-/Issue-Referenz** festhalten; Abgleich mit automatisch erzeugten TODO-Reports möglich.

**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/TODO-SPRINT-001.yaml`, [docs/roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md](../roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md), Ergänzungen in `scripts/update_todos.py` (Slice-Ausgaben `docs/TODO-next-slices.md`, `docs/todo-report.json` → `next_slices`).

**Kurzreferenz Meilensteine**

| Sprint | Meilensteine |
|--------|----------------|
| S1 | M-01 (Auth-/Tenant-**Vertrag**), M-02 (Pagination Contract erp-domain) |
| S2 | M-03 (Pagination Rollout), M-04 (ERP Actor), M-05 (**E2E-Auth früh**) |
| S3 | M-06 (CRM Auth), M-07 (CRM E-Mail/Queue) |
| S4 | M-08 (GDPR Export), M-09 (GDPR Löschung inkl. Retention), M-10 (FiBu Perioden/Saldo) |
| S5 | M-11 (Strecke DB + Migration/Rollback), M-12 (Einkauf OCR, Teilprojekt) |

**Abnahmekriterien (Doku-Slice):** Workboard enthält Slice-ID und Tabelle; kanonisches Dokument existiert und ist vom Board aus erreichbar; Tracking-Hinweis für `python scripts/update_todos.py --repo-only` / `docs/TODO-next-slices.md` genannt.

**Erledigt:** Kanonische Sprint-Matrix und Meilenstein-Details in `docs/roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md`; dieser Eintrag.

**Checks (optional):** `python scripts/update_todos.py --repo-only`; Doku-Link im Browser öffnen.

**Offene Risiken:** Die Meilensteine **M-01–M-12** sind Umsetzungsarbeit — dieser Slice ist **Planungs-/Referenz-Ebene**. Konkrete Implementierungs-Slices sollten eigene IDs im Workboard erhalten und auf **M-xx** im Titel oder Body verweisen.

## HR-TIME-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Lizenz- und Zielarchitektur fuer deutsche Abwesenheitsverwaltung, Zeiterfassung und VALEO-eigenen Driver-Time-Layer festhalten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-001.yaml`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Urlaubsverwaltung wird als Apache-2.0-Abwesenheitskandidat bewertet; AGPL/GPL-Zeiterfassung ist als Codebasis ausgeschlossen; VALEO-Driver-Time-Layer, Integrationsgrenzen, Pilotumfang und Lizenzrisiken sind dokumentiert.
**Erledigt:** Zielarchitektur und Lizenzlinie in `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md` dokumentiert; `open-gaps` fuehrt HR-TIME-001 als P2-Thema mit naechstem Pilot-Slice.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Finale Rechtspruefung, Anbieter-AVV/DPA und produktive Tacho-/Telematik-Schnittstellen liegen ausserhalb des Repos.

## HR-TIME-PILOT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Ersten VALEO-eigenen Driver-Time-Toolkern fuer LKW-Fahrerzeit, Tour-/Fahrzeugbezug und Plausibilitaetschecks umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-001.yaml`, `packages/hr-domain/src/domain/entities/driver-time-event.ts`, `packages/hr-domain/src/domain/services/driver-time-service.ts`, `packages/hr-domain/dist/domain/entities/driver-time-event.*`, `packages/hr-domain/dist/domain/services/driver-time-service.*`, `packages/hr-domain/tests/domain/driver-time-service.test.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Fahrerzeitereignisse besitzen typisierte Ereignisarten, Tour-/Fahrzeugbezug, Quellen- und Auditfelder; Plausibilitaetschecks erkennen Ueberlappungen, fehlende Tour-/Fahrzeugdaten, fehlende Korrekturbegruendung und Abwesenheitskollisionen; die Zeiterfassungsseite zeigt den Driver-Time-Pilot ohne AGPL-/GPL-Codeuebernahme.
**Erledigt:** `DriverTimeEventEntity` und `DriverTimeService` eingefuehrt; fokussierte Vitest-Regression deckt Zusammenfassung, Blocker, Abwesenheitskollision und Tacho-/Manuell-Abweichung ab; `personal/zeiterfassung.tsx` zeigt Driver-Time-Pilot-KPIs und Ereignistabelle.
**Checks:** `pnpm --filter @valero-neuroerp/hr-domain exec vitest run tests/domain/driver-time-service.test.ts`; `pnpm --filter @valero-neuroerp/hr-domain build`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Produktive Persistenz, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices. Der volle `@valero-neuroerp/hr-domain test`-Lauf ist aktuell durch den bestehenden `testcontainers`-Import im Repository-Integrationstest blockiert.

## HR-TIME-PILOT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Driver-Time-Pilot als Backend-/Frontend-Toolvertrag an die bestehende Personal-API anbinden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-002.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_driver_time_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** `/api/v1/personal/driver-time/summary` liefert Fahrerzeit-KPIs, Ereignisse und Plausibilitaetsbefunde aus einem stabilen API-Vertrag; Frontend nutzt diesen Hook statt harter lokaler Driver-Time-Daten; Tests decken Happy Path und Befundlogik ab.
**Erledigt:** Personal-API liefert Driver-Time-Summary mit DB-ableitung aus Stundenzetteln, Abwesenheitskollisionen und Pilot-Fallback; Frontend-Hook `useDriverTimeSummary` ersetzt harte lokale Driver-Time-Daten; Tests decken Helper, API-Happy-Path und Fallback ab.
**Checks:** `pytest tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Persistente Fahrerzeitereignisse, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices.

## HR-TIME-PRO-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Zeiterfassung vom Fahrerzeit-Pilot zu einem professionellen Time-&-Labor-Cockpit mit Freigabe-, Compliance- und Payroll-Sicht ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PRO-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_cockpit_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Backend liefert ein Time-Cockpit mit Perioden-KPIs, Freigabequeue, Compliance-Befunden, Payroll-Readiness und Driver-Time-Zusammenfassung; Frontend zeigt diese Steuerung statt reiner Mock-/Tabellenseite; Tests sichern Kernvertrag und Regelbefunde.
**Erledigt:** `GET /api/v1/personal/time-cockpit` liefert professionelle Steuerungsdaten inklusive Payroll-Readiness und Compliance-Befunden; Zeiterfassungsseite nutzt Tabs fuer Steuerung, Driver-Time, Arbeitszeit und Payroll; Tests decken API-Vertrag und Regelbefunde ab.
**Checks:** `pytest tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Rechtsfeingranulare ArbZG-/Lenkzeitregeln, echte Dienstplanung, Buchungsworkflow und Lohnexport bleiben Folgeslices.

## HR-TIME-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** GAP-Liste, Lastenheft, Roadmap, Integrationsanforderungen und Landhandel-spezifische HRM-Planung gegen SAP/Oracle/Shiftfy-Benchmark dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-GAP-001.yaml`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** SAP-/Oracle-/Shiftfy-Benchmark ist quellenbasiert; VALEO-GAPs, Lastenheft, Roadmap-Milestones, Integrationsanforderungen, Kreuzverbindungen, Mitarbeitertypen im Landhandel, Kalenderintegration, Saison-/Arbeitsspitzenplanung, Kampagneninterferenzen und Aussendienstplanung sind als umsetzbare Planung dokumentiert.
**Erledigt:** GAP-/Lastenheft-/Roadmap-Dokument in `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md` erstellt und in die HR-Time-Zielarchitektur verlinkt.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detailauslegung Arbeitszeit-/Lenkzeitrecht, Tarif-/Betriebsvereinbarungen, Anbieter-AVV/DPA und echte Kalender-/Tacho-/Telematik-Zugangsdaten bleiben fachlich oder extern zu klaeren.

## HR-TIME-DATA-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Persistenten HR-Time-Datenkern fuer Mitarbeiter-Zeitprofile, produktive Zeitereignisse und Audit-/Statusfelder einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-DATA-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_data_api.py`, `migrations/sql/hr/001_hr_time_core.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`
**Abnahmekriterien:** Kanonisches HR-Time-Kerndatenmodell und Konsistenzregeln sind dokumentiert; API liefert kanonische HR-Time-Profile aus Datenbank oder Pilot-Fallback; produktive Zeitereignisse besitzen Quelle, Status, Kostenstelle, Arbeitsbereich, Audit und Korrekturgrund im Migrationsvertrag; Tests sichern Profil- und Event-Transformation.
**Erledigt:** Kanonisches Kerndatenmodell inklusive API-Resource-URLs und Konsistenzanalyse dokumentiert; SQL-Vertrag fuer `employee_time_profiles`, erweiterte `time_entries` und `driver_time_events` erstellt; `GET /api/v1/personal/time-profiles` mit Datenbank-, User- und Pilot-Fallback umgesetzt; fokussierte API-/Mapping-Regression ergaenzt.
**Checks:** `pytest tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Anwendung der Migration, echte HR-Stammdatenquelle und Lohnartenmapping bleiben Folgeslices.

## HR-TIME-BOOK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Buchungs-, Korrektur-, Einreichungs- und Freigabe-Workflow fuer kanonische HR-Time-Zeitereignisse bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-BOOK-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_booking_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Zeitbuchungen koennen erstellt, eingereicht und freigegeben werden; Korrekturen verlangen einen Grund; exportierte Eintraege werden nicht still mutiert; API-Tests sichern Statusuebergaenge und Fehlerfaelle.
**Erledigt:** `POST /api/v1/personal/time-entries`, `/submit`, `/approve` und `/correct` eingefuehrt; Korrekturgrund und Export-Schutz werden serverseitig erzwungen; fokussierte API-Regression deckt Happy Path und Fehlerfaelle ab.
**Checks:** `pytest tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rollenbasierte echte Managerfreigabe, Payroll-Export und UI-Aktionen bleiben Folgeslices.

## HR-TIME-ABS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Abwesenheits-Contract als kanonischen Planungsblocker fuer Urlaubsverwaltung/SaaS-Adapter, Tour, Schicht, Kalender und Payroll bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-ABS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_absence_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Abwesenheiten koennen als Contract importiert und gelesen werden; genehmigte Abwesenheiten werden als `time_entries` mit Quelle `absence` gespiegelt; API weist Planungsblocker fuer Tour, Schicht, Kalender und Payroll aus; Tests sichern Import, Listing und Driver-Time-Kollision.
**Erledigt:** `GET /api/v1/personal/absences` und `POST /api/v1/personal/absences/import` umgesetzt; Import spiegelt genehmigte Abwesenheiten als kanonische `time_entries` mit Quelle `absence`; Planungsblocker und Driver-Time-Kollision sind regressionsgesichert.
**Checks:** `pytest tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echter Urlaubsverwaltung-HTTP-Connector, AVV/DPA und bidirektionale Konfliktaufloesung bleiben Folgeslices.

## HR-TIME-SCHED-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Schicht- und Einsatzplanung mit Standort, Rolle, Qualifikationen, Besetzung und Abwesenheitskonflikten auf dem kanonischen HR-Time-Modell bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-SCHED-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_shift_planning_api.py`, `migrations/sql/hr/002_hr_time_scheduling.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Schichten koennen erstellt und gelesen werden; Planung prueft Mindestbesetzung, aktive Profile, Qualifikationen und genehmigte Abwesenheiten; Konflikte werden als Warnung/Blocker im API-Vertrag ausgewiesen; Tests sichern Happy Path und Konfliktfaelle.
**Erledigt:** `domain_hr.shifts` als SQL-Vertrag, `GET/POST /api/v1/personal/shifts` und Konfliktpruefung gegen Mindestbesetzung, Profile, Qualifikationen und genehmigte Abwesenheiten umgesetzt; Regression fuer Blocker/Warnungen ergaenzt.
**Checks:** `pytest tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** UI-Kalender, echte Optimierung/Auto-Staffing und rollenbasierte Managerfreigabe bleiben Folgeslices.

## HR-TIME-CAL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Provider-neutralen Kalendervertrag fuer HR-Time-Blocker, Schichten, Abwesenheiten, Touren und Aussendienst bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAL-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_calendar_api.py`, `migrations/sql/hr/003_hr_time_calendar.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kalenderereignisse koennen erstellt und gelesen werden; private externe Termine werden nur als Busy-Blocker ohne Betreffdetails gefuehrt; Konfliktlevel und Sync-State sind im Contract sichtbar; Tests sichern Datenschutzmaskierung und Vertrag.
**Erledigt:** `domain_hr.calendar_events` als SQL-Vertrag, `GET/POST /api/v1/personal/calendar-events`, Sync-State, Konfliktlevel und Datenschutzmaskierung fuer private/busy-only Termine umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Microsoft/Google OAuth, Delta-Sync und echte externe Kalenderzugriffe bleiben Folgeslices.

## HR-TIME-PAY-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Payroll-/DATEV-Exportvertrag fuer freigegebene HR-Time-Zeitwerte mit Lohnarten, Kostenstellen und Blockerpruefung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PAY-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_payroll_export_api.py`, `migrations/sql/hr/004_hr_time_payroll_exports.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Payroll-Export kann fuer Zeitraum erzeugt und gelesen werden; nur freigegebene Zeitwerte werden exportfaehig; offene/nicht freigegebene Buchungen werden als Blocker ausgewiesen; Tests sichern Lohnartenmapping und Blocker.
**Erledigt:** `domain_hr.payroll_exports`, `GET/POST /api/v1/personal/payroll-exports`, Lohnartenmapping fuer Regelzeit/Ueberstunden/Abwesenheit und Blocker fuer nicht freigegebene Zeitbuchungen umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte DATEV-/Lohnsoftware-Dateiformate, Steuerberaterfreigabe und Rueckschreibstatus bleiben Folgeslices.

## HR-TIME-CAMPAIGN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Saison-/Kampagnen-Kapazitaetsplanung mit Rollenbedarf, Abwesenheiten, Schichten und Engpassbewertung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAMPAIGN-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_campaign_capacity_api.py`, `migrations/sql/hr/005_hr_time_campaign_capacity.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kampagnenkapazitaet kann erstellt und gelesen werden; Rollenbedarf wird gegen aktive Profile, Abwesenheiten und bereits geplante Schichten bewertet; Engpaesse werden als Warnung/Blocker im Contract ausgewiesen.
**Erledigt:** `domain_hr.campaign_capacity_plans`, `GET/POST /api/v1/personal/campaign-capacity` und Rollenbedarfspruefung gegen aktive Profile, Abwesenheiten und geplante Schichten umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Optimierungsalgorithmus, Wetter-/Mengenforecast und UI-Heatmap bleiben Folgeslices.

## HR-TIME-FIELD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Aussendienstplanung mit Kunde, Gebiet, Kampagne, Kalender- und Abwesenheitskonflikten auf HR-Time-Basis bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-FIELD-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_field_service_api.py`, `migrations/sql/hr/006_hr_time_field_service.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Aussendiensttermine koennen erstellt und gelesen werden; Planung prueft HR-Time-Profil, Abwesenheit und Kalenderueberschneidung; Konflikte werden im Contract ausgewiesen; Tests sichern Blocker und Happy Path.
**Erledigt:** `domain_hr.field_service_plans`, `GET/POST /api/v1/personal/field-service-plan` und Konfliktpruefung gegen HR-Time-Profil, Abwesenheiten und Kalenderblocker umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_field_service_api.py tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** CRM-Live-Connector, Routenoptimierung und mobile Aussendienst-UI bleiben Folgeslices.

## HR-TIME-UI-CRUD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Tools als Human/AI-Agent-Interface mit CRUD-Aktionen fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UI-CRUD-001.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Frontend nutzt die neuen HR-Time-Contracts fuer Listen und Create-Mutations; Nutzer koennen zentrale HR-Time-Objekte aus dem Cockpit anlegen; Agent-Hinweise fassen Blocker, Freigaben und naechste Aktionen zusammen; Typecheck ist gruen.
**Erledigt:** Frontend-API-Hooks fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst ergaenzt; Zeiterfassungsseite zu einem kompakten ERP-Object-Page-Cockpit mit Agent Worklist, CRUD-Formulargruppen und Planungs-/Payroll-Tabellen ausgebaut.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detail-CRUD mit Edit/Delete, echte Optimierungsvorschlaege und mobile Offline-UX bleiben Folgeslices.

## HR-TIME-OPS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Verdrahtung fuer Navigation vor/zurueck, Bearbeiten/Nachbearbeiten, Drucken, Arbeitsplanabruf und praferenzbasierte Planung mit Nachttouren, Urlaub, Schulferien, Brueckentagen und Feiertagsdruck operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_work_plan_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Backend liefert einen Arbeitsplanvertrag mit Planungsbefunden und Mitarbeiterpraeferenzen; Zeitbuchungen koennen aus der UI nachbearbeitet und neu eingereicht werden; Frontend bietet vor/zurueck-Navigation, Druckpfade und Arbeitsplanabruf; Tests sichern Arbeitsplan- und Praeferenzlogik.
**Erledigt:** `/api/v1/personal/work-plan` mit Praeferenz-, Ferien-, Brueckentags-, Feiertags- und Abwesenheitsbefunden umgesetzt; Frontend-Hooks fuer Arbeitsplan, Einreichen und Korrektur ergaenzt; Zeiterfassungsseite bietet Tagesnavigation, Arbeitsplan-Druck, Arbeitsplan-Tab und Nachbearbeitungsmaske.
**Checks:** `pytest tests/test_personal_work_plan_api.py tests/test_personal_shift_planning_api.py tests/test_personal_time_booking_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Ferienkalender-Provider, Betriebsvereinbarungen und echte Optimierungsengine bleiben Folgeslices.

## HR-TIME-OPS-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Durchklicktest-Befund beheben: HR-Time-GET-Hooks duerfen leere Platzhalterdaten nicht als frische Daten cachen und muessen beim Oeffnen der Maske wirklich laden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-002.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** HR-Time-Durchklicktest sieht geladene Arbeitsplan-/Cockpitdaten; GET-Hooks verwenden Platzhalter statt frischer Initialdaten; Formular-POSTs und Druckaktion bleiben funktionsfaehig.
**Erledigt:** React-Query-HR-Time-Hooks von `initialData` auf `placeholderData` umgestellt; Playwright-Durchklicktest fuer Navigation, Arbeitsplan, Erfassung, Nachbearbeitung, Submit/Korrektur-POSTs und Druckpfad ergaenzt; Testlauf hat GET-Requests und UI-Rendering verifiziert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Der temporäre E2E-Smoke nutzt API-Mocks; produktive Browser-E2E gegen echte FastAPI/Postgres bleibt Folgeslice.

## HR-TIME-OPS-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Nachbearbeitung ergonomisch aus der Arbeitszeitliste starten statt manuelle Zeitbuchungs-ID-Eingabe zu erzwingen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-003.yaml`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Arbeitszeitzeilen haben eine Bearbeiten-Aktion; Klick fuellt die Nachbearbeitung mit ID, Zeiten, Stunden und Typ; die UI springt zur Erfassungs-/Nachbearbeitungsgruppe; E2E-Durchklicktest nutzt diesen Pfad.
**Erledigt:** Arbeitszeitliste erhaelt Bearbeiten-Aktion mit ID-/Zeit-/Typ-Uebernahme; Tabs sind kontrolliert und springen in die Erfassung; Playwright-Durchklicktest nutzt den realen Bearbeiten-Pfad vor Submit/Korrektur.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Voller Edit/Delete-Workflow fuer alle HR-Time-Objekte bleibt Folgeslice.

## HR-TIME-UX-ROADMAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Workflows als klickarme End-to-End UX-Roadmap mit Milestones, Quervernetzungen, User-Fragen, Masken, Such-/Filter-/Sortierfunktionen planen und den ersten Filter-/Such-Slice im Cockpit umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UX-ROADMAP-001.yaml`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Roadmap beschreibt Milestones mit Quervernetzungen und Abhaengigkeiten; User-Fragen sind Masken, Datenquellen und Aktionen zugeordnet; UI bietet zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit/Arbeitsplan; Durchklicktest nutzt Suche/Filter/Sortierung.
**Erledigt:** UX-Workflow-Roadmap mit Milestones UX-M1 bis UX-M7, User-Fragen, Masken, Datenquellen, Aktionen, Quervernetzungen und Folge-Slices dokumentiert; Zeiterfassungs-Cockpit um zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit und Arbeitsplan erweitert; E2E-Durchklicktest nutzt Suche/Filter/Sortierung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Weitere Milestones wie Action Panel, Wizard, Driver-Dispo und Payroll Closeout bleiben Folge-Slices.

## AGENT-ORCH-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Symphony als Blaupause fuer einen VALEO-eigenen Agent-Orchestrator in einem kleinen, repo-sicheren Pilot umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/agent-orchestrator-pilot.md`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Ein CLI-Pilot erkennt Workboard-Slices, erzeugt Claim-Vorschlaege, listet Checks und Handoff-Geruest, ohne automatisch zu claimen, zu committen, zu pushen oder Agents zu starten.
**Erledigt:** Read-only Supervisor `scripts/agent_workboard_supervisor.py` eingefuehrt; Parser erkennt Slice-IDs, Statusklassen, Owner, Dateibesitz, Checks und Risiken; CLI liefert `list`, `claim-proposal`, `checks` und `handoff-template`. Pilotdoku liegt in `docs/agent-ops/agent-orchestrator-pilot.md`.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py list --status open`; `python scripts/agent_workboard_supervisor.py claim-proposal DOM-FIN-002 --owner Codex`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Markdown-Workboard ist kein striktes Datenformat; der Pilot muss konservativ parsen und unklare Bloecke melden statt still zu raten.

## AGENT-ORCH-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Maschinenlesbare Slice-Dateien oder ein Validierungs-Gate fuer Workboard-Claims einfuehren, damit der Orchestrator nicht dauerhaft auf weichem Markdown basiert.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/**`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Claim-Pflicht ist maschinenlesbar validierbar; unklare Status-/Owner-/Dateibesitz-Felder werden als Fehler gemeldet, ohne automatische Git-Aktionen auszufuehren.
**Erledigt:** YAML-Slice-Format eingefuehrt (`docs/agent-ops/slices/*.yaml`); `validate`-Subcommand in `agent_workboard_supervisor.py` ergaenzt; 14 neue Tests gruen; historische Markdown-Bloecke werden nur validiert wenn YAML-Datei oder `--strict-ids` vorhanden.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Bestehende historische Workboard-Bloecke sind uneinheitlich und duerfen nicht durch ein zu striktes Gate blockieren.

## ERP-CRIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Testabdeckung und Vertragsstabilitaet fuer kritische ERP-Pfade zuerst an real roten Tests und Ratchet-Pfaden verbessern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/payment_runs.py`, `tests/test_process_kernel_wave1_contracts.py`, relevante Coverage-/Ratchet-Doku.
**Abnahmekriterien:** Der aktuell rote Payment-Return-Vertrag laeuft wieder; Coverage-Ratchet-Status ist dokumentiert; naechste unterdeckte Pfade sind als konkrete Test-Slices priorisiert.
**Erledigt:** `payment_runs.return_payment` toleriert aktuelle und Legacy-Zeilenformate fuer Ruecklaeufer-Betraege; der rote Vertragstest ist gruen. Coverage-Ratchet-Folgereihenfolge ist dokumentiert in `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`.
**Checks:** `pytest tests/test_process_kernel_wave1_contracts.py::test_return_payment_persists_outbox_event tests/test_process_kernel_wave1_contracts.py::test_payment_return_amount_accepts_current_and_legacy_row_shapes -q`
**Offene Risiken:** `check_critical_backend_coverage.py` bleibt nach dem gruenen Sammellauf noch rot fuer `dunning.py`, `booking_templates.py`, `chart_of_accounts.py`, `finance_read_models.py`, `waage.py`, `warehouses.py`, `warehouse_transfers.py`; diese Pfade sind in der Coverage-Plan-Datei als Folgeslices priorisiert.

## ERP-CRUD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Browser-/CRUD-Abnahme der wichtigsten E2E-Prozesse in eine ausfuehrbare, priorisierte Testmatrix ueberfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/browser-use-checklists.md`, `docs/quality-assurance/e2e-crud-acceptance-matrix-2026-04-24.md`, ggf. vorhandene Frontend-E2E-Testkonfiguration.
**Abnahmekriterien:** Die neun Flow-Spine-Prozesse besitzen eine priorisierte CRUD-/Statuswechsel-/Korrekturmatrix mit klaren P0/P1-Prueffaellen und Repo-Pruefkommandos.
**Erledigt:** Neue priorisierte E2E-CRUD-Matrix fuer P0/P1-Flow-Spine-Prozesse erstellt und in den Browser-Use-Checklisten verlinkt.
**Offene Risiken:** Echte Browser-Ausfuehrung haengt vom lokal startbaren Fullstack und Seed-Daten ab.

## ERP-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Live-Integrations-Readiness mit echten Secrets/Zielsystemen so weit repo-seitig vorbereiten, dass Ops nur noch Werte eintragen und Pruefkommandos ausfuehren muss.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `scripts/check_integration_bootstrap.py`, `app/services/integration_bootstrap.py`, `.env.example`.
**Abnahmekriterien:** Readiness-Bericht trennt deterministische Repo-Pruefung und externe Live-Probes; fehlende Secrets/Ziele werden maschinenlesbar als Blocker ausgewiesen.
**Erledigt:** `--strict-live` ergaenzt; Live-Probe-Plan und Gate sind dokumentiert.
**Offene Risiken:** Produktive Tenant-Secrets und Zielsystem-URLs liegen ausserhalb des Repos.

## FIBU-CUTOVER-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Cutover-Mappings fachlich abschliessbar machen, indem Pflichtmapping, Freigabezustand und Validierung formalisiert werden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/fibu-cutover-mapping-readiness-2026-04-24.md`, `config/fibu_cutover_mapping.template.yaml`, `scripts/check_fibu_cutover_mapping.py`, `tests/test_fibu_cutover_mapping.py`.
**Abnahmekriterien:** Konten-, Steuer-, Kostenstellen- und Gegenkonto-Mappings haben eine Vorlage, einen Validator und einen klaren Blockerstatus fuer fachliche Freigabe.
**Erledigt:** FIBU-Cutover-Template, Validator, Tests und Readiness-Doku erstellt.
**Offene Risiken:** Fachlich freigegebene Zielkonten/-steuerschluessel muessen vom Fachbereich geliefert werden.

## RATIONS-SPLIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-Solver technisch weiter entkoppeln, ohne die LP-Semantik zu aendern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/*`, relevante Rations-Tests.
**Abnahmekriterien:** Ein weiterer klarer Solver-Baustein wird aus `rations_optimization.py` in das Solver-Paket gezogen oder mit typisierter Hilfslogik isoliert; Regression bleibt gruen.
**Erledigt:** Mischgruppen-Reihenfolge als `app/agrar/rations/solver/mixing.py` aus dem Endpoint-Pfad herausgezogen und separat getestet.
**Offene Risiken:** Vollstaendige `_run_lp`-Zerlegung ist ein mehrstufiger Refactor.

## DOMAIN-PARITY-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Domänenparitaet in schwächeren Bereichen als messbares Ausbauprogramm statt loser Absicht fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`.
**Abnahmekriterien:** Finance, Supply/Inventory, Procurement, Contracts, CRM und Documents sind nach Fachlogik, Testtiefe, Integration und UI-Operationalisierung bewertet; naechste Code-/Test-Slices sind priorisiert.
**Erledigt:** Domain-Parity-Roadmap mit Bewertungsraster, Prioritaeten und naechsten Code-Slices erstellt und in `open-gaps` verlinkt.
**Offene Risiken:** Tiefe fachliche Paritaet braucht weitere domänenspezifische Arbeit und Fachentscheidungen.

## RATIONS-HARD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-/Fuetterungsmodul nach Punkt 4 gezielt haerten, ohne den Solver grossflaechig umzubauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_feeding_system.py`, `tests/test_rations_mixing_protocol.py`
**Abnahmekriterien:** Weide wird auch bei nominellem TMR-Input nicht ins Mischprotokoll aufgenommen; Auto-Promotion TMR -> PMR_pasture ist regressionsgesichert; Mischprotokoll nutzt die vorhandene Feed-Dataclass als typisierte Solver-Sicht.
**Erledigt:** Mischprotokoll nutzt `Feed.from_dict()` fuer die typisierte Feed-Sicht; TMR+verfuegbare Weide wird auf PMR_pasture auto-promoted; falsch als `tmr_block` gelabelte Weide wird aus der Mischung ausgeschlossen und im Protokoll als `excluded_pasture` ausgewiesen.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_mixing_protocol.py tests/test_rations_feed_dataclass.py -q`
**Offene Risiken:** Vollstaendige Zerlegung von `_run_lp` und regelbasiertes Warnsystem bleiben Folgeslices. Konzentrat-Tagesmax wird jetzt als Stage-2-LP-Slack abgebildet (siehe RATIONS-POLICY-PIPE-001).

## RATIONS-POLICY-PIPE-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Rationspipeline policy-/fachlich schaerfer machen (Saftfutter-Caps, PMR-Weide-Profile, k_l, Infeasibility-Hilfen, Konzentrat-Slack) und Frontend/TS an die erweiterte API anbinden.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_feeding_system.py`, ggf. `app/agrar/rations/solver/mixing.py` / `tests/test_rations_solver_mixing.py`.
**Abnahmekriterien:** Backend liefert die neuen Meta-Felder (u. a. Konzentrat-Slack, `ration_blocks.feeding_system.auto_promoted_from_tmr`, Mixing `excluded_pasture`); Frontend sendet `feeding_system_config` und zeigt RationBlocks/Mixing/KF-Slack; Regression gruen.
**Erledigt:** Saftfutter/nasse CoP: weiche/harte Caps, LP-hart, Soft-Constraint + Referenz-HTML; `_POLICY_PROFILE_TARGETS` um `tmr_standard`, `pmr_standard`, `pmr_pasture_spring/summer/autumn`; Stage-2 Konzentrat-Tagesmax-Slack + Response `concentrate_max_lp_slack_*`; nach Solve FS mit Ist-Mengen neu aufgeloest, `_block_labels` aktualisiert; Infeasibility: Heu/Stroh-Abdeckung, aNDFom-Kapazitaet (`ndf_capacity`), generischer Zweig nur bei grobfutterarmem Set; k_l bei PMR+Weide ueber FANi + TMR-ME-Dichte (`_kl_milk_from_me_density`); `result.x` auf Feed-Laenge begrenzt. Frontend: Typen, Default-Config im Request, Panels, Policy-Badge fuer KF-Slack.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_optimization_milk_plausibility.py -q`; im Paket `frontend-web`: `pnpm run type-check`
**Offene Risiken:** Optional Wizard fuer manuelle `feeding_system_config`-Overrides; E2E-Smoke Rations-UI; weiteres Zerlegen von `_run_lp`.

## RATIONS-WIZARD-E2E-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Wizard-Schritt 3 (Grenzen + weiche Ziele) als State/API an Backend anschließen, Prioritäten grob an `objective_strategy` koppeln, TM-Ziel/`target_dmi_kg` und Wizard-TM-Band im `_gfe_requirements` nutzen, Workbench-Duplikatnamen klären, Playwright mit `webServer`, kurze Pytest-Regression, QA-Checkliste ohne private Fixtures.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py` (`_gfe_requirements`, `_run_lp` Wizard-Dichten), `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/playwright.config.ts`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `tests/test_rations_wizard_requirements.py`, `docs/agent-ops/rations-manual-compound-qa.md`.
**Abnahmekriterien:** Frontend sendet `objective_strategy`, `policy_overrides.wizard_*`, `wizard_dmi_*` am Profil; Backend klemmt TM-Band; Playwright kann Vite selbst starten; Regressionstests gruen.
**Checks:** `pytest tests/test_rations_wizard_requirements.py -q`; im Paket `frontend-web`: `pnpm exec playwright test tests/e2e/rations-compound-upload.spec.ts` (mit laufendem Backend) bzw. `pnpm run type-check`.
**Erledigt (Folgesession LP):** `policy_overrides.wizard_hard_bounds` steuert ME-/Stärke-/aNDFom-Mindest- bzw. Höchst-Dichten (linear auf Gesamtration); `andfom_gf_min_pct_tm` schärft die aNDFomGF+CoP-Untergrenze vor LP-Aufbau.
**Erledigt (Session 2026-04-24ff):** `wizard_soft_goals` wirken solver-seitig fuer `minimize_soya` (Stage-1-Welfare-Penalty + Stage-2-Kostenzuschlag auf Soja-Futtermittel), `prefer_homegrown` (Bonus fuer `gfa_`-/`_source=="gfa"`-Feeds), `maximize_n_efficiency_rmd` (Penalty bei hohem Feed-RMD); Metadata `wizard_soft_goals_lp` listet aktive Flags. `optimization_strategy` bleibt Legacy-Kurzstring; Detail in `optimization_strategy_pipeline`. Milch-Kennziffern GF/Weide: anteilige Erhaltungsbuchung ueber GF-ME-/Teilmengen-ME-Anteil (`_maintenance_allocation_fraction`).
**Erledigt (Session 2026-04-24 Baseline-L1):** `minimize_deviation_from_baseline` mit `policy_overrides.wizard_baseline_kg_dm` (feed_id -> kg TM): L1-Abstand via Hilfsvariablen in Stage 1 (`_WIZARD_BASELINE_L1_WEIGHT`) und gekoppeltes Gewicht in Stage 2; Frontend speichert nach erfolgreicher Optimierung die Ist-Ration als Baseline und sendet sie bei Re-Optimierung. Playwright-Smoke `tests/e2e/rations-smoke.spec.ts` (Demo-Pfad).
**Offene Risiken:** Gewicht `_WIZARD_BASELINE_L1_WEIGHT` ggf. kalibrieren; weiteres Zerlegen von `_run_lp`.

## INT-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Produktnahe Live-Integrationspruefung nach Punkt 6 repo-seitig konkreter machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py`, `tests/test_integration_bootstrap.py`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Bootstrap-Readiness liefert zusaetzlich einen Probe-Plan fuer echte Connectivity-Pruefungen; CLI kann diesen Plan ausgeben; Tests unterscheiden ready, disabled, blocked und manual/external.
**Erledigt:** `build_integration_bootstrap_summary()` liefert jetzt `probe_plan`; `scripts/check_integration_bootstrap.py --probe-plan` gibt nur diesen Live-Probe-Plan aus; Tests decken ready/blocked/disabled fuer OIDC, NATS, Superglue, Voice und CRM-Downstream ab.
**Checks:** `pytest tests/test_integration_bootstrap.py -q`
**Offene Risiken:** Echte Produktivtests benoetigen weiterhin externe Tenant-Secrets, Zielsystem-URLs und Ops-Freigaben.

## RATIONS-REFACTOR Schritte 1-5 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Auslöser:** User-Feedback "rations_optimization.py: too large, too much in one pass, Refactoring-Roadmap in 5 Schritten".
**Stand:** Alle 5 Refactoring-Schritte umgesetzt; 561 passende Tests in der Rations-Regression (547 + 8 Aggregator + 6 Feed).

**Auslieferung:**
- **Paketstruktur** (Schritt 1a-e): Neues Paket `app/agrar/rations/` mit Subpackages `constants/`, `compound_feed/`, `repository/`, `http/`, `solver/`, `response/`. Konstanten, HTTP-Proxy, DLG-JSON-Loader und Compound-Feed-Parser (OCR/PDF/Etikett) leben jetzt in dedizierten Modulen; Re-Exports in `rations_optimization.py` halten die öffentliche Schnittstelle stabil.
- **Zentrale Aggregation** (Schritt 2): `RationAggregates` @dataclass(slots=True) + `aggregate_ration()` in `app/agrar/rations/response/aggregator.py`. `_build_response` nutzt sie jetzt in einem einzigen Pass statt 16+ `_sum()`-Aufrufen plus separaten Schleifen für Forage, CoP, pabKH und pendf. Block-Aggregation (Slice 1f) ist integriert.
- **Constraint-Registry** (Schritt 3): `ConstraintRegistry` + 17 symbolische Constraint-Namen in `app/agrar/rations/solver/constraint_registry.py`. `_run_lp` registriert jeden `_geq`/`_leq`-Aufruf benannt; die 4 historisch magischen Relaxations-Indizes (`_IDX_XL`, `_IDX_ANDFOM_GF`, `_IDX_RMD`, `_IDX_ME_ABS`) werden jetzt via `registry.index_of(...)` aufgelöst. Regressions-Asserts sichern die historische Reihenfolge.
- **Relaxations-Kapselung** (Schritt 4): Die 4-stufige Relaxations-Kaskade (XL → RMD → aNDFomGF-Drop → sidP-85%) ist aus dem LP-Hauptblock in eine benannte Closure `_relax_stage1()` ausgezogen. Semantik unverändert.
- **Feed-Dataclass** (Schritt 5): `Feed` @dataclass(slots=True) in `app/agrar/rations/solver/feed.py` als read-only View auf die Dict-Struktur. Bietet `Feed.from_dict()` mit konsistenter Typkonvertierung (None → 0.0 bei numerischen Pflichtfeldern, Optional bei unsicheren). Slot-Schutz verhindert unbeobachtete Attributerweiterungen. **Keine Breitenumstellung**, Opt-in für künftige Module.

**Tests:**
- Neue Unit-Tests `tests/test_rations_aggregator.py` (8 Tests) und `tests/test_rations_feed_dataclass.py` (6 Tests).
- Volle Rations-Regression: **561 pass** (davon 547 bestehende, unverändert grün).

**Offene Folgeschritte (bewusst separat):**
- Vollständige Zerlegung von `_run_lp` in Constraint-Builder/Relaxation/Stage2-Cost/Solve-Orchestrator (Schritt 4 ist bewusst minimal invasiv geblieben; ein echter Split ist ein eigener, größerer Slice).
- Breitenumstellung `Feed.from_dict`-basiert in `_run_lp` und `_build_response` (Schritt 5 legt nur das Fundament).
- Warnsystem regelbasiert (`WarningRule` statt if-Kaskade).
- Feed-Matrix mit NumPy für den Koeffizienten-Aufbau.



Dieses Board ist bewusst schlank gehalten, damit Session-Starts und Agent-Handoffs weniger Kontext verbrauchen.

## RATIONS-LP-SPLIT-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** `_run_lp` in `rations_optimization.py` durch Extraktion des Constraint-Matrix-Aufbaus in `app/agrar/rations/solver/lp_constraints.py` und der Stage-2-Policy-Extension in `app/agrar/rations/solver/lp_stage2.py` von ~1350 auf ~800 Zeilen reduzieren.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/lp_constraints.py` (neu), `app/agrar/rations/solver/lp_stage2.py` (neu), `tests/test_rations_lp_constraints.py` (neu)
**Abnahmekriterien:** Volle Rations-Regression gruen; `_run_lp` < 900 Zeilen; `lp_constraints.py` exportiert `build_lp_constraint_matrix`; `lp_stage2.py` exportiert `build_policy_band_lp_extension`.

## COV-RATCHET-004

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Coverage-Schwellen fuer bereits gruene kritische Pfade kontrolliert anheben (Puffer auf 97 % des gemessenen Wertes) und drei neue Ratchet-Pfade aufnehmen (strecke.py, sales_orders.py, ap_invoices.py).
**Dateibesitz:** `scripts/check_critical_backend_coverage.py`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Alle Schwellen liegen <= gemessener Wert; `python scripts/check_critical_backend_coverage.py` gibt gruenen Exit-Code wenn coverage.xml vorhanden.

## DOMAIN-PARITY-COV-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** COV-INT-002: Integrations-Governance-Tests fuer `strecke.py`, `kontrakte.py` und `ap_invoices.py` hinzufuegen; domain-parity-roadmap um abgeschlossene Slices aktualisieren.
**Dateibesitz:** `tests/test_strecke_api.py` (neu), `tests/test_kontrakte_api.py` (neu), `tests/test_ap_invoices_api.py` (neu), `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Neue Testdateien vorhanden, >= 5 Tests je Datei, pytest gruen; Roadmap-Dokument aktualisiert.

## RATIONS-FS-WIZARD-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Wizard-Schritt fuer `feeding_system_config` im Rations-Wizard in `rationsoptimierung.tsx` sichtbar machen (System-Auswahl TMR/PMR_stall/PMR_pasture, Konzentratsverteilung, Limits je Verteilung).
**Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/src/lib/api/rations-optimization.ts`
**Abnahmekriterien:** Wizard-Schritt sichtbar, `feeding_system_config` wird im Request gesendet, TypeScript-Typen passen, `pnpm run type-check` gruen.

## RATIONS-FANI-KL-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** FANi-basiertes dynamisches k_l in den Solver-Iterationsloop einbauen: `_gfe_requirements` erhaelt optionales `fani`-Argument, das `k_l_planning` (bisher fix 0,60) via `_kl_milk_from_me_density` iterativ anpasst. Gilt fuer PMR_pasture und TMR.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_fani_kl.py` (neu)
**Abnahmekriterien:** `_gfe_requirements(profile, fani=3.2)` gibt anderen `me_mj` als `fani=None`; Rations-Regression gruen; FANi-Iteration in `_run_lp` reicht FANi an `_gfe_requirements` durch.

Archiv des vorherigen Boards:
- [active-workboard-2026-04-10-pre-slim.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/archive/active-workboard-2026-04-10-pre-slim.md)

## AGRAR-COV-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `agrar_contracts.py` und `agrar_settlements.py` — Abnahme-Status-Logik, Abrechnungs-Rundung, DQ-Datensatz-Aufbau und CRUD-Smoke-Pfade.
**Dateibesitz:** `tests/test_agrar_contracts_api.py` (neu), `tests/test_agrar_settlements_api.py` (neu)
**Abnahmekriterien:** >= 15 Tests je Datei; `_compute_status`, `_round_money`, `_round_qty`, `_build_*_dq_datensatz` und HTTP-Pfade gruendeckend; pytest gruen.
**Erledigt:** 20 agrar_contracts-Tests (Status-Logik, DQ, CRUD); 17 agrar_settlements-Tests (Rundung, Modell-Validierung, Smoke-HTTP). 54 pass gesamt.

## FIN-COV-002

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `closing_checklists.py` und `bank_reconciliation.py` — Mapping-Funktion, Freigabe-Logik, Pydantic-Modelle und Smoke-Pfade.
**Dateibesitz:** `tests/test_closing_checklists_api.py` (neu), `tests/test_bank_reconciliation_api.py` (neu)
**Abnahmekriterien:** `build_closing_checklist_response` vollstaendig getestet inkl. approval_can_close und explainability; Pydantic-Modelle fuer BankReconciliation; HTTP-Smoke-Pfade gruen.
**Erledigt:** 17 closing_checklists-Tests (Mapping, Freigabe, Explainability, Validierung, HTTP); 11 bank_reconciliation-Tests (Pydantic-Modelle, HTTP-Smoke). 54 pass gesamt.

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
- Fuer den Flow-Spine-Kern liegt jetzt eine gemeinsame Lifecycle-Zieldoku vor:
  - [flow-spine-instance-lifecycle-overview.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/flow-spine-instance-lifecycle-overview.md)

## FEEDING-SYSTEM-ARCHITECTURE Slices 1-3 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Stand:** Slice 1a-1f/1h + Slice 2 (Futterabruf-Staffel) + Slice 3 (Mischprotokoll) komplett implementiert und gruen; 98 Slice-spezifische Tests plus 386 pass in der vollen Rations-Regression.
**Auslieferung:**
- **Datenmodell** (Slice 1a): Neue Pydantic-Modelle `ConcentrateRecipeProfile` (starch_breakdown_class rapid/mixed/slow, rumen_buffer_present, source), `FeedingSystemConfig` (system TMR/PMR_stall/PMR_pasture, concentrate_distribution transponder/ams/milkparlor/included_in_tmr, Grenzen je Verteilung), `FeedBlockAssignment` (manuelles Override fuer Feed->Block).
- **Block-Zuordnung** (Slice 1b): Helper `_feeding_system_defaults`, `_resolve_feeding_system_config`, `_auto_assign_block`, `_split_feeds_by_block`; Mineralfutter wird prioritaer ins `tmr_block` gesetzt (auch wenn im Namen "Weide" steht).
- **k_l-Logik** (Slice 1d): `_kl_milk_from_me_density` setzt bei `PMR_pasture` fix `k_l=0.60` (dokumentiertes Uebergangs-Fallback; FANi-basiertes k_l ist Folgeslice).
- **Solver-Scoping** (Slice 1c): Struktur-/CP-/XL-/pabKH-Dichten im LP nur auf den TMR-Block, wenn PMR-System mit aktivem pasture_block oder concentrate_staged_block vorliegt. Weide wird nicht als strukturell irrelevant behandelt (eigene Weide-/Aufnahmelogik weiterhin aktiv).
- **Konzentrat-Limits** (Slice 1e, nachgeschaerft): Einzelgabe physiologisch hart als 1.5x-Sicherheitsnetz im LP; empfohlenes Tagesmax weich im Constraint-Status (Klasse B, Halbbreite 1,5 kg). Rezepturklassen wirken: rapid REDUZIERT Tagesmax (SARA-Schutz), slow+Puffer = Premium.
- **Response-Payload** (Slice 1f): Neue Felder `ration_items[*].block` und `ration_blocks` (feeding_system + tmr_block/pasture_block/concentrate_staged_block mit DMI, Kosten, ME, sidP, CP und Items-Liste). Abwaertskompatibel: bei TMR bleibt pasture_block/concentrate_staged_block leer.
- **Wire-up** (Slice 1h): `_OptimizeFromProfileBody.feeding_system_config` und `feed_block_overrides` freigegeben; `_resolve_runtime_options` normalisiert beide und reicht sie bis in den Solver durch.
- **Regressionstests erweitert**: Bruder-Fall (PMR+Weide Fruehjahr) prueft jetzt explizit (a) keine harte globale Strukturstrafe, (b) plausible Milch-aus-Grobfutter (10-40 kg nach 1-kg-Milch/kg-TM-Praxisregel), (c) vollstaendige Mg/K-Diagnose, (d) kein technisches False-Infeasible, (e) ration_blocks-Aggregat deckungsgleich mit Gesamt-DMI.
- **Slice 2 - Konzentrat-Futterabruf-Staffel** (`_build_concentrate_call_up_table`): Linear / stueckweise linear oberhalb Basisleistung (Milch aus Grobfutter). Band 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch (Praxisrichtwert, nicht KI-Bildwerte). Einzelgabe-Limit je Verteilungssystem (Transponder/AMS/Melkstand), empfohlenes Tagesmax (weich) und physiologische Obergrenze 1,5x (hart) werden explizit geprueft. Nur fuer gestaffelte Systeme; `None` bei TMR/included_in_tmr. Response-Feld: `concentrate_call_up`. Neues UI-Panel `ConcentrateCallUpPanel` unterhalb des Weide-Risiko-Panels. 12 neue Tests.
- **Slice 3 - Misch- und Fuetterungsprotokoll** (`_build_mixing_protocol`): Nur bei TMR-Block (TMR / PMR_stall). Reihenfolge Vertikalmischer: Strukturfutter -> Silagen -> Saftfutter/CoP -> Sonstiges -> KF/Mineralien. Wasserzugabe auf Ziel-TM 40 % (Standard), Uebermenge +5 % fuer Mischverluste. Transparente Warnungen bei sehr trockener / sehr nasser Mischung. Response-Feld: `mixing_protocol`. UI-Panel `MixingProtocolPanel` rendert direkt aus Backend-Daten (keine Heuristik im Frontend mehr). 11 neue Tests.
**Offene Folgeslices / Mittelfristig:** FANi-basiertes dynamisches k_l (statt fixem 0,60 bei PMR_pasture); dedizierte Weideaufnahme-/Substitutionslogik mit saisonalen Profilen (Sommer-Hitzestress, Herbst-N-Ueberschuss); echte LP-Slacks fuer das Konzentrat-Tagesmax (aktuell Post-Solve-Penalty); Wizard-UI fuer `feeding_system_config` (derzeit nur ueber API).

## FAN-MODE-V1 (abgeschlossen 2026-04-21)

**Von:** Codex
**Stand:** alle sechs Slices umgesetzt, committed und gruen; 63 FAN-MODE-Gate-Tests plus bestehende Rations-Regression passen (266 pass + 6 pre-existing wave74-Fehler, unabhaengig von FAN-MODE).
**Freigegebene Spezifikation:** [docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md)
**Kernentscheidungen V1 (alle 2026-04-21 freigegeben, siehe §11.1):**
- `fan_tolerance=0.05`, warn `0.10`, max 5 Iterationen
- FAN-Presets `2.5 / 3.0 / 3.5` + Freiwert
- `relaxation_policy` dreistufig `strict` / `standard` / `soft`, Default `standard`
- Strafterme **dimensionslos normiert** auf Zielkorridor, Basis 1,0 EUR, Klassen A x10 / B x3 / C x1
- Drei-Block-Limits als versionierte **Policy-Profile** (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring`), Override nur im Expertenmodus
- FAN-Formel-Katalog mit **Herkunftsflag** `exact | mapped | fallback` (Mapping auf DLG-Hauptgruppen GF/KF/SF, saisonal bei Weide/Gras)
- Wizard-FAN-Modus **sichtbar-kompakt** (Default `auto_iterative` direkt sichtbar, Reference/EvaluationOnly einklappbar)
- Bruder-Regression als **fachlich differenziertes** Abnahmekriterium (kein technisches False-Infeasible)
**Abgeschlossene Slices und zugehoerige Commits:**
- FAN-MODE-001: additiver Datenvertrag, neue Request-/Response-Felder, `_resolve_runtime_options`, Policy-/Season-Enums (commit vor dieser Session, +11 Gate-Tests).
- FAN-MODE-002: Hart/Weich-Split mit normierter Penalty (`_build_constraint_status_v2`, `_compute_penalty`, `_summarize_penalty`), erweiterte Infeasibility-Diagnose (commit `82b02735c`, +11 Gate-Tests).
- FAN-MODE-003: Fixpunkt-FAN-Iteration (`_apply_fan_effect`, `_fani_from_result`) mit Katalog `app/config/fan_slope_catalog.json` und drei Modi `auto_iterative` / `reference` / `evaluation_only`; Startwert aus geschaetzter DMI fuer schnelle Konvergenz (commit `f0dce8abb`, +12 Gate-Tests).
- FAN-MODE-004: Wizard-UI-Erweiterung in `rationsoptimierung.tsx` (Bewertungsmodus-Block, Reference-Presets, Advanced-Optionen) und Ergebnispanels `FanCalibrationPanel` + `ConstraintStatusPanel` in der Workbench (commit `b6bd983c7`).
- FAN-MODE-005: Saisonales Weideprofil im UI (PMR+Weide oeffnet Advanced, preset `spring_mid`, zeigt aktives Profil `pmr_pasture_spring`); Backend-Auto-Mapping in `_resolve_policy_profile` abgedeckt (commit `9a035ddd8`, +7 Gate-Tests).
- FAN-MODE-006: Strafsatz-Konfiguration vollstaendig sichtbar (Normalisierung, Klassen A/B/C, relaxation-Policy Monotonie), `penalty_summary` im Response und in der UI (commit `769cd1527`, +10 Gate-Tests).
**Offene Risiken / Follow-ups:** siehe §13 der Spec.
**Naechster Schritt:** Beobachtung der Fruehjahrsration-Regression unter `pmr_pasture_spring` in der Praxis, anschliessend optionaler Spec-Folge-Slice fuer explizite Slack-Variablen im Solver (Vollwert-3-Stage-Objective statt Post-Solve-Penalty) – nur bei konkretem Bedarf.

## peNDF als Kontrollgroesse + aNDFomGF-staerkeadaptiv (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 22 neue peNDF-Demotion-Gate-Tests plus volle Rations-Regression `357 pass` (keine Regression gegenueber vorherigem Stand).
**Kontext / DLG-Position:** Die DLG 01|2023 stellt explizit fest: peNDF steht fuer die Rationsplanung **nicht zur Verfuegung**. Empfohlene primaere Planungsgroesse ist die aNDFomGF-Dichte (Grobfutter-NDF) mit Zielwert >= 200 g/kg TM fuer Hochleistungsrationen, bei hoeheren pansenabbaubaren Kohlenhydraten entsprechend mehr. peNDF bleibt als Kontroll-/Validierungsgroesse erhalten.
**Auslieferung:**
- **Neuer Helper `_andfom_gf_min_target`**: aNDFomGF-Mindestdichte setzt sich zusammen aus Basis (200 g/kg TM non-pasture, 180 g/kg TM PMR+Weide) + staerkeadaptivem Aufschlag (+10 g/kg TM pro 20 g/kg TM Staerke oberhalb 180, Cap +40) + Saisonal-Boost + SARA-Boost. Ist jetzt die primaere Pansenstruktur-Planungsgroesse.
- **Stage-2-LP umgebaut** (`_run_lp`): Der bisherige harte `pendf_floor` in Stage 2 (Cost-Stage) wurde durch ein staerkeadaptives `stage2_andfom_gf_min` ersetzt. peNDF bleibt nur noch als absolute physiologische Sicherheits-Floor (120 g/kg TM) im LP, nicht mehr als Planungsgroesse.
- **Kalibrierungsstatus `_pendf_model_calibrated`**: Das peNDF-Lookup-Modell gilt als kalibriert, wenn Staerke in [0, 250] g/kg TM und TM-Aufnahme in [10, 25] kg/d liegt. Ausserhalb laufen Fallback-Regeln. In `dlg_indicators` neu: `pendf_model_calibrated: bool`, `pendf_model_status: "peNDF-Modell im kalibrierten Bereich" | "peNDF ausserhalb Modellbereich; Fallback-Regeln verwendet"`, `pendf_role: "Kontrolle/Validierung (DLG 01|2023)"`. Ebenfalls neu: `andfom_gf_base` und `andfom_gf_starch_uplift` als transparente Herkunfts-Aufschluesselung.
- **Warnungen angepasst**: peNDF-Warnung laueft jetzt **primaer ueber den Kalibrierungs-Status** - ausserhalb Modellbereich erscheint ein expliziter Fallback-Hinweis statt einer pauschalen Unterdeckungs-Ampel. Innerhalb des Modellbereichs wird peNDF als "Kontrollgroesse im Warnbereich" markiert, mit Verweis auf aNDFomGF und pabKH als eigentliche Steuergroessen.
- **SARA-Trigger-Logik angepasst** (`_detect_sara_risk`): peNDF-Trigger feuert nur, wenn das Modell kalibriert ist. Zusaetzlich feuert jetzt ein expliziter `aNDFomGF < Ziel - 10`-Trigger als primaerer Struktur-Sicherheitspfad. pH-Trigger und pabKH-Trigger bleiben unveraendert.
- **Frontend-Panel `rationsoptimierung.tsx`** neu zweigeteilt: oberhalb "Planung (primaer)" mit Strukturindex, aNDFomGF (inkl. Staerke-Aufschlag-Zerlegung), pabKH, RMD - darunter "Kontrolle / Validierung (DLG 01|2023)" mit peNDF-Modell-Status-Zeile und peNDF/pH-Ampel. peNDF-Zeile heisst jetzt explizit "peNDF (Kontrolle)" und die Ampel wird neutralisiert (grau), wenn das Modell im Fallback-Bereich laeuft.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_pendf_demotion.py` (neu, 22 Tests).
**Tests:** `pytest -k "rations or optim or wave74"` -> **357 pass**. Neue Suite `tests/test_rations_optimization_pendf_demotion.py`: staerkeadaptive aNDFomGF-Berechnung parametrisiert, Kalibrierungsflag fuer typische und Extremwerte, `dlg_indicators`-Zeichenketten ("Kontrolle"/"aNDFomGF"/Fallback-Status), SARA-Trigger respektiert Kalibrierungsstatus, Warnung bei peNDF-Fallback.
**Simulation bestaetigt:** Variant B (Hochleistung 48 kg Milch, DMI 26.6 kg/d > 25) liefert jetzt den Hinweis "peNDF ausserhalb Modellbereich ... Fallback-Regeln verwendet - peNDF-Ampel nur eingeschraenkt belastbar". Keine False-Alarme bei fachlich guten Rationen.
**Offene Follow-ups:** Praxisvalidierung der staerkeadaptiven aNDFomGF-Staffelung mit echten Hochleistungsrationen. Ggf. Sekundaer-Kalibrierungs-Flag fuer die pH-Formel analog dokumentieren (ist bereits via `ph_formula_applicable` verfuegbar).

## Gras-/Silage-/Heu-Klassifikation TM-basiert (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `96 pass` (inkl. `32 neue Gate-Tests` in `tests/test_rations_optimization_grass_classification.py`).
**Kontext:** User-Feedback zum Screenshot vom 2026-04-21: In der Ration war "Gras, frisch o. konserviert, 2. Aufwuchs" mit 6,6 kg FM / 2,32 kg TM (→ 35 % TM) enthalten, wurde aber faelschlich als Weide klassifiziert - das UI-Panel zeigte "Grassilage TM: 0,00 kg". Die Namens-Heuristik konnte die drei DLG-Varianten (frisch/siliert/trocken, `TMGEHALT` 175/350/860 g/kg) nicht sauber unterscheiden, weil das Feed-Namens-Feld fuer alle drei identisch ist.
**Fachliche Regel (User):** "Haupterkennung fuer Silagen sind ein TM Gehalt von 30 bis 40 %, bei ueber 80 % Heulage, bei ueber 85 % Heu bei Gras."
**Auslieferung:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert Gras-basierte Grobfutter **primaer ueber `dm_frac`** (TM-Anteil), mit Name-Fallback wenn TM fehlt. Rueckgabe `"pasture"` (TM < 30 %), `"grass_silage"` (30-80 % TM, inkl. Anwelksilage/Heulage), `"grass_hay"` (≥ 80 % TM bei Gras-Kontext) oder `None` (Nicht-Gras).
- **Vier Call-Sites vereinheitlicht:** `_is_pasture_feed` und `_is_grass_silage` (in `_build_response`), `_max_kg_for` (LP-Obergrenze), `_feed_pendf_factor_base`, `_has_pasture_forage`, `weide_mask` (TMR-Deckelung) und `_map_feed_to_gfe_group` (FAN-Gruppen-Zuordnung) nutzen jetzt durchgaengig die TM-basierte Klassifikation.
- **Regression aufgeloest:** "Gras, frisch o. konserviert, 2. Aufwuchs" mit 35 % TM wird jetzt korrekt als `grass_silage` erkannt; "Weide, Fruehjahr, jung" mit 17,5 % TM bleibt Weide. Die UI-Anzeige "Grassilage TM" im Weide-Panel listet kuenftig die konservierten DLG-Varianten korrekt.
- **Tests**: `tests/test_rations_optimization_grass_classification.py` (neu, 32 Tests) deckt ab: TM-Grenzen 30 %/80 %, alle drei DLG-Varianten, Weide-Erkennung, Heulage/Heu, Nicht-Gras-Futtermittel (Mais/Weizen/Soja/Stroh/Mineral), Name-Fallback ohne TM, Screenshot-Regression.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (6 Aenderungen: neue Helper-Funktion `_grass_feed_kind`, `_is_pasture_feed`/`_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`), `tests/test_rations_optimization_grass_classification.py` (neu), `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_dlg2025.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_grass_classification.py` → **96 pass**, keine Regression.
**Offene Follow-ups:** - (keine).

## Milch-aus-Grundfutter Plausibilitaet + TM-basierte Gras-Klassifikation (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `115 pass` in 4 relevanten Rations-Suiten (davon `51 neue Gate-Tests`: 32 in `test_rations_optimization_grass_classification.py`, 19 in `test_rations_optimization_milk_plausibility.py`).

**Kontext:** Zwei verschraenkte User-Beobachtungen aus dem Screenshot vom 2026-04-21:
1. "Gras, frisch o. konserviert, 2. Aufwuchs" (35 % TM) wurde faelschlich als Weide klassifiziert -> UI zeigte "Grassilage TM: 0,00 kg". Der Feed-Name konnte die drei DLG-Varianten (frisch 17,5 % / siliert 35 % / trocken 86 % TM) nicht unterscheiden, weil das Namensfeld fuer alle identisch ist.
2. Faustregel "1 kg TM Grundfutter ~ 1 kg Milch, Spitzengrundfutter bis 1,2" wurde massiv ueberschritten (37,6 kg Milch / 22,1 kg GF-TM = 1,70 kg/kg).

**Auslieferung - TM-basierte Klassifikation:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert primaer ueber `dm_frac` (Frischgras < 30 %, Grassilage inkl. Anwelksilage/Heulage 30-80 %, Heu >= 80 %), Name-Fallback wenn TM fehlt.
- **Sechs Call-Sites vereinheitlicht:** `_is_pasture_feed`, `_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group` nutzen jetzt durchgaengig die TM-Klassifikation.

**Auslieferung - Milch-aus-GF-Plausibilitaet (drei Slices):**
- **Slice A - Weide-Aktivitaetszuschlag:** In `_gfe_requirements` und `_milk_requirement_factors` wird bei `feeding_type == "PMR+Weide"` ME_maint um **+15 %** erhoeht (DLG-Merkblatt 417 / GfE 2001: Lauf-, Rupf-, Thermoregulations-Aktivitaet). Das wirkt sowohl auf die Solver-Bedarfsberechnung (Konsistenz) als auch auf die Anzeige "Milch aus Grundfutter".
- **Slice B - Weide-TM-Obergrenze:** In `_max_kg_for` wurde die Weide-Obergrenze von 14 auf **12 kg TM/d** reduziert (DLG 417: Praxismittel Hochleistungs-Standweide 10-12 kg). Das begrenzt die LP-Optimierung auf physisch erreichbare Aufnahmemengen.
- **Slice C - dichte-abhaengiges k_l:** Neue Helper-Funktion `_kl_milk_from_me_density(me_density)` implementiert GfE 2001 §5: **k_l = 0,463 + 0,24 * q** mit q = ME/GE (GE ~ 18,4 MJ/kg TM), begrenzt auf den Arbeitsbereich [0,58 ; 0,64]. Statt fix `k_l = 0,62` rechnet der Code jetzt fuer jede Auswerte-Ebene (Gesamt, Grundfutter, Weide, Grassilage, Weide+Silage) mit der ration-spezifischen ME-Dichte. In `_gfe_requirements` selbst bleibt `k_l_planning = 0,60` als konservativer Default fuer den Solver-Bedarf (leichte Verschaerfung gegenueber vorher 0,62, ~3 % mehr ME-Bedarf).

**Wirkung auf den Screenshot-Fall (ME-Dichte 11,6 MJ/kg TM, 22,1 kg GF-TM, PMR+Weide):**
- Alte Anzeige: 37,6 kg Milch aus GF -> 1,70 kg/kg TM
- Neu (A+C in fester Ration): 37,1 kg -> 1,68 kg/kg TM (nur -0,5 kg, weil bei 11,6 MJ/kg ME-Dichte die Faustregel rechnerisch hoeher liegt)
- **Eigentlicher Hebel ist Slice B in der LP-Optimierung**: Die naechste Demo-Rueckoptimierung wird statt 14 kg Weide nur noch 12 kg ansetzen duerfen, wodurch der Solver mehr Kraftfutter einsetzt und "Milch aus Grundfutter" auf realistische 28-32 kg faellt (~1,3-1,4 kg/kg TM).

**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (neue Helper `_grass_feed_kind`, `_kl_milk_from_me_density`; modifiziert: `_gfe_requirements`, `_milk_requirement_factors`, `_milk_from_supply`, `_max_kg_for`, `_is_pasture_feed`, `_is_grass_silage`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`, alle Weide-/Grassilage-Milch-Aufrufe im `_build_response`).
**Neue Tests:** `tests/test_rations_optimization_grass_classification.py` (32 Gate-Tests), `tests/test_rations_optimization_milk_plausibility.py` (19 Gate-Tests fuer k_l-Kurve, Weide-Zuschlag, Screenshot-Regression, Faustregel-Korridor).

**Tests:** `pytest tests/test_rations_optimization_*.py` -> **115 pass**, keine Regression in den bestehenden Suites (dlg2025: 60, compound_feed: 4).

**Fachliche Quellen:**
- GfE 2001 (Empfehlungen fuer die Energie- und Naehrstoffversorgung der Milchkuh), §5 k_l-Berechnung
- DLG-Merkblatt 417 "Fuetterung der Milchkuh auf der Weide"
- DLG-Futterwerttabellen 2025 (Feld `KONSERVIERUNG`: frisch / siliert / trocken mit TM 175/350/860 g/kg)

**Offene Follow-ups:** - (keine). Weitere Feldvalidierung erfolgt durch den naechsten Durchlauf der Bruder-Regression mit den neuen Grenzen.

## DLG-01|2025 LP-Slacks + Praxisvalidierung Bandgewichte (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `155 pass` in den acht relevanten Rations-Suiten (inkl. `+22 neue Gate-Tests` in `tests/test_rations_optimization_dlg2025.py` → jetzt 60 DLG2025-Tests).
**Kontext:** Zwei Follow-ups aus dem Slice "DLG-01|2025 Solver-Bindung" zusammengezogen - (a) die Post-Solve-Penalty fuer Policy-Baender wurde durch **native LP-Slack-Variablen** ersetzt, und (b) die Halbbreiten (`min_halfwidth`) je Parameter wurden mit typischen Hochleistungs- und Trockensteher-Rationen kalibriert und als Tests abgesichert.
**Auslieferung:**
- **Backend `_build_policy_band_lp_extension`** (neu in `rations_optimization.py`): baut fuer jedes Policy-Band (ME-/CP-/sidP-/pabKH-/XL-/Grundfutter-/aNDFomGF+CoP-/aNDFom-Dichte) eine **Slack-Variable** `s_min` bzw. `s_max >= 0` mit normierter Penalty im Objective auf. Die Slack-Kosten skalieren mit `base × class_B × relax_factor / (halfwidth × DMI_typ)`, so dass LP-Slack und Post-Solve-Penalty fachlich aequivalent sind. `_run_lp` fuehrt, wenn ein DLG-2025-Profil aktiv ist, einen **erweiterten Stage-2-Solve** durch (`prices ⊕ slack_costs`, `A ⊕ slack_cols`, `bounds ⊕ (0, ∞)`); bei Erfolg werden nur die Feed-Anteile uebernommen, die Slack-Werte gehen als Diagnose-Payload `policy_profile_lp_slacks` in die Response. Metadaten-Strategie ist dann `stage1_balance_then_stage2_cost_plus_policy_slack`.
- **Response-Erweiterung:** neue Felder `policy_profile_lp_slacks` (pro Band: `slack_value`, `weight`, `halfwidth`, `penalty_cost`, `active`), `policy_profile_lp_total_penalty`, `policy_profile_lp_mode`. Die bisherige Post-Solve-Auswertung `policy_profile_evaluation` bleibt als unabhaengiger Gegencheck erhalten, wenn die LP-Slacks aus technischen Gruenden kein Payload liefern.
- **Frontend `rations-optimization.ts`**: neuer Typ `PolicyProfileLpSlack`, Response-Interface um die drei neuen Felder erweitert.
- **UI `rationsoptimierung.tsx`**: im Panel "Leistungsstufen-Check (DLG 01|2025)" neues Badge **"LP-Slack aktiv"** (gruen) bei nativer Bindung plus Subsection "LP-Solver-Slacks (aktive Korridor-Verletzungen)" mit Slack-Wert/Einheit und Penalty pro Band sowie Summen-Penalty - zeigt, welche Baender der Solver selbst relaxieren musste.
- **Praxisvalidierung `test_rations_optimization_dlg2025.py`**: neue Klassen `TestPolicyBandLpSlackExtension` (6 Tests) und `TestPolicyBandHalfwidthCalibration` (16 parametrisierte Tests) belegen fuer typische Hochleistungs- (35-45 kg, ME 7,0-7,2 / CP 155-170 / sidP 78-85) und Trockensteher-Rationen (ME 5,8-6,2 / CP 120-135 / aNDFom 380-460), dass Werte **im Korridor zero-penalty** sind und Abweichungen > Halbbreite **monoton zunehmende Strafen** erzeugen. Zusaetzlich: `test_halfwidth_is_reference_for_penalty_unit` fixiert, dass eine Abweichung von exakt `1 × min_halfwidth` ausserhalb des Korridors die Einheits-Strafe `base × class_B × relax_standard` ergibt.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`, `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_*.py tests/test_drying_rule_engine.py` → **155 pass**, keine Regression.
**Offene Follow-ups:** - (keine mehr aus dem DLG-01|2025-Block; weitere Feldvalidierung erfolgt im Rahmen der Bruder-Regression und der Hitzestress-/Herbstrations-Slices.)

## DLG-01|2025 Solver-Bindung + Wizard-Leistungsstufen (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `138 pass` in den sieben relevanten Rations-Suiten (inkl. 7 neue Band-/Solver-Bindungs-Tests in `tests/test_rations_optimization_dlg2025.py`).
**Kontext:** Follow-ups aus dem "DLG-01|2025-Alignment"-Slice wurden zusammen gezogen - (a) die Referenzkorridore aus `_POLICY_PROFILE_TARGETS` waren bisher nur im Response sichtbar, aber nicht im Solver gebunden, und (b) die neuen DLG-2025-Leistungsstufen waren nicht im Wizard anwaehlbar.
**Auslieferung:**
- **Backend `rations_optimization.py`**: Neue Helfer `_policy_profile_band_evaluate` + `_build_policy_profile_evaluation`. Nach jedem erfolgreichen LP-Lauf werden die Ist-Werte der Ration gegen die DLG-01|2025-Referenzkorridore des aktiven Profils als **weiche Bandchecks** (direction = min / max / target, Band-Modell) ausgewertet. Penalty faellt in **Klasse B** (Balance), relaxation_policy skaliert wie gewohnt (strict = 3x, standard = 1x, soft = 0.3x). Innerhalb des Korridors gilt `deviation_norm = 0`, also keine Strafe - dadurch keine zusaetzliche Infeasibility-Gefahr fuer schwierige Praxisrationen.
- **Ausgewertete Baender:** ME-Dichte (MJ/kg TM), CP-Dichte (g/kg TM), sidP-Dichte (g/kg TM), pabKH (max), Rohfett XL, Grundfutteranteil (%TM), aNDFomGF+CoP (min), aNDFom (min). Jedes Band traegt den Namen `DLG-Policy: ...` in `constraint_status` (source=`policy_profile`).
- **Response-Erweiterung:** neues Feld `policy_profile_evaluation` mit `profile`, `label`, `bands` (alle Checks inkl. `ok`), `violation_count`, `violations`, `penalty_total`, `source`. `penalty_summary.by_class.B` enthaelt die Policy-Strafe mit.
- **Frontend `rations-optimization.ts`**: neue Typen `PolicyProfileBand` + `PolicyProfileEvaluation`, Response um `policy_profile_evaluation` erweitert, `PolicyProfileTargets`-Feldnamen an das Backend angepasst (`forage_share_min_pct` / `forage_share_max_pct` / `ndf_kgdm_min`).
- **Wizard `rationsoptimierung.tsx`**: Im Advanced-Block neuer Dropdown **"Leistungsstufe (DLG 01|2025 Tab. 13-15)"** mit sechs Leistungs-/Physiologiestufen (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_transit`, `tmr_dry_cow`) plus den Bestandsprofilen (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring|summer|autumn`). Default "Auto (aus Fuetterungstyp/Saison)". Die Auswahl wird durch den vorhandenen `policy_profile`-Request-Parameter an das Backend durchgereicht. Hinweistext macht sichtbar, dass die Bindung **weich** ist (Klasse B, relaxation-policy-skaliert).
- **Ergebnispanel:** neues Panel "Leistungsstufen-Check (DLG 01|2025)" direkt nach dem DLG-Strukturkontrolle-Panel. Zeigt Profil-Label, Gesamtstrafe Klasse B, pro Band `Ist-Wert`, `Korridor (min … max)`, Abweichungs-Norm und Ampelpunkt (gruen/ok oder orange/violated). Badge oben zeigt "alle Baender im Korridor" oder "N Abweichung(en)".
- **Tests (7 neu in `tests/test_rations_optimization_dlg2025.py`):** `_policy_profile_band_evaluate` → ok-Band ohne Strafe, Unter-Min und Ueber-Max erzeugen Strafe in Klasse B, strict/standard/soft skaliert Strafe monoton, `_build_policy_profile_evaluation` returniert `None` ohne Profil/Targets, End-to-End-Response belegt `policy_profile_evaluation` + `constraint_status`-Eintraege mit `source=policy_profile` und fuettert `penalty_summary.by_class.B`. Negativtest: `tmr_standard` liefert kein `policy_profile_evaluation`.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`.
**Tests:** `pytest tests/test_rations_optimization_*.py` → **138 pass** in den sieben relevanten Suiten, keine Regressionen gegenueber dem vorherigen Stand (82 pass).
**Offene Follow-ups:**
- Praxisvalidierung der Bandgewichte (min_halfwidth je Parameter) mit echten Hochleistungs-/Trockensteher-Rationen.
- Optional: Umstellung von Post-Solve-Penalty auf native LP-Slacks mit gemeinsamer Stufe-2-Zielfunktion (fachlich aequivalent, aber zukunftssicherer fuer Priorisierungsschemata).

## DLG-01|2025-Alignment (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 32 neue DLG2025-Gate-Tests plus volle Rations-Regression `82 pass` in den vier relevanten Suiten.
**Kontext:** Nach dem SARA-Reopt + peNDF-Demotion hat der User um Abgleich der aktuellen Annahmen und Gleichungsformeln mit `DLG-Information 01|2025` (und, soweit nicht ueberholt, `01|2023`) gebeten. Der Abgleich hat vier konkrete Differenzen offengelegt, die in diesem Slice zusammen umgesetzt wurden.
**Auslieferung:**
- **DLG2025-PH-FORMEL**: Pansen-pH-Prediction nach Zebeli 2008 (zitiert in DLG 01|2025 Kap. 8.3), jetzt mit korrekten Koeffizienten `pH = 6,05 + 0,044·peNDF − 0,0006·peNDF² − 0,017·abbauSt − 0,016·TM`. Neuer Helfer `_abbaust_density_kgdm` ermittelt die **pansenabbaubare Staerke** (`ST − bST`), die als zweite formelwirksame Eingangsgroesse dient. Zucker beeinflusst die Formel **nicht** mehr. `dlg_indicators.ph_formula_source` = `Zebeli 2008 (DLG 01|2025)`, zusaetzlich `abbaust_kgdm` in `nutrient_supply` / `dlg_indicators`.
- **DLG2025-ANDFOMGF-COP**: Einfuehrung der Co-Produkt-Klassifikation (`structural_coproduct`-Flag je Feed; Heuristik ueber `_is_structural_coproduct` auf Namen/Kategorie; Saftfutter wie Biertreber/Pressschnitzel/Kartoffelpuelpe/Trockenschnitzel/Malztreber werden jetzt automatisch als strukturwirksam gefuehrt). `aNDFomGF`-Planung wird ersetzt durch `aNDFomGF+CoP` mit **binaerer DLG-Kaskade** (pabKH ≤ 210 → 200 g/kg TM, pabKH > 210 → 280 g/kg TM, pabKH > 260 loest Warnung). `_andfom_gf_min_target` nimmt `pabkh_density_kgdm` und greift auf die Kaskade zurueck, wenn verfuegbar; die alte Staerke-uplift-Linearitaet bleibt nur als Fallback. LP-Constraint in `_run_lp` ist entsprechend auf `aNDFomGF+CoP-Dichte` umgezogen; `constraint_report`, `nutrient_supply`, `dlg_indicators` und `_detect_sara_risk` nutzen die neue Groesse.
- **DLG2025-FIKH**: Neue Kontrollgroesse **Fermentationsindex Kohlenhydrate** (DLG 01|2025 Kap. 8.4): `FIKH [%] = DNDF / (DNDF + ST+ZU−bST) · 100`, Zielwert ≥ 50 %. Helfer `_fikh_percent` beruecksichtigt fehlende `NDFD`-Werte und liefert Diagnose (`no_ndfd` / `ok`). Ergebnis unter `dlg_indicators.fikh_pct | fikh_ziel | fikh_erfuellt | fikh_diagnose | fikh_quelle`. Warnung wenn FIKH < 50 %.
- **DLG2025-POLICY-TABELLE14**: `_POLICY_PROFILES` erweitert um leistungs-/physiologiestufige Profile (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_dry_cow`, `tmr_transit`). Neuer Katalog `_POLICY_PROFILE_TARGETS` mit Referenzkorridoren fuer ME, CP, sidP, pabKH, XL, Grobfutteranteil, `aNDFomGF+CoP`, `aNDFom` je Profil. Response liefert `policy_profile_targets`, wenn ein DLG-2025-Profil aktiv ist - Basis fuer die Folge-Slices (Solver-Bindung / UI-Auswahl).
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_optimization_sara_reopt.py`, `tests/test_rations_optimization_dlg2025.py` (neu, 32 Tests).
**Tests:** `pytest tests/test_rations_optimization_sara_reopt.py tests/test_rations_optimization_pendf_demotion.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_dlg2025.py` → **82 pass**.
**Offene Follow-ups:**
- Frontend `rationsoptimierung.tsx`: FIKH-Zeile im "Kontrolle / Validierung"-Block und `aNDFomGF+CoP` im Planung-Block ergaenzen (bisher nur `aNDFomGF` sichtbar).
- Wizard: Auswahl der neuen Leistungsstufen-Profile (`tmr_fresh_lactation` usw.) per Expertenmodus freischalten; derzeit nur per API-Override.
- Solver-Bindung der `policy_profile_targets`: aktuell nur Referenzwerte im Response, noch nicht als weiche Constraints im LP gefuehrt. Folge-Slice bei Bedarf.

## SARA-Safety-Reopt + pH/peNDF-Fixes (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 23 neue SARA-Gate-Tests plus volle Rations-Regression `335 pass` (keine Regression).
**Kontext:** Der User hat eine Szenariosimulation mit gezielter Pansenacidose-Provokation angefragt. Dabei kamen False-Positive-SARA-Alarme (pH=5.50 ROT auch bei fachlich guter Ration) zum Vorschein. Ursachenanalyse: (a) `_feed_pendf_factor` unrealistisch hoch (z. B. `0.90` fuer Grundfutter), (b) Zebeli/Schwarz-pH-Formel wurde mit **g/kg TM** statt **% TM** gefuettert, (c) es gab keinen automatischen Reopt-Loop.
**Auslieferung:**
- **pH-Formel-Korrektur (`_ph_predict`)**: Inputs werden jetzt von g/kg TM nach % TM umgerechnet (`peNDF_%`, `Staerke_%`), zusaetzlich auf den publizierten Validitaetsbereich geclippt (peNDF 60-250 g/kg TM, Staerke 50-350 g/kg TM, DMI 10-25 kg/d). Neue Helfer `_ph_inputs_in_range` und Response-Flag `dlg_indicators.ph_formula_applicable`.
- **peNDF-Faktor-Neukalibrierung (`_feed_pendf_factor`)** nach Zebeli 2012 / DLG 01|2023: Grundfutter 0.90 -> 0.50 Default, dazu Overrides: Stroh 1.00, Heu 0.95, Luzerne 0.70, Grassilage 0.55, Maissilage 0.45, Trockenkraftfutter 0.10, Getreide 0.10, Melasse 0.00.
- **SARA-Safety-Reopt-Loop (`_maybe_run_sara_safety_reopt`)**: Nach der primaeren FAN-Iteration prueft `_detect_sara_risk` auf pH < 5.9, peNDF < Minimum oder pabKH am Limit. Bei Trigger laeuft eine zweite LP-Runde mit verschaerften Constraints (pabKH-Max -20 g/kg TM, peNDF-Floor +15 g/kg TM, aNDFomGF +10 g/kg TM, NaHCO3-Pansenpuffer als Pflicht mit min. 0.15 kg TM/d). Ergebnis-Payload `sara_safety_reopt` mit `triggered`, `reason`, `actions`, `resolved`, `metrics_before` / `metrics_after`.
- **Frontend-Badge**: Neues Panel in `rationsoptimierung.tsx` zeigt bei aktivem Reopt-Loop die Ausloese-Indikatoren, durchgefuehrte Verschaerfungen und Vorher/Nachher-Metriken (pH, peNDF, pabKH). Farbcode orange = `resolved`, rot = `resolved=false`. DLG-Panel verdeckt die pH-Ampel, wenn die Formel ausserhalb ihres Validitaetsbereichs liegt, um False-Positives zu unterdruecken.
- **Defense-in-Depth**: Provokationsszenarien (`scripts/simulate_acidosis_scenarios.py`, Varianten G/H: 42-45 kg Milch, Maissilage + viel Getreide, ohne Grundstruktur) werden bereits vom LP als `infeasible` abgelehnt (harte Constraints: CP-Dichte, XL-Dichte, Mg-Kapazitaet) - der Reopt-Loop greift als zweite Sicherung, wenn die LP eine scheinbar optimale Loesung mit SARA-Risiko liefert.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_sara_reopt.py` (neu, 23 Tests), `scripts/simulate_acidosis_scenarios.py`, `scripts/_list_feeds.py` (neu, Helper).
**Tests:** `pytest -k "rations or optim or wave74"` -> **335 pass**. Neue Suite `tests/test_rations_optimization_sara_reopt.py`: pH-Clipping + Einheit, peNDF-Faktoren (parametrisiert 13 Feed-Typen), SARA-Risikoerkennung, End-to-End-Reopt, False-Positive-Regression.
**Simulation (Live-Nachweis):** Alle sechs fachlich guten Varianten A-F (TMR, PMR+Weide spring/summer/autumn) zeigen jetzt Pansen-pH 6.46-6.50 GRUEN und peNDF 200-215 g/kg TM GRUEN. Keine False-Positives mehr.
**Offene Follow-ups:** Winterration-Profil bei Bedarf nachziehen. Felddaten sammeln, um den Reopt-Loop in echten SARA-Fruehwarnfaellen zu validieren.

## FAN-MODE-V1 §12 Saisonprofile + wave74-Fix (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, committed und gruen; 30 neue Saisonprofile-Gate-Tests + 6 wave74-Tests repariert. Keine offenen Regressionen in `rations`/`optim` (303 pass).
**Auslieferung:**
- **Wave74-Fix:** `get_rations_base_url()` ist jetzt oeffentlich (vormals `_rations_base_url`). Die wave74-Proxy-Tests bilden den neuen **hybriden Kontrakt** ab: Ohne `RATIONS_OPTIMIZATION_URL` laeuft der interne GfE-2023-Solver (200 + `active_policy_profile`), 503 nur wenn Proxy konfiguriert **und** nicht erreichbar.
- **Sommerration (Hitzestress, DLG-Merkblatt 417 / GfE-Workshop 2023):**
  - Neues Policy-Profil `pmr_pasture_summer` fuer PMR+Weide + `summer_young|mid|late`.
  - DMI-Reduktion je Saisonstufe: `summer_young -3 %`, `summer_mid -7 %`, `summer_late -12 %` (auf `dmi_target/min/max/ndf_min/k_max`).
  - Na-Boost +15 % / +25 % / +30 % fuer Schwitzverluste.
  - Neues Spezialsupplement `special_summer_rumen_buffer` (NaHCO3, 220 g Na/kg TM) wird automatisch als Pflichtbaustein mit `min_kg >= buffer_min_kg` gefuehrt.
  - `summer_late` zusaetzlich +10 g/kg TM aNDFomGF-Boost.
- **Herbstration (stickstoffreicher Grasaufwuchs):**
  - Neues Policy-Profil `pmr_pasture_autumn` fuer PMR+Weide + `autumn`.
  - CP-Dichte-Obergrenze hart auf 175 g/kg TM (Harnstoffschutz, vs. 185 Default PMR+Weide).
  - aNDFomGF-Mindestdichte +15 g/kg TM (Strukturstuetzung gegen N-Ueberschuss).
  - RMD-Korridor kontrolliert um +1 g N/kg TM entspannt (weidetypisch, nicht beliebig).
- **Frontend:** `PolicyProfile`-Typ erweitert; Wizard zeigt je Saison aktive Policy-Hinweise (Sommer/Herbst) im PMR+Weide-Block.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_process_kernel_wave74_rations_optimization.py`, `tests/test_rations_optimization_fan_mode_004_policy.py`, `tests/test_rations_optimization_fan_mode_v1.py`, `tests/test_rations_optimization_seasonal_profiles.py` (neu).
**Tests:** `pytest -k "rations or optim"` → 303 pass; neue Suite `tests/test_rations_optimization_seasonal_profiles.py` mit 30 Tests gruen; wave74-Suite mit 28 Tests gruen.
**Offene Follow-ups:**
- Winterration bei Zukunftsbedarf modellieren (aktuell neutraler `winter`-Profilpunkt ohne Anpassungen).
- Felddaten aus Praxistests Sommer/Herbst sammeln, um DMI-Faktoren und Buffer-Minima zu kalibrieren.

## RAT-OPT-001

**Von:** Codex
**Stand:** in arbeit
**Ziel des Slices:** Rationsoptimierung fachlich und technisch auf belastbaren DLG-01|23-Stand ziehen: Frontend-Submit stabilisieren, TMR/PMR-Logik explizit machen und Ergebnisdarstellung um Grundfutter-/Kraftfutter-Leistungsbeitrag inklusive Grundfutterverdrängung ergänzen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, ggf. gezielte Tests unter `tests/`
**Abnahmekriterien:** Optimierung startet stabil aus dem Wizard ohne State-Race; Response und UI zeigen Milch aus Energie/Protein als IST-/Soll-Sicht aus Grundfutter sowie Zusatz-Kraftfutter für Zielmilch; PMR berücksichtigt Konzentratgabe und Grundfutterverdrängung nachvollziehbar; DLG-01|23-Abgleich ist dokumentiert.
**Offene Risiken:** DLG-Dokument liefert fachliche Leitplanken, aber keine 1:1-Formeln für jede Betriebsheuristik; Grundfutterverdrängung muss daher als dokumentierte Näherung implementiert und klar gekennzeichnet werden.
**Update 2026-04-21:** Wizard-Submit auf mutierende State-Race geprüft und auf parameterisierte Mutation umgestellt; `feeding_type` geht jetzt explizit in den Request. Backend liefert `forage_performance` mit Milch aus Energie/Protein aus Grundfutter, Zielmilch, Kraftfutter-TM und dokumentierter Grundfutterverdrängungs-Heuristik für TMR/PMR. Frontend zeigt die Kennzahlen in Workbench und Review. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `cmd /c pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, direkte Modulverifikation via `python -` auf `_optimize_internal(_demo_profile())`. Laufender lokaler FastAPI-Prozess muss für die neuen Response-Felder ggf. neu geladen werden.
**Update 2026-04-21 (Upload/Bridge):** `main.py` loggt Dev-Warnungen jetzt ASCII-sicher. `POST /api/v1/agrar/rations-optimization/compound-feed/upload` nimmt PDF- und Foto-Dokumente für Kraftfutter-Rezepturen/Lieferscheine an, parst Deklarationswerte, matched Rezepturanteile gegen die DLG-Futterdatenbank und liefert eine Legacy-zu-GfE-2023-Brücke inkl. direkt nutzbarem Optimizer-Feed. Der Wizard in `rationsoptimierung.tsx` kann diese Uploads jetzt als betriebseigenes Kraftfutter in die Futtermittelauswahl übernehmen. Regressionstest `tests/test_rations_optimization_compound_feed.py` ist grün; API-Vertrag lokal per `TestClient` mit `Bödeker Ditzum.pdf` geprüft. Die enge Praxisprobe `Weide + Grassilage 2. Schnitt + 1 kg Maismehl + 1 kg Gerstenmehl + Milchleistungsfutter` bleibt unter den aktuellen harten PMR-Restriktionen noch `infeasible` und ist damit jetzt ein fachlicher Solver-Kalibrierpunkt, kein Upload-/UI-Defekt mehr.
**Update 2026-04-21 (Solver-Prinzip):** Interner LP-Solver priorisiert jetzt nicht mehr direkt Kosten, sondern rechnet zweistufig: Stage 1 sucht zuerst eine fachlich ausgeglichene, pansenstabile Basisration; Stage 2 optimiert erst innerhalb dieses Balance-Korridors auf Kosten. Außerdem greift die starre `Weide <= 4 kg TM`-Grenze jetzt nur noch bei `TMR`, nicht mehr pauschal auch bei `PMR/Weide`. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, Praxisprobe via `python -` auf `_optimize_internal(...)`, Regression `pytest tests/test_rations_optimization_compound_feed.py -q --no-cov`. Die konkrete Frühjahrsration bleibt trotz korrigierter PMR-Logik noch `infeasible`; nächster fachlicher Slice ist damit die Kalibrierung der harten XL-/CP-/Weide-Regeln für Weidesysteme.
**Update 2026-04-21 (Weide/PMR):** Auf Basis von DLG 443/444, DLG 417, DLG-Information 01|2023 und dem GfE-Workshop-Stand vom 5. März 2026 ist jetzt ein erster `PMR+Weide`-Pfad eingezogen: Weide-/Frischgrasfutter sind nicht mehr global auf 4 kg TM gedeckelt, TMR-Deckelung greift nur noch im echten TMR-Fall; fuer PMR+Weide werden `aNDFomGF`, `pabKH`, `XL`, `CP`, `K` und Mindest-Grundfutteranteil adaptiv bewertet. Die Fruehjahrsprobe mit `Weide + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` bleibt fachlich weiter `infeasible`; die Diagnose weist jetzt explizit auf das reale Mg-/Energie-Problem der engen Auswahl hin (`Magnesiumdichte ... reicht innerhalb der zulaessigen Energieversorgung nicht aus`) statt nur pauschal auf PMR/Weide zu zeigen.
**Update 2026-04-21 (Weidemineral + PMR+Weide-Modus):** Drei fachliche Slices umgesetzt: (1) Weidemineral `Weidemineral Mg/Na Ausgleich` ist jetzt ein echter Optimierungsbaustein in der Feedbasis (`_SPECIAL_SUPPLEMENTS`) und wird bei `feeding_type="PMR+Weide"` automatisch als Sicherheitsbaustein (>= 0,05 kg TM/d) in die Ration gezwungen – Ableitung aus DLG 417/443 / GfE-Workshop 2023 (K/Mg-Antagonismus, Grastetanie-Risiko). (2) Der Wizard in `rationsoptimierung.tsx` bietet jetzt `TMR / PMR / PMR+Weide` als explizite Modi inkl. kurzer fachlicher Info; `feeding_type` wird ueber den `CowProfile`-Contract an das Backend uebergeben und per `_normalize_feeding_type` robust normalisiert (`PMR+Weide`, `PMR_WEIDE`, `pasture` u.ae.). (3) Response enthaelt neu `pasture_risk` (aktiv bei `PMR+Weide` oder bei > 1 kg TM Weideaufnahme) mit `K:Mg`-Verhaeltnis, Weide-Rohprotein, Mg-Supplement-Menge und drei Milch-Panels (Milch aus Weide, Milch aus Grassilage, Milch aus Weide+Grassilage); `PastureRiskPanel` ist in Workbench- und Review-Ansicht sichtbar. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `pytest tests/test_rations_optimization_pasture.py tests/test_rations_optimization_compound_feed.py -q --no-cov` (5 passed), `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`, E2E-Sanity-Test via FastAPI-`TestClient` mit `feeding_type="PMR+Weide"` (Response liefert `pasture_risk.active=true`, `mg_supplement_dmi_kg=0.05`, K:Mg-Warnung wird ausgeworfen).
**Update 2026-04-21 (Fruehjahrsfall-Abschluss, RMD + Compound-Parser):** Die Praxisprobe `Weide Fruehjahr jung + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` ist jetzt im Modus `PMR+Weide` `optimal` (Kosten 1,66 EUR/d, DMI 18 kg TM, ME 204,6 MJ, Mg 37,3 g, K:Mg 12,4 → Grastetanie-Warnung wird korrekt gemeldet). Zwei zusammenhängende Blocker wurden aufgelöst: (a) **RMD-Dichte-Obergrenze** (DLG 01|25 Ziel ≤ 1,5 g N/kg TM) ist für Weidesysteme strukturell nicht erreichbar, weil Jungweide laut DLG-Futterwerttabelle bereits 7–9 g N/kg TM liefert. Die Grenze wird jetzt nach DLG-Merkblatt 417 je Fütterungsmodus gestaffelt (`TMR 1,5 / PMR 3,0 / PMR+Weide 8,0`, Relaxation-Stufe `TMR 3,0 / PMR 5,0 / PMR+Weide 12,0`) – die Stall-Norm bleibt für Stallfütterung unverändert. (b) **Compound-Feed-Parser** (`_parse_compound_feed_text`) produzierte physikalisch unmögliche Werte (ME 15,4 MJ/kg TM, XL 165 g/kg TM, Ca 72 g/kg TM), verursacht durch zwei Bugs: ein Off-by-one-Matching in `_extract_labelled_value` (Pattern-Reihenfolge vertauscht, `"Rohfett"` nahm den Wert von `"Rohprotein"` etc.) und eine fehlende FM→TM-Umrechnung der Deklaration (% FM wurde direkt als g/kg TM interpretiert). Beides gefixt: Label-zuerst-Pattern hat jetzt Priorität, Deklaration wird konsistent mit `1/dm_frac` auf g/kg TM gehoben. Regressionstests: `tests/test_rations_optimization_compound_feed.py` (3 neue Tests gegen Off-by-one, physikalische Plausibilität, FM→TM), `tests/test_rations_optimization_spring_pasture_case.py` (4 neue E2E-Tests für den Bruder-Fall). Komplette `rations_optimization`-Suite: 34 passed (6 Pre-Existing-Errors in `test_process_kernel_wave74_rations_optimization.py` wegen entfallener `get_rations_base_url`-Funktion, unabhängig von diesem Slice).

## FLOW-LC-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Flow-Spine-Instanzen vom reinen Routing-/Node-Status-Anker auf einen echten, restart-sicheren Lifecycle mit Timeline und Resume-Vertrag heben.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `app/domains/operations/models.py`, `alembic/versions/*`, `app/api/v1/endpoints/flow_spines.py`, `tests/test_flow_spines_api.py`
**Abnahmekriterien:** `FlowSpineInstance` traegt technische Lifecycle-Felder; eine Event-/Timeline-Spur ist modelliert; API-Contracts fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail` sind dokumentiert oder implementiert; bestehende `transition`-Logik ist sauber in den Gesamtvertrag eingeordnet.
**Erledigt:** `FlowSpineInstance` fuehrt jetzt Lifecycle-, Resume-, Owner-, Grund- und Abschlussfelder; `domain_ops.ops_flow_spine_instance_events` bildet Timeline/Audit persistent ab; `flow_spines.py` bietet jetzt `PATCH`, `save`, `resume`, `hold`, `complete`, `cancel`, `fail` und `timeline`; `transition` schreibt ebenfalls in die Eventspur und hebt `draft` auf `in_progress`.
**Checks:** `python -m py_compile app/api/v1/endpoints/flow_spines.py app/domains/operations/models.py alembic/versions/flow_spine_lifecycle_20260417.py tests/test_flow_spines_api.py`, `pytest tests/test_flow_spines_api.py -q --no-cov`
**Naechster Schritt:** `FLOW-LC-002` bis `FLOW-LC-006` entlang der neuen Lifecycle-Uebersicht staffeln, beginnend mit generischen Workspace-Actions und Resume-/Abbruch-Dialogen im Frontend.

## FLOW-LC-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Gemeinsamen Workspace-Lifecycle-Rahmen fuer alle 9 Flow-Spines einziehen: Aktionsleiste, Resume-Hinweis, Timeline und generische Dialoge fuer `save`, `hold`, `complete`, `cancel`, `fail`.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/lib/api/flow-spines.ts`, relevante UI-Tests falls vorhanden
**Abnahmekriterien:** Der Workspace zeigt Lifecycle-Status, Resume-Ziel und Timeline; die generischen Lifecycle-Aktionen sprechen den neuen Backend-Vertrag an; `cancel` und `fail` erzwingen Pflichtgruende auch im UI; der Rahmen ist prozessneutral fuer alle 9 Flows nutzbar.
**Erledigt:** `flow-spines.ts` kennt jetzt Lifecycle-Status, Timeline-Events und Mutationen fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail`; `FlowSpineWorkspace.tsx` zeigt fuer geladene Instanzen eine generische Lifecycle-Leiste mit Status, Resume-Ziel, Timeline und prozessneutralen Dialogen; die Instanzliste zeigt den Lifecycle-Status direkt in der Sidebar.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** `FLOW-LC-004` fuer OTC / P2P / Inventory aufsetzen und dort Resume-/Handover-Pfade mit den jeweiligen Fachmasken wirklich durchgaengig machen.

## FLOW-LC-004

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OTC, P2P und Inventory so an den Lifecycle-Vertrag anbinden, dass `save` und `resume` nicht nur im Workspace leben, sondern in reale Wiedereinstiegspfade der Fachmasken zeigen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/lib/api/flow-spines.ts`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** OTC speichert einen belastbaren Resume-Punkt in die Auftragsmaske; P2P speichert nach Erstanlage in die echte Bestell-Detailroute; Inventory speichert vor vertieften Dashboard-Spruengen den operativen Zielpfad als Resume-Ziel.
**Erledigt:** `flow-spines.ts` bietet jetzt einen schlanken `saveFlowSpineResumeCheckpoint()`-Helper; `order-editor.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Auftragsmaske und ersetzt nach Erstanlage die URL auf `?id=...`; `bestellung-anlegen.tsx` schreibt nach Erstanlage den Resume-Punkt auf die echte Bestell-Detailroute `/einkauf/bestellungen/{id}`; `bestandsuebersicht.tsx` persistiert vor den Spruengen in `mhd-uebersicht`, `psm-abverkauf`, `renner-liste` und `penner-liste` den jeweiligen Zielpfad als Inventory-Resume-Ziel und traegt den Workflow-Kontext dorthin weiter.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Naechster Schritt:** `FLOW-LC-005` aufsetzen und die restlichen sechs Prozessraeume mit denselben Resume-/Handover-Mustern nachziehen.

## FLOW-LC-005

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Die restlichen sechs Flow-Spine-Prozessraeume mit denselben Resume-/Handover-Mustern wie OTC, P2P und Inventory anbinden.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, relevante Zielseiten unter `packages/frontend-web/src/pages/**`, ggf. `packages/frontend-web/src/lib/api/flow-spines.ts`
**Abnahmekriterien:** `harvest-to-settlement`, `contract-to-settlement`, `complaint-to-resolution`, `service-to-customer`, `finance-to-close` und `compliance-to-report` schreiben oder tragen echte Resume-/Handover-Ziele in ihre Fachmasken; die Workflow-Kontexte bleiben beim Wiedereinstieg erhalten.
**Erledigt:** `ernte-annahme-erfassung.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Annahme-Route und ersetzt nach Erstsave die URL auf `/agrar/ernte-annahme-erfassung/{id}`; `FrmKontraktDetail.tsx` schreibt nach Save auf die echte Kontrakt-Detailroute; `reklamationen.tsx` und `service/anfragen.tsx` sichern vor `neu`- und Detail-Spruengen die jeweiligen Zielpfade; `abschluss-cockpit.tsx` speichert beim Oeffnen den Cockpit-Resume-Punkt und vor Detail-Spruengen den Checklistenpfad; `co2-bilanz.tsx` persistiert die Reporting-Maske selbst als Resume-Ziel.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** Die verbleibende Vertiefung ist kein generischer Resume-Rahmen mehr, sondern fachliche Feinarbeit: pro Flow konkrete Grundcode-Kataloge, weitergehende Handover in Untermasken und Abschluss-/Abbruchregeln.

## CRM-PICKER-001

**Von:** Claude Code / Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Order-to-Cash-Kundenauswahl im Flow-Spine-Startdialog von Modal-Auswahl auf schnellen Inline-Typeahead mit Neuanlage-Ruecksprung umstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/CUSTOMER-PICKER-PLAN.md`, `app/api/v1/endpoints/customers.py`, `alembic/versions/crm_customers_search_index_20260414.py`, `packages/frontend-web/src/components/crm/CustomerCombobox.tsx`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/pages/verkauf/kunde-neu.tsx`, `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx`
**Abnahmekriterien:** Typeahead nutzt schlanke Quick-/Recent-Endpoints; neuer Kunde kann aus dem Flow-Spine-Dialog angelegt werden; nach Speichern kehrt die App in den Dialog mit vorausgewaehltem Kunden zurueck; erweiterte Kundensuche bleibt erreichbar.
**Erledigt:** `CustomerCombobox` ist fuer `order-to-cash` integriert; `/quick-search` und `/recent` liefern schlanke Picker-Daten; `returnTo` bleibt ueber den Alias-Redirect erhalten; kanonischer Kundenstamm liest `initialName` und navigiert nach Save zurueck; `FlowSpineWorkspace` setzt `customerId` und `customerNumber` im Order-Editor-Handover; der `order-editor` prefilled den uebergebenen Kunden jetzt direkt beim Workflow-Einstieg; bestehende Flow-Spine-Instanzen loesen den kompakten Kundenkontext robust ueber `business_partner_id`; `CustomerSelectionDialog` ist als "Erweiterte Suche" angebunden.
**Checks:** Browser-Use Roundtrip `Flow Spine -> Kunde neu -> Flow Spine Dialog -> Order Editor`, `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `pytest tests/test_flow_spines_api.py tests/test_customers_picker_api.py -q --no-cov`, `node scripts/docs-governance-check.cjs`, `GET /api/v1/crm/customers/recent`, `GET /api/v1/crm/customers/quick-search`

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
**Stand:** erledigt
**Ziel des Slices:** FIBU-Operatorpfade fuer Abschluss, Reorganisator, Zinswesen und Revisionssicht semantisch verdichten.
**Abnahmekriterien:** Abschluss- und FIBU-Operatorraeume tragen denselben klaren Status-, Fristen-, Revisions- und Folgeaktionsrahmen.
**Ergebnis:** Alle 4 FIBU-Masken (abschluss-cockpit, schnittstellen-center, mahnwesen, zahlungslaeufe) tragen OperationalCaseHeader mit Status/Blocker/Folgeaktion.

## DOM-SUPPLY-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Die physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` fachlich und statusseitig durchgaengig harmonisieren.
**Abnahmekriterien:** Jeder Uebergabepunkt zeigt Objektbezug, Abweichung, naechste Aktion und Folgeobjekt konsistent.
**Ergebnis:** Alle 6 Supply-Masken (waage/liste, tourenplanung, wareneingang, wiegeschein-detail, rohware, frachtbriefe) tragen OperationalCaseHeader.

## DOM-PROC-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation auf echte Folgefaelle heben.
**Abnahmekriterien:** Beschaffungsfaelle bilden Matching-Ausnahmen, Nachforderung und Folgekommunikation als echte Arbeitsobjekte ab.
**Ergebnis:** Alle 5 Einkauf-Masken (rechnung-abgleich, rechnungseingang, lieferanten-dokumente, anlieferavis, auftragsbestaetigung) tragen OperationalCaseHeader.

## DOM-CON-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Kontraktfixierung, Marktbewertung, Mahnung und Engagement als vollwertige Operatorraeume ausbauen.
**Abnahmekriterien:** Fixierungs-, Markt- und Mahnlogik ist nicht nur sichtbar, sondern als klarer Operatorpfad bedienbar.
**Ergebnis:** Alle 4 Kontrakt-Masken (contracts-v2, KontraktPositionsmonitor, FrmKontraktDetail, KontraktAlarmDashboard) tragen OperationalCaseHeader.

## DOM-CRM-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** CRM-/Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.
**Abnahmekriterien:** CRM und Service tragen denselben Fallbezug, Ownership-Rahmen und Abschlusspfad.
**Ergebnis:** Alle 4 CRM-/Service-Masken (LegacyKundenStammModern, anfrage-detail, opportunity-detail, kontakt-management) tragen OperationalCaseHeader.

## DOM-DOC-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.
**Abnahmekriterien:** Dokumente und Meldungen zeigen revisionsrelevanten Nachweisstatus, Rueckmeldungspfad und Wiedervorlage konsistent.
**Ergebnis:** Alle 3 Dokumenten-/Compliance-Masken (ablage, meldewesen-konsole, atlas) tragen OperationalCaseHeader.

## COV-FIN-002

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Coverage-Tiefe fuer FIBU-Kernpfade aufbauen: Journal, Zahlungslaeufe, DATEV/ELSTER-nahe Follow-up-Logik und Abschlusskontext.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, relevante Finance-/FIBU-Services und Endpunkte
**Abnahmekriterien:** Kritische FIBU-Kernpfade besitzen gezielte Tests statt nur allgemeiner Gesamtquote; Ratchet kann fuer Finance spaeter angehoben werden.
**Fortschritt:** Start auf den API-/Service-Kern fuer Follow-up, Mahnwesen, Lastschrift- und Kassenexport sowie FIBU-nahe Exportpersistenz; `tests/test_finance_followup_api.py` deckt jetzt Preview-, Export-, Download-, DMS-Redirect- und Upload-Metadatenpfade ab. Zusaetzlich haertet `tests/test_fibu_connectors_api.py` jetzt Profile-CRUD, Import-Upload, Run-Summary, Run-Items und Workflow-Folgeaktionen in `api/v1/endpoints/fibu_connectors.py`. `tests/test_finance_actions.py` deckt Bankabgleich, Buchungsfreigabe, Kassenabschluss, Lastschriftlauf, Periodenabschluss, Kreditlimits, Sicherheiten, Zahlungsvorschlaege und Buchungsuebergabe ab. Die zuvor `skipped` Finance-API-Tests wurden auf deterministische Test-Doubles umgestellt (`tests/test_finance_dunning_api.py`, `tests/test_finance_exchange_rates_api.py`, `tests/test_finance_payment_runs_api.py`), damit sie nicht mehr an einer zufaelligen Live-DB haengen. Nebenbei wurden echte Ursachen im Code behoben: Geldbetraege im Mahnwesen werden jetzt quantisiert, `payment_runs.py` serialisiert Zahlungsobjekte sauber und der Ruecklaeuferpfad nutzt wieder den korrekten Betrag. Fuer Bestandsinstallationen erzwingt `ensure_finance_api_tables_20260413` die fehlenden Finance-API-Tabellen auch dann, wenn ein aelterer Migrationspfad sie ausgelassen hat.

## COV-FIN-003

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Die verbliebenen Finance-Ratchet-Luecken `booking_templates.py` und `chart_of_accounts.py` ueber deterministische API-/Unit-Tests und einen stabilen JSON-Serialisierungspfad schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/booking_templates.py`, `tests/test_booking_templates_api.py`, `tests/test_chart_of_accounts_api.py`
**Abnahmekriterien:** `booking_templates.py` liegt ueber 40 Prozent, `chart_of_accounts.py` ueber 50 Prozent; der kritische Coverage-Ratchet laeuft gegen die Sammelsuite gruen.
**Erledigt:** `booking_templates.py` serialisiert Template-Lines jetzt ueber `model_dump_json()` JSON-sicher; `tests/test_booking_templates_api.py` und `tests/test_chart_of_accounts_api.py` decken Listen-, CRUD-, Validierungs-, Export- und Fehlerpfade ab. Der vollstaendige kritische Ratchet ist gruen.
**Checks:** `pytest tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py -q --no-cov`; `pytest tests/test_tenant_enforcement.py tests/test_secrets_vault.py tests/test_event_bus_runtime.py tests/test_process_kernel_wave2_events.py tests/test_integration_bootstrap.py tests/test_finance_actions.py tests/test_finance_followup_api.py tests/test_fibu_connectors_api.py tests/test_dunning_api.py tests/test_finance_payment_runs_api.py tests/test_finance_exchange_rates_api.py tests/test_finance_read_models_api.py tests/test_process_kernel_wave1_contracts.py tests/test_inventory_operations.py tests/test_inventory_counts.py tests/test_waage_api.py tests/test_warehouses_api.py tests/test_warehouse_transfers_api.py tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py tests/test_l3c_smoke.py -q`; `python scripts/check_critical_backend_coverage.py`

## COV-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Coverage fuer Bestandsfuehrung, Lagerbewegung, Inventur und physische Objektkette erweitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, Inventory-/Ops-/Logistik-Endpunkte und Services
**Abnahmekriterien:** Stock-Movements, Inventur und kritische Lagerpfade sind ueber gezielte Tests gegen Regressionen abgesichert.
**Erledigt:** `waage.py`, `warehouses.py`, `warehouse_transfers.py`, `inventory_counts.py` und `inventory_operations.py` liegen im kritischen Coverage-Ratchet ueber Schwelle; die Sammelsuite laeuft gruen.
**Checks:** siehe `COV-FIN-003` Sammelsuite und `python scripts/check_critical_backend_coverage.py`

## COV-INT-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Integrations-Governance tiefer testen: Superglue, Secrets, Outbound-Gates, Bootstrap und Tenant-Schutz.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, `app/services/**`, `app/integrations/**`
**Abnahmekriterien:** Integrationsnahe Kernpfade werden nicht nur konfiguriert, sondern auch testseitig breiter abgesichert.
**Erledigt:** `IntegrationCircuitBreaker` (12 Tests), `superglue_execution_journal` (9 Tests), `superglue_admin_state` (11 Tests), `superglue_monitoring` (5 Tests) — 37 Tests gruen. Stand: 2026-05-12.

## DOM-FIN-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** FIBU-/L3-Parity fachlich weiter vertiefen, insbesondere Abschluss-, Revisions- und Operator-Pfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante FIBU-/Finance-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Finance/FIBU ist nicht nur breit, sondern in den priorisierten Operatorpfaden semantisch konsistenter und tiefer.
**Erledigt:** (1) `accruals_provisions.py`: GET/PUT/DELETE-Endpoints fuer Einzelobjekte hinzugefuegt (waren fehlend — nur List+Create+Post vorhanden); (2) `closing_checklists.py`: POST `/{id}/approve` + DELETE `/{id}` hinzugefuegt (approve-Schritt fehlte im Workflow); (3) Tests: `test_accruals_provisions_api.py` (12), `test_subsidiary_ledger_reconciliation_api.py` (12) — 24 Tests gruen. Stand: 2026-05-12.

## DOM-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Inventory-/Ops-/Logistik-Parity weiterziehen, insbesondere physische Objektkette, Queue, Wiegung, Fracht und Charge.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante Inventory-/Ops-/Logistik-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Die physische Kette ist fachlich tiefer und konsistenter ueber mehrere Kernmasken und Backend-Pfade hinweg.
**Erledigt:** Tests fuer `silo_operations_api.py` (DOM-INV-002, `test_silo_operations_api.py`) und `charges.py` (`test_charges_api.py`) hinzugefuegt — Modellvalidierung + HTTP-Smoke-Tests.

## DOM-CRM-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** CRM-/Sales-/Service-Parity angleichen, insbesondere Vorgangsbezug, Folgeobjekte und echte Arbeitsobjekte statt Listenbreite.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante CRM-/Sales-/Service-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** CRM-/Sales-/Service-Raeume besitzen vergleichbare fachliche Tiefe in den priorisierten Kernobjekten.
**Erledigt:** Tests fuer `sales_orders.py`, `sales_delivery_notes.py`, `reklamation_api.py`, `contacts.py` hinzugefuegt — Helper-Unit-Tests + HTTP-Smoke (60 Tests grueen).

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

## ERP-FINANZ-ROADMAP-P3P4

**Von:** Claude Code
**Owner:** (Team)
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** ERP-Finanz Roadmap Phase 3 (Orders-REST Architektur-Entscheid + Tenant-Isolation-Tests) und Phase 4 (Observability Counter + DB-Indexes) abschliessen.

**Dateibesitz:**
- `packages/erp-domain/src/bootstrap.ts` — Architektur-Kommentar Orders-REST = Python
- `packages/erp-domain/tests/integration/tenant-isolation.spec.ts` — Negative Tenant-Tests
- `app/core/metrics.py` — tenant_auth_errors_total Counter
- `app/middleware/tenant_enforcement.py` — Counter-Inkrementierung
- `migrations/sql/erp/006_missing_tenant_indexes.sql` — Composite-Indexes domain_sales/inventory/erp/finanz
- `alembic/versions/faf00a6bfc11_006_missing_tenant_indexes.py` — No-Op Alembic-Revision
- `tests/test_gap_fixes_phase4.py` — Phase-4-Smoke-Tests

**Abnahmekriterien:**
- bootstrap.ts dokumentiert: Orders-REST = Python; controller-Token nicht registriert (Invariante)
- Tenant-Isolation: fremder Tenant sieht keine Debitoren/Kreditoren des anderen Tenants
- `tenant_auth_errors_total{route, error_type}` Counter in Prometheus scrappbar
- 006_missing_tenant_indexes.sql: idempotente Composite-Indexes auf alle relevanten Schemas
- `alembic upgrade head` laeuft ohne drop_table-Operationen

**Erledigt:** Alle 4 Phase-3+4-Ziele umgesetzt, committed `f4d0462ae` + `6cf97afcc`; Linter sauber; 4/4 Phase-4-Tests gruen; `alembic upgrade head` = no-op; main + develop auf GitHub gepusht.

**Checks:** `pytest tests/test_gap_fixes_phase4.py -v`; `alembic upgrade head`; `flake8 app/core/metrics.py app/middleware/tenant_enforcement.py`
