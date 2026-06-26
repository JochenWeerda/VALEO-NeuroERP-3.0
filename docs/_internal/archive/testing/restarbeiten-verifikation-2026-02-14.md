# Restarbeiten Verifikation 2026-02-14

## Qualität & Tests

### Unit/Coverage Nachweis
- Befehl: `python -m pytest --maxfail=1`
- Ergebnis: `61 passed, 7 skipped, 1 failed`
- Gesamt-Coverage: `40%` (`TOTAL 26926 / 16150 miss`)
- Blocker: `tests/test_gobd_compliance.py` erwartet Endpunkte unter `/api/gobd/*`, die aktuell `404` liefern.

### Agrar-Kern-Tests (fokussiert)
- Befehl:
  `python -m pytest tests/test_agrar_compliance_exports.py tests/test_agrar_contract_status.py tests/test_agrar_event_contracts.py tests/test_agrar_mig01_backfill.py tests/test_agrar_settlement_calculation.py -q`
- Ergebnis: `17 passed`

## Performance / Lasttest
- Prüfschritt: `k6 version`
- Ergebnis: `k6_not_installed`
- Konsequenz: Lokaler Lauf nicht möglich, daher Ausführung containerbasiert mit `grafana/k6`.
- Ausführung:
  `docker run --rm -e BASE_URL=http://host.docker.internal:8000 -e API_TOKEN=dev-token -e TENANT_ID=00000000-0000-0000-0000-000000000001 -v "${PWD}:/work" -w /work grafana/k6 run tests/performance/agrar-core-loadtest.js`
- Ergebnis:
  - `iterations`: `6388`
  - `http_req_failed rate`: `0.000092885` (< 2%)
  - `http_req_duration p95`: `144.76ms` (< 900ms)
  - `agrar_billing_preview_duration p95`: `114.44ms` (< 1000ms)
  - Threshold-Status: bestanden (Exit Code 0)
- Artefakt: `reports/performance/agrar-perf-summary.json`
- Referenzskript: `scripts/run-agrar-loadtest.ps1`

## Staging Smoke (lokale Docker-Umgebung)
- Lauf: `scripts/check-staging.ps1 -BaseUrl http://localhost:8000`
- Ergebnis: bestanden.
- Details:
  - `/healthz` -> `200`
  - `/readyz` -> `200`
  - `/api/v1/openapi.json` -> `200`

## Gate-Kriterien
- Alembic-Head geprüft mit `alembic heads`: `agrar_settlements_initial_20260213 (head)`
- OpenAPI-Artefakt geprüft: `docs/api/openapi.json` (`openapi 3.1.0`, `590` Pfade)
- E2E-Flow Wiegeschein -> Abrechnung -> Buchung:
  - Lauf: `scripts/run-agrar-e2e-flow.ps1 -BaseUrl http://localhost:8000`
  - Ergebnis: bestanden (`flow_ok=true`)
  - Beispielartefakt: Ticket `E2E-WT-1771057504`, Settlement `E2E-SET-1771057504`, Journal `JE-SET-20260214-8DF2DF34`
- Keine neue Agrar-Fachlogik außerhalb `modules/agrar`:
  - Umsetzung: Fachberechnung aus Endpunkten nach `modules/agrar/services/settlement_calculator.py` und `modules/agrar/services/weighing_domain.py` ausgelagert.
  - Scan: `rg -n "derive_billing_weight|resolve_ticket_allocation_quantity|compute_settlement_amounts|calc_deduction_amount" app/api/v1/endpoints modules/agrar/services -S`
  - Ergebnis: Endpunkte verwenden nur Service-Aufrufe; fachliche Kernlogik liegt im Modulpfad.

## Operative Punkte (extern)
- GitHub Secrets, Staging-Deployment, UAT, Blue-Green und Monitoring-Freigabe sind umgebungs- und rollenabhängig und lokal nicht abschließend durchführbar.
