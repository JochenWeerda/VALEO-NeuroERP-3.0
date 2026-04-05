# INT-SG-035 - Superglue Runtime Contract

## Ziel

Den Self-Host-Stack auf den aktuellen Upstream-Runtime-Vertrag ziehen.

## Umsetzung

- Compose-, K8s- und Helm-Pfad auf `WEB_PORT=3001` und `API_PORT=3002` umgestellt
- Upstream-Env-Pflichtfelder fuer Auth, Postgres, MinIO und Encryption nachgezogen
- `POSTGRES_SSL=false` fuer den lokalen Self-Host-Compose-Pfad explizit gesetzt
- MinIO-Image-Pin auf einen verfuegbaren Docker-Hub-Release korrigiert

## Ergebnis

Der VALEO-Self-Host-Pfad folgt jetzt dem aktuellen Upstream-Port- und Env-Modell statt einem aelteren Eigenvertrag.
