---
title: Backup & Restore
type: how-to
audience: [betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-11
version: 3.1.0
---

# Backup & Restore

Datensicherung umfasst PostgreSQL (führend), den DMS-Dokumentenbestand und
relevante Konfiguration. GoBD verlangt Nachvollziehbarkeit und
Unveränderbarkeit der aufbewahrten Daten.

## 15-min-RTO-Drill (SPEC-P0-08)

Repo-seitig vorbereitet; der reale Lauf gegen Staging bleibt Betriebsverantwortung.

```bash
# Ops: gegen produktionsnahe Umgebung (Backup-Pfad/DB-Env setzen)
DRILL_OPERATOR="<name>" bash scripts/run_restore_drill.sh

# Evidence prüfen (Exit 2 = noch kein Protokoll / EXTERNAL_GATE)
python scripts/check_restore_drill_evidence.py
# Release-Gate mit Fail-closed: python scripts/check_restore_drill_evidence.py --strict
```

Protokoll landet unter `docs/operations/drill-protocols/restore-drill-<datum>.json`
(siehe [drill-protocols/README.md](../operations/drill-protocols/README.md)).
Keine Secrets/PII ins Protokoll schreiben.

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
