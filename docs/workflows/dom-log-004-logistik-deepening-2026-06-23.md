# DOM-LOG-004 — Logistik Domänen-Vertiefung

**Slice:** DOM-LOG-004\
**Datum:** 2026-06-23\
**Owner:** Claude Code

---

## 1. Scope

Drei fachliche Subdomänen der Logistik werden auf Tiefe .2–.4 gehoben:

| Sub-Slice | Fachgebiet | Kern-Endpunkt |
|---|---|---|
| .2 | Tour-Disposition (Kapazität + Zeitfenster) | `POST /logistik/tours/{id}/disposition-check` |
| .3 | ePOD-Lifecycle (Ablieferungsbeleg → Settlement) | `POST /logistik/tours/{id}/stops/{sid}/settle` |
| .5 | E2E / UAT | Playwright @smoke + Python-UAT-Script |

---

## 2. .2 Tour-Disposition

### Soll-Prozess

1. Disponent legt Tour mit Fahrzeug und Stopps an (`POST /logistik/tours`).
2. Vor Fahrer-Abfahrt ruft das System `POST /tours/{id}/disposition-check` auf.
3. Service aggregiert Lieferscheingewichte aus `delivery_note_ref`-Feldern der Stopps.
4. Ergebnis: `utilization_pct = total_weight_kg / capacity_kg * 100`.
5. Bei `utilization_pct > 100`: HTTP 422 mit Fehlerdetail.
6. Prüf-Record wird in `domain_logistics.tour_disposition_checks` persistiert.

### Kapazitäts-Konfiguration

Fahrzeugkapazität wird über `DEFAULT_VEHICLE_CAPACITY_KG` aus Backend-Config gelesen (Default: 20.000 kg). Eine spätere `vehicles`-Tabelle kann dies überschreiben.

### Zeitfenster-Validierung

`planned_arrival` der Stopps muss streng monoton steigen. Verletzung → 422.

---

## 3. .3 ePOD-Lifecycle

### Statusmaschine

```
GEPLANT → UNTERWEGS → GELIEFERT → SIGNED → SETTLED
                    ↘ FEHLGESCHLAGEN
```

- `GELIEFERT` + `PodIn`-Payload (Unterschrift + Name) → setzt `epod_status = SIGNED`.
- `POST /settle` → setzt `epod_status = SETTLED` + schreibt Record in `epod_settlements`.
- Settlement ist idempotent: unique constraint `(stop_id)` in `epod_settlements`.
- Rückabwicklung nur über expliziten Storno-Endpunkt (nicht implementiert in diesem Slice).

### ePOD-Felder am Stopp

| Feld | Typ | Beschreibung |
|---|---|---|
| `epod_status` | VARCHAR | PENDING / SIGNED / SETTLED |
| `recipient_name` | VARCHAR | Bei Übergabe erfasst |
| `delivered_at` | TIMESTAMP | Zeitpunkt Übergabe |
| `epod_photo_ref` | VARCHAR | Optional: Foto-Upload-Referenz |

---

## 4. Frachtkostenabrechnung (Referenz)

Bestehende `carrier_invoices`-Tabelle (log_carrier_invoices_20260618) deckt Eingangsrechnungen von Spediteurs ab. Slice .4 der Vertiefung ist vorerst über `carrier_invoices`-Endpunkte in `logistics_freight.py` abgedeckt — keine zusätzliche Tabelle erforderlich.

---

## 5. Datenmodell-Erweiterungen

### `tour_disposition_checks` (neu)

```sql
CREATE TABLE domain_logistics.tour_disposition_checks (
    id VARCHAR(36) PRIMARY KEY,
    tour_id VARCHAR(36) NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_weight_kg NUMERIC(14,2),
    capacity_kg NUMERIC(14,2),
    utilization_pct NUMERIC(8,2),
    stops_count INTEGER,
    result VARCHAR(20),   -- OK / OVERLOADED / NO_WEIGHT_DATA
    tenant_id VARCHAR(36)
);
```

### `epod_settlements` (neu)

```sql
CREATE TABLE domain_logistics.epod_settlements (
    id VARCHAR(36) PRIMARY KEY,
    tour_id VARCHAR(36) NOT NULL,
    stop_id VARCHAR(36) NOT NULL UNIQUE,
    settled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recipient_name VARCHAR(255),
    delivered_at TIMESTAMPTZ,
    notes TEXT,
    tenant_id VARCHAR(36)
);
```

---

## 6. Nicht-Ziele dieses Slices

- Echtzeit-GPS-Tracking (kein Websocket-Push)
- Fahrzeug-Stammdaten-Verwaltung (vehicles-Tabelle)
- Automatische Nachfakturierung bei Gewichtskorrektur
- Integration mit Buchhaltungs-Schnittstelle
