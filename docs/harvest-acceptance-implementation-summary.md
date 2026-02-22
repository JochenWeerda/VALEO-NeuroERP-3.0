# Harvest Acceptance (Ernte-Annahme) - Implementierungs-Zusammenfassung

**Erstellt:** 2026-02-17  
**Aktualisiert:** 2026-02-17 (Erweiterungen nach praxisnahen Default-Entscheidungen)  
**Status:** ✅ Backend-Implementierung abgeschlossen + Erweiterungen

---

## Übersicht

Vollständige Backend-Implementierung der Ernte-Annahme-Maske (Harvest Acceptance) für den Landhandel, inklusive NUTS-2-Unterstützung, Berechnungslogik, Drying Rule Engine Integration und automatischer Wareneingang-Erstellung.

---

## Implementierte Komponenten

### 1. Datenbank-Modelle

#### `HarvestAcceptance` (Hauptbeleg)
- **Header-Bereich:** Niederlassung, Lagerhalle, Liefer-Datum, Wiegeschein-Referenz
- **Kunden-Bereich:** Debitor, Vertrag, Spediteur, Zwischenhändler
- **ANLIEFERUNG Tab:** Artikel, Sorte, Fahrzeug
- **NUTS-2-Felder:** `origin_nuts2_code`, `nuts_version`, `origin_postal_code`, `origin_city`, `origin_country_code`
- **Nachhaltigkeit:** `is_sustainable_biomass` (für RED-II/ISCC/REDcert)
- **Status:** `release_status` (draft/provisional/final/credit_note_created/paid/disputed/cancelled)
- **Belegkette:** `stock_movement_id`, `quality_protocol_id`, `invoice_id`
- **Summen:** `total_net_amount_eur`, `total_vat_amount_eur`, `total_gross_amount_eur`, `vat_rate_percent`

#### `HarvestAcceptancePosition` (Abrechnungs-Positionen)
- **14 Positionen:** 10, 15, 20, 30, 40, 50, 60, 63, 65, 70, 75, 78, 80, 110
- **Berechnungslogik:** `is_calculable`, `is_printable`, `calculation_formula`
- **NUTS-2 pro Position:** Für Mischladungen (mehrere Herkunftsorte)
- **Werte:** `quantity_kg`, `lab_value_pct`, `amount_eur`, `price_per_unit_eur`

### 2. Migration

**Datei:** `alembic/versions/b38680c2f581_add_harvest_acceptance_with_nuts2_20260217.py`

- Erstellt `harvest_acceptances` Tabelle
- Erstellt `harvest_acceptance_positions` Tabelle
- Foreign Keys zu: `tenants`, `branches`, `warehouses`, `weighing_tickets`, `customers`, `agrar_contracts`, `business_partners`, `articles`, `inventory_stock_movements`
- Indizes für Performance: `uq_harvest_acceptances_tenant_number`, `ix_harvest_acceptances_customer`, `ix_harvest_acceptances_weighing_ticket`, `ix_harvest_acceptances_nuts2`, `ix_harvest_acceptance_positions_nuts2`

### 3. API-Endpoints

**Base Path:** `/api/v1/agrar/harvest-acceptance`

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| `POST` | `/` | Ernte-Annahme anlegen |
| `GET` | `/` | Liste (mit Filtern: customer_id, contract_id, release_status, origin_nuts2_code) |
| `GET` | `/{acceptance_id}` | Einzelne Ernte-Annahme abrufen |
| `PUT` | `/{acceptance_id}` | Aktualisieren (nur Draft/Provisional) |
| `DELETE` | `/{acceptance_id}` | Löschen (nur Admin, nur Draft) |
| `POST` | `/{acceptance_id}/derive-nuts2` | NUTS-2-Code aus PLZ ableiten |
| `POST` | `/{acceptance_id}/release` | Freigeben (provisional/final) mit automatischer Stock-Movement-Erstellung |
| `POST` | `/{acceptance_id}/calculate` | Berechnung aller Abrechnungs-Positionen |

### 4. Berechnungslogik

**Service:** `modules/agrar/services/harvest_calculator.py`

#### Berechnungsreihenfolge (14 Positionen):

