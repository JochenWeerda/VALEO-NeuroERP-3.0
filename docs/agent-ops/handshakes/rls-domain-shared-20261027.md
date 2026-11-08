---
title: Handshake RLS-DOMAIN-SHARED-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain shared mit Fachkorrekturen an Mandant (Token statt Query/Kopf) und Identität (Absender, Rations-Zugang, Grundfutter aus den geprüften Claims).
---

# Handshake RLS-DOMAIN-SHARED-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis: `claude/rls-domain-einkauf-20261027` (#78). Der PR zielt auf den einkauf-Zweig und wird nach #78 integriert.
- Alembic: `rls_domain_einkauf_20261027 → rls_domain_shared_20261027`. `alembic heads` zeigt einen einzigen Head.

## Prüfstand

Das Fenster wurde nach deiner Freigabe genutzt. Gegenproben: ohne Verbund-FKs 20 rot, mit dem alten Code 13 rot.
Die gewachsene Datenbank habe ich nur lesend geprüft: kein Abbruchgrund. Danach steht `valeo_probe` unverändert auf
`loading_stop_fk_20261023`, 0 offene Sitzungen.

## Für dich

1. **Live-relevant (Mandant):** `/admin/branches*`, `/master-data/*`, `/messages/`, `/agribusiness/farmers*`,
   `/agrar/grundfutter-analysen*`, `/agrar/psm/*` nehmen den Token-Mandanten; `?tenant_id=` und der Kopf werden
   nicht mehr gelesen. Ohne Angabe galt vorher der Standardmandant.
2. **Live-relevant (Identität):** `POST /messages/` nimmt kein `sender_id` mehr an; Absender ist der angemeldete
   Nutzer, ohne eindeutige lokale Zuordnung 403. `/agrar/rations/{tenant_id}/zugang*` und der Portalpfad der
   Grundfutteranalysen lesen die E-Mail aus dem Token (Claim `email`), nicht aus `X-User-Email`; ohne geprüfte E-Mail
   403 bei der Zugangsverwaltung. **Bitte prüfen**, ob der Keycloak-Client den Claim `email` ausstellt.
3. **Maskenbrücken:** `/pos/rabatte` und `/preise/konditionen` in `mask_frontend_bridges.py` lasen Konditionen aller
   Mandanten. Ich habe nur die beiden SQL-Abfragen auf die Gruppe des Mandanten eingeschränkt; Maskenbindungen und
   generierte Artefakte sind unverändert.
4. **Vertragstest** `tests/test_keine_client_identitaet.py` erkennt jetzt auch `x_user_email: … = Header(…)` und
   `payload.sender_id`.
5. **`psm.py`** liegt unter `app/domains/agrar/api/` neben deinen Biostimulanzien; die Datei selbst gehört nicht zu
   deinem Claim, ich habe nur die Mandantenquelle getauscht.
6. OpenAPI nur für die genannten Pfade und `MessageCreate`. Die vorbestehende Drift (`/finance/closing-checklists*`,
   `/agrar/biostimulanzien*`, `/weighing-tickets*`) bleibt bei dir.
7. Bewusst offen: `users`, API-Schlüssel, ICS-Tokens, `outbox_events`, `audit_logs`, `policy_rules`
   (Begründung im QA-Dokument).
8. Nicht berührt: Codex-Claims (Agrar-Allokationen, MATERIAL-FLOW-SQL), Studio/Masken, Systemrollen, Live.
