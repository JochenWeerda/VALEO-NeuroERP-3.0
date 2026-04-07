# Superglue Ops Scripts

Diese Skripte decken den operativen Standardpfad fuer Superglue ab:

- lokales Compose starten
- Helm/K8s rendern und validieren
- Backup/Restore gegen den Compose-Stack
- einfache HTTP-Smokes
- Tenant-Onboarding-Pack und Template-Exporte rendern

Voraussetzungen:

- Docker Desktop mit `docker compose`
- fuer Helm-Render: `helm`
- fuer K8s-Deploy: `kubectl`

Die Skripte schreiben keine Secrets ins Repo. Alle benoetigten Werte kommen ueber bestehende `SUPERGLUE_*`-Variablen.

Zusatz:

- `export-onboarding-pack.ps1` / `export-onboarding-pack.sh`
  - rendert den Tenant-Onboarding-Pack als `json`, `env` oder `vault`
  - Beispiel: `bash scripts/superglue/export-onboarding-pack.sh tenant-a env`

