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

## Slice 004.2 — Ketten-Event-Log + kanonischer Übergabestatus (umgesetzt)

Revisionsfestes, **append-only** Ereignis-Protokoll der Kette + einheitlicher
Übergabestatus, abgeleitet aus den Ereignissen.

- Migration: `supply_chain_events_20260610` — `domain_inventory.supply_chain_events`
  (append-only; partieller Unique-Index für idempotenten Backfill).
- Service: `app/services/supply_chain_event_service.py`
  - `record(...)` — append (kein UPDATE/DELETE) für Korrektur/Abweichung/Storno/Notiz.
  - `sync_from_state(ticket)` — erzeugt idempotent (source='backfill') die Lifecycle-
    Ereignisse aus dem Ist-Zustand; Mengen-Abweichung wird als Ereignis festgehalten.
  - `derive_status(ticket)` — kanonischer Status: **erfasst → freigegeben →
    eingelagert → abgerechnet** (storniert überschreibt).
  - `timeline(ticket)` — Stufen-/Zeit-sortierter Verlauf.
- Integration: `trace()` liefert zusätzlich `ereignisse` + `kanon_status` (read-only).
- API: `POST /supply-chain/traceability/sync?ticket=…` (Backfill, idempotent),
  `POST /supply-chain/events` (manuelles Ereignis mit Grund/Menge).
- Frontend: Status-Badge, Ereignis-Log-Timeline (abgeleitet/manuell gekennzeichnet)
  und „Ereignis erfassen" (Korrektur/Abweichung/Storno/Notiz) in
  `pages/lager/rueckverfolgbarkeit.tsx`; Auto-Backfill bei Auswahl.

### Verifiziert
`WG-2026-00001` → sync legt 3 Lifecycle-Ereignisse an (erfasst/freigegeben/
eingelagert), zweiter Sync = 0 (idempotent), kanon_status = „eingelagert"; manuelles
Korrektur-Ereignis wird angehängt und erscheint im Log.

## Slice 004.3 — Lager-Lot-Folgeaktionen mit Abweichungsgrund (umgesetzt)

Operative Folgeaktionen auf Silo-Lots, jeweils mit **Pflicht-Grund**, einer
Lager-Bewegung (`silo_lot_movements`) und einem Eintrag im Event-Log:

- Service: `app/services/supply_chain_lot_service.py`
  - `block` → Sperrbestand (`status='gesperrt'`, Bewegung `sperre`, Event `gesperrt`)
  - `release` → QS-Freigabe (`status='active'`, Bewegung `freigabe`, Event `qs_freigabe`)
  - `shrinkage` → Schwund (Menge reduzieren, Bewegung `schwund`, Event `schwund`);
    Guard: Menge > 0 und ≤ Lot-Bestand.
- API: `POST /supply-chain/lots/{lot}/block|release|shrinkage` (422 bei Fachfehler).
- Frontend: Aktionsleiste unter Lager-Knoten (Sperren/QS-Freigabe/Schwund mit
  Grund/Menge) in `pages/lager/rueckverfolgbarkeit.tsx`.
- Tests: `tests/test_supply_chain_lot.py` (Guards, 4 grün).

### Verifiziert
block → 422 bei erneutem block; release nur aus „gesperrt"; shrinkage 200 kg
reduziert Lot 25.000→24.800 kg + Event; Übermenge → 422. Seed danach restauriert.

## Definition „fachliche Tiefe erreicht" (Sprint-Maßstab) — Status 004.1–004.3

1. Kernfall läuft (Kette sichtbar/prüfbar) ✅
2. Sonderfälle (Lücken/Abweichung/Mehrfach-Folgeobjekte) ✅ erkannt
3. Storno/Korrektur — ✅ als Ereignis erfassbar (004.2); durchgängige Wirkung ⏳ 004.4
4. Folgeobjekte nachweisbar ✅ (Annahme/Lager/Abrechnung je Wiegeschein)
5. Rechte/Tenant/Audit — Tenant ✅; **append-only Audit-Event-Log ✅ (004.2)**
6. Tests (BE-Logik) ✅; Browser-E2E ⏳
7. Externe/betriebliche Abnahme — ⏳ (UAT-Paket)

## Geplante Folge-Slices
- **004.2** Einheitlicher Übergabestatus + append-only Ketten-Event-Log ✅ **fertig**
- **004.3** Schwund/Sperrbestand/QS-Freigabe als Folgeaktionen mit Abweichungsgründen ✅ **fertig**
- **004.4** Storno/Korrektur durchgängig über die Kette (Wirkung auf Status/Bestand).
- **004.5** Browser-/E2E-Abnahme + UAT-Nachweispaket.
