# Ernte-Annahme - Finale Features Implementierung

**Datum:** 2026-02-17  
**Status:** ✅ Alle verbleibenden Features implementiert

---

## Übersicht

Alle vier verbleibenden Features wurden erfolgreich implementiert:

1. ✅ **Supplier Tax Profile Integration** - Automatische Ermittlung von `taxation_type`
2. ✅ **Partie/Charge-Generierung** - Automatische Generierung bei Release
3. ✅ **Price Adjustment Formulas** - Konfigurierbare Zu-/Abschläge (HL-Gewicht, Besatz, Mykotoxin)
4. ✅ **NUTS-2 Eurostat Tables** - PLZ zu NUTS-2 Mapping über Datenbank

---

## 1. Supplier Tax Profile Integration ✅

### Implementierung

**Datei:** `modules/agrar/services/tax_profile_service.py`

#### Funktion: `get_taxation_type_for_supplier()`

- ✅ Ermittelt `taxation_type` aus `SupplierTaxProfile` Tabelle
- ✅ Berücksichtigt Gültigkeitszeitraum (`valid_from`, `valid_to`)
- ✅ Priorität: Supplier Tax Profile > Fallback "regular"
- ✅ Integration in `harvest_acceptance.py` Release-Endpoint

**Verwendung:**
```python
taxation_type = get_taxation_type_for_supplier(
    db=db,
    supplier_id=acceptance.customer_id,  # Bei Ernte-Annahme ist customer_id der Lieferant
    tenant_id=tenant_id,
    effective_date=acceptance.delivery_date,
)
```

---

## 2. Partie/Charge-Generierung ✅

### Implementierung

**Datei:** `modules/agrar/services/partie_service.py`

#### Funktionen:

1. **`generate_lot_number()`**
   - ✅ Generiert automatisch Partie-Nummer
   - ✅ Format: `{PREFIX}-{YYYYMMDD}-{SEQUENCE}` (z.B. `LOT-20260217-001`)
   - ✅ Sequenznummer basierend auf bestehenden Partien

2. **`create_harvest_acceptance_lines()`**
   - ✅ Erstellt `HarvestAcceptanceLine` Einträge für Silo-Verteilungen
   - ✅ Automatische Partie-Generierung, falls nicht vorhanden

**Integration:**
- ✅ Automatische Generierung bei `release_status="final"`
- ✅ Erstellt `HarvestAcceptanceLine` mit generierter Partie-Nummer
- ✅ Verwendet Nettogewicht aus Wiegeschein

---

## 3. Price Adjustment Formulas ✅

### Implementierung

**Datei:** `modules/agrar/services/price_adjustment_service.py`

#### Funktionen:

1. **`calculate_price_adjustment()`**
   - ✅ Berechnet Preis-Anpassung basierend auf konfigurierten Regeln
   - ✅ Unterstützt: `hl_weight`, `impurity`, `mycotoxin`, `other`
   - ✅ Methoden: `table`, `factor`, `percentage`
   - ✅ Artikel- oder Warengruppe-spezifische Regeln

2. **`apply_price_adjustments()`**
   - ✅ Wendet alle konfigurierten Anpassungen an
   - ✅ Gibt finalen Preis und Liste der Anpassungen zurück

**Integration:**
- ✅ Automatische Anwendung in `POST /{acceptance_id}/calculate`
- ✅ Verwendet HL-Gewicht, Besatz, Mykotoxin aus Quality Protocol
- ✅ Gibt Warnungen aus, wenn Anpassungen angewendet wurden

**Beispiel:**
```python
adjusted_price, adjustments = apply_price_adjustments(
    db=db,
    tenant_id=tenant_id,
    base_price_eur_per_ton=unit_price_eur_per_ton,
    article_id=acceptance.article_id,
    hl_weight_kg_per_hl=hl_weight_kg_per_hl,
    impurity_pct=impurities_pct,
    mycotoxin_ppb=mycotoxin_ppb,
    effective_date=acceptance.delivery_date,
)
```

---

## 4. NUTS-2 Eurostat Tables ✅

### Implementierung

