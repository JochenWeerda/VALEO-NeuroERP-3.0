# DOM-SUPPLY-004 — Durchgängige Lieferkette & Rückverfolgbarkeit (2026-06-10)

Sprint-Ziel: die Kette **Partie → Wiegung → Charge → Lager → Abrechnung** als
durchgängige, revisionsfeste Kette. Dieser erste Slice (004.1) macht die heute
getrennt geführten Stufen als **eine prüfbare Genealogie** sichtbar und deckt
Mengen-Abweichungen (Schwund) und Lücken (fehlende Folgeobjekte) auf.

## Ist-Befund (kartiert)

Die Stufen werden in getrennten Schemata geführt und sind nur lose verknüpft:

| Stufe | Tabelle | Verknüpfung |
|---|---|---|
| Wiegung | `domain_inventory.weighing_tickets` | **Rückgrat** (`id`) |
| Annahme | `domain_inventory.harvest_acceptances` | `weighing_ticket_id` → Wiegung |
| Lager | `domain_inventory.silo_lots` (+ `silo_lot_movements`) | `source_ticket_id` → Wiegung |
| Abrechnung | `domain_inventory.agrar_settlements` | `ticket_id` → Wiegung |

`ops_wiegungen`/`ops_chargen` (via `chargennummer`) sind ein **paralleler** Strang;
`partiestamm` ist Stammdaten. → Kernlücke: keine einheitliche Traceability-Sicht,
keine durchgängige Mengen-/Status-Prüfung.

## Slice 004.1 — Traceability-Spine (umgesetzt)

Read-only, nicht-invasiv (keine Änderung an den heißen Stufen-Tabellen).

- Service: `app/services/supply_chain_trace_service.py`
  - `trace(ticket|acceptance|lot|settlement)` — löst die Eingabe auf das Wiegeschein-
    Rückgrat auf und baut die Kette (Wiegung → Annahme[n] → Lager-Lot[s] inkl.
    Bewegungen → Abrechnung[en]).
  - **Mengen-Konsistenz**: vergleicht kg-Mengen benachbarter Stufen; Abweichung
    > 2 % wird als Schwund/Differenz markiert.
  - **Lücken**: unallocated Wiegeschein, fehlende/nicht-freigegebene Annahme,
    fehlendes Lager, fehlende Abrechnung.
  - `list_tickets()` — Übersicht/Picker mit Ketten-Vollständigkeit.
- API: `app/api/v1/endpoints/supply_chain.py`
  - `GET /api/v1/supply-chain/traceability?ticket=…|acceptance=…|lot=…|settlement=…`
  - `GET /api/v1/supply-chain/traceability/tickets?limit=…`
- Frontend: `pages/lager/rueckverfolgbarkeit.tsx` (Picker + Genealogie-Timeline,
  Mengen-Konsistenz, Lücken) · Hooks `lib/api/supply-chain.ts`
  (`useTraceTickets`/`useTrace`) · Nav „Rückverfolgbarkeit" (operations.tsx).
- Tests: `tests/test_supply_chain_trace.py` (Mengen-Check + Lücken, 5 grün).

### Verifiziert (echte Seed-Daten)
`WG-2026-00001`: Wiegung 25.000 kg → Annahme `EA-2026-0001` (released) → Lager
`LOT-2026-S001-001` (25,0 t). Mengen-Konsistenz 0 % (innerhalb Toleranz); Lücken:
Wiegeschein unallocated, keine Abrechnung. Kette korrekt als unvollständig markiert.

## Definition „fachliche Tiefe erreicht" (Sprint-Maßstab) — Status 004.1

1. Kernfall läuft (Kette sichtbar/prüfbar) ✅
2. Sonderfälle (Lücken/Abweichung/Mehrfach-Folgeobjekte) ✅ erkannt
3. Storno/Korrektur — ⏳ Folge-Slice
4. Folgeobjekte nachweisbar ✅ (Annahme/Lager/Abrechnung je Wiegeschein)
5. Rechte/Tenant/Audit — Tenant ✅; Audit-Event-Log ⏳ Folge-Slice
6. Tests (BE-Logik) ✅; Browser-E2E ⏳
7. Externe/betriebliche Abnahme — ⏳ (UAT-Paket)

## Geplante Folge-Slices
- **004.2** Einheitlicher Übergabestatus + append-only Ketten-Event-Log (Audit/Revision).
- **004.3** Schwund/Sperrbestand/QS-Freigabe als Folgeaktionen mit Abweichungsgründen.
- **004.4** Storno/Korrektur durchgängig über die Kette.
- **004.5** Browser-/E2E-Abnahme + UAT-Nachweispaket.
