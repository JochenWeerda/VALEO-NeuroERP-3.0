---
title: Self-Billing M3-Konsolidierung
status: in arbeit
type: reference
owner: Cursor Cloud
last_reviewed: 2026-11-27
---

# Self-Billing M3 — Konsolidierung

Kanonischer kreditorischer Buchungsweg über `buche_eingangsrechnung` (posted, Personenkonto, ein OP). DocFlow `purchase_invoice` (source `self_billing`) ist führend; `domain_finance.self_billing_invoices` ist Agrar-Erweiterung. Steuerauflösung multi-param; fehlendes Lieferantenprofil und fehlende Selbstfakturierungsvereinbarung (`business_partner_billing_configs.self_billing_purchase`) blockieren endgültige Ausstellung mit HTTP 422. API-Buchung ist Adapter ohne Freigabe-Umgehung. Freigabe setzt Beleg-VAT aus dem kanonischen Resolver (Align zu §24/§19/Kleinunternehmer).

## Nachweise

- Contract: `tests/test_self_billing_accounting_contract.py`, angepasste Fälle in `tests/test_posting_services.py`
- PostgreSQL Lead-Auftrag A: `tests/test_self_billing_m3_verhalten.py` (`needs_live_db`)
  - Besteuerung 7 % / 19 % / §24 / §19 Kleinunternehmer + Bundle (DocFlow, Journal, OP, Personenkonto, Cent, Bestand)
  - Jahresgrenze Profil + historischer Steuerschlüssel
  - Zwei PostgreSQL-Sessions (Concurrent)
  - Storno nach Profilwechsel (Original-`tax_context`)
  - API-Umgehung Freigabe → 422; Create ohne Freigabe ohne Journal
  - Mandantentrennung Lese-/Schreibpfade
  - E-Rechnung Typ 389 + EN16931-Mindest-UBL; drafthorse `type_code=389`
- Handshake: `docs/agent-ops/handshakes/cursor-self-billing-atomic-m3-20261127.md`

## Offen / Rest

KoSIT-/Schematron-Vollvalidierung gegen offizielle Regeln bleibt P1-Erweiterung (Generator-Fallback ist strukturell geprüft; drafthorse-Serialize-Vollschema flaky).
