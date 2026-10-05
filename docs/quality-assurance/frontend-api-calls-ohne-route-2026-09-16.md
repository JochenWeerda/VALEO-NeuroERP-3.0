---
title: Frontend-Aufrufe ohne Route
type: reference
audience: [agent, entwickler, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.1.0
description: Bestandsaufnahme der Frontend-Aufrufe, fuer die es keine Backend-Route gibt — gemessen, nicht geschaetzt.
---

# Frontend-Aufrufe ohne Route (Stand 2026-09-17)

Ein Aufruf an eine nicht existierende Route ergibt einen 404. Steht darum ein
`catch` mit leerer Liste — im Frontend die Regel, nicht die Ausnahme — zeigt die
Maske eine **leere Liste** statt eines Fehlers. Genau so sah die Faktura-Liste
monatelang aus, als gaebe es keine Rechnungen.

Gemessen mit `python scripts/check_frontend_api_calls.py --list`. Gezaehlt werden
nur Zeilen, die selbst einen Aufruf absetzen; zusammengesetzte Pfade
(`${BASE}/feeds`) erkennt das Skript nicht. Die Liste ist damit ein starker
Hinweis, kein Beweis — und keine Obergrenze.

**0 verschiedene Pfade** (Stand 2026-09-17, Ratsche `BASELINE = 0`). Start 110.
Die Abarbeitung steht in `docs/agent-ops/todo-frontend-backend-luecken.md`.
Die historische Pfadliste vor der Schliessung liegt in Git vor `6be9626d6`.

Jeder Eintrag hat genau zwei moegliche Antworten: **Pfad korrigieren** (die Route
heisst anders) oder **Endpunkt bauen** (es gibt ihn wirklich nicht). Ein dritter
Weg — den Aufruf still zu lassen — ist keiner.

`lager/leitstand` ist kein toter Aufruf: Der Leitstand bleibt ein Twin-Read-Model
ohne dekorative Leerseite, solange die Fachfrage offen ist.
