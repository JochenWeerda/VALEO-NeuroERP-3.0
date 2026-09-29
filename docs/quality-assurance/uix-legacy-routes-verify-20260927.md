---
title: UIX Legacy-Routen Revalidierung
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-27
description: Revalidierung der nativen Detailrouten und ihres blockierenden CI-Gates.
---

# UIX Legacy-Routen Revalidierung

Der Gap-Tracker fuehrte das Umhaengen bestehender `:id`-Routen weiterhin als
offen, obwohl UIX-051 im Runtime-Status bereits abgeschlossen war. Der aktuelle
Vertrag wurde deshalb erneut gegen Wrapper-Dateien, `screenId` und Route-Aliase
geprueft.

## Nachweis

`pytest tests/test_uix051_legacy_route_migration.py -q --no-cov`

**49 Tests bestanden.** Die erwarteten nativen Wrapper existieren, verwenden die
richtige ScreenDefinition und alle 26 migrierten Detailmasken besitzen ihre
festgelegte `/:id`-Route. Der Test ist in `.github/workflows/universal-mask-ci.yml`
als eigener Schritt ohne `continue-on-error` verdrahtet.

Die gleichzeitig im Arbeitsbaum liegende, fremde CRM-Routenergänzung wurde weder
uebernommen noch veraendert. Dieser Slice aendert keine Runtime-Datei.
