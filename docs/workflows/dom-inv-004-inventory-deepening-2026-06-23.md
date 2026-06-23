# DOM-INV-004 — Inventory Domänen-Vertiefung

**Slice:** DOM-INV-004\
**Datum:** 2026-06-23\
**Owner:** Claude Code

---

## 1. Scope

Drei fachliche Subdomänen werden auf Tiefe .2–.4 gehoben:

| Sub-Slice | Fachgebiet | Kern-Endpunkt |
|---|---|---|
| .2 | Chargen-/MHD-Traceability (FEFO) | `POST/GET /lager/lots`, `POST /lager/lots/{id}/consume` |
| .3 | Inventur-Differenzbeleg-Automatik | `POST /lager/inventur/{count_id}/differenz-buchen` |
| .4 | Bestandskorrektur-Storno | `POST /lager/korrekturen/{id}/storno` |
| .5 | E2E UAT | Playwright @smoke + Python-UAT-Script |

---

## 2. .2 Chargen-/MHD-Traceability (FEFO)

### Soll-Prozess

1. Wareneingang bucht Lot an: `POST /lager/lots` mit `lot_number`, `article_id`, `warehouse_id`, `mhd`, `initial_qty`.
2. Verbrauch per `POST /lager/lots/{id}/consume` — reduziert `current_qty`, schreibt `lot_movement`.
3. FEFO-Abfrage: `GET /lager/lots?article_id=X` gibt Lots sortiert nach `mhd ASC` (frühestes MHD zuerst).
4. Abgelaufene Lots (mhd < heute) können nicht mehr verbraucht werden (fail-closed, 422).
5. Unterdeckung (consume.quantity > current_qty) → 422.

### Status-Maschine

```
AKTIV → ERSCHÖPFT (current_qty = 0)
      → ABGELAUFEN (mhd < heute, automatisch bei Consume-Check)
```

---

## 3. .3 Inventur-Differenzbeleg-Automatik

### Soll-Prozess

1. Inventur wird gezählt (count lines) und per `POST /{count_id}/post` gebucht.
2. Danach: `POST /lager/inventur/{count_id}/differenz-buchen` erzeugt für jede
   Zeile mit `delta != 0` eine Bestandskorrektur:
   - `delta > 0` → Korrektur `+delta`, Grund `messdifferenz`
   - `delta < 0` → Korrektur `delta`, Grund `messdifferenz`
3. Nur für Inventuren mit `status = 'posted'` erlaubt.
4. Idempotent: bereits erstellte Korrekturen werden nicht doppelt angelegt
   (referenziert via `count_line_id`).

---

## 4. .4 Bestandskorrektur-Storno

### Soll-Prozess

1. `POST /lager/korrekturen/{id}/storno` erzeugt eine neue Bestandskorrektur
   mit negierter Menge (`menge = -original.menge`), Grund `storno`.
2. Beide Korrekturen sind über `storno_ref` verknüpft.
3. Idempotent: zweiter Aufruf gibt bestehenden Storno zurück (409 nicht nötig).
4. Original-Korrektur bekommt `status = 'storniert'`.

---

## 5. Datenmodell-Erweiterungen

### `inventory_lots` (neu)

```sql
CREATE TABLE domain_inventory.inventory_lots (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    article_id VARCHAR(64) NOT NULL,
    warehouse_id VARCHAR(64) NOT NULL,
    lot_number VARCHAR(100) NOT NULL,
    mhd DATE,
    initial_qty NUMERIC(14,3) NOT NULL,
    current_qty NUMERIC(14,3) NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    status VARCHAR(20) DEFAULT 'AKTIV',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `inventory_lot_movements` (neu)

```sql
CREATE TABLE domain_inventory.inventory_lot_movements (
    id VARCHAR(36) PRIMARY KEY,
    lot_id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(36),
    movement_type VARCHAR(10) NOT NULL,  -- IN/OUT/ADJUST
    quantity NUMERIC(14,3) NOT NULL,
    reference_id VARCHAR(36),
    reference_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Spalte `storno_ref` auf `inventory_stock_movements` (neu)

```sql
ALTER TABLE domain_inventory.inventory_stock_movements
ADD COLUMN IF NOT EXISTS storno_ref VARCHAR(36);
```

---

## 6. Nicht-Ziele dieses Slices

- Automatisches MHD-Abschreibungs-Scheduling (kein Cron-Job)
- Integration mit Einkauf-Wareneingang (kein automatisches Lot-Anlegen bei WE)
- RFID/Barcode-Scanner-Integration
- Bewertung nach LIFO/Durchschnitt (nur FEFO implementiert)
