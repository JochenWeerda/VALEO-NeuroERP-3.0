# INT-SG-037 - Superglue Run Envelope

## Ziel

Tool-Execution auf den Upstream-Run-Contract ziehen und sauber in den VALEO-Envelope ueberfuehren.

## Umsetzung

- Execution-Service ruft `POST /v1/tools/{toolId}/run`
- Request-Payload nutzt `inputs` und `options.traceId`
- Upstream-Run-Status wird auf VALEO-`result_status` gemappt
- Journal- und Security-Trail fuehren jetzt `run_id` und `upstream_status`

## Ergebnis

Der Broker-/Execution-Pfad arbeitet jetzt gegen den aktuellen Run-Contract statt gegen einen veralteten Execute-Endpunkt.
