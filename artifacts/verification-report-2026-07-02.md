---
title: Verifikationsreport A0
type: report
audience: [lead, betrieb, entwickler, agent]
owner: Claude
status: aktiv
last_reviewed: 2026-07-02
version: 1.0.0
description: Unabhaengige Verifikation der README-/Tracker-Claims durch reproduzierte Messlaeufe (Prompt A0, keine Codeaenderungen).
---

# Verifikationsreport A0 — VALEO NeuroERP 3.0

Datum: 2026-07-02 · Rolle: unabhängiger Verifikations-Agent (nur lesen/ausführen/protokollieren)
Basis: Branch `fix/pii-remediation` (= `main` `4a32d41c7` + A2-Hygiene-Commits, fachlich unverändert)
**Wichtig:** Der Arbeitsbaum enthielt uncommittete In-Flight-Änderungen (`app/api/v1/api.py`,
`app/api/v1/endpoints/beleg_vordrucke.py`, `alembic/versions/beleg_vordrucke_20260702.py`).
Alle Messwerte beziehen sich auf diesen Stand.

## 1. Messumgebung

- Windows 11, Python 3.11, Node 24.4.1, Docker 29.5.3
- Voller Compose-Stack lief (Postgres 15-alpine, Keycloak, NATS, CRM-Services)
- Leere Verifikations-DB: `valeo_verify_a0` auf der laufenden Postgres-Instanz (127.0.0.1:5432)
- Frontend-Package-Manager laut Lockfile: **npm** (`packages/frontend-web/package-lock.json`); Root-Monorepo: pnpm

## 2. Ergebnisse der Prüfschritte

### 2.1 Migration auf leerer DB

| Messung | Ergebnis |
|---|---|
| `alembic upgrade head` auf leerer DB | **exit 0** |
| Ziel-Head | `beleg_vordrucke_20260702` (inkl. uncommitteter In-Flight-Migration) |
| Ergebnis-Struktur | 31 Schemas, **595 Tabellen**, 28 `domain_*`-Schemas |

### 2.2 Backend-Testsuite

| Messung | Ergebnis |
|---|---|
| `pytest --collect-only -q` | **11.838 Tests collected** (7:16 min) |
| Voll-Lauf `pytest -q --cov=app` | **11.796 passed · 7 failed · 34 skipped · 1 xfailed** in 19:27 min |
| Gesamt-Coverage | **65,69 %** (`fail-under 60` erreicht) |

Die 7 Failures, klassifiziert:

| Test | Ursache | Klasse |
|---|---|---|
| `test_log_frachtbrief.py` (3×) | `domain_logistics.frachtbriefe` fehlt in der **Dev-DB**; auf der frisch migrierten DB existiert die Tabelle (verifiziert) | Dev-DB-Migrationsdrift, kein Code-Bug |
| `test_generate_architecture_index.py::test_build_index_mapping_complete` | `mask_rollout_summary_service` + 2 Endpoints ohne Domain-Mapping | Governance-Drift (Architektur-Index nicht nachgezogen) |
| `test_process_kernel_wave3_ap1_ap2.py` (2×) | Klasse-A-Masken-Explainability/Agent-Contract-Gap | Governance-Drift |
| `test_roadmap_closure_fints_low_stock.py::test_low_stock_agent_routes` | Routen-Erwartung verletzt | Drift/Regression — vor A1 (CI-Grün) zu klären |

### 2.3 Frontend

| Messung | Ergebnis |
|---|---|
| `npx tsc --noEmit` | **0 Fehler** (exit 0) |
| `npm run build` | **erfolgreich** (2:54 min; Hinweis: Chunks > 500 kB, maplibre 1,06 MB) |
| `npm run lint` | **0 Errors, 8 Warnings** (exit 0) |

### 2.4 Gate-Skripte (alle in Doku behaupteten Skripte existieren — 9/9)

| Skript | Exit | Ergebnis |
|---|---|---|
| `check_alembic_single_head.py` | 0 | Head OK: `beleg_vordrucke_20260702` (single) |
| `check_required_domain_schemas.py` | 0 | Struktur OK |
| `check_toolchain_pins.py` | 0 | Pins OK |
| `check_sql_fstrings.py` | **1 (ROT)** | **2 ungeflaggte SQL-f-Strings:** `app/api/v1/endpoints/inventory_operations.py:761`, `app/api/v1/endpoints/pricing.py:290` |
| `check_critical_backend_coverage.py` | 0 | grün **nach** dem Voll-Lauf (gegen stale `coverage.xml` fälschlich rot — Gate hängt an frischer Coverage) |
| `check_production_readiness.py --contract-only` (production, Compose+Helm) | 0 | `status: ready`, 0 Findings |
| `simulate_external_assessors.py` | 0 | 5 Profile, alle **conditional** (external gates offen); **kein SOC-2-Profil** (bestätigt Audit-Befund) |
| `release_evidence_report.py --fail-on-red` | **1 (ROT)** | Gesamtstatus FAIL: drift **FAIL** (15 Items), openapi **FAIL** (Drift → `generate_openapi.py` ausführen), coverage WARN (66 Dateien unter Ratchet), external WARN (kein Assessment-Artefakt); inventories PASS, slice_harness PASS |
| `doc_drift_report.py` | – | nicht separat ausgeführt (Drift bereits via release_evidence quantifiziert: 15) |

### 2.5 OpenAPI

