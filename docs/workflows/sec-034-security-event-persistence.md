# SEC-034 - Security Event Persistence

## Ziel

Security-Events aus SSRF-/Tenant-Verletzungen duerfen nach Prozessneustarts nicht verloren gehen.

## Umsetzung

- `security_observability.py` schreibt Events jetzt optional append-only in `SECURITY_EVENT_LOG_PATH`.
- `config.py` bekommt die Schalter `SECURITY_EVENT_PERSISTENCE_ENABLED` und `SECURITY_EVENT_LOG_PATH`.
- `security_monitoring.py` und `admin_monitoring.py` lesen ueber den bestehenden Recorder automatisch auch persistierte Events nach Restart.

## Abnahme

- Unit-Test prueft append-only File-Persistenz und Reload.
- Monitoring- und Admin-Regressionen pruefen, dass Endpunkte nach Observer-Neuaufbau dieselben Events weiter sehen.

## Restrisiko

- JSONL ist bewusst leichtgewichtig; fuer langfristige Auswertung und zentrale Audit-Kopplung fehlt noch eine DB-/Audit-Bridge.
