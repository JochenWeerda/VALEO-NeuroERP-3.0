# NC-A14 - Broker Tenant Overrides

## Ziel

Tenant-Overrides sollen nicht an der Verification enden, sondern bis in Broker- und Tool-Execution-Kontexte durchgereicht werden.

## Umsetzung

- `NeuroToolBroker._verify_step()` gibt `policy_context` und `tenant_policy_overrides` pro Step an die Verification weiter
- `NeuroToolBroker._execute_tool_contract()` reicht dieselben Daten an die Tool-Execution weiter
- Step-spezifische Override-Daten koennen globale Kontextdaten ueberschreiben

## Ergebnis

- Broker, Verification und Tool-Aufruf arbeiten auf demselben Tenant-spezifischen Regelkontext
- nachgelagerte Compliance-/Policy-Tools sehen jetzt dieselben Overrides wie der Verification-Pfad