**Datei:** `modules/agrar/services/nuts2_service.py`

#### Funktionen:

1. **`derive_nuts2_from_postal_code()`**
   - ✅ Leitet NUTS-2-Code aus PLZ ab (über `Nuts2PostalCode` Tabelle)
   - ✅ Berücksichtigt Gültigkeitszeitraum
   - ✅ Fallback auf vereinfachte Zuordnung (wenn Tabelle nicht gefüllt)

2. **`bulk_import_nuts2_postal_codes()`**
   - ✅ Importiert NUTS-2 Postal Code Zuordnungen in Bulk
   - ✅ Für zukünftige Integration von Eurostat-Daten

**Integration:**
- ✅ Erweitert `derive_nuts2_from_postal_code()` in `harvest_acceptance.py`
- ✅ Verwendet Datenbank-Session für Lookup
- ✅ Fallback auf vereinfachte Zuordnung

---

## API-Änderungen

### Geänderte Endpoints

1. **POST `/{acceptance_id}/calculate`**
   - ✅ Wendet Preis-Anpassungen automatisch an
   - ✅ Verwendet HL-Gewicht, Besatz, Mykotoxin aus Quality Protocol
   - ✅ Gibt Warnungen für angewendete Anpassungen aus

2. **POST `/{acceptance_id}/release`**
   - ✅ Erstellt automatisch Partie/Charge bei `release_status="final"`
   - ✅ Verwendet `get_taxation_type_for_supplier()` für Self-Billing

3. **POST `/{acceptance_id}/derive-nuts2`**
   - ✅ Verwendet `Nuts2PostalCode` Tabelle für Lookup
   - ✅ Fallback auf vereinfachte Zuordnung

---

## Neue Services

### 1. Tax Profile Service

- ✅ `modules/agrar/services/tax_profile_service.py`
- ✅ Funktion: `get_taxation_type_for_supplier()`

### 2. Partie Service

- ✅ `modules/agrar/services/partie_service.py`
- ✅ Funktionen: `generate_lot_number()`, `create_harvest_acceptance_lines()`

### 3. Price Adjustment Service

- ✅ `modules/agrar/services/price_adjustment_service.py`
- ✅ Funktionen: `calculate_price_adjustment()`, `apply_price_adjustments()`

### 4. NUTS-2 Service

- ✅ `modules/agrar/services/nuts2_service.py`
- ✅ Funktionen: `derive_nuts2_from_postal_code()`, `bulk_import_nuts2_postal_codes()`

---

## Exports

### `modules/agrar/services/__init__.py`

Alle neuen Services wurden exportiert:

```python
from .tax_profile_service import get_taxation_type_for_supplier
from .partie_service import generate_lot_number, create_harvest_acceptance_lines
from .price_adjustment_service import apply_price_adjustments, calculate_price_adjustment
from .nuts2_service import derive_nuts2_from_postal_code, bulk_import_nuts2_postal_codes
```

---

## Nächste Schritte

### Backend

1. ⏳ **Datenbank-Seeding:**
   - NUTS-2 Postal Code Tabelle mit Eurostat-Daten füllen
   - Beispiel-Regeln für Price Adjustments anlegen

2. ⏳ **Weitere Features:**
   - E-Rechnung-Generierung (XRechnung/ZUGFeRD) vollständig implementieren
   - Dispute-Handling UI

### Frontend

3. ⏳ **UI-Integration:**
   - Partie/Charge-Verwaltung
   - Price Adjustment Rules Konfiguration
   - NUTS-2 Import-Dialog

---

## Dateien

### Neue Services

- ✅ `modules/agrar/services/tax_profile_service.py`
- ✅ `modules/agrar/services/partie_service.py`
- ✅ `modules/agrar/services/price_adjustment_service.py`
- ✅ `modules/agrar/services/nuts2_service.py`

### Geänderte Dateien

- ✅ `app/api/v1/endpoints/harvest_acceptance.py`
- ✅ `modules/agrar/services/__init__.py`

### Dokumentation

- ✅ `docs/ernte-annahme-final-features-summary.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ Alle verbleibenden Features implementiert, bereit für Tests und Migration


