# INT-SG-053 - Superglue Quarantine Retry

## Ziel

Retry- und Dead-letter-Pfade fuer degradierte Connector-Runs schliessen.

## Umgesetzt

- `retry_quarantine_entry()` ergaenzt offenen Eintraegen Retry- und Dead-letter-Zustaende.
- Quarantaene-Summary zaehlt jetzt Dead-letter-Eintraege mit.
- Der Admin-/API-Pfad kann Retry und Resolve getrennt ausloesen.

## Verifikation

- `pytest tests/test_superglue_refresh_and_quarantine.py -q --no-cov`

