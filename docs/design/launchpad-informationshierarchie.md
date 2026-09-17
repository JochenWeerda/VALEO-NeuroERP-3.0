---
title: Launchpad Informationshierarchie
type: decision
audience: [design, entwickler, agent, produkt]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Startseite und globale Navigation als Arbeitsplatz, nicht als Menü aller Funktionen. Fiori als Orientierung, nicht als visuelle Kopie.
---

# Launchpad: Weniger Navigation, mehr situative Arbeit

Stand 2026-09-17, nach dem direkten Vergleich Startseite gegen SAP Fiori
Launchpad (Flexus-Glossar / Fiori-Verhalten) und dem Screenshot
Handel & CRM → Meine Kunden.

**Befund:** VALEO ist fachlich bereits reichhaltiger. Fiori ist bei visueller
Hierarchie, Ruhe, Konsistenz und Orientierung weiter. Das Problem ist nicht
„zu wenig Design“, sondern **zu viele Navigationsebenen gleichzeitig**.

Die Personalisierung (`HOME-LAUNCHPAD-PERSONALIZE`) bleibt. Dieser Text legt
den nächsten strukturellen Umbau fest, bevor weitere Kacheln oder Farben
kommen. Spaces/Pages als **Informationsarchitektur** stehen in
[`launchpad-spaces.md`](launchpad-spaces.md). Meridian bleibt der Vertrag der
Masken; die Startseite ist Einstieg, nicht Maske.

## IST — fünf konkurrierende Ebenen

Was der Screenshot gleichzeitig zeigt:

1. Hauptnavigation links (AppShell)
2. Arbeitswelten oben (Spaces)
3. Seiten darunter (Pages)
4. Kacheln der gewählten Seite
5. Schnellaktionen und KPI-Karten darunter, plus Sidebar und oft die
   Realtime-Leiste im Footer

Kette im Beispiel: **Handel & CRM → Meine Kunden → Kunden-Cockpit → KIM**.
Das liest sich wie mehrere Systeme, nicht wie ein Arbeitsplatz.

Belege im Code (nicht raten):

| Fläche | Quelle |
|---|---|
| Spaces/Pages/Kacheln | `launchpad-spaces.ts`, `LaunchpadBoard.tsx` |
| Seite „Meine Kunden“ | fünf IDs: `kunden`, `kunden-schnellauswahl`, `kunden-cockpit`, `kim-cockpit`, `kontakte` |
| Schnellaktionen | `ACTION_SHORTCUTS` plus „Letzte Dokumente“ in `start-dashboard.tsx` |
| KPI-Streifen | `KPI_TILES` (Umsatz, Aufträge, Kunden, Lager) — Wert, kein Trend |
| Realtime-Leiste | `DashboardLayout.tsx`, dauerhaft wenn Realtime an |

## SOLL — vier Ebenen, eine Frage je Ebene

| Ebene | Inhalt | Frage |
|---|---|---|
| 1 Globale Navigation | Start · Aufgaben · Suche · Bereiche | Wo bin ich im System? |
| 2 Bereich | z. B. Handel & CRM | In welcher Arbeitswelt? |
| 3 Prozess-/Arbeitsraum | z. B. Meine Kunden | Was kann ich hier tun? |
| 4 Inhalt | Liste, Cockpit, aktuelle Aufgaben | Was ist jetzt wichtig? |

Erst **innerhalb eines Kunden** (Object Page / KIM):

Übersicht | Kontakte | Angebote | Aufträge | Kontrakte | Dokumente | Aktivitäten

Sekundäre Navigation (linke Modulbaum, Unterreiter der Startseite, lange
Schnellaktionsleiste) erscheint erst bei Bedarf, nicht dauerhaft neben den
Kacheln.

Nicht kopieren: Belize-Farben, SAP-Aktionsblatt, Transaktionscodes, Statusgrün
als Dekoration. Chart-Slots und semantische Tokens bleiben VALEO.

## Prioritäten

