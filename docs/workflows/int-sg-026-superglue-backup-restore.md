# INT-SG-026 - Superglue Backup und Restore

## Ziel

DB- und Artefakt-Backups fuer Superglue wiederholbar machen und einen Restore-Testpfad definieren.

## Umsetzung

- Helm-Templates fuer Backup-PVC, DB-Backup-CronJob, MinIO-Mirror-CronJob und Restore-Test-CronJob
- lokale Compose-Skripte fuer Backup und Restore unter `scripts/superglue/`

## Ergebnis

Backups sind jetzt sowohl im Helm-Pfad als auch lokal im Compose-Pfad als wiederholbarer Standardfluss modelliert.

