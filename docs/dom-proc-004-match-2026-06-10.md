# DOM-PROC-004 — Beschaffung / 3-Wege-Match (2026-06-10)

Sprint-Ziel: P2P mit 3-Wege-Match (Bestellung ↔ Wareneingang ↔ Rechnung),
Abweichungen, Nachforderung. Erster Slice (004.1) liefert den **Match-Spine
Bestellung ↔ Wareneingang** mit Mengen-/Wertabweichung und Lücken.

## Ist-Befund (kartiert)
| Stufe | Tabelle |
|---|---|
| Bestellung | `domain_einkauf.bestellungen` + `bestellung_positionen` |
| Wareneingang | `public.inventory_goods_receipts` + `inventory_goods_receipt_lines` (Link: `po_id`/`po_number`, `po_line_number`) |
| Rechnung (Eingang) | `public.finance_erechnungen` — **kein PO-Bezug** (`zugeordneter_auftrag`/`_lieferschein`); 3. Stufe folgt mit Datenmodell |

**Hinweis:** Alle PO/WE/Rechnungs-Tabellen sind in DEV aktuell **leer** → Verifikation
über reine Logik-Unit-Tests + Endpoint-Struktur (statt Zeilendaten wie bei DOM-SUPPLY).

## Slice 004.1 — Match-Spine (umgesetzt, read-only)
- Service: `app/services/procurement_match_service.py`
  - `match_position(bestellt, geliefert)` — **reine** Vergleichslogik: Status
    offen/teilgeliefert/vollstaendig/ueberliefert (1 % Toleranz) + Abweichung %.
  - `match(bestellung)` — je Position bestellt vs. geliefert (aggregiert aus
    WE-Zeilen `po_line_number`, Fallback `menge_geliefert`), offene Menge,
    offener Wert, Über-/Unterlieferung; Lücken; Wareneingangs-Liste; Summary.
  - `list_orders()` — Bestellungen mit Match-Übersicht (Picker).
- API: `GET /api/v1/procurement/match` + `/match/orders`.
- Tests: `tests/test_procurement_match.py` (6 grün, reine Logik).

### Verifiziert
Unit-Tests (offen/teil/voll/über/Toleranz/ohne_menge); Endpoint liefert saubere
leere Struktur (`{"items":[]}`) bzw. `found:false` ohne Daten.

## Slice 004.3 — Seed-Daten + Frontend (umgesetzt)
- Seed: `scripts/seed_demo_procurement.py` (idempotent, Präfix `DEMO-`) erzeugt
  Lieferant/Lager + 2 Bestellungen mit Wareneingängen — Fälle vollständig /
  teilgeliefert / überliefert. Lauf: `docker exec valeo-neuro-erp-backend python scripts/seed_demo_procurement.py`.
- Bugfix: `_delivered_by_line`/`_goods_receipts` casten `po_id` auf `str`
  (vorher `text = uuid`-Fehler).
- Frontend: `pages/einkauf/wareneingangsabgleich.tsx` (Bestell-Picker + Positions-
  Match mit Status/Offen/Wert, Wareneingänge, Lücken) + Hooks
  `lib/api/procurement-match.ts` + Nav „Wareneingangs-Abgleich" + Route-Alias.

### Verifiziert (Seed-Daten)
DEMO-PO-001: Weizen vollständig (100/100), Gerste teilgeliefert (30/50, 3.800 € offen)
+ Lücke; DEMO-PO-002: Raps überliefert (22/20, +10 %).

## Slice 004.2 — Rechnungsstufe (umgesetzt 2026-06-11)
- Migration: `proc_three_way_invoice_20260611` — `public.finance_erechnungen` idempotent.
- Service: `match_three_way_value()` + `ProcurementMatchService.match_three_way()`.
- API: `GET /api/v1/procurement/match/three-way`.
- Verknüpfung: `zugeordneter_auftrag` = Bestellnummer; Kopfvergleich gelieferter Wert vs. fakturiert.
- Seed: `DEMO-RE-001` für `DEMO-PO-001` (27.700 € netto = gelieferter Wert).
- UI: `wareneingangsabgleich.tsx` zeigt Rechnungsstufe, Rechnungen und Ausnahmen.
- Tests: `tests/test_procurement_three_way_match.py` (4 Unit-Tests).

### Verifiziert
- Rechnung innerhalb 2 %-Toleranz → `abgeglichen`.
- Fehlende Rechnung → Ausnahme `keine_rechnung`.
- Wertabweichung → Ausnahme `rechnungswert_abweichung` (blocker).

## Slice 004.4 — Folgeaktionen (umgesetzt 2026-06-11)
- Migration: `proc_follow_up_20260611` — append-only `domain_einkauf.procurement_follow_up`.
- Service: `list_follow_ups()`, `create_follow_up()` (nachforderung | reklamation | eskalation | freigabe).
- API: `GET` + `POST /api/v1/procurement/match/follow-up`; `match_three_way` liefert `follow_ups`.
- UI: Folgeaktionen-Karte in `wareneingangsabgleich.tsx` bei Ausnahmen/Lücken.
- Tests: `tests/test_procurement_follow_up.py` (4 Unit-Tests).

### Verifiziert
- Unbekannte Aktion / leerer Grund → `ValueError`.
- Eskalation erhöht `eskalationsstufe` gegenüber vorheriger Eskalation.
- Fehlende Tabelle → leere Liste (tolerant bis Migration).

## Slice 004.5 — ERS + UAT (umgesetzt 2026-06-11)
- Migration: `proc_ers_credit_20260611` — `domain_einkauf.procurement_ers_credits`.
- Service: `calculate_ers_credit()` (Überlieferung + Rechnungsüberzahlung), `create_ers_credit()`.
- API: `GET /match/ers/preview`, `GET/POST /match/ers`.
- UI: ERS-Karte in `wareneingangsabgleich.tsx` bei berechtigter Vorschau.
- UAT: `scripts/uat/proc_match_lifecycle_uat.py` + `docs/dom-proc-004-uat-2026-06-11.md`.
- Smoke: `playwright-tests/specs/einkauf/procurement-match-smoke.spec.ts`.
- Tests: `tests/test_procurement_ers.py` (4 Unit-Tests).

### Verifiziert
- DEMO-PO-002 (2 t Überlieferung × 480 €) → 960 € Gutschrift-Vorschau.
- Keine Berechtigung ohne Abweichung → 422.
- 18 kumulierte Procurement-Unit-Tests grün.

## Status
**DOM-PROC-004 abgeschlossen** (004.1–004.5).
