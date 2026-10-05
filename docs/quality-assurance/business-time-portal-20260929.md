---
title: Geschaeftstag der Portal-Shop-Tagesstatistik
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis der lokalen Tagesgrenze fuer Orders Observability.
---

# Geschaeftstag der Portal-Shop-Tagesstatistik

`GET /orders/observability` wertet die Kennzahl `today` jetzt mit dem zentralen
`business_today()` aus. Damit entspricht die Tagesgrenze der konfigurierten
`BUSINESS_TIMEZONE` und faellt im deutschen Standard nicht kurz nach Mitternacht
auf den vorherigen UTC-Tag zurueck.

## Nachweis

`pytest tests/test_portal_shop_business_time.py tests/test_business_time.py -q --no-cov`

**10 Tests bestanden.** Der Regressionstest setzt bewusst ein lokales Datum und
prueft dieses als Bindewert des SQL-Tagesfilters. Wochenfenster, technische
Zeitstempel und Bestellnummern sind nicht Bestandteil dieser Aenderung.
