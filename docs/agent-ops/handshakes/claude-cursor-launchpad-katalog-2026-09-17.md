# Handshake: Claude Code → Cursor (App-Katalog der Startseite)

Stand: 2026-09-17
Von: Claude Code
An: Cursor
Slice: `HOME-LAUNCHPAD-PERSONALIZE-20260917` (Owner: Cursor, Status: abgeschlossen)
Branch: `main`

## Kontext in einem Satz

Der Anwender hat die Fiori-Spezifikation „Behavior and Interaction" der
Launchpad-Personalisierung vorgelegt; dein Slice deckt sie fast vollständig ab,
drei Punkte fehlen — alle im App-Katalog.

## Was bereits trägt

Gegen die Spezifikation geprüft, alles vorhanden: Anpassen-Modus oben rechts,
Kachel entfernen, App Settings (Titel/Beschreibung), Move in eine andere
Gruppe, Drag & Drop für Kacheln innerhalb und zwischen Gruppen, normaler
Kachelklick öffnet die App, Gruppe anlegen mit Platzhaltername, Gruppe
verschieben, umbenennen mit Escape-Verwerfen, löschen (erste Seite geschützt),
zurücksetzen, aus- und einblenden.

Die Tastaturumordnung (`onKeyReorder`) geht über die Spezifikation hinaus. Gut
so — Drag & Drop allein ist nicht bedienbar ohne Zeigegerät.

## Drei offene Punkte

Alle in `packages/frontend-web/src/components/navigation/LaunchpadBoard.tsx`,
im Dialog `finderOpen` (ab Zeile 313).

1. **Kategorieauswahl im Katalog fehlt.** Die Spezifikation nennt sie
   ausdrücklich: „select a tile category from the dropdown box **and/or** use
   the search field". Vorhanden ist nur das Suchfeld. Die Kategorien liegen
   nahe, weil der Katalog ohnehin nach Arbeitswelten gegliedert ist —
   `Select` ist in der Datei bereits importiert (Move-Dialog).

2. **Der Katalog ist nur im Anpassen-Modus erreichbar.** `setFinderOpen(true)`
   hängt allein an „Kachel hinzufügen" auf einer Seite. Die Spezifikation hat
   ihn zusätzlich im Benutzermenü („Open App Finder"), also auch ohne
   Anpassen-Modus.

3. **Die Suche greift nur auf `tile.label`** (Zeile 327), nicht auf
   `tile.description`. Wer „Waage" sucht, findet eine Kachel nicht, die anders
   heißt und nur so beschrieben ist.

## Eine bewusste Abweichung — kein Nachtrag

Die Spezifikation legt App Settings und Move hinter ein Aktionsblatt, das sich
beim Klick auf die Kachel öffnet. Du zeigst die Aktionen direkt an der Kachel.
Das ist ein Klick weniger; SAP braucht das Aktionsblatt vor allem wegen Touch.
Aus meiner Sicht bleibt das so, solange der Anwender die Fiori-Gewohnheit nicht
ausdrücklich will.

## Warum von mir und nicht gebaut

Alle vier betroffenen Dateien stehen in deinem `file_ownership`, der Stand liegt
unversioniert in deinem Arbeitsbaum. Der Anwender hat entschieden, dass der
Slice in einer Hand bleibt.
