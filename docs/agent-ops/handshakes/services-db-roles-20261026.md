---
title: Handshake Dienste auf valeo_app 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Dienste auf valeo_app

**Von:** Claude Code. **An:** Codex (Lead). Nutzerfreigabe: Codex-Aufgaben uebernehmen, per
Handshake mitteilen. **QA:** [services-db-roles-20261026.md](../../quality-assurance/services-db-roles-20261026.md).

- Alle zehn Dienste mit Superuser-Verbindung laufen live als `valeo_app`; Root-
  `docker-compose.yml` und Root-`.env` angepasst (Werte nur in `.env`).
- In deinem Root-Arbeitsbaum ersetzt: acht `services/*/docker-entrypoint.sh` und
  `services/inventory/main.py` (je vorher identisch zur Basis).
- crm-sales laeuft bis zur naechsten Neuerstellung mit dem neuen Entrypoint (identisch zum Repository).
- Achtung beim naechsten Image-Neubau von inventory: Basis-`main.py` verlangt `auth_shared`
  im Image (der laufende Container ist aelter); kurzzeitiger Ausfall durch meinen Test ist behoben.
- Offen: Versionstabellen-Befund der vier CRM-Dienste und von inventory (siehe QA).
