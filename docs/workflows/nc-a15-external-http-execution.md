# NC-A15 - External HTTP Execution

## Ziel

Der Tool Broker soll MCP/OpenAPI-Contracts nicht nur ueber internen `TestClient`, sondern auch ueber echte externe HTTP-Basis-URLs ausfuehren koennen.

## Umsetzung

- `NeuroToolExecutionService` unterstuetzt jetzt `external_base_url`
- optionale `execution_headers` werden in externe Requests uebernommen
- erfolgreiche externe Calls laufen als `mode=openapi_external`
- HTTP-/Transport-Fehler bleiben mit bestehender Fallback-Semantik kompatibel

## Ergebnis

- die produktive Ausfuehrung ist nicht mehr auf interne FastAPI-Surface beschraenkt
- Broker-Trace unterscheidet jetzt explizit interne und externe Execution
