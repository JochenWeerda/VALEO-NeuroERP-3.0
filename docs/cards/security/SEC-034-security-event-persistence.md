# SEC-034

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_observability.py

- Bereich: Security Observability
- Risiko: In-Memory-Only-Recorder verliert Block-/Violation-Events bei Neustart
- Ergebnis: append-only JSONL-Persistenz mit konfigurierbarem Pfad; Monitoring und Admin-Summary lesen Persistenz nach Restart weiter
- Tests: `tests/test_security_observability.py`, `tests/test_security_monitoring.py`, `tests/test_security_admin_monitoring.py`
