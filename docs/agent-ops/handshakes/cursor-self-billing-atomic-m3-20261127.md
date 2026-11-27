# Handshake: SELF-BILLING-ATOMIC-M3-KONSOLIDIERUNG

**Von:** Cursor Cloud (Claim-Owner)  
**An:** Lead / Claude (Admin-Merge); Codex (zur Kenntnis — Slice war nicht aktiv)  
**Datum:** 2026-11-27 (Europe/Berlin)  
**Plan:** Agent-Store `/cursor/stores/bc-09bb92a0-aa51-4a65-9673-4842242a5460/docs/self-billing-atomic-plan.md`

## Claim

- Slice `SELF-BILLING-ATOMIC-M3-KONSOLIDIERUNG` reserviert im Active Workboard.
- Historischer Slice `SELF-BILLING-ATOMIC-20261014` bleibt abgeschlossen.
- Branch: `cursor/self-billing-atomic-m3-34fe`

## Lieferung P0

- Kanonischer Kern `app/services/self_billing_buchung.py` → `buche_eingangsrechnung` (posted + Personenkonto + OP).
- DocFlow führend: `app/services/self_billing_docflow.py` (`purchase_invoice`, source `self_billing`); `SelfBillingInvoice` = Agrar-Erweiterung (`docflow_header_id`, `journal_entry_id`, `taxation_type`, `tax_context`).
- Multi-Parameter-Steuer in `tax_profile_service.py`; fehlendes Profil → 422; Entwürfe ok.
- Vereinbarung: `business_partner_billing_configs.self_billing_purchase` (Tab 24).
- Erntefreigabe endgültig nutzt Kern; vorläufig unverändert ohne endgültige Buchung.
- API `…/buchung` nur Adapter (keine Freigabe-Umgehung); Legacy `Buchung`/1600/4200 entfernt.
- Storno: Original-`taxation_type` / Journal-Reverse; Preview mandantengebunden.
- Migration `self_billing_m3_konsolidierung_20261127` (Unique-Indexes Idempotenz).
- E-Rechnung Typcode 389 vorgezogen (P1-Anteil, produktionsrelevant).

## Tests

- `tests/test_self_billing_accounting_contract.py` — erweitert (Profil 422, Vereinbarung, Resolver §24, Kern-Idempotenz).
- `tests/test_posting_services.py` — Self-Billing-Fälle auf Kern umgestellt.
- `tests/test_self_billing_m3_verhalten.py` — Integration/Skip ohne Prüfstand + 389-Vertrag.

Lokal in dieser Cloud-VM: kein Postgres/Docker — SQL-Verhaltenstests skippen bis CI/`valeo_probe`. Contract-Mocks sind die Primärnachweise hier; CI muss Migration + Suite fahren.

## CI-Nachzug (Head nach b35a57138)

3. Tabellenkatalog-Drift nach Migration: `docs/admin/table-catalog.{json,md}` aus frischem Schema (CI-Artifact / `generate_table_catalog.py`).

## CI-Nachzug (Head nach ac3a23afa)

1. Domain-Mapping: `self_billing_buchung` → finance, `self_billing_docflow` → dms-compliance, `self_billing` → agrar (`exact_service_stems` + Index-Regen).
2. Studio grain.v1: Freigabe bucht bereits (`booked` + Journal posted) — Simulation akzeptiert gebuchten Status, postet Drafts nur nach; ORM nach Raw-SQL-Update refreshen.

## Merge

CI am Head abwarten → **Claude Admin-Merge** („bereit zum Merge, Head \<sha\>”). Kein Self-Merge.
