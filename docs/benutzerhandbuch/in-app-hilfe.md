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

1. Hilfe-Symbol (`HelpCircle`) in der Kopfzeile (`TopBar`) – auf jeder Maske sichtbar.
2. Das Symbol verlinkt anhand des aktuellen Routen-Pfads auf die zugeordnete
   Doku-URL (Mapping in `src/lib/docs-help.ts`, gepflegt analog zu
   `route-aliases.json`).
3. Fällt keine spezifische Zuordnung an, wird das Benutzerhandbuch
   (Bereichs-Startseite) geöffnet.
4. Zusätzlich öffnet der Eintrag **„Dokumentation"** im User-Menü die Doku-Site.

## Implementierungsstand

- **Stufe 1 (umgesetzt):** Hilfe-Button + User-Menü-Eintrag öffnen die Doku-Site
  in einem neuen Tab. Basis-URL über `VITE_DOCS_URL` konfigurierbar (Fallback:
  veröffentlichte GitHub-Pages-Site, vgl. `mkdocs.yml#site_url`).
- **Stufe 2 (umgesetzt):** Kontextsensitives Mapping `Routen-Pfad → Handbuch-Seite`
  in `src/lib/docs-help.ts` (`resolveHelpUrl`), inkl. Längster-Prefix-Auflösung
  und Fallback. Abgedeckt durch `src/__tests__/lib/docs-help.test.ts`.

## Pflege

- Das Mapping (`ROUTE_DOC_MAP` in `src/lib/docs-help.ts`) wird gemeinsam mit neuen
  Masken erweitert.
- Diese Seite ist die fachliche Referenz für die Zuordnung; die technische
  Umsetzung liegt im Frontend (`docs-help.ts` + `TopBar.tsx`).
