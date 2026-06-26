# Harvest Acceptance (Ernte-Annahme) - README

**Modul:** Agrar / Ernte-Annahme  
**Status:** ✅ Backend-Implementierung abgeschlossen  
**Version:** 1.0.0  
**Datum:** 2026-02-17

---

## Schnellstart

### 1. Migration ausführen

```bash
# Prüfe aktuellen Stand
alembic current

# Führe Migration aus
alembic upgrade head

# Prüfe Tabellen
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptances"
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptance_positions"
```

### 2. API-Endpoints verwenden

**Base URL:** `/api/v1/agrar/harvest-acceptance`

#### Ernte-Annahme anlegen:

```bash
POST /api/v1/agrar/harvest-acceptance
Content-Type: application/json

{
  "customer_id": "customer-uuid-123",
  "weighing_ticket_id": "ticket-uuid-456",
  "article_id": "article-uuid-789",
  "delivery_date": "2025-02-17",
  "warehouse_id": "warehouse-uuid-abc",
  "origin_nuts2_code": "DE12",
  "origin_postal_code": "01067",
  "origin_city": "Dresden",
  "is_sustainable_biomass": true
}
```

#### Berechnung durchführen:

```bash
POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/calculate
```

#### Freigabe:

```bash
POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/release?release_status=provisional&create_stock_movement=true
```

---

## Architektur

### Datenbank-Schema

```
domain_inventory.harvest_acceptances
├── Header: branch_id, warehouse_id, delivery_date, weighing_ticket_id
├── Kunde: customer_id, contract_id, forwarder_id, intermediate_dealer_id
├── Anlieferung: article_id, variety_id, vehicle_plate
├── NUTS-2: origin_nuts2_code, nuts_version, origin_postal_code, origin_city
├── Status: release_status, stock_movement_id, quality_protocol_id, invoice_id
└── Summen: total_net_amount_eur, total_vat_amount_eur, total_gross_amount_eur

domain_inventory.harvest_acceptance_positions
├── Abrechnungs-Positionen (14 Positionen: 10, 15, 20, 30, 40, 50, 60, 63, 65, 70, 75, 78, 80, 110)
├── Berechnungslogik: is_calculable, is_printable, calculation_formula
└── NUTS-2 pro Position (für Mischladungen)
```

### Service-Layer

```
modules/agrar/services/
├── harvest_calculator.py          # Berechnungslogik (14 Positionen)
├── drying_rule_engine.py          # Feuchte-Berechnung (LOOKUP_TABLE, FACTOR_FROM_BASE, DRY_MATTER_NORMALIZATION)
└── settlement_calculator.py       # Basis-Funktionen (rounding, etc.)
```

### API-Layer

```
app/api/v1/endpoints/
└── harvest_acceptance.py          # CRUD + Berechnung + Freigabe
```

---

## Features

### ✅ Implementiert

- **Vollständiges CRUD** für Ernte-Annahmen
- **14 Abrechnungs-Positionen** automatisch berechnet
- **Drying Rule Engine Integration** für Feuchte-Berechnung
- **NUTS-2-Unterstützung** (Herkunft/Region der Erzeugung)
- **Automatische Wareneingang-Erstellung** bei Freigabe
- **Preisermittlung** (Vertrag > Artikel)
- **Status-Workflow** (Draft → Provisional → Final)
- **Audit-Trail** (calculation_formula für jede Position)

### ⏳ TODO

- **Tagespreis-API:** Für dynamische Preise (Vertrag > Tagespreis > Artikel)
- **Gutschrift-Erstellung:** Self-Billing Workflow mit E-Rechnung
- **Qualitätsprotokoll:** Integration für Laborwerte-Import
- **Frontend-Integration:** Eingabemaske für Ernte-Annahme
- **Vollständige PLZ → NUTS-2-Zuordnungstabelle:** Eurostat correspondence tables

---

## Berechnungslogik

### Abrechnungs-Positionen (14 Positionen)

| Pos. | Bezeichnung | Typ | Berechnung |
|------|-------------|-----|------------|
| 10 | Angelieferte Menge | Linked | Aus Wiegeschein (Nettogewicht) |
| 15 | Windabgang | Calculated | Menge × Windabgang % |
| 20 | Besatz 2% frei | Calculated | max(0, Besatz% - 2%) × Menge |
| 30 | Gereinigte Menge | Calculated | Angelieferte - Besatz |
| 40 | Feuchte/Tr.verlust | Calculated | Drying Rule Engine oder vereinfacht |
| 50 | Zwischenmenge | Calculated | Gereinigte - Feuchte |
| 60 | Hektolitergewicht | Info | Aus Laborwert |
| 63 | Lagerschwund | Calculated | Zwischenmenge × Lagerschwund % |
| 65 | Nettogewicht | Calculated | Zwischenmenge - Lagerschwund |
| 70 | Feuchtigkeitsabzug / Trocknungskosten | Calculated/EUR | Aus Drying Rule Engine (falls vorhanden) |
| 75 | Lagergeld | Input | EUR/Monat × Monate |
| 78 | Frachtkosten | Input | EUR |
| 80 | Wiegegebühren | Input | EUR |
| 110 | Gutschriftsbetrag | Calculated | (Nettogewicht × Preis) - Abzüge |

### Drying Rule Engine

**Automatisch aktiviert**, wenn:
- `crop_code` vorhanden (aus Artikel-`warengruppe` abgeleitet)
- `moisture_pct` vorhanden
- Drying Rule Repository verfügbar

