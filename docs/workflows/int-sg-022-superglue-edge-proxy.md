# INT-SG-022 - Superglue Edge / Proxy Overlay

## Ziel

Den lokalen Superglue-Ops-Stack aus `INT-SG-021` um einen staging-/prod-naeheren Edge-Pfad erweitern:

- Reverse Proxy mit TLS vor dem Stack
- direkte Host-Ports fuer Superglue-, MinIO- und DB-Container im Overlay schliessen
- Header-Hardening und Admin-Zugriff fuer MinIO-Console

## Umsetzung

- Neues Overlay [docker-compose.integration.edge.yml](C:/Users/Jochen/VALEO-NeuroERP-3.0/docker-compose.integration.edge.yml)
- Neuer Proxy-Config-Pfad [Caddyfile](C:/Users/Jochen/VALEO-NeuroERP-3.0/ops/superglue/Caddyfile)
- `superglue-edge` exponiert nur `80/443`
- `superglue`, `superglue-minio` und `superglue-db` werden im Overlay auf interne `expose`-Ports reduziert
- MinIO-Console ist ueber eigenen Hostnamen und Basic Auth separat abgesichert

## Pflichtvariablen

- `SUPERGLUE_DB_PASSWORD`
- `SUPERGLUE_AUTH_TOKEN`
- `SUPERGLUE_MINIO_ROOT_PASSWORD`
- `SUPERGLUE_TLS_DOMAIN`
- `SUPERGLUE_MINIO_TLS_DOMAIN`
- `SUPERGLUE_EDGE_BASICAUTH_HASH`

Optional:

- `SUPERGLUE_TLS_EMAIL`
- `SUPERGLUE_EDGE_BASICAUTH_USER`

## Startbeispiel

```powershell
$env:SUPERGLUE_DB_PASSWORD="..."
$env:SUPERGLUE_AUTH_TOKEN="..."
$env:SUPERGLUE_MINIO_ROOT_PASSWORD="..."
$env:SUPERGLUE_TLS_DOMAIN="superglue.example.test"
$env:SUPERGLUE_MINIO_TLS_DOMAIN="superglue-minio.example.test"
$env:SUPERGLUE_EDGE_BASICAUTH_HASH="..."
docker compose -f docker-compose.integration.yml -f docker-compose.integration.edge.yml --profile superglue-edge up -d
```

## Abnahme

- kombinierte Compose-Konfiguration validiert
- Edge-Service ist der einzige externe Ingress
- Superglue-/MinIO-/DB-Container bleiben im Overlay intern
- TLS- und Security-Header sind im Proxy modelliert

## Offene Punkte

- DNS und Zertifikatsbeschaffung bleiben deploymentabhaengig
- fuer echte Prod-Landschaften kann ein Ingress/Load-Balancer statt Caddy sinnvoller sein