| Prio | Bereich | VALEO heute | Übernahme |
|---|---|---|---|
| **1** | Informationshierarchie | Links + Bereichsreiter + Unterreiter + Kacheln + Schnellaktionen gleichzeitig | Pro Ebene eine Frage; Rest erst bei Bedarf |
| **1** | Startseite entschlacken | Viele Einstiege auf einem Schirm | **6–10** Kacheln pro Rolle; Rest Suche/App-Finder |
| **1** | Kacheldesign | Gleiche visuelle Gewichtung | App-, KPI-, Alert-, Task-Tile; Wichtiges darf stärker sein |
| **1** | Abstände | Dicht | Vertikale Luft zwischen Navigation, Kacheln, Aktionen, KPIs |
| **1** | Navigationstiefe | Konkurrierende Systeme | **Bereich → Prozessraum → App/Objekt** |
| **2** | Rollen | Viele Funktionen grundsätzlich sichtbar | Außendienst ≠ Disposition ≠ Buchhaltung ≠ GF (UIX-061) |
| **2** | Persönliche Startseite | Anpassen vorhanden, optisch sekundär | Favoriten, häufig, zuletzt, eigene Reihenfolge vorn |
| **2** | KPI-Karten | Wert ohne Kontext | Wert + Trend + Zeitraum + Abweichung + Drilldown |
| **2** | Schnellaktionen | Lange horizontale Reihe | Max. **4–6** primäre; Rest in **Mehr** oder kontextabhängig |
| **2** | Suche | Startfeld + Ctrl+K, oft nur Label | Universal-Suche: Kunden, Artikel, Belege, Kontrakte, Aktionen |
| **2** | Typografie | Ähnliche Gewichtung | Seitentitel, Bereich, Objekt, Metadaten, Hilfe klar getrennt |
| **3** | Icons | Gemischte Sprache | Ein System, gleiche Strichstärke und Bedeutung |
| **3** | Farbe | Zurückhaltend, wenig Führung | Nur Status und Ausnahme, nicht dekorativ |
| **3** | Cards | Bereiche laufen ineinander | Klare Blöcke, gleiche Innenabstände |
| **3** | Microinteractions | Zustände uneinheitlich | Hover, Fokus, Selected, Loading, Skeleton, Disabled, Erfolg |
| **3** | Responsive | Desktop-breit | Notebook, Tablet, Außendienstgerät |
| **3** | Barrierefreiheit | Fundament da, Anwendung lückenhaft | WCAG 2.2 AA: Fokus, Kontrast, Tastatur, Touch 44 px, Screenreader |
| **4** | App-Finder | Nur im Anpassen-Modus, Suche nur Label | Zentral, mit Kategorie = Arbeitswelt, auch ohne Anpassen |
| **4** | Leere Fläche unter KPIs | Ungenutzt | Aufgaben, Warnungen, Wiedervorlagen, Ausnahmen — keine Extra-Navigation |
| **4** | Statusleiste | Realtime dauerhaft | Nur Admin/Support; Fachnutzer nur bei Störung |

## Screenshot Handel & CRM → Meine Kunden

Fünf Kacheln überlappen:

| Heute | Entscheidung |
|---|---|
| Kunden | bleibt: zentrale Liste + Suche |
| KIM | bleibt: 360°-Arbeitsplatz |
| Kunden-Cockpit | **aus der produktiven UI**, abgelöst durch KIM |
| Kunden-Schnellauswahl | Funktion der Suche, keine eigene Startkachel |
| Kontakte | in den Kundenkontext (KIM-Register), nicht paralleler Einstieg |

Dritter Einstieg der Seite: **Meine Aufgaben / Wiedervorlagen**, nicht ein
fünftes Kunden-Alias.

Schnellaktionen für Außendienst, nicht zwölf gleichberechtigte Buttons:

**+ Kunde** · **+ Angebot** · **+ Auftrag** · **+ Aktivität** · **Mehr**

## Wo VALEO Fiori überholen kann

Kein generisches App-Verzeichnis. Morgens ein **operatives Cockpit** für
Agrarhandel, sobald die Zahlen echt sind (keine Registry-Demos, siehe FSX-002):

**Heute**

- offene Kundenrückrufe
- Kontrakte kurz vor Ausschöpfung
- überfällige Lieferungen
- Kunden mit Düngerbedarf
- PSM-Aufbrauchfristen
- heutige Tour-Kunden
- Lagerauslastung (z. B. KAS)

Die Startseite zeigt Ausnahmen und Arbeit, nicht ein zweites Menü. Der
Vorgangsstand bleibt am Beleg (`ProcessBand`). Der Leitstand bleibt Ebene 3.

