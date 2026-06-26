# INT-SG-021 - Superglue Compose Stack

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** `docker-compose.integration.yml`, `docs/workflows/int-sg-021-superglue-compose-stack.md`

## Kontext

`INT-SG-005` hatte den Deploymentpfad nur vorbereitet. Fuer eine praktikable lokale und Staging-nahe Inbetriebnahme fehlten Persistenz, Objektablage und ein sauberer Init-/Health-Pfad.

## Ergebnis

- `docker-compose.integration.yml` hat jetzt einen profilierten Superglue-Stack
- Postgres, MinIO und Bucket-Init sind enthalten
- Volumes und Healthchecks sind gesetzt
- Secrets werden nur ueber Umgebungsvariablen injiziert

## Dateibesitz

- `docker-compose.integration.yml`
- `docs/workflows/int-sg-021-superglue-compose-stack.md`
- `docs/architecture/superglue-integration-implementation-plan.md`

## Risiken

- das konkrete Superglue-Image kann andere Health-/S3-Variablen benoetigen
- Compose ersetzt keine produktive Secret-/Network-Policy-Verkabelung

## Naechster Schritt

Ops-seitig folgen ein echtes Deployment-Template fuer Staging/Prod oder ein separater Infrastruktur-Slice fuer Proxy, TLS und Network Policy.
