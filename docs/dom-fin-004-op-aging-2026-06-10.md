# DOM-FIN-004 — Offene Posten / OP-Aging (2026-06-10)

Sprint-Ziel: FIBU-Tiefe (Abschluss, Storno, OP, Steuer, DATEV). Erster Slice
(004.1): **OP-Aging-Cockpit** — der in-repo verifizierbare Teil (Mahnwesen/
Zahlungsdisposition); Abschluss/DATEV bleiben extern gegated.

## Slice 004.1 — OP-Aging-Cockpit (umgesetzt, read-only)
- Service: `app/services/finance_op_service.py`
  - `aging_bucket(faelligkeit, today)` — **reine** Einstufung: nicht fällig /
    1–30 / 31–60 / 60+ (testbar).
  - `list_open_items(typ)` — offene Posten (COALESCE offen/open_amount/betrag > 0,
    nicht storniert) je Konto-Typ; pro OP Bucket, Überfälligkeit, Mahnstufe
    (`dunning_level`), aktives Skonto-Fenster; Summen je Bucket + Überfällig-Summe.
- API: `GET /finance/offene-posten?typ=debitor|kreditor|alle`.
- Seed: `scripts/seed_demo_finance.py` (idempotent, Präfix `DEMO-RE-`) — 4 OP:
  überfällig 1–30 (Mahnstufe 1), nicht fällig + Skonto, Kreditor, überfällig 60+
  (Mahnstufe 2).
- Frontend: `pages/finance/offene-posten-cockpit.tsx` (Aging-Summen-Kacheln +
  Tabelle mit Mahnstufe/Skonto, überfällige hervorgehoben) + Hooks
  `lib/api/finance-op.ts` + Nav „OP-Cockpit (Aging)" + Route-Alias.
- Tests: `tests/test_finance_op.py` (6 grün).

### Verifiziert (Seed-Daten)
4 OP, Summe offen 10.400 €, überfällig 5.800 €; Buckets nicht_faellig (2/4.600),
1-30 (1/5.000), 60+ (1/800); Mahnstufen + Skonto korrekt erkannt.

## Folge-Slices (teils extern gegated)
- **004.2** Mahnlauf (dunning_notices/-rules) erzeugen + Mahnstufen-Eskalation.
- **004.3** OP-Auszifferung/Zahlungseingang (op_auszifferungen) + Zahlungslauf.
- **004.4** Abschluss/Periodensteuerung, Storno-Konsistenz.
- **004.5** DATEV-Export + Steuerberater-Cutover (extern) + UAT.
