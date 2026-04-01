# SEC-016 - Zentrale Egress-/SSRF-Policy

## Ziel

Alle ausgehenden HTTP-Ziele, die aus Tenant-, User- oder Integrationskontext stammen, sollen denselben SSRF-Schutz nutzen.

## Scope

- `app/core/outbound_security.py`
- `app/api/v1/endpoints/webhooks.py`
- `app/services/neuro_tool_execution.py`
- `tests/test_security_outbound_policy.py`

## Umsetzung

- zentraler Helper `validate_outbound_http_target()` fuer HTTP/HTTPS-Ziele
- Block fuer localhost, private/loopback/link-local/reserved/multicast/unspecified IPs
- Block fuer typische interne Host-Suffixe wie `.local` und `.internal`
- optionale Allowlists ueber `OUTBOUND_HTTP_ALLOWED_HOSTS` und `OUTBOUND_HTTP_ALLOWED_DOMAINS`
- Webhook-Registrierung und externer Neuro-Tool-Execution-Pfad nutzen denselben Helper

## Verifikation

- `pytest tests/test_security_outbound_policy.py tests/test_security_webhooks_vies.py tests/test_neuro_tool_execution.py -q --no-cov`
- `python -m py_compile app/core/outbound_security.py app/api/v1/endpoints/webhooks.py app/services/neuro_tool_execution.py`

## Restrisiken

- DNS-Rebinding und private Zieladressen hinter oeffentlichen Hostnamen werden ohne Resolver-/Egress-Gateway nicht vollstaendig verhindert
- produktive Allowlists muessen pro Umgebung bewusst gepflegt werden
