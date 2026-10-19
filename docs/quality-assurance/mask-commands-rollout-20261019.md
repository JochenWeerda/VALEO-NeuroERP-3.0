# Maskenaktionen als Kommando-Weg (MASK-COMMANDS-ROLLOUT-20261019)

Ziel: jede Maskenfunktion per Maske, CLI und MCP ueber denselben Fachweg. Maskenweise, ein Commit je Schritt.

## Schritt 1: Belegkontrolle (4 Masken)

`auswertungen/beleg-kontrolle` und die gespeicherten L3-Sichten `auswertungen/auftrags-kontrolle`,
`auswertungen/lieferschein-kontrolle`, `abrechnung/eb-lieferschein-kontrolle` (gleiche Zeilenaktionen).

- Neuer Kommando-Endpunkt `POST /api/v1/document-control/exceptions/{entity_id}/actions/{assign_me|start_work|resolve|waive}`
  ueber `run_delegated_mask_action`: Begruendung Pflicht, Trockenlauf prueft Fall, Mandant und Statusuebergang
  gegen die Datenbank, Wiederholung mit demselben Schluessel wirkt einmal. Delegiert an
  `DocumentControlService.assign`/`transition`.
- ScreenDefinition: die vier Aktionen tragen `commandEndpoint`; `waive` zusaetzlich `humanApprovalRequired`
  (Agenten bleiben gesperrt); `open_source` ist `localEffect: navigation`.
- Seite `DocumentControlScopePage` ruft nur noch den Kommando-Weg, wertet `success=false` als Fehler und
  sperrt Doppelausfuehrung je Fall und Aktion. `beleg-kontrolle.tsx` nutzt dieselbe Seite statt einer Kopie.

### Sicherheitsbefund und Korrektur

Die bestehenden Wege `/exceptions`, `/project`, `/assign`, `/transition` nahmen den Audit-Urheber aus dem
Client-Header `X-User-ID` (sonst `document-control-operator`); die Seite setzte als Zustaendigen die Zeichenkette
`current-user`. Jeder Schreibberechtigte konnte so Audit-Eintraege unter fremdem Namen erzeugen. Urheber und
Zustaendiger kommen jetzt aus dem geprueften Token; ohne `sub` antwortet der Weg 403.

## Nachweis

- `tests/test_document_control_mask_commands.py` (8, gegen `valeo_probe`): Bearbeiter aus Token trotz
  gefaelschtem Kopf, Trockenlauf schreibt nichts, Wiederholung wirkt einmal, abgeschlossener Fall kein Erfolg,
  Begruendung Pflicht, fremder Mandant findet den Fall nicht, unbekannte Aktion 422, alle vier Masken zeigen
  auf den Kommando-Weg.
- Zusammen mit Projektion und Rollenvertrag 711 gruen; angrenzende MCP-/CLI-/Katalog-/Inventarsuiten 185 gruen.
- Vitest `beleg-kontrolle.test.tsx` 3 gruen (Kommando-Weg, Ablehnung kein Erfolg, keine Doppelausfuehrung);
  ESLint und volle `tsc` ohne Befund in den Dateien.
- Neu erzeugt: OpenAPI, Architekturindex, CLI-Register (153 Aktionen, vorher 137), Inventar und Ratsche
  (`aktionen_nicht_deklariert` 119 -> 99). Gates Kommando-Inventar, MCP-REST-Bindungen, Architektur-Drift gruen.
