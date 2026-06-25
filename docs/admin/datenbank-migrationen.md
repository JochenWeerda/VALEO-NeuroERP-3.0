---
title: Datenbank-Migrationen
type: how-to
audience: [betrieb, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Datenbank-Migrationen

Schemaänderungen werden über **Alembic** versioniert und kontrolliert
ausgerollt.

## Grundbefehle

```bash
# Alle Migrationen anwenden (bei Neuinstallation/Clone Pflicht)
alembic upgrade head

# Neue Migration aus Modelländerungen erzeugen
alembic revision --autogenerate -m "beschreibung"
```

## Regeln

- **Single-Head:** Es darf nur ein Alembic-Head existieren. Mehrere Heads
  zusammenführen, bevor ausgerollt wird.
- **Vorwärts gerichtet:** Migrationen müssen reproduzierbar `upgrade head`
  durchlaufen.
- **Multi-Schema:** Das Datenmodell nutzt mehrere PostgreSQL-Schemata
  (`domain_shared`, domänenspezifische Schemata).

## ERP-Domain (Finanz) — SQL-Migrationen

Für die Monorepo-ERP-Domain existiert ein separater SQL-Runner:

```bash
pnpm migrate:erp-finanz
```

Verbindungsreihenfolge: `ERP_DATABASE_URL` → `DATABASE_URL` → `CRM_DATABASE_URL`.

## Ablauf beim Release

1. Backup erstellen (siehe [Backup & Restore](backup-restore.md)).
2. `alembic upgrade head` ausführen.
3. Health-Checks und Smoke-Test je Kernprozess.
4. Im Fehlerfall: Restore aus Backup.

## Häufige Fehler

- **Multiple heads:** `alembic merge` durchführen.
- **Autogenerate erkennt Änderung nicht:** Modell-Import/`Base`-Registrierung
  prüfen.
