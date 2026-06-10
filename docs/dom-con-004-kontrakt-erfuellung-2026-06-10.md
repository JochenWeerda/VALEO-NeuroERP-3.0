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

## Folge-Slices
- **004.2** Fixierungs-Arbeitsraum (Teilfixierung) + Marktwert/MATIF-Bewertung.
- **004.3** Engagement-Sicht (Summe offen je Artikel/Partei) + Kontraktmahnung.
- **004.4** Settlement-Übergabe (Bewegung→Abrechnung) + Storno.
- **004.5** Browser-E2E + UAT.
