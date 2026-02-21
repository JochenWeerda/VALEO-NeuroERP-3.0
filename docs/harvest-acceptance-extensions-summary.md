# Harvest Acceptance - Erweiterungen nach praxisnahen Default-Entscheidungen

**Datum:** 2026-02-17  
**Status:** ✅ Implementiert

---

## Übersicht

Erweiterung der Harvest Acceptance Implementierung gemäß den praxisnahen Default-Entscheidungen für den Landhandel-Standard.

---

## Implementierte Erweiterungen

### 1. Preisermittlung (`pricing_mode` + `price_source_id`)

**Model:** `HarvestAcceptance`
- `pricing_mode`: `fixed_contract` | `spot_daily` | `exchange_fix_later` (default: `spot_daily`)
- `price_source_id`: Referenz zu Preisquelle (daily_price_id, exchange_index_id, etc.)

**Validierung:**
- `fixed_contract` ⇒ `contract_id` required
- `spot_daily` ⇒ `price_source_id` optional (kann auch aus daily_prices Tabelle geladen werden)
- `exchange_fix_later` ⇒ TODO: pricing_fixation_status + Referenz auf Börsen/Indexdaten

**API:**
- `HarvestAcceptanceCreate`: `pricing_mode` und `price_source_id` hinzugefügt
- `HarvestAcceptanceUpdate`: `pricing_mode` und `price_source_id` hinzugefügt
- `HarvestAcceptanceOut`: `pricing_mode` und `price_source_id` hinzugefügt
- Validierung in `validate_pricing_mode()` implementiert

---

### 2. Erweiterte Status-Workflow

**Model:** `HarvestAcceptance.release_status`
- Erweitert von: `draft` | `provisional` | `final`
- Zu: `draft` | `provisional` | `final` | `credit_note_created` | `paid` | `disputed` | `cancelled`

**Status-Übergänge:**
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

**API:**
- `ReleaseStatus` Literal erweitert
- Kommentar in Migration aktualisiert

---

### 3. Harvest Acceptance Lines (für Silo/Partie-Splits)

**Model:** `HarvestAcceptanceLine` (NEU)

**Felder:**
- `harvest_acceptance_id`: FK zu `harvest_acceptances`
- `line_number`: Zeilennummer (1, 2, 3, ...)
- `silo_id`: Silo-Nr./Lagerort
- `lot_id`: Partie/Charge
- `qty_kg_allocated`: Zugeordnete Menge (kg)
- `notes`: Bemerkungen zur Verteilung

**Default-Entscheidung:**
- 1 Wiegeschein = 1 Ernte-Annahme, aber mit Zeilen für Verteilungen
- Constraint: Sum(line.qty) = Wiegeschein.netto (± Rundungstoleranz)

**Migration:**
- Tabelle `harvest_acceptance_lines` erstellt
- Index: `ix_harvest_acceptance_lines_acceptance`

---

### 4. Supplier Tax Profiles (Steuerprofile mit Gültigkeit)

**Model:** `SupplierTaxProfile` (NEU)

**Felder:**
- `supplier_id`: FK zu `business_partners`
- `taxation_type`: `regular` | `ustg24_flat_rate` | `small_business`
- `vat_id`: USt-ID (optional)
- `valid_from`: Gültig ab
- `valid_to`: Gültig bis (NULL = unbegrenzt)
- `notes`: Hinweise/Texts

**Priorität:**
- Lieferant-Profil > Artikel/Warengruppe > Standard
- (weil §24/Kleinunternehmer lieferantenbezogen ist)

**Migration:**
- Tabelle `supplier_tax_profiles` erstellt
- Index: `ix_supplier_tax_profiles_supplier_valid` (für Gültigkeitsprüfung)

---

### 5. Price Adjustment Rules (Konfigurierbare Zu-/Abschläge)

**Model:** `PriceAdjustmentRule` (NEU)