| Messung | Ergebnis |
|---|---|
| `GET /openapi.json` | 200 (lokaler uvicorn, Arbeitsstand) |
| Pfade / Operationen | **2.533 Pfade · 3.274 Operationen** |
| Operationen mit `summary` | **3.274/3.274 = 100 %** |
| GET-Operationen | 1.510 |

## 3. Claim-Diff (README-Statusblock + open-gaps)

| Behauptung | Gemessen | Delta | Verdikt |
|---|---|---|---|
| Frontend TypeScript: 0 Fehler | 0 Fehler | – | ✅ bestätigt |
| Backend-Tests: > 9.500 collected | 11.838 collected | +2.300 | ✅ bestätigt (übertroffen) |
| Letzter Voll-Pass 9.228 grün (2026-05-26) | 11.796/11.838 passed, **7 failed** | Suite gewachsen, aber kein Voll-Grün | ⚠️ teilweise widerlegt: aktueller Stand ist NICHT voll grün (3× Dev-DB-Drift, 4× Governance-Drift) |
| Gesamt-Coverage 64,85 % | **65,69 %** | +0,84 pp | ✅ bestätigt |
| Kritische Coverage-Ratchets: 33 Pfade grün | Gate grün (mit frischer coverage.xml) | – | ✅ bestätigt |
| OpenAPI 3.041 Routen, 100 % summary | 3.274 Operationen, 100 % summary | +233 | ✅ bestätigt (Statusblock-Zahl veraltet, Wachstum) |
| Alembic 1 Head (`final_single_head_merge_20260626`) | 1 Head (`beleg_vordrucke_20260702`) | Head gewandert | ✅ bestätigt (single head; README-Zahl veraltet) |
| Migration auf leerer DB → alle Tabellen | exit 0, 595 Tabellen, 28 domain-Schemas | – | ✅ bestätigt |
| Runtime-Sweep: 1.059 GET live getestet, 5xx geschlossen | nicht wiederholt (Skript nicht als `scripts/api_runtime_sweep.py` vorhanden) | – | ⏳ nicht verifizierbar — Wiederholung ist P0 (Prompt A3) |
| Produktreife „Beta" | konsistent mit Messwerten | – | ✅ plausibel |
| CI-Voll-Grün auf GitHub Actions | nicht Teil dieses lokalen Laufs | – | ⏳ offen (Prompt A1) |

## 4. Top-5-Abweichungen

1. **PII-Befund schwerwiegender als im Tracker angenommen (A2-Querverweis):** 2 getrackte Dateien mit
   Namen/Ort/Förderbetrag natürlicher Personen (30 Einträge; historisch 100 inkl. Lead-Score),
   ~7,5 Monate öffentlich → `artifacts/pii-remediation-report.md`. Die namensgebende
   `PLZ_26XXX_final_leads.json` selbst war dagegen PII-frei.
2. **`check_sql_fstrings.py` ist ROT auf dem Arbeitsstand** — 2 ungeflaggte dynamische SQL-Stellen
   (`inventory_operations.py:761`, `pricing.py:290`; letztere aus dem Staffelrabatt-Commit `d23d6c136`).
3. **`release_evidence_report.py --fail-on-red` ist ROT** — 15 Drift-Items + OpenAPI-Drift:
   Doku/Inventare hinken dem Code hinterher; deckt sich mit 4 der 7 pytest-Failures (Governance-Drift).
4. **Kein Voll-Grün der Backend-Suite auf dem aktuellen Arbeitsstand** (7 Failures) — die
   README-Impression „stabil grün" gilt nur für den Stand 2026-05-26; Wiederherstellung ist Teil von A1.
5. **README-Statuszahlen veraltet** (OpenAPI 3.041→3.274, Head-Name, Testzahl) — kein inhaltlicher
   Widerspruch, aber Doku-Drift; Aktualisierung gehört zu Prompt A10 (nach A1–A9, kein Wunschstand).

## 5. Umgebungs-Findings (kein Abbruchgrund, protokolliert)

- `pytest --collect-only` triggert die Coverage-Konfiguration und **überschreibt `coverage.xml` mit
  einem 43-%-Artefakt** → nachgelagerte Ratchet-Checks liefern False-Reds, wenn kein Voll-Lauf folgte.
- Die Dev-DB (`valeo_neuro_erp`) ist gegenüber dem Migrations-Head drift-behaftet
  (`domain_logistics.frachtbriefe` fehlt) — Tests laufen dort statt gegen eine frisch migrierte DB.
- `check_production_readiness.py`/`simulate_external_assessors.py`/`release_evidence_report.py`
  verlangen Pflicht-Argumente, die in der Prompt-Doku fehlen (Compose/Helm-Pfade bzw. Output-Pfade).
- `git archive` meldet 23 PNG-Dateien, die LFS-Pointer sein sollten, aber Binärdaten enthalten
  (docs/screenshots, l3-migration-toolkit, storybook-Assets) — LFS-Hygiene-Finding.
- gitleaks/trufflehog nicht lokal installiert; Scans via Docker `ghcr.io/gitleaks/gitleaks` durchgeführt.

## 6. Anhang: Rohprotokolle

Lokal (Session-Scratchpad): `a0_pytest_full.log`, `alembic_a0.log`, `assessors.{json,md}`,
`release_evidence.log`, `gitleaks/tracked.json`. Auf Wunsch in `artifacts/` übernehmbar;
bewusst nicht committet, da teils maschinenspezifisch.
