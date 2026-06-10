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

## Folge-Slices
- **004.2** Rechnungs-Stufe (echter 3-Wege-Match) — PO-Bezug am Eingangsrechnungsmodell.
- **004.4** Nachforderung/Reklamation/Eskalation als Folgeaktionen mit Grund (Event-Log).
- **004.5** ERS (Gutschriftsverfahren) + UAT-Nachweispaket.