**Methoden:**
- `LOOKUP_TABLE`: Feuchte → Tabelle (entzug_pct_points, loss_pct, optional fee)
- `FACTOR_FROM_BASE`: loss_pct = (moisture - base) × factor (stufig)
- `DRY_MATTER_NORMALIZATION`: invoice_weight = weight × (100 - moisture) / (100 - base)

**Fallback:** Vereinfachte Berechnung, falls Engine nicht verfügbar

---

## NUTS-2-Unterstützung

### Bedeutung

- **NUTS-2 = "Herkunft/Region der Erzeugung"** (nicht Standort des Lagers)
- **Hauptzweck:** Nachhaltigkeitsnachweise / Biomasse-Zertifizierung (RED-II, ISCC, REDcert, SURE)
- **Weitere Zwecke:** Statistik/Reporting, Warenstrom-Auswertungen

### Validierung

- **Format:** 2 Buchstaben + 1-2 Ziffern (z.B. DE12, FR10)
- **Versionierung:** `nuts_version` für Audit (z.B. "NUTS 2024")
- **PLZ-Ableitung:** Placeholder-Implementierung (TODO: vollständige Eurostat-Zuordnungstabelle)

### Mischladungen

Bei mehreren Herkunftsorten: Jede Position kann eigene `origin_nuts2_code` haben.

---

## Status-Workflow

```
Draft
  ↓ (Berechnung + Freigabe)
Provisional
  ↓ (Qualitätsfreigabe)
Final
  ↓ (Gutschrift-Erstellung)
Credit Note Created
  ↓ (Zahlung)
Paid

Alternative:
  → Disputed (aus Credit Note Created/Paid)
  → Cancelled (aus jedem Status)
```

### Validierungen

- **Draft:** Kann geändert/gelöscht werden
- **Provisional:** Kann geändert werden, nicht gelöscht
- **Final:** Read-only (außer Admin)
- **Credit Note Created:** Read-only
- **Cancelled:** Read-only

---

## Preisermittlung

### Priorität

1. **Vertragspreis** (`agrar_contracts.fixed_price`)
2. **Artikel-Verkaufspreis** (`articles.sales_price`) - Fallback
3. **TODO:** Tagespreis-API für dynamische Preise

### Crop-Code-Ableitung

Automatisch aus Artikel-`warengruppe`:
- MAIS → MAIZE
- WEIZEN → WHEAT
- GERSTE → BARLEY
- HAFER → OATS
- RAPS → RAPESEED
- ACKERBOHNE → FIELD_BEANS
- ERBSE → PEAS
- LUPINE → LUPINS

---

## Belegkette

```
Vertrag/Preisvereinbarung
  ↓
Wiegeschein (Brutto/Tara/Netto) [PRIMÄRBELEG]
  ↓
Ernte-Annahme (Harvest Acceptance)
  ↓ (bei Freigabe)
Wareneingang (Stock Movement) [Sperrbestand]
  ↓ (Qualitätsfreigabe)
Qualitätsprotokoll (Quality Protocol)
  ↓ (Berechnung)
Abrechnungsblatt (14 Positionen)
  ↓ (Gutschrift-Erstellung)
Gutschrift (§14) [Self-Billing Rechnung]
  ↓
Zahlung / Kontoauszug / OP-Ausgleich
```

---

## API-Referenz

### POST /api/v1/agrar/harvest-acceptance

Erstellt eine neue Ernte-Annahme.

**Request Body:**
```json
{
  "customer_id": "string (required)",
  "delivery_date": "2025-02-17 (required)",
  "weighing_ticket_id": "string (optional)",
  "article_id": "string (optional)",
  "warehouse_id": "string (optional)",
  "origin_nuts2_code": "DE12 (optional)",
  "origin_postal_code": "01067 (optional)",
  "is_sustainable_biomass": false
}
```

**Response:** `HarvestAcceptanceOut`

### POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/calculate

Berechnet alle Abrechnungs-Positionen.

**Response:**
```json
{
  "acceptance_id": "...",
  "positions": [...],
  "total_net_amount_eur": 2500.00,
  "total_vat_amount_eur": 195.00,
  "total_gross_amount_eur": 2695.00,
  "vat_rate_percent": 7.8,
  "warnings": []
}
```

### POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/release

Gibt Ernte-Annahme frei (provisional oder final).

**Query Parameters:**
- `release_status`: `provisional` oder `final` (required)
- `create_stock_movement`: `true` oder `false` (default: `true`)

**Response:** `HarvestAcceptanceOut`

---

## Tests

### Unit Tests

```bash
# Berechnungslogik testen
pytest tests/test_harvest_calculator.py

# Drying Rule Engine testen
pytest tests/test_drying_rule_engine.py
```

### Integration Tests

```bash
# API-Endpoints testen
pytest tests/integration/test_harvest_acceptance_api.py
```

---

## Dokumentation

- **Implementierungs-Zusammenfassung:** `docs/harvest-acceptance-implementation-summary.md`
- **NUTS-2-Details:** `docs/harvest-acceptance-nuts2.md`
- **Offene Fragen:** `docs/ernte-annahme-pruefung-fragen.md`
- **Datenfeld-Analyse:** `docs/ernte-annahme-datenfeld-analyse.md`
- **Drying Rule Engine:** `docs/drying-rule-engine.md`

---

## Support & Kontakt

Bei Fragen oder Problemen:
1. Prüfe die Dokumentation in `docs/`
2. Prüfe die API-Dokumentation (Swagger UI)
3. Prüfe die Logs für Fehlermeldungen

---

**Stand:** 2026-02-17  
**Nächster Schritt:** Migration ausführen, dann Frontend-Integration oder Gutschrift-Erstellung


