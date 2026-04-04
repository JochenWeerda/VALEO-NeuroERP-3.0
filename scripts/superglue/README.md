# Superglue Ops Scripts

Diese Skripte decken den operativen Standardpfad fuer Superglue ab:

- lokales Compose starten
- Helm/K8s rendern und validieren
- Backup/Restore gegen den Compose-Stack
- einfache HTTP-Smokes

Voraussetzungen:

- Docker Desktop mit `docker compose`
- fuer Helm-Render: `helm`
- fuer K8s-Deploy: `kubectl`

Die Skripte schreiben keine Secrets ins Repo. Alle benoetigten Werte kommen ueber bestehende `SUPERGLUE_*`-Variablen.

