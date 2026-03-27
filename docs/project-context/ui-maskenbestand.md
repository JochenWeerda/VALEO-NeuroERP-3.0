# UI-Maskenbestand

## Zweck

Diese Datei beschreibt den methodischen Umgang mit vorhandenen Standardmasken und prozessnahen Spezialmasken.

## Grundsatz

Nicht jeder Workflow braucht eine neue Maske.

Bevor eine Spezialmaske entworfen wird, ist zu pruefen:

1. Kann die bestehende Standardmaske fachlich sauber erweitert werden?
2. Bleibt die Maske danach fuer andere Prozesse klar und wartbar?
3. Bleibt die Benutzerfuehrung auch unter Zusatzfunktionen verstaendlich?

## Typische Maskentypen

- Standard-Belegmasken fuer Auftrag, Bestellung, Wareneingang, Lieferschein, Rechnung, Kontrakt
- Arbeitslisten und Uebersichten
- Dialoge fuer Teilmengen, Storno, Korrektur, Freigabe
- Schnellstarts oder Intake-Dialoge fuer pragmatische Direktprozesse
- Flow-Spine-Prozessraeume als Steuerungs- und Kontextschicht

## Pruefkriterien fuer bestehende Masken

- sind alle Pflichtdaten erfassbar?
- sind Statuswechsel sichtbar und ausloesbar?
- sind fachlich zulaessige Aenderungen moeglich?
- ist Storno/Korrektur statt hartem Delete vorhanden?
- sind Uebergaben zwischen Masken konsistent?
- gibt es Sackgassen oder fehlende Felder?

## Pflichtregel

Wenn eine Maske im Rahmen einer Analyse oder Fehlerbehebung geaendert wird:

- Soll-Ist-Bewertung aktualisieren
- Browser-Use-Pruefung ergaenzen
- Entscheidung Standardmaske vs Spezialmaske dokumentieren, wenn relevant
