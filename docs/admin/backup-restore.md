---
title: Backup & Restore
type: how-to
audience: [betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Backup & Restore

Datensicherung umfasst PostgreSQL (führend), den DMS-Dokumentenbestand und
relevante Konfiguration. GoBD verlangt Nachvollziehbarkeit und
Unveränderbarkeit der aufbewahrten Daten.

## Was sichern?

| Komponente | Inhalt | Hinweis |
|---|---|---|
| PostgreSQL | Geschäftsdaten aller Mandanten | führendes System |
| DMS (Paperless-ngx) | Belege/Dokumente | revisionssicher |
| Konfiguration | `.env`, Compose, Secrets-Quelle | Secrets separat/verschlüsselt |

## Datenbank sichern (Beispiel)

```bash
pg_dump "$DATABASE_URL" --format=custom --file=backup_$(date +%F).dump
```

## Restore (Beispiel)

```bash
pg_restore --clean --if-exists --dbname "$DATABASE_URL" backup_2026-06-25.dump
```

!!! warning "Restore-Test"
    Ein Backup ist nur gültig, wenn der Restore regelmäßig getestet wurde.
    Restore-Übungen mindestens quartalsweise durchführen.

## Aufbewahrung

- Aufbewahrungsfristen gemäß GoBD beachten.
- Backups verschlüsselt und zugriffsbeschränkt ablegen.
- Mandantentrennung bleibt auch in Backups gewahrt (gemeinsame DB, aber
  Tenant-Bezug je Datensatz).
