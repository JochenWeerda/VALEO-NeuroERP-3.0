---
title: Finance — Tests
type: reference
audience: [qa, entwickler]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance — Tests

eBilanz: `tests/test_ebilanz_xbrl_draft.py` und
`tests/test_ebilanz_honest_persistence.py`; 49 Katalog-/XML-/HTTP-/PostgreSQL-
Vertraege. Gemeinsamer Pruefstand mit eigenen Transaktionen/Savepoints, keine
neue Datenbank. [Abnahme und Grenzen](../../../quality-assurance/ebilanz-xbrl-draft-20261008.md).

Rechnungstapel: `pytest tests/test_billing_batch.py -q --no-cov` und
`vitest run src/__tests__/pages/finance/rechnungstapel.test.tsx`.

Abfrage-Center: `pytest tests/test_query_center.py -q --no-cov` und
`vitest run src/__tests__/pages/auswertungen/abfrage-center.test.tsx`.

```bash
pytest tests/ -k "finance or fibu or ap_invoice or closing" -m "not slow"
```

Frontend: `packages/frontend-web/src/pages/finance/`, `fibu/`, `meldewesen/`, `pos/`

E2E: Playwright Finance/FiBu-Flows in `tests/e2e/`

L3-Berichte, Bonus und Kontrollsichten:
`pytest tests/test_l3_report_catalog.py tests/test_document_control.py -q --no-cov`.

## Bankmodell-Retirement

tests/test_bank_legacy_retirement.py prueft die tatsaechliche Router-Montage,
Entfernung der DTOs und aller produktiven Altspeicher-Verweise. PostgreSQL-
Vertraege pruefen leere/belegte Alttabellen, unveraenderte kanonische Auszuege
und OP-Reste, Abbruch bei unvollstaendigem Schema und unbekannten
Abhaengigkeiten, Transaktionsrollback und explizit irreversiblen Downgrade.
Ein eigenes kleines Schema auf vorhandenem valeo_probe, gezieltes Cleanup;
keine neue Testdatenbank/Dockerinstanz und kein gemeinsam genutzter Reset.
Bestehende Import-/Replay-/Zahlungsvertraege bleiben verbindlich.

## Zahlungslauf: belegte Vier-Augen-Freigabe

25 neue Guard-/HTTP-Vertraege in tests/test_payment_run_approval_evidence.py,
sechs bestehende Payment-API-Vertraege und fuenf echte PG-Vertraege in
TestZahlungslauf: insgesamt36 ohne Skip gruen. Fehlende Identitaetsnachweise
werden in allen Modi gesperrt; Tenant, Rowlock, Rollen und atomare Wirkung
bleiben erhalten. Bestehender gemeinsamer valeo_probe, nur eigene Testdaten,
keine Migration oder Ruecksetzung. [QA/Handshake](../../../quality-assurance/payment-run-evidence-20261008.md).