1. **Pos. 10:** Angelieferte Menge (aus Wiegeschein)
2. **Pos. 15:** Windabgang (berechnet: Menge × %)
3. **Pos. 20:** Besatz 2% frei (berechnet: max(0, Besatz% - 2%) × Menge)
4. **Pos. 30:** Gereinigte Menge (berechnet: Angelieferte - Besatz)
5. **Pos. 40:** Feuchte/Tr.verlust (berechnet mit Drying Rule Engine oder vereinfacht)
6. **Pos. 50:** Zwischenmenge (berechnet: Gereinigte - Feuchte)
7. **Pos. 60:** Hektolitergewicht (Info, aus Laborwert)
8. **Pos. 63:** Lagerschwund (berechnet: Zwischenmenge × %)
9. **Pos. 65:** Nettogewicht (berechnet: Zwischenmenge - Lagerschwund)
10. **Pos. 70:** Feuchtigkeitsabzug oder Trocknungskosten (EUR, falls vorhanden)
11. **Pos. 75:** Lagergeld (EUR, Eingabe)
12. **Pos. 78:** Frachtkosten (EUR, Eingabe)
13. **Pos. 80:** Wiegegebühren (EUR, Eingabe)
14. **Pos. 110:** Gutschriftsbetrag (berechnet: Nettogewicht × Preis - Abzüge)

#### Drying Rule Engine Integration:

- **Automatisch aktiviert**, wenn:
  - `crop_code` vorhanden (aus Artikel-`warengruppe` abgeleitet)
  - `moisture_pct` vorhanden
  - Drying Rule Repository verfügbar
- **Fallback:** Vereinfachte Berechnung, falls Engine nicht verfügbar
- **Trocknungskosten:** Werden automatisch als Pos. 70 hinzugefügt, falls vorhanden
- **Audit:** Regel-ID und Version werden in `calculation_formula` dokumentiert

### 5. NUTS-2-Unterstützung

**Dokumentation:** `docs/harvest-acceptance-nuts2.md`

- **Bedeutung:** "Herkunft/Region der Erzeugung" (nicht Standort des Lagers)
- **Hauptzweck:** Nachhaltigkeitsnachweise / Biomasse-Zertifizierung (RED-II, ISCC, REDcert, SURE)
- **Validierung:** Format 2 Buchstaben + 1-2 Ziffern (z.B. DE12)
- **Versionierung:** `nuts_version` für Audit (z.B. "NUTS 2024")
- **PLZ-Ableitung:** Placeholder-Implementierung (TODO: vollständige Eurostat-Zuordnungstabelle)
- **Mischladungen:** NUTS-2 pro Position unterstützt

### 6. Automatische Wareneingang-Erstellung

**Endpoint:** `POST /{acceptance_id}/release`

- **Bei Freigabe (provisional/final):** Automatische Erstellung eines Stock Movement
- **Sperrbestand:** Ware wird zunächst als "Sperrbestand" gebucht
- **Referenzierung:** `stock_movement_id` wird in `HarvestAcceptance` gespeichert
- **Parameter:** `create_stock_movement` (default: true)

### 7. Preisermittlung

**Priorität:**
1. **Vertragspreis** (`agrar_contracts.fixed_price`)
2. **Artikel-Verkaufspreis** (`articles.sales_price`) - Fallback
3. **TODO:** Tagespreis-API für dynamische Preise

**Crop-Code-Ableitung:**
- Automatisch aus Artikel-`warengruppe`:
  - MAIS → MAIZE
  - WEIZEN → WHEAT
  - GERSTE → BARLEY
  - HAFER → OATS
  - RAPS → RAPESEED
  - ACKERBOHNE → FIELD_BEANS
  - ERBSE → PEAS
  - LUPINE → LUPINS

---

## Datenfluss

