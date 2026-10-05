---
title: AgentMaskContract-Gate fuer alle nativen Masken
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-27
description: Registry-weite Abnahme von Agentenvertrag und Generator-Readiness.
---

# AgentMaskContract-Gate fuer alle nativen Masken

Der bisherige Test belegte Vertrag und Readiness an wenigen Beispielmasken.
Das neue Ratchet iteriert die zentrale `SCREEN_DEFINITION_BUILDERS`-Registry und
prueft jede nicht temporaere ScreenDefinition. Damit werden neue native Masken
automatisch aufgenommen; eine handgepflegte Maskenliste entfaellt.

Pro Maske werden die richtige `screenId`, ein fachlicher Zweck, die Aktionsliste,
ein stabiler Root-Selektor und `generatorReady=True` verlangt. Zusaetzlich darf
der Bestand nicht unter 71 native Masken fallen. Das Gate ist als eigener,
blockierender Schritt in `universal-mask-ci` verdrahtet und wird bei Aenderungen
am Test oder an den ScreenDefinitions ausgeloest.

## Nachweis

`pytest tests/test_agent_mask_contract.py -q --no-cov -m unit --tb=short`

**25 Tests bestanden.** Der Registry-Test hat alle **71 nativen
ScreenDefinitions** ohne Vertrags- oder Readiness-Befund geprueft.

Architektur-Impact: nur ein zentrales CI-Ratchet; keine neue Runtime,
Domaenengrenze, Route oder Persistenz.
