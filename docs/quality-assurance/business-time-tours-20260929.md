---
title: Geschaeftstag fuer Heute-Touren
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis der lokalen Tagesgrenze fuer den Touren-Heute-Endpunkt.
---

# Geschaeftstag fuer Heute-Touren

`GET /tours/today` uebergibt jetzt den zentral ermittelten `business_today()` an
das TourRepository. Der Endpunkt mischt damit keinen ungenutzten UTC-Tag mehr mit
dem Datum der Windows- oder Container-Hostzeitzone.

## Nachweis

`pytest tests/test_tours_business_time.py tests/test_business_time.py -q --no-cov`

**10 Tests bestanden.** Der Regressionstest setzt einen lokalen Tag explizit und
prueft den exakten Repository-Parameter. Wochenfilter und Tourzeitpunkte bleiben
unveraendert.
