---
title: Pagination-Ratchet auf Schwelle 53 wiederhergestellt
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Ursachenanalyse und Abnahme des Pagination-Rueckfalls von 55 auf 53 Dateien.
---

# Pagination-Ratchet wiederhergestellt

## Befund

Der Backend-Quality-Gate erwartete hoechstens 53 Dateien mit unbegrenztem
`.all()`, der aktuelle Stand enthielt 55. Der Vergleich mit dem letzten gruenen
Stand isolierte genau zwei neu hinzugekommene Dateien:

- `crm_consents.py` enthielt drei echte Listen-Endpunkte ohne Begrenzung.
- `document_allocations.py` liefert ein vollstaendiges Belegaggregat. Eine
  Teilseite wuerde Gesamtmenge und offene Menge fachlich falsch berechnen.

## Umsetzung

Die drei Consent-Listen akzeptieren nun `skip` ab 0 und `limit` von 1 bis 1000
mit einem Standard von 100. Sortierung und Mandantenfilter bleiben erhalten;
die Begrenzung wird direkt auf die Datenbankabfrage angewendet.

`document_allocations.py` ist im Gate mit der fachlichen Begruendung als
Vollaggregat ausgenommen. Die Ausnahme hebt die globale Schwelle nicht an und
wird durch einen Vertragstest abgesichert.

## Nachweis

- `python scripts/check_pagination.py --threshold 53`: Exit 0, genau 53 Dateien.
- `pytest tests/test_pagination_contract.py -q --no-cov`: 34 Vertragstests.
- `python -m py_compile app/api/v1/endpoints/crm_consents.py scripts/check_pagination.py tests/test_pagination_contract.py`: Exit 0.

Die Schwelle bleibt 53. Weitere Bereinigungen muessen sie senken oder den
Bestand mindestens unveraendert lassen.
