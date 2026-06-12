# Welle „Physische Landhandels-Kette“ — Tiefen-Audit Produktion/Futtermittel

**Stand:** 2026-06-12
**Ziel:** Medienbruch-Reduktion entlang **Rohware (Einzelfutter) → Rezept → Produktionsauftrag → Fertigwaren-Charge → QS/Trace**
**Scope:** In-Repo; gleiche Methode wie Logistik-Audit (`wave-physical-chain-logistics-audit-2026-06-12.md`): erst Audit, dann gezielte Lifecycle-Slices. Zweig gehört Claude (Logistik-Zweig: Cursor).

## 1. Ist-Inventar (API / Persistenz)

| Bereich | Modul | Persistenz | Bemerkung |
|---------|-------|------------|-----------|
| Komponenten / Rohwaren | `futtermittel_rohwaren.py`, `produktion_mischfutter.py` (`/verfuegbarkeit`) | `domain_shared.futtermittel_einzelfutter` (Alembic `futtermittel_sorten_produktion_20260410`) | Nährstoffprofil, GVO-/QS-Flags, `verfuegbar_t` |
| Rezepte | `futtermittel_rezepte.py`, `/produktion/mischfutter/rezepte` | `domain_shared.futtermittel_rezepte` + `_rezept_komponenten` | Anteile mit `einzelfutter_id`-Ref |
| Produktionsauftrag | `produktion_mischfutter.py` | `domain_shared.futtermittel_produktionsauftraege` | Lifecycle erstellt→freigegeben→in_produktion→fertig / storniert; Bestandsabzug bei Freigabe, Rückgabe bei Storno |
| Charge / QS | `charges.py` (`/chargen`) | `domain_ops.ops_chargen` (+ `ops_chargen_qs_fields_20260214`) | reiche QS-Felder: `rohstoffe`, `produktionsprozess`, `digitales_mischbuch`, HACCP …; `/qs-readiness`-Score |
| Quality-Lot-Binding | `quality_lot_binding.py` | **in-memory** | Daten weg bei Restart |

## 2. Bruchstellen (fachlich / technisch)

1. **Produktion → Charge (Belegbruch, Kern):** `PATCH /auftrag/{id}/status` auf `fertig`
   setzt nur `fertig_am`. Die `chargen_id` (MF-…) des Auftrags existiert **nie** in
   `ops_chargen` → QS-Readiness, Freigabe-Workflow und Chargen-Liste sehen die
   produzierte Ware nicht. Depth-Plan: „Chargen-Rueckverfolgung Futtermittel ❌ Kritisch“.
2. **Verbrauch ohne Beleg + Bestandsdrift-Bug:** Freigabe dekrementiert `verfuegbar_t`
   direkt nach **aktuellem** Rezept; Storno re-inkrementiert ebenfalls nach **aktuellem**
   Rezept. Ändert sich das Rezept zwischen Freigabe und Storno, driftet der Bestand.
   Es gibt keinen Snapshot, *was* tatsächlich abgezogen wurde (kein Mischprotokoll-Beleg).
3. **Kein Trace:** weder Auftrag→Komponenten noch Fertigcharge→Rohwaren auflösbar
   (`/futtermittel/chargen/{id}/trace` aus Depth-Plan fehlt).
4. **`quality_lot_binding` in-memory** — persistenzloser Beleg (separater Slice).
5. **Kanonische Lagerbewegungen:** `domain_inventory.inventory_stock_movements` verlangt
   `article_id`/`warehouse_id`-FKs; Einzelfuttermittel sind dort nicht gemappt →
   Bewegungs-Integration erst nach Artikel-Mapping (Folge-Slice, nicht Teil von 001).

## 3. Slice-Reihenfolge

1. **FEED-CHAIN-001 (erledigt 2026-06-12):** Verbrauchs-Snapshot (`verbrauch` JSONB) bei
   Freigabe (inkl. fail-closed Bestandsprüfung 409); Storno restauriert exakt den Snapshot
   (Bestandsdrift-Bug behoben); `fertig` erzeugt idempotent + fail-closed die
   `ops_chargen`-Charge mit `rohstoffe`-Mischprotokoll (GVO-/QS-Stammdaten angereichert)
   und `produktionsprozess`-Referenz (`charge_id` am Auftrag);
   `GET /produktion/mischfutter/auftraege/{id|chargen_id}/trace`. Migration
   `feed_chain_verbrauch_20260612`; Service `feed_production_chain_service.py`;
   Seed `seed_demo_feed_chain.py` (DEMO-MLF-18); Tests `test_feed_production_chain.py`
   (7 grün, inkl. Snapshot-Restore nach Rezeptänderung und fremde-chargen_id-409);
   UAT `scripts/uat/feed_production_chain_uat.py` (dry-run + `--execute` live grün).
2. **FEED-CHAIN-002:** Frontend-Arbeitsraum Produktion (Auftrag→Charge-Link, Mischprotokoll,
   QS-Readiness-Anzeige) im DOM-SUPPLY-004-Stil.
3. **FEED-CHAIN-003:** `quality_lot_binding` persistent (Alembic statt in-memory) und an
   `ops_chargen.qualitaetsstatus`/Freigabe gebunden.
4. **FEED-CHAIN-004:** Artikel-Mapping Einzelfutter ↔ `domain_inventory.articles` und
   Bewegungsbelege in `inventory_stock_movements` (Abstimmung: INV-STOCK-MOVEMENTS-001/Cursor).

## 4. Bewusst nicht in diesem Zweig

Logistik/Tour/Fracht (Cursor, eigener Zweig der Welle), HRM, POS, Webshop, Compliance/Meldewesen.

## Verweise

- Logistik-Zweig: `docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`
- Depth-Plan: `docs/project-context/domain-depth-plan-2026-05-17.md` (§10 Futtermittel)
- Workboard: `docs/agent-ops/active-workboard.md` → FEED-CHAIN-001
