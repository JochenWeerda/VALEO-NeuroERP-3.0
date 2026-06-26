# Drying Rule Engine (Trocknungsschwund & Trocknungskosten)

Diese Implementierung liefert eine **robuste, konfigurierbare Berechnung** für:

- **Rechnungsgewicht / Trocknungsschwund** (Mengenabzug in kg/%)
- optional **Trocknungskosten** (EUR-Abzug)

und trennt diese beiden Aspekte strikt (keine doppelte Feuchte-Logik).

## Komponenten

- **Engine**: `modules/agrar/services/drying_rule_engine.py`
  - Methoden:
    - `LOOKUP_TABLE`
    - `FACTOR_FROM_BASE` (stufig)
    - `DRY_MATTER_NORMALIZATION`
  - Rounding/Clamp:
    - `ROUND_NEAREST | ROUND_UP | ROUND_DOWN` auf **0.1%**
    - `CLAMP_TO_MAX | HARD_ERROR` (out-of-range & missing row)
  - Ergebnis enthält `used_*` Felder (Audit) + `warnings[]`

- **DB-Config** (domain_inventory):
  - `drying_rule_sets` (mit Versionsverwaltung, Audit, Vertrags-/Kundenverknüpfung, DMS-Referenz)
  - `drying_rule_lookup_rows`
  - `drying_rule_factor_ranges`
  - Migrationen:
    - `alembic/versions/agrar_drying_rules_20260217.py` (Basis)
    - `alembic/versions/agrar_drying_rules_audit_contract_dms_20260217.py` (Erweiterungen)
  - Seed (Starter): `scripts/seed-drying-rules.sql`

- **API**:
  - **Compute**:
    - `POST /api/v1/agrar/settlements/drying/compute`
      - Rechnet trocken-basiertes Rechnungsgewicht + optional Fee aus.
      - Unterstützt `contract_id` und `customer_id` für Priorisierung.
  - **Settlement-Integration**:
    - `POST /api/v1/agrar/settlements`
      - akzeptiert optional `drying: { crop_code, site_id?, moisture_pct, calc_date?, rounding_mode?, contract_id?, customer_id? }`
      - Persistiert Snapshot in `AgrarSettlement.drying_result`
      - setzt (wenn `billing_quantity_kg` nicht explizit übergeben) `billing_quantity_kg = invoice_weight_kg`
      - wenn Fee vorhanden: erzeugt zusätzlich eine Deduction-Line (`deduction_type="drying"`, `mode="fixed"`)
  - **CRUD (Admin-only Write, Read für alle)**:
    - `GET /api/v1/agrar/settlements/drying-rules` – Liste (mit Filtern: crop_code, contract_id, customer_id, is_customer_specific)
    - `GET /api/v1/agrar/settlements/drying-rules/{rule_id}` – Einzelne Regel
    - `POST /api/v1/agrar/settlements/drying-rules` – Anlegen (nur Admin)
    - `PUT /api/v1/agrar/settlements/drying-rules/{rule_id}` – Aktualisieren (nur Admin, erstellt neue Version bei Änderungen)
    - `DELETE /api/v1/agrar/settlements/drying-rules/{rule_id}` – Soft-Delete (nur Admin)
    - `GET /api/v1/agrar/settlements/drying-rules/{rule_id}/download` – Portal-Download (für Kunden)
  - **Lookup-Rows CRUD (Admin-only)**:
    - `GET /api/v1/agrar/settlements/drying-rules/{rule_id}/lookup-rows` – Liste
    - `POST /api/v1/agrar/settlements/drying-rules/lookup-rows` – Anlegen
    - `PUT /api/v1/agrar/settlements/drying-rules/lookup-rows/{row_id}` – Aktualisieren
    - `DELETE /api/v1/agrar/settlements/drying-rules/lookup-rows/{row_id}` – Löschen
  - **Factor-Ranges CRUD (Admin-only)**:
    - `GET /api/v1/agrar/settlements/drying-rules/{rule_id}/factor-ranges` – Liste
    - `POST /api/v1/agrar/settlements/drying-rules/factor-ranges` – Anlegen (mit Überlappungsprüfung)
    - `PUT /api/v1/agrar/settlements/drying-rules/factor-ranges/{range_id}` – Aktualisieren
    - `DELETE /api/v1/agrar/settlements/drying-rules/factor-ranges/{range_id}` – Löschen

