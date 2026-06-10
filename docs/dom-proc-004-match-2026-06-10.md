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

## Folge-Slices
- **004.2** Rechnungs-Stufe (echter 3-Wege-Match) — benötigt PO-Bezug am Eingangs-
  rechnungsmodell (Preis-/Wertabweichung Rechnung↔Bestellung).
- **004.3** Frontend (Picker + Match-Sicht + Abweichungen) — sobald Seed/Echtdaten.
- **004.4** Nachforderung/Reklamation/Eskalation als Folgeaktionen mit Grund (Event-Log).
- **004.5** ERS (Gutschriftsverfahren) + UAT-Nachweispaket.
