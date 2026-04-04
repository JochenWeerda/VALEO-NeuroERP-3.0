# INT-SG-021 - Superglue Compose Stack

## Ziel

Den vorbereiteten Superglue-Deploymentpfad aus `docker-compose.integration.yml` zu einem belastbaren lokalen Ops-Stack ausbauen:

- eigener Postgres-Container
- eigener MinIO-Container fuer Objekt-/Artefaktablage
- Init-Job fuer Bucket-Erstellung
- Healthchecks, Volumes und internes Netz
- keine harten Secrets im Compose-File

## Umsetzung

- Die Superglue-Services laufen unter dem Compose-Profil `superglue`, damit der restliche Integrations-Stack nicht ungeplant mitstartet.
- `superglue-db` nutzt benannte Persistenz und `pg_isready`.
- `superglue-minio` stellt S3-kompatiblen Storage bereit; `superglue-minio-init` erzeugt den Bucket `SUPERGLUE_MINIO_BUCKET`.
- `superglue` haengt an DB-, MinIO- und Init-Health und bekommt nur env-basierte Secrets.

## Erforderliche Variablen

- `SUPERGLUE_DB_PASSWORD`
- `SUPERGLUE_AUTH_TOKEN`
- `SUPERGLUE_MINIO_ROOT_PASSWORD`

Optional:

- `SUPERGLUE_DB_NAME`
- `SUPERGLUE_DB_USER`
- `SUPERGLUE_MINIO_ROOT_USER`
- `SUPERGLUE_MINIO_BUCKET`
- `SUPERGLUE_S3_REGION`
- `SUPERGLUE_PUBLIC_BASE_URL`

## Startbeispiel

```powershell
$env:SUPERGLUE_DB_PASSWORD="..."
$env:SUPERGLUE_AUTH_TOKEN="..."
$env:SUPERGLUE_MINIO_ROOT_PASSWORD="..."
docker compose -f docker-compose.integration.yml --profile superglue up -d
```

## Abnahme

- `docker compose ... config` validiert mit gesetzten Pflichtvariablen
- `superglue-db` und `superglue-minio` haben Healthchecks
- Bucket-Init ist als separater Step modelliert
- keine Passwoerter mehr fest im Compose-File

## Offene Punkte

- das exakte produktive Image-/Env-Schema von Superglue kann je Deployment abweichen
- Proxy-/Network-Policy-Hardening folgt im Infrastruktur-Layer ausserhalb des Repo-Compose
