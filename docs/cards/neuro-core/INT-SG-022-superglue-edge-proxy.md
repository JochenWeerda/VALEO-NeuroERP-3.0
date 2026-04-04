# INT-SG-022 - Superglue Edge / Proxy Overlay

## Kontext

`INT-SG-021` liefert den internen Compose-Stack. Fuer Staging und produktionsnahe Setups fehlte noch ein externer Ingress-Pfad mit TLS und sauber geschlossenen Service-Ports.

## Ergebnis

- neues Overlay `docker-compose.integration.edge.yml`
- `caddy` als Edge-Service fuer TLS und Header-Hardening
- direkte Host-Ports fuer interne Services im Overlay entfernt
- separater MinIO-Console-Host mit Basic Auth

## Dateibesitz

- `docker-compose.integration.edge.yml`
- `ops/superglue/Caddyfile`
- `docs/workflows/int-sg-022-superglue-edge-proxy.md`
- `docs/architecture/superglue-integration-implementation-plan.md`

## Risiken

- echtes DNS/TLS-Setup ist infra-abhaengig
- Caddy ist ein Repo-Template, keine verbindliche Prod-Plattformentscheidung

## Naechster Schritt

Infra-Folgepfad fuer Kubernetes/Ingress/Load-Balancer oder Secrets-/Certificate-Automation als eigener Slice.
