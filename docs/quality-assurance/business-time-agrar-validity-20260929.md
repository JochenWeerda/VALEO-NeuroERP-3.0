---
title: Geschaeftstag fuer Agrar-Zulassungen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis einheitlicher lokaler Tagesgrenzen fuer Agrar-Zulassungen.
---

# Geschaeftstag fuer Agrar-Zulassungen

PSM-, Saatgut- und Duenger-Stammdaten pruefen abgelaufene Zulassungen jetzt
gegen `business_today()`. Der PSM-Statistikendpunkt berechnet den heutigen Tag
und das 90-Tage-Fenster aus derselben Tagesgrenze. Die als `datetime`
transportierten Zulassungswerte werden fuer die fachliche Pruefung auf ihr
Kalenderdatum reduziert.

Technische Synchronisations- und Auditzeitpunkte bleiben UTC-Zeitpunkte.

## Nachweis

`pytest tests/test_agrar_business_time.py tests/test_business_time.py -q --no-cov`

**16 Tests bestanden.** Sechs Schreibpfade werden gegen einen explizit gesetzten
Geschaeftstag geprueft. Der Statistiktest weist den Stichtag und den 90-Tage-
Grenzwert als gebundene Abfragewerte nach.

