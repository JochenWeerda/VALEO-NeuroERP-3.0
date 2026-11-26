---
title: Installationshandbuch (Gerüst)
type: how-to
audience: [betrieb, entwickler]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-26
version: 0.1.0
description: Gerüst einer Neuinstallation aus dem Repo — Compose, Alembic, Mandant, Restore. Keine Produktionsfreigabe.
---

# Installationshandbuch (Gerüst)

Stand: 2026-11-26. **Gerüst** entlang einer Neuinstallation aus dem Repository
(`docs/roadmap/m7-m8-vorarbeiten.md` §1 / §3). Keine vollständige
Betriebsabnahme; M5-Geheimnisse und Produktionsreife bleiben offen.

## 1. Voraussetzungen

- Docker / Docker Compose
- Git-Checkout dieses Repositories
- Produktionsgeheimnisse bereitstellen (nicht im Repo): mindestens
  `POSTGRES_PASSWORD`, `OIDC_CLIENT_SECRET` — siehe
  `docker-compose.production.yml` (`:?… fehlt`)

## 2. Stack starten

```bash
# Aus dem Repo-Wurzelverzeichnis
cp .env.example .env   # Werte lokal setzen; keine echten Geheimnisse committen
docker compose -f docker-compose.production.yml up -d --build
```

Health: Backend `http://localhost:8000/health` (im Compose-Netz intern),
Frontend laut Compose an `127.0.0.1:8080`.

## 3. Schema (Alembic)

Auf leerem PostgreSQL (oder frischem Volume):

```bash
alembic upgrade head
```

Für den gemeinsamen Prüfstand (Schema frisch, nicht als Routine-Reset vor
Fachtests):

```bash
python scripts/pruefstand_db.py --status
# Nur in abgestimmtem Wartungsfenster: python scripts/pruefstand_db.py
```

## 4. Erster Mandant

Produktive Mandantenanlage folgt dem M5-Mandantenweg (offen / nicht dieser
Schnitt). Für **synthetische** Demo-/Schulungsdaten:

```bash
# gegen valeo_probe / TEST_DATABASE_URL
python scripts/demo_mandant.py --anlegen
python scripts/demo_mandant.py --loeschen
```

Keine echten Personen- oder L3-Daten.

## 5. Restore-Probe

Siehe [Backup & Restore](../admin/backup-restore.md):

```bash
pg_dump "$DATABASE_URL" --format=custom --file=backup_$(date +%F).dump
pg_restore --clean --if-exists --dbname "$DATABASE_URL" backup_YYYY-MM-DD.dump
# Drill (Staging/Ops):
DRILL_OPERATOR="<name>" bash scripts/run_restore_drill.sh
```

## 6. Offen

- Installationsskript / CI-Probe auf leerem Host (M7, braucht M5-Betriebsreife)
- Helm-/Update-Verfahren und Geheimnisrotation
- Vollständige Betriebsabnahme mit Live-SSO

## Verweise

- `docker-compose.production.yml`
- `docs/admin/backup-restore.md`
- `docs/roadmap/m7-m8-vorarbeiten.md`
- `scripts/demo_mandant.py`