## Features

### Versionsverwaltung & Audit

- **Version**: Automatische Versionsnummer (bei Änderungen wird neue Version erstellt, alte bleibt für Audit)
- **Audit-Felder**: `created_at`, `created_by`, `updated_at`, `updated_by`
- **Unveränderbarkeit**: Alte Versionen bleiben erhalten (GoBD-konform)

### Rollenrechte

- **Schreibrechte**: Nur Admin (`require_inventory_admin`) kann Regeln anlegen/ändern/löschen
- **Leserechte**: Alle authentifizierten Benutzer können Regeln einsehen
- **Portal-Download**: Kunden können ihre Vertragsregeln herunterladen

### Vertragsverknüpfung

- **`contract_id`**: Verknüpfung zu Ankaufskontrakt (fester Vertragsteil)
- **Priorität bei Regelauswahl**:
  1. Kundenspezifische Regel (`customer_id` + `is_customer_specific=True`)
  2. Vertragsregel (`contract_id`)
  3. Standortregel (`site_id`)
  4. Globale Regel (Fallback)

### Kundenspezifische Sonderregelungen

- **`customer_id`**: Kunde für Sonderregelung
- **`is_customer_specific`**: Flag für kundenspezifische Regel
- **`justification`**: **Pflicht** bei Sonderregelungen (z.B. "Freigrenze ab 15,5% Feuchte")
- **Validierung**: Wenn `is_customer_specific=True`, dann `customer_id` und `justification` erforderlich

### DMS-Integration

- **`document_id`**: DMS-Referenz für Tabelle/Formel-Dokument
- **Portal-Download**: `GET /drying-rules/{rule_id}/download` (später: PDF-Export oder DMS-Dokument)

## Mapping auf „Ernte“-Positionen (konzeptionell)

- **Pos. 40 (Trocknungsverlust/Schwund)**: `loss_kg` und/oder `loss_pct` (kein EUR Betrag)
- **Pos. 70 (Trocknungskosten)**: `drying_fee_eur` (falls vorhanden)
- **Audit/GoBD**: `used_rule_set_id`, `used_rule_version`, `used_row_moisture_pct` + Snapshot in `drying_result`

## Tests

- Unit Tests: `tests/test_drying_rule_engine.py`
  - Mais: 1000kg @ 20.0% → loss_pct=6.75; invoice=932.5
  - Raps: 1000kg @ 12.0% base9 → invoice≈967.03297
  - Weizen: 1000kg @ 18.0% base14.5, factor=1.3 → entzug=3.5; loss_pct=4.55; invoice=954.5
  - Rounding: 20.27% → 20.3/20.3/20.2 (nearest/up/down)

## Verwendung

### Regel anlegen (Admin)

```json
POST /api/v1/agrar/settlements/drying-rules
{
  "crop_code": "MAIZE",
  "method": "LOOKUP_TABLE",
  "base_moisture_pct": 15.0,
  "contract_id": "contract-uuid-123",
  "document_id": "dms-doc-456"
}
```

### Kundenspezifische Sonderregelung (Admin)

```json
POST /api/v1/agrar/settlements/drying-rules
{
  "crop_code": "WHEAT",
  "method": "FACTOR_FROM_BASE",
  "base_moisture_pct": 14.5,
  "customer_id": "customer-uuid-789",
  "is_customer_specific": true,
  "justification": "Freigrenze ab 15,5% Feuchte gemäß Sondervereinbarung 2025"
}
```

### Lookup-Rows hinzufügen (Admin)

```json
POST /api/v1/agrar/settlements/drying-rules/lookup-rows
{
  "rule_set_id": "rule-uuid-123",
  "moisture_pct": 20.0,
  "entzug_pct_points": 5.0,
  "loss_pct": 6.75,
  "fee_value": 2.50,
  "fee_unit": "EUR_PER_T"
}
```

### Berechnung durchführen

```json
POST /api/v1/agrar/settlements/drying/compute
{
  "crop_code": "MAIZE",
  "net_weight_kg": 1000.0,
  "moisture_pct": 20.0,
  "contract_id": "contract-uuid-123",
  "customer_id": "customer-uuid-789"
}
```

Die Engine wählt automatisch die passende Regel nach Priorität (Customer > Contract > Site > Global).


