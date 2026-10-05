---
title: Geschaeftstag fuer HR-Retention und Zeitfunktionen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis einheitlicher lokaler HR-Tagesgrenzen.
---

# Geschaeftstag fuer HR-Retention und Zeitfunktionen

HR-Retention, Fahrerzeit, Zeitcockpit, datumslose Ausgaben und manuelle
Arbeitszeitkorrekturen verwenden jetzt `business_today()`. Explizite Datumswerte
und technische Ereigniszeitpunkte bleiben unveraendert.

## Nachweis

`pytest tests/test_personal_business_time.py tests/test_business_time.py tests/test_personal_driver_time_api.py tests/test_personal_time_cockpit_api.py -q --no-cov`

**16 Tests bestanden.** Die Tests erzwingen einen lokalen Geschäftstag, der vom
UTC-Datum abweichen kann, und prüfen Fallbacks sowie Fahrerzeit-Endpunkte.
