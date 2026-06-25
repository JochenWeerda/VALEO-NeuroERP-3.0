---
title: In-App-Hilfe & Deep-Links
type: explanation
audience: [endnutzer, entwickler, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# In-App-Hilfe & Deep-Links

Konzept, wie die Anwendung kontextsensitiv auf diese Dokumentation verweist.

## Ziel

Aus jeder Maske heraus soll mit einem Klick die passende Anleitung erreichbar
sein – ohne dass Nutzer:innen manuell suchen müssen.

## Prinzip: Routen-ID → Doku-Anker

Jede Maske/Route hat eine stabile **Routen-ID**. Diese wird auf eine Doku-Seite
abgebildet:

| Routen-ID (Beispiel) | Doku-Ziel |
|---|---|
| `agrar/annahme` | [Ernteannahme durchführen](annahme.md) |
| `verkauf/auftrag` | [Vom Auftrag zur Rechnung](verkauf.md) |
| `lager/bestand` | [Lager – Bestand, Umlagerung, Inventur](lager.md) |
| `finanzen/offene-posten` | [Finanzbuchhaltung](finanzbuchhaltung.md) |

## Umsetzungsweg (Frontend)

1. Hilfe-Symbol in der Kopf- oder Fußzeile jeder Maske.
2. Das Symbol verlinkt anhand der aktuellen Routen-ID auf die zugeordnete
   Doku-URL (Mapping-Tabelle, gepflegt analog zu `route-aliases.json`).
3. Fällt keine spezifische Zuordnung an, wird die Bereichs-Startseite geöffnet.

## Pflege

- Das Mapping wird gemeinsam mit neuen Masken erweitert.
- Diese Seite ist die fachliche Referenz für die Zuordnung; die technische
  Umsetzung erfolgt im Frontend.

> Die konkrete Frontend-Integration (Hilfe-Button + Mapping) ist als Folgearbeit
> vorgesehen; dieses Dokument legt das verbindliche Konzept fest.
