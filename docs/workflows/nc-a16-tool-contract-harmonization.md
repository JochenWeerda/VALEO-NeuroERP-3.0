# NC-A16 - Tool Contract Harmonization

## Ziel

Spezialisierte Request-Payloads des Neuro Tool Brokers sollen nicht mehr ueber `tool_name`-Sonderfaelle im Executor haengen, sondern ueber explizite Metadaten im MCP/OpenAPI-Contract.

## Umsetzung

- `MCPToolContract` besitzt jetzt `request_payload_mode`
- die spezialisierten Modi `dataset_validation`, `policy_context` und `approval_context` sind als Enum modelliert
- `NeuroToolExecutionService` baut Request-Bodies anhand dieses Contract-Felds statt anhand harter Tool-Namen
- die betroffenen Wave-31-Contracts fuer Data-Quality, Policy-Evaluation und Approval-Evaluation sind auf diese Modi gezogen

## Ergebnis

- Tool-spezifische Payload-Logik ist jetzt contract-gesteuert und besser erweiterbar
- Broker/Execution bleiben kompatibel, ohne die bisherigen spezialisierten Endpunkte zu verlieren
- die Restluecke des Tool Brokers verschiebt sich von interner Sonderlogik hin zu weiteren produktiven Adaptern und Runtime-Nutzung
