---
title: Acht Logistik-Aktionsdeklarationen ohne Alt-Ausnahmen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# Acht Logistik-Deklarationsluecken geschlossen

Die vier nativen Capture-Masken Frachtbrief, Verladung, Tour-Fracht-Arbeitsraum
und Frachttabellen hatten acht bereits verdrahtete Seitenaktionen lediglich als
`stubReason` beschrieben. Backend-ScreenDefinition und Frontend-Fallback tragen
jetzt die tatsaechlichen Wege; die Seitenhandler wurden nicht umgebaut.

| Aktion | Deklarierter bestehender Weg |
|---|---|
| Frachtbrief: Verladung | `/verladung` |
| Verladung: Neu | `/verladung/lkw-beladung` |
| Tour-Fracht: Touren | `/logistik/tourenplanung` |
| Tour-Fracht: Fracht | `/logistik/frachtbriefe` |
| Tour-Fracht: Tabellen | `/logistik/frachttabellen` |
| Tour-Fracht: Probe | `fracht.calculateProbe`, vorhandener Seiten-Callback |
| Frachttabellen: Anlegen | `fracht.createTable`, vorhandener Seiten-Callback |
| Frachttabellen: Position | `fracht.addPosition`, vorhandener Seiten-Callback |

Die drei lokalen Formular-/Berechnungs-Callbacks sind explizit fuer Agenten
gesperrt. Sie sind menschliche Seitenbefehle mit vorhandenem Formularkontext;
es wurden keine fingierten API-Endpunkte oder Generik-Erfolgsmeldungen eingefuehrt.
Die fuenf Navigationsziele entsprechen exakt den committeten Seitenhandlern.

`SEITENAKTIONEN_OHNE_BEFEHL` und seine acht Ausnahmen sind entfernt. Das
Inventurgate prueft diese Aktionen jetzt ohne Ausnahme. Die beiden echten
Fachluecken in `BEKANNTE_LUECKEN` bleiben unveraendert beim anderen Fachowner.

## Abnahme

- Inventurgate gruen fuer 99 native ScreenDefinitions, noch zwei echte Fachluecken.
- 791 bestehende Backend-/Safety-/SPEC-/Tourvertraege bestanden ohne Skip (4,45 s).
- 33 Frontendpruefungen bestanden (1,99 s), einschliesslich eines direkten
  Sprachgrenzen-Abgleichs der acht Aktionen: echte Python-Builder gegen echte
  TypeScript-Fallbacks; keine nachgebauten Erwartungsstrings.
- Fuenf Handbuchartefakte regeneriert und mit `--check` aktuell.
- TypeScript `--noEmit` auf der isolierten committed Frontendquelle plus eigenen
  Fallback-Hunks Exit 0.
- Godfile-Gate unveraendert gruen, keine Baseline erhoeht.

Die erste Zuordnung traf wegen identischem Beschreibungstext die Fahreraktion
statt der Tour-Fracht-Aktion. Das strengere Inventurgate hat den Fehler erkannt;
der eigene falsche Hunk wurde korrigiert. Die abschliessende Diffpruefung betrifft
genau die acht beanspruchten Aktionen. Kein fremder Hunk zurueckgesetzt.

Keine Fachmutation, DB, neuer Container, Migration oder Reset fuer diese
Deklarationsabnahme. Neue GitHub-Abnahme erforderlich; die Browser- und
Persistenznachweise der bereits bestehenden Fachhandler werden dadurch nicht ersetzt.
