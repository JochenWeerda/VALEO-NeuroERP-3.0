---
title: Self-Billing M3-Konsolidierung
status: in arbeit
type: reference
owner: Cursor Cloud
last_reviewed: 2026-11-27
---

# Self-Billing M3 — Konsolidierung

Kanonischer kreditorischer Buchungsweg über `buche_eingangsrechnung` (posted, Personenkonto, ein OP). DocFlow `purchase_invoice` (source `self_billing`) ist führend; `domain_finance.self_billing_invoices` ist Agrar-Erweiterung. Steuerauflösung multi-param; fehlendes Lieferantenprofil und fehlende Selbstfakturierungsvereinbarung (`self_billing_purchase`) blockieren endgültige Ausstellung mit HTTP 422. API-Buchung ist Adapter ohne Freigabe-Umgehung.

## Nachweise

- Contract: `tests/test_self_billing_accounting_contract.py`, angepasste Fälle in `tests/test_posting_services.py`
- Verhalten/Skip: `tests/test_self_billing_m3_verhalten.py`
- Handshake: `docs/agent-ops/handshakes/cursor-self-billing-atomic-m3-20261127.md`

## Offen für CI/Prüfstand

Vollständige HTTP/PostgreSQL-Fälle der Lead-Zusatzliste (concurrent, Jahreswechsel, Storno nach Satzwechsel, bezahlter OP, keine Doppel-WE) auf `valeo_probe` nach Migration.
