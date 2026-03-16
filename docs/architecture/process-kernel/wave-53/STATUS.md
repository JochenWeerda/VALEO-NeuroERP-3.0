# Wave-53 Status

## Scope
Process Rate Limit Contracts + Workflow Idempotency Contracts

## Zielbild

Wave 53 ergänzt den Process-Kernel um Überlastschutz und Duplikatvermeidung:

1. **Process Rate Limit Contracts**: Anfragedrosselung pro Tenant/Benutzer/Endpunkt/Global mit
   4 Zeitfenstern (SEKUNDE/MINUTE/STUNDE/TAG) und 3 Ergebnissen (ERLAUBT/GEDROSSELT/BLOCKIERT).
   `pruefe_und_inkrementiere()`: Abgelaufenes Fenster → Reset auf 1; Anfrage > max → BLOCKIERT
   (kein Increment); Anfrage > weich_limit → GEDROSSELT; sonst ERLAUBT.

2. **Workflow Idempotency Contracts**: Schlüsselbasierte Duplikatvermeidung mit
   3 Strategien (STRIKTE_EINMALIGKEIT/WIEDERHOLUNG_BEI_FEHLER/ZEITFENSTER).
   `pruefe_idempotenz()`: ABGELAUFEN → immer soll_verarbeiten=True;
   STRIKTE_EINMALIGKEIT + DUPLIKAT → gespeichertes Ergebnis zurückgeben;
   WIEDERHOLUNG_BEI_FEHLER + FEHLGESCHLAGEN → Neuversuch erlaubt.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_rate_limit_contracts.py` | `RateLimitRegel.fenster_sekunden()`, `RateLimitZaehler.pruefe_und_inkrementiere()`, 5 Default-Regeln RL-001..RL-005 | abgeschlossen |
| AP2 | `app/core/workflow_idempotency_contracts.py` | `IdempotenzEintrag.aktueller_status()`, `pruefe_idempotenz()` (3 Strategien), 5 Default-Einträge KEY-001..KEY-005-ALT | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/rate-limit/regeln`, `POST /process/rate-limit/pruefe` | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/idempotenz/eintraege`, `POST /process/idempotenz/pruefe` | abgeschlossen |

## Abnahmekriterien

- `fenster_sekunden()`: SEKUNDE=1, MINUTE=60, STUNDE=3600, TAG=86400
- Abgelaufenes Fenster → immer ERLAUBT, counter=1
- max_anfragen überschritten → BLOCKIERT, counter unverändert
- `pruefe_idempotenz()`: ABGELAUFEN → soll_verarbeiten=True unabhängig von Strategie
- KEY-005-ALT (erstellt_am - 2 Tage, TTL=86400) → aktueller_status=ABGELAUFEN
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave53_rate_limit_idempotency.py` — 146 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave53_rate_limit_idempotency.py -q --no-cov
# Ergebnis: 146 passed
```

## Status
`abgeschlossen`
