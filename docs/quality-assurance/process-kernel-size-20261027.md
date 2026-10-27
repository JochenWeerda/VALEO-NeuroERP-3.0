---
title: Process-Kernel-Groessenratsche nach RLS-Integration
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# Neue CI-Groessenregression behoben

Quality Gate 40488618550 meldete process_kernel_api.py mit 6110 statt maximal
6108 Zeilen. Die RLS-Kontextimporte hatten den Grenzwert ueberschritten.
Die bestehende Aufbereitung oeffentlicher Datenqualitaets-Regelsets liegt nun
in app/api/v1/schemas/data_quality_output.py. Der Router importiert dieselbe
Funktion unter seinem bisherigen lokalen Namen; Routen, Antworten und
Mandanten-/Rechtepruefungen bleiben unveraendert. Keine Baseline angehoben.

17 gezielte Faelle bestanden: oeffentliche Regelsets behalten die fachlichen
Felder, geben weder format_regex noch unique_felder aus und veraendern nicht
die Quelldefinition. Die Groessenratsche besteht wieder.

Ein breiterer isolierter Lauf der alten Wave31-Tests ergab 62 bestanden und
12 fehlgeschlagen: Die HTTP-Faelle der Testanwendung hatten ohne globalen
Conftest keinen authentifizierten Mandanten und wurden mit 400/401 abgelehnt.
Daraus wird kein erfolgreicher HTTP-/Integrationsnachweis behauptet. Die
gezielte Formatterabnahme ruft den tatsaechlichen Endpoint direkt auf;
sie prueft die Ausgabegrenze und ersetzt keinen Authentifizierungstest.
