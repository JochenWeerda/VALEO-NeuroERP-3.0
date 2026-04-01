# SEC-012 - Webhook SSRF Hardening

## Ziel

Webhook-Ziele gegen SSRF auf localhost und interne Netze haerten.

## Umsetzung

- `HttpUrl`-Validierung fuer Payload
- Block fuer localhost, private, loopback- und link-local-IP-Ziele

## Tests

- `tests/test_security_webhooks_vies.py`