```
1. Wiegeschein erstellen (Brutto/Tara/Netto)
   ↓
2. Ernte-Annahme anlegen (POST /harvest-acceptance)
   - Wiegeschein verknüpfen
   - Kunde, Artikel, NUTS-2 erfassen
   ↓
3. Laborwerte erfassen (Windabgang, Besatz, Feuchte, HL-Gewicht)
   ↓
4. Berechnung durchführen (POST /{id}/calculate)
   - Alle 14 Positionen berechnen
   - Drying Rule Engine (falls crop_code vorhanden)
   - Summen aktualisieren
   ↓
5. Freigabe (POST /{id}/release)
   - Status: Draft → Provisional/Final
   - Stock Movement erstellen (Sperrbestand)
   ↓
6. Qualitätsfreigabe (später)
   - Sperrbestand → verfügbar
   ↓
7. Gutschrift erstellen (TODO)
   - Self-Billing Rechnung
   - E-Rechnung (XRechnung/ZUGFeRD)
```

---

## Validierungen & Sicherheit

### Status-Workflow:
- **Draft:** Kann geändert/gelöscht werden
- **Provisional:** Kann geändert werden, nicht gelöscht
- **Final:** Read-only (außer Admin)
- **Credit Note Created:** Read-only
- **Cancelled:** Read-only

### Rollenrechte:
- **Lesen:** Alle authentifizierten Benutzer
- **Schreiben:** Alle authentifizierten Benutzer (für Draft/Provisional)
- **Löschen:** Nur Admin (`require_inventory_admin`)

### Validierungen:
- **NUTS-2:** Format-Validierung (2 Buchstaben + 1-2 Ziffern)
- **Wiegeschein:** Muss existieren und zum Tenant gehören
- **Kunde:** Muss existieren und zum Tenant gehören
- **Artikel:** Muss existieren (falls angegeben)
- **Vertrag:** Muss existieren (falls angegeben)

---

## Offene Punkte / TODOs

### Priorität 1 (für Produktivbetrieb):
1. ⏳ **Tagespreis-API:** Tabelle/API für dynamische Preise (Vertrag > Tagespreis > Artikel)
2. ⏳ **Gutschrift-Erstellung:** Self-Billing Workflow mit E-Rechnung (XRechnung/ZUGFeRD)
3. ⏳ **Qualitätsprotokoll:** Integration für Laborwerte-Import

### Priorität 2 (für Vollständigkeit):
4. ⏳ **Vollständige PLZ → NUTS-2-Zuordnungstabelle:** Eurostat correspondence tables integrieren
5. ⏳ **Dispute-Handling:** Widerspruch gegen Gutschrift
6. ⏳ **Nachträge & Korrekturen:** Storno + Neu Workflow

### Priorität 3 (nice-to-have):
7. ⏳ **Frontend-Integration:** Eingabemaske für Ernte-Annahme
8. ⏳ **Reporting:** Mengen/Qualitäten/Preise nach Herkunftsregion (NUTS-2)
9. ⏳ **Portal-Download:** Trocknungs-/Schwundtabellen für Kunden

---

## Migration ausführen

```bash
# Prüfe Migration-Status
alembic current

# Führe Migration aus
alembic upgrade head

# Prüfe, ob Tabellen erstellt wurden
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptances"
psql -d neuroerp -c "\dt domain_inventory.harvest_acceptance_positions"
```

---

## API-Beispiele

### Ernte-Annahme anlegen:

```json
POST /api/v1/agrar/harvest-acceptance
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

### Berechnung durchführen:

```json
POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/calculate
```

**Response:**
```json
{
  "acceptance_id": "...",
  "positions": [
    {
      "position_number": 10,
      "description": "Angelieferte Menge",
      "quantity_kg": 1000.0,
      "unit": "kg"
    },
    ...
  ],
  "total_net_amount_eur": 2500.00,
  "total_vat_amount_eur": 195.00,
  "total_gross_amount_eur": 2695.00,
  "vat_rate_percent": 7.8
}
```

### Freigabe:

```json
POST /api/v1/agrar/harvest-acceptance/{acceptance_id}/release?release_status=provisional&create_stock_movement=true
```

---

## Referenzen

- **NUTS-2-Dokumentation:** `docs/harvest-acceptance-nuts2.md`
- **Offene Fragen:** `docs/ernte-annahme-pruefung-fragen.md`
- **Datenfeld-Analyse:** `docs/ernte-annahme-datenfeld-analyse.md`
- **Drying Rule Engine:** `docs/drying-rule-engine.md`

---

**Stand:** 2026-02-17  
**Nächster Schritt:** Migration ausführen, dann Frontend-Integration oder Gutschrift-Erstellung