## Personalisierung — Abgleich Spezifikation

`HOME-LAUNCHPAD-PERSONALIZE` deckt das Fiori-Verhalten fast vollständig ab.
Handshake: [`claude-cursor-launchpad-katalog-2026-09-17.md`](../agent-ops/handshakes/claude-cursor-launchpad-katalog-2026-09-17.md).

Vorhanden: Anpassen-Modus, Kachel entfernen, Titel/Beschreibung, Verschieben,
Drag (auch gruppenübergreifend), Klick öffnet die App, Gruppe anlegen /
verschieben / umbenennen (Escape verwirft) / löschen (erste Seite geschützt) /
zurücksetzen / ausblenden. Zusätzlich Tastaturumordnung.

Drei Lücken, alle im App-Katalog:

1. Keine Kategorieauswahl — Arbeitswelten sind die Kategorien.
2. Katalog nur im Anpassen-Modus, nicht im Benutzermenü.
3. Suche nur `tile.label`, nicht `description`.

Bewusste Abweichung, keine Lücke: Aktionen liegen an der Kachel, nicht hinter
einem SAP-Aktionsblatt.

## Sprints (Reihenfolge bindend)

Stand 2026-09-17 **Sprint 1+2 umgesetzt** (nicht committed): Kunden-Seite drei
Einstiege, 6–10 Kacheln, Luft, Schnellaktionen 4+Mehr, App-Finder mit Kategorie,
Beschreibung und Nav-Stichworten, Finder ohne Anpassen-Modus, KPI mit Zeitraum/
Trend/Abweichung/Drilldown ohne Fake-Lagerzahl, globale Ebene Start · Aufgaben · Suche,
Sidebar auf Start eingeklappt und ausgeblendet, Realtime-Leiste nur bei Störung.
Startfläche (Katalog, Reiter, Schnellaktionen, Finder) auf **44 px** Touchziel.
Prozessräume sind keine zweite Reiterleiste mehr, sondern eine Auswahl
(eine Überschrift, wenn nur ein Raum). Sprint 3 (KIM-Workspace in der Maske)
bleibt eigene Claim-Grenze. Operatives „Heute“ ohne echte Quellen nicht gebaut.
Vollständige WCAG-2.2-AA-Härtung der übrigen Masken bleibt **danach**.

Nicht umdrehen. Keine FSX-Dateien in diesen Slices. Kein SAP-Lookalike.
`screen_definitions.py` / Auftrag / Rechnung bleiben Claude, außer KIM als
Object-Page-Workspace in Sprint 3 (eigene Claim-Grenze).

| Sprint | Inhalt | Nicht |
|---|---|---|
| **1** | Navigation + Informationshierarchie: eine Ebene sichtbar; 6–10 Kacheln/Rolle; Kunden-Seite auf drei Einstiege; Luft | Neue Farben, neue Apps |
| **2** | Tile-Typen, KPI mit Kontext, Schnellaktionen 4–6 + Mehr, Personalisierung sichtbarer, App-Finder-Lücken 1–3 | KIM umbauen |
| **3** | KIM als durchgängiger Object-Page-Workspace; Kontakte/Cockpit/Schnellauswahl nicht mehr als parallele Startkacheln | Pixel-Fiori |
| **danach** | Responsive, WCAG 2.2 AA, Icon- und Farbhärtung, Realtime-Leiste rollenbasiert, operatives „Heute“ mit echten Quellen | Erfundene Kennzahlen |

UIX-061 (Rollen-Workspaces) nährt Sprint 1/2, ersetzt sie nicht. Die Omnibox
(UIX-060) nährt die Universal-Suche, ersetzt den App-Finder nicht.

## Abnahme für spätere Slices

- Eine Startansicht beantwortet: Wo bin ich? Was kann ich hier tun? Was ist wichtig?
- „Meine Kunden“ hat höchstens drei produktive Einstiege.
- Schnellaktionen: höchstens sechs sichtbare primäre plus Mehr.
- App-Finder: Kategorie und Beschreibung, auch ohne Anpassen-Modus.
- Keine Statusfarbe ohne fachliche Ausnahme.
- Keine erfundenen Heute-Zahlen.
