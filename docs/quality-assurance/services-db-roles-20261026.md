---
title: Dienste auf valeo_app (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Dienste auf valeo_app (2026-10-26)

Slice `SERVICES-DB-ROLES-20261026`, Zweig `claude/services-db-roles-20261026`.
Vorstufe: [db-roles-rollout-20261026.md](db-roles-rollout-20261026.md) (Backend).

## Ausgangslage

Zehn Dienste verbanden sich als Superuser `valeo_dev` mit `valeo_neuro_erp`:
crm-analytics, crm-communication, crm-core, crm-multichannel, crm-sales, crm-security,
crm-service, crm-workflow, dms-adapter, inventory-service. Kein Dienst fuehrt ausserhalb
seiner Migrationen Laufzeit-DDL aus; inventory legt beim Start per `create_all` acht
Tabellen ohne Migration an (alle vorhanden, `valeo_app` hat volle Datenrechte). Sieben
Dienste und inventory fuehren beim Start `alembic upgrade head` aus und verschlucken
Fehler. Kein Dienst bindet Code ein; Code-Aenderungen wirken erst mit neuem Image.

## Umstellung (live)

- `docker-compose.yml`: Datenbank-URL je Dienst (`DATABASE_URL`, `CRM_CORE_DATABASE_URL`,
  `INVENTORY_DATABASE_URL`) = `${VALEO_APP_CONTAINER_ASYNC_DATABASE_URL:-<bisher>}`, dazu
  `MIGRATION_DATABASE_URL: ${VALEO_MIGRATOR_CONTAINER_ASYNC_DATABASE_URL:-<bisher>}`;
  Werte nur in der Root-`.env`.
- Zehn Container ohne Neubau neu erstellt: alle nach 24 s `healthy`; in `valeo_neuro_erp`
  verbindet niemand mehr als `valeo_dev` (nur `valeo_app`). Startlogs: 0 Rechtefehler,
  0 Tracebacks. crm-core, crm-sales, crm-service: Migrationen erfolgreich (auf Head, ohne
  DDL); die vier unten genannten Dienste und inventory scheitern wie zuvor (Befund).

## Repository (wirkt mit dem naechsten Image)

- Entrypoints der sieben CRM-Dienste und von inventory: `alembic upgrade head` mit
  `DATABASE_URL`/`INVENTORY_DATABASE_URL = ${MIGRATION_DATABASE_URL:-…}`.
- `services/inventory/main.py`: `create_all` ueber eine kurzlebige Migrator-Engine, wenn
  `MIGRATION_DATABASE_URL` gesetzt ist.
- Live geprueft: neuer Entrypoint in crm-sales (per stdin eingespielt, Image-Fassung war
  identisch zur Basis): Migration ueber die Migrator-Anmeldung erfolgreich, healthy.
- Root-Arbeitsbaum: dieselben neun Dateien uebernommen (vorher je identisch zur Basis).

## Zwischenfall

Ein Live-Test von `inventory/main.py` per `docker cp` kopierte die Basis-Fassung in einen
Container, dessen Image auf aelterem Code gebaut ist; die Basis-Fassung verlangt
`auth_shared`, das dem Image fehlt. inventory startete rund drei Minuten in Schleife und
wurde durch Neuerstellung aus dem Image wiederhergestellt (healthy, 0 Neustarts). Die
`main.py`-Aenderung ist deshalb nur syntaktisch und per Codepfad geprueft, nicht im Container.
Beim naechsten Image-Neubau von inventory muss `auth_shared` ins Image (vorbestehende
Basis-Anforderung, nicht Teil dieses Slices).

## Befund: fremde Versionstabelle (nicht geaendert)

crm-analytics, crm-communication, crm-multichannel, crm-workflow und inventory nutzen die
Standard-Versionstabelle `public.alembic_version` des Backends. Ihr Start-Upgrade findet die
Backend-Revision nicht ("Can't locate revision …") und scheitert bei jedem Start still;
ihre Migrationen laufen nie. Waere `alembic_version` leer, schrieben sie ihre Revisionen
in die Backend-Tabelle. crm-core, crm-sales, crm-service haben eigene Versionstabellen.
Behebung: eigene `version_table` je Dienst und Abgleich ihrer Ketten mit dem vorhandenen
Schema (stamp nach Strukturvergleich); eigener Slice.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.
