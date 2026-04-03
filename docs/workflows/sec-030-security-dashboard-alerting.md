# SEC-030 - Security Dashboard und Alerting

## Ziel

Die neue Security-Monitoring-Surface soll operativ im bestehenden Admin-Monitoring sichtbar werden.

## Umsetzung

- `admin_monitoring.py` blendet Security-Alerts jetzt in `/alerts` ein.
- neuer Endpoint `/admin/monitoring/security-summary` surfact Status, Block-/Denied-Zaehler, Top-Kategorien und die konfigurierten Monitoring-Regeln/Kanaele.
- die CI-Lane zieht die neuen Monitoring-Regressionen explizit mit.

## Abnahme

- Security-Regressionen fuer Admin-Monitoring und Security-Monitoring gruen
- Docs-Governance gruen

## Restrisiko

- Alerts sind weiterhin In-Memory-basiert; externes Alerting und Persistenz sind noch Folgearbeit