**Felder:**
- `article_id`: Artikel (optional, wenn warengruppe-basiert)
- `warengruppe`: Warengruppe (optional, wenn artikel-basiert)
- `adjustment_type`: `hl_weight` | `impurity` | `mycotoxin` | `other`
- `parameter_name`: Parameter (z.B. 'hl_weight_kg_per_hl', 'impurity_pct')
- `method`: `table` | `factor` | `percentage`
- `steps`: Staffeln/Tabelle (JSONB)
- `effective_from`: Gültig ab
- `effective_to`: Gültig bis (NULL = unbegrenzt)

**Default-Entscheidung:**
- Rules konfigurierbar, nicht hart codieren
- Produkt- & gültigkeitsbezogen
- Beispiele: HL-Gewicht, Besatz-Staffel, Mykotoxin, etc.

**Migration:**
- Tabelle `price_adjustment_rules` erstellt
- Index: `ix_price_adjustment_rules_article_valid` (für Regel-Suche)

---

## Migration

**Datei:** `alembic/versions/c4d5e6f7a8b9_add_harvest_acceptance_extensions_20260217.py`

**Änderungen:**
1. Erweitert `harvest_acceptances` um `pricing_mode`, `price_source_id`
2. Erweitert Status-Workflow (Kommentar aktualisiert)
3. Erstellt `harvest_acceptance_lines` Tabelle
4. Erstellt `supplier_tax_profiles` Tabelle
5. Erstellt `price_adjustment_rules` Tabelle

**Revisions:**
- `down_revision`: `b38680c2f581` (Harvest Acceptance Basis-Migration)
- `revision`: `c4d5e6f7a8b9`

---

## API-Änderungen

### Pydantic Models

**`HarvestAcceptanceCreate`:**
- `pricing_mode: PricingMode = Field("spot_daily", ...)`
- `price_source_id: Optional[str] = Field(None, ...)`
- Validierung: `validate_pricing_mode()`

**`HarvestAcceptanceUpdate`:**
- `pricing_mode: Optional[PricingMode] = None`
- `price_source_id: Optional[str] = Field(None, ...)`

**`HarvestAcceptanceOut`:**
- `pricing_mode: str`
- `price_source_id: Optional[str]`

### Imports

**Erweitert:**
```python
from app.infrastructure.models import (
    HarvestAcceptance,
    HarvestAcceptancePosition,
    HarvestAcceptanceLine,      # NEU
    SupplierTaxProfile,         # NEU
    PriceAdjustmentRule,        # NEU
    ...
)
```

---

## Nächste Schritte (TODO)

### 1. API-Endpoints für neue Modelle

- [ ] CRUD für `HarvestAcceptanceLine`
- [ ] CRUD für `SupplierTaxProfile`
- [ ] CRUD für `PriceAdjustmentRule`

### 2. Berechnungslogik erweitern

- [ ] Integration von `PriceAdjustmentRule` in `harvest_calculator.py`
- [ ] Windabgang-Modus (`wind_loss_mode`: `info` | `settlement`)
- [ ] Besatz-Regel-Engine (`impurity_method`, `impurity_steps`)

### 3. Validierung erweitern

- [ ] `exchange_fix_later`: pricing_fixation_status + Referenz auf Börsen/Indexdaten
- [ ] Constraint: Sum(harvest_acceptance_lines.qty) = Wiegeschein.netto (± Rundungstoleranz)

### 4. Tagespreis-API

- [ ] `daily_prices` Tabelle/API für dynamische Preise
- [ ] Integration in Preisermittlung (Vertrag > Tagespreis > Artikel)

---

## Status

✅ **Abgeschlossen:**
- Modelle erstellt (`HarvestAcceptanceLine`, `SupplierTaxProfile`, `PriceAdjustmentRule`)
- `HarvestAcceptance` erweitert (`pricing_mode`, `price_source_id`)
- Status-Workflow erweitert
- Migration erstellt
- API-Models erweitert
- Validierung implementiert
- Imports aktualisiert

⏳ **TODO:**
- API-Endpoints für neue Modelle
- Berechnungslogik erweitern
- Tagespreis-API

---

**Stand:** 2026-02-17  
**Bereit für:** Migration ausführen


