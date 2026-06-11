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

## Slice 004.2 — Mahnlauf + Mahnstufen-Eskalation (umgesetzt, 2026-06-11)
- Service: `app/services/finance_dunning_service.py` — reine Logik
  `days_based_level`/`next_dunning_level` (Eskalation gedeckelt bei 3) +
  `compute_dunning` (Gebühr + anteilige Zinsen p.a. + Gesamt). `candidates()`
  (überfällige Debitoren-OP aus `domain_erp.offene_posten` + nächste Stufe/Beträge),
  `run_dunning()` (erzeugt `dunning_notices` + eskaliert `dunning_level`),
  `list_notices()`. Regeln aus `domain_erp.dunning_rules`; ist die Tabelle leer
  (DEV-Stand), greifen konservative Default-Regeln (Stufe 1/2/3: 5/10/20 € Gebühr,
  0/5/8 % p.a., Frist 14/10/7 Tage).
- API: `GET /finance/mahnlauf/candidates`, `GET /finance/mahnlauf/notices`,
  `POST /finance/mahnlauf/run`.
- Frontend: `pages/finance/mahnlauf.tsx` (Kandidaten + „Mahnlauf ausführen" mit
  Mutation-Guard + Mahnungs-Liste) + Hooks `lib/api/finance-dunning.ts` + Nav
  „Mahnlauf" + Route-Alias.
- Tests: `tests/test_finance_dunning.py` (5 grün, reine Mahnlogik).

### Verifiziert (Live, mit Restore)
DEMO-RE-103 (76 Tage, Stufe 2→3, Zins 13,33 €, Gesamt 833,33 €); DEMO-RE-100
(15 Tage, Stufe 1→2, Zins 10,27 €, Gesamt 5.020,27 €). Mahnlauf erzeugt 2 Mahnungen
+ eskaliert Stufen; Restore ok.

## Slice 004.3 — Zahlungseingang / OP-Auszifferung (umgesetzt, 2026-06-11)
- Service: `app/services/finance_clearing_service.py` — reine `clearing_result`
  (Ausgleich = Zahlung + Skonto, Restsaldo, voll/teil, Überzahlung) +
  `record_payment` (zifferung gegen `domain_erp.offene_posten`: reduziert `offen`,
  setzt `op_status='ausgeziffert'` bei Vollausgleich; protokolliert
  `domain_shared.op_auszifferungen`) + `clearings`. Guard: Überzahlung → 422.
- **Schließt Lücke**: die vorhandene `op_skonto_auszifferung.py` schrieb nur
  `op_auszifferungen`, reduzierte aber den OP-Saldo im Aging-Cockpit nicht.
- Kreditoren-Zahlungslauf (SEPA) ist bereits via `payment_runs.py` abgedeckt
  (nicht dupliziert).
- API: `POST /finance/zahlungseingang`, `GET /finance/zahlungseingang/clearings`.
- Frontend: `pages/finance/zahlungseingang.tsx` (offene Debitoren-OP-Picker +
  Zahlungs-/Skonto-Formular + Auszifferungs-Historie) + Hooks
  `lib/api/finance-clearing.ts` + Nav „Zahlungseingang / Auszifferung" + Route.
- Tests: `tests/test_finance_clearing.py` (5 grün).

### Verifiziert (Live, mit Restore)
DEMO-RE-100 (5.000): Teilzahlung 2.000 → offen 3.000 (teilausgleich); Rest 2.900 +
100 Skonto → offen 0, op_status „ausgeziffert"; erneute Zahlung → 422.

## Slice 004.4 — Periodenabschluss + Storno-Konsistenz (umgesetzt, 2026-06-11)
- Service: `app/services/finance_period_service.py` — reine `period_bounds`
  ('YYYY-MM'→Monatsgrenzen) + `close_readiness` (offene + Storno-inkonsistente
  Posten blockieren). `list_periods` (aus `finance_accounting_periods`, leer →
  aus OP-Rechnungsmonaten abgeleitet, self-contained), `readiness`, `close_period`
  (Guard: nur abschlussreif, `force` erzwingt), `reopen_period` (Pflicht-Grund,
  in `metadata` protokolliert).
- Storno-Konsistenz: OP mit `op_status='storniert'` aber `offen > 0` blockieren
  den Abschluss.
- API: `GET /finance/perioden`, `GET /finance/perioden/{p}/readiness`,
  `POST /finance/perioden/{p}/close`, `POST /finance/perioden/{p}/reopen`.
- Frontend: `pages/finance/periodenabschluss.tsx` (Perioden + Reife + Abschließen/
  Erzwingen/Öffnen, Reopen-Dialog) + Hooks `lib/api/finance-period.ts` + Nav + Route.
- Tests: `tests/test_finance_period.py` (5 grün).

### Verifiziert (Live, mit Restore)
2026-06 (2 offene OP) → Abschluss 422 „nicht abschlussreif"; Force-Abschluss ok;
erneut → 422 „bereits abgeschlossen"; Reopen ok.

## Folge-Slices (teils extern gegated)
- **004.5** DATEV-Export + Steuerberater-Cutover (extern) + UAT.
