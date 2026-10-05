---
title: Geschaeftstag fuer fachliche Demo- und Fallback-Daten
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis lokaler Tagesgrenzen in OCR, ATLAS und Compliance-Trend.
---

# Geschaeftstag fuer fachliche Demo- und Fallback-Daten

Der OCR-Fallback setzt ein fehlendes Rechnungsdatum auf `business_today()`.
ATLAS erzeugt das MRN-Jahr und simulierte Ausgangsdatum aus demselben
Geschaeftstag. Die simulierte Compliance-Trendserie endet am Geschaeftstag.

Technische Felder wie `processed_at`, `erledigt_am`, Laufzeiten und geplante
Ausfuehrungszeitpunkte bleiben UTC-Zeitpunkte.

## Nachweis

`pytest tests/test_business_time_demo_placeholders.py tests/test_business_time.py tests/test_einkauf_ocr_invoice_unit.py tests/test_service_units_wave73.py -q --no-cov`

**31 Tests bestanden.** Die Regressionstests erzwingen am Jahreswechsel einen
Geschaeftstag, der vom UTC-Datum abweicht, und pruefen fachliches Datum und
technischen Zeitstempel getrennt.

