# Wave 53 - Process Rate Limit Contracts + Workflow Idempotency Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 146 gruen, 0 Fehler

## Scope

Wave 53 ergaenzt den Process-Kernel um Ueberlastschutz via Rate Limiting und Duplikatvermeidung via Idempotenz-Contracts.

## Zielbild

Anfragen sollen pro Tenant, Benutzer oder Endpunkt sauber gedrosselt werden koennen, waehrend idempotente Workflows Duplikate reproduzierbar erkennen und behandeln.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_rate_limit_contracts.py` | `RateLimitRegel`, `RateLimitZaehler.pruefe_und_inkrementiere()`, fuenf Default-Regeln | abgeschlossen |
| AP2 | `app/core/workflow_idempotency_contracts.py` | `IdempotenzEintrag.aktueller_status()`, `pruefe_idempotenz()`, fuenf Default-Eintraege | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/rate-limit/regeln`, `POST /process/rate-limit/pruefe` | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/idempotenz/eintraege`, `POST /process/idempotenz/pruefe` | abgeschlossen |

## Abnahmekriterien

- `fenster_sekunden()` liefert fuer Sekunde, Minute, Stunde und Tag die korrekten Werte.
- Abgelaufene Fenster fuehren zu Reset und erlaubter Anfrage.
- Ueberschreitung von `max_anfragen` blockiert ohne Counter-Erhoehung.
- Abgelaufene Idempotenz-Eintraege erlauben immer Verarbeitung.
- Keine `app/api`-Imports in `app/core`.

## Tests

**Datei:** `tests/test_process_kernel_wave53_rate_limit_idempotency.py`
**Anzahl:** 146

## Status

`abgeschlossen`
Stand: 2026-03-16
