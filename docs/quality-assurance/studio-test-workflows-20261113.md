---
title: Studio-Testmigration der Flow-Spine-Prozessraeume
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Studio-Testmigration der Flow-Spine-Prozessraeume

Zwoelf erwartete Fehlschlaege aus neun alten Seitentests wurden durch dreizehn
Verhaltenstests in `flow-spine-workspaces.test.tsx` ersetzt. Die neun echten
Prozessseiten laden je ihre Backend-ScreenDefinition, den Compiler, die
Runtime und den Renderer; ein synthetischer HTTP-Rand liefert die Prozessdaten.
Die Tests pruefen fuer jede Prozesskennung den richtigen Endpunkt, Titel,
Knoten, Statuswert und Hinweis. Fuer die gemeinsame Prozessaktion pruefen sie
HTTP 403 und 409 ohne Navigation oder Erfolgsmeldung, erfolgreiche Ausfuehrung
vor Navigation und reine Navigation ohne POST. Die bestehenden Tests fuer
Ansichtsmodi, Fusslinks und Katalog bleiben ergaenzend erhalten.

Die Fixture `src/__tests__/fixtures/flow-spine-workspaces-studio.json` wurde aus
`app.core.screen_definitions_domain_batch15._build_flow_spine_workspace` fuer
die neun Schluessel erzeugt; die neun oeffentlichen Builder rufen diese Funktion
auf. Der Lead prueft die Fixture gegen diese oeffentlichen Builder auf Drift.
HTTP, Navigation, Toast und der in jsdom fehlende EventSource sind Testgrenzen;
die Runtime und ihre Prozessdarstellung sind nicht ersetzt. Die Daten sind
synthetisch. Die Ablehnungen zeigen die Reaktion auf eine simulierte
Serverentscheidung, sie beweisen keine Rollen- oder Mandantenpruefung.

Gezielter Vitest-Lauf am 13.11.2026 mit hoechstens zwei Workern: **13/13
bestanden**, Dauer 38,45 s (Tests 3,86 s). Der vorherige Lauf hatte wegen des
Lazy-Imports beim ersten Test das einsekundige Wartefenster ueberschritten;
das Wartefenster wurde auf zehn Sekunden erhoeht. Keine Datenbank, kein Build
und keine Gesamtsuite. Angemeldete Browser- und reale Backend-/Berechtigungs-
und Prozesskettenabnahme bleiben separat erforderlich.
