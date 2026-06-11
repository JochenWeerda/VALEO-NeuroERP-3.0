# DOM-CON-004 — Kontrakte / Erfüllungsstand (2026-06-10)

Sprint-Ziel: Kontrakt-Tiefe (Fixierung, Marktwert, Engagement, Liefer-/Abnahme-
verpflichtung, Kontraktmahnung). Erster Slice (004.1): **Erfüllungsstand** —
kontrahiert vs. abgerufen, mit Status/Lücken.

## Ist-Befund
`domain_ops.kon_contract` (+ `_line` + `_movement`) modelliert Kontrakt → Position
→ Abrufe/Bewegungen — ideal für den Erfüllungsstand. (Bestandsdaten lagen unter
einem Test-Tenant → DEMO-Seed unter Dev-Tenant ergänzt.)

## Slice 004.1 — Erfüllungsstand (umgesetzt, read-only)
- Service: `app/services/contract_fulfillment_service.py`
  - reine `fulfillment_status(qty, abgerufen, allow_over)` — offen/teilerfüllt/
    erfüllt/übererfüllt (+ Abweichung bei Übererfüllung ohne Erlaubnis).
  - `detail(kontrakt)` — Positionen (kontrahiert vs. abgerufen aus Bewegungen),
    offen, Erfüllungs-%, Pricing (Prämie/Mindestpreis/MATIF), Lücken (überfällig
    untererfüllt; Übererfüllung); `list_contracts(typ)` (Picker mit Balken).
- API: `GET /contracts/fulfillment?kontrakt=…` + `/contracts/fulfillment/list`.
- Seed: `scripts/seed_demo_contracts.py` — DEMO-KT-001 teilerfüllt (120/200),
  DEMO-KT-002 überfällig (40/100), DEMO-KT-003 erfüllt (50/50).
- Frontend: `pages/agrar/kontrakt-erfuellung.tsx` (Picker mit Erfüllungs-Balken +
  Positions-Tabelle + Pricing + Lücken) + Hooks `lib/api/contract-fulfillment.ts`
  + Nav „Kontrakt-Erfüllung" + Route-Alias.
- Tests: `tests/test_contract_fulfillment.py` (6 grün).

### Verifiziert (Seed)
DEMO-KT-001 60% teilerfüllt; DEMO-KT-002 40% + überfällig (Lücke); DEMO-KT-003 100% erfüllt.

## Slice 004.2 — Fixierungs-Arbeitsraum + MATIF-Bewertung (umgesetzt, 2026-06-11)
Teilfixierung MATIF-bepreister Kontrakte (Schreibvorgang) + Mark-to-Market gegen
Marktnotierung.
- Migration `con_fixing_matif_20260611` — **zugleich Head-Merge** (die zwei offenen
  Abend-Heads `repair_customer_contract_20260610` + `sales_o2c_link_20260610` wurden
  nie zusammengeführt → `init_db.py upgrade head` (Singular) scheiterte → Backend-
  Crash-Loop; behoben). Neue Tabellen `domain_ops.kon_contract_fixing` (append-only,
  storno-fähig via `is_storniert` für 004.4) + `domain_ops.matif_quote` (Notierung
  je Symbol/Datum, unique).
- Service `app/services/contract_fixing_service.py`:
  - reine, testbare Bewertung: `effektiv_preis` (MATIF+Prämie), `restmenge`
    (offen zu fixieren, nie negativ), `mtm_fixiert` (Vorzeichen: Einkauf=unter Markt
    gut, Verkauf=über Markt gut), `marktwert_offen`.
  - `create_fixing` (Guards: nur MATIF-Position, Menge>0, ≤ offen, Preis>0),
    `workspace` (je Position fixiert/offen/Ø-Fixpreis/Notierung/Bewertung),
    `upsert_quote`, `list_fixings`. Fail-closed: ohne Notierung keine Bewertung.
- API: `GET /contracts/fixing/workspace`, `GET /contracts/fixing/list`,
  `POST /contracts/fixing`, `POST /contracts/matif-quote`.
- Seed: DEMO-KT-004 (MATIF-Verkauf, 300/500 t fixiert, Ø effektiv 220,33; Notierung
  208 + Prämie 12 → Markt 220) → Bewertung fixiert +99,99 €, offener Marktwert
  44.000 €.
- Frontend: `pages/agrar/kontrakt-fixierung.tsx` (Picker + Summen-Kacheln + Positions-
  tabelle mit Fixierungsgrad + Fixierungsformular mit Mutation-Guard/Toast +
  Fixierungs-Historie) + Hooks `lib/api/contract-fixing.ts` + Nav „Kontrakt-Fixierung"
  + Route-Alias.
- Tests: `tests/test_contract_fixing.py` (6 grün); Live-API verifiziert
  (Guards 422, Fixierung 200, Workspace-Bewertung).

### Verifiziert
12 Unit-Tests grün (6 Fixing + 6 Fulfillment-Regression); tsc 0, eslint clean.
DEMO-KT-004: 60 % fixiert, Bewertung +99,99 €, offener Marktwert 44.000 €.

## Folge-Slices
- **004.3** Engagement-Sicht (Summe offen je Artikel/Partei) + Kontraktmahnung.
- **004.4** Settlement-Übergabe (Bewegung→Abrechnung) + Storno (inkl. Fixierungs-Storno).
- **004.5** Browser-E2E + UAT.
