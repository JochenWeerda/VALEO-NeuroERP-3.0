# SEC-016

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_outbound_policy.py, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

## Titel

Zentrale Egress-/SSRF-Policy fuer externe HTTP-Pfade

## Problem

Webhook-Ziele und externe Broker-Aufrufe validierten Outbound-Ziele uneinheitlich oder gar nicht. Dadurch blieb SSRF-Schutz inkonsistent.

## Loesung

- gemeinsamer Core-Helper fuer Outbound-URL-Validierung
- konsistente Blockliste fuer interne Hosts/IPs
- optionale Allowlist fuer produktive Integrationsziele
- Umstellung der betroffenen Pfade auf den Shared Helper

## Abnahme

- private/localhost/interne Hosts werden zentral abgelehnt
- Webhook-Registrierung nutzt nur noch den Shared Helper
- externe Neuro-Tool-Execution faellt bei verbotenem Ziel kontrolliert auf Contract-Fallback zurueck
