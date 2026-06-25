# Ernte-Annahme - Service-Integration Zusammenfassung

**Datum:** 2026-02-17  
**Status:** ✅ Integration in Harvest Acceptance API abgeschlossen

---

## Übersicht

Die drei neuen Services (Quality Protocol, Daily Price, Self-Billing) wurden erfolgreich in die Harvest Acceptance API integriert.

---

## 1. Quality Protocol Integration ✅

### Implementierung

**Datei:** `app/api/v1/endpoints/harvest_acceptance.py`

#### GET `/{acceptance_id}`

- ✅ Lädt automatisch Quality Protocol (falls vorhanden)
- ✅ Setzt `quality_protocol_id` auf Harvest Acceptance, wenn Protokoll gefunden wird

#### POST `/{acceptance_id}/calculate`

- ✅ Liest Laborwerte aus Quality Protocol (höchste Priorität)
- ✅ Fallback auf Wiegeschein, wenn kein Protokoll vorhanden
- ✅ Unterstützt `moisture_pct`, `impurities_pct`, `hl_weight_kg_per_hl`
- ✅ Liest zusätzliche Werte aus `other_values` (z.B. `windage_pct`)

**Priorität:**
1. Quality Protocol (wenn `is_final=True`)
2. Wiegeschein (Fallback)

---

## 2. Daily Price Integration ✅

### Implementierung

**Datei:** `app/api/v1/endpoints/harvest_acceptance.py`

#### POST `/{acceptance_id}/calculate`

- ✅ Ermittelt Tagespreis für Verträge mit `pricing_model="follow"`
- ✅ Verwendet `DailyPriceRepository` für Preis-Lookup
- ✅ Filtert nach `article_id`, `crop_code`, `price_date`
- ✅ Setzt `price_source_id` auf Harvest Acceptance
- ✅ Gibt Warnung aus, wenn kein Tagespreis gefunden wird

**Preisermittlung (Priorität):**
1. Vertrag (fixed price)
2. Tagespreis (für `pricing_model="follow"`)
3. Artikel-Preis (Fallback)

---

## 3. Self-Billing Integration ✅

### Implementierung

**Datei:** `app/api/v1/endpoints/harvest_acceptance.py`

#### GET `/{acceptance_id}`

- ✅ Lädt Self-Billing Invoice (falls vorhanden)
- ✅ Gibt Invoice-Informationen in Response zurück:
  - `invoice_number`
  - `status`
  - `dispute_status`
  - `total_gross_amount_eur`

#### POST `/{acceptance_id}/release`

- ✅ Neuer Parameter: `create_credit_note` (optional, default: `false`)
- ✅ Erstellt automatisch Self-Billing Gutschrift bei `release_status="final"`
- ✅ Prüft, ob `total_gross_amount_eur` gesetzt ist
- ✅ Verwendet `vat_rate_percent` aus Harvest Acceptance
- ✅ Setzt `invoice_id` und `release_status="credit_note_created"`

**Workflow:**
1. Berechnung durchführen (`/calculate`)
2. Freigabe mit `create_credit_note=true` (`/release`)
3. Status wird automatisch auf `credit_note_created` gesetzt

---

## 4. Mengenprüfung (Contract Validation) ✅

### Implementierung

**Datei:** `app/api/v1/endpoints/harvest_acceptance.py`

#### POST `/{acceptance_id}/calculate`

- ✅ Prüft Vertragsmengen bei `contract_id` vorhanden
- ✅ Vergleicht `delivered_quantity_kg` mit `contract.remaining_quantity_kg`
- ✅ Gibt Warnung aus, wenn Liefermenge verfügbare Vertragsmenge überschreitet

**Warnung:**
```
"Warnung: Liefermenge (X kg) überschreitet verfügbare Vertragsmenge (Y kg)"
```

---

## API-Änderungen

### Neue Imports

```python
from modules.agrar.services.quality_protocol_service import (
    get_latest_protocol,
)
from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl
from modules.agrar.services.daily_price_service import (
    get_price_for_date,
    DailyPriceFilter,
)
from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl
from modules.agrar.services.self_billing_service import (
    create_credit_note,
    CreditNoteCreate,
)
from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
```

### Geänderte Endpoints

1. **GET `/{acceptance_id}`**
   - Lädt Quality Protocol automatisch
   - Lädt Self-Billing Invoice (falls vorhanden)

2. **POST `/{acceptance_id}/calculate`**
   - Liest Laborwerte aus Quality Protocol
   - Ermittelt Tagespreis für Verträge
   - Prüft Vertragsmengen

3. **POST `/{acceptance_id}/release`**
   - Neuer Parameter: `create_credit_note`
   - Erstellt Self-Billing Gutschrift automatisch

---

## Nächste Schritte

### Backend

1. ⏳ **Supplier Tax Profile Integration:**
   - Hole `taxation_type` aus `supplier_tax_profiles` Tabelle
   - Verwende für Self-Billing Gutschrift

2. ⏳ **Partie/Charge-Generierung:**
   - Automatische Generierung bei Release
   - Verknüpfung mit `HarvestAcceptanceLine`

3. ⏳ **Weitere Features:**
   - Formeln für Zu-/Abschläge (HL-Gewicht, Besatz, Mykotoxin)
   - Eurostat correspondence tables für NUTS-2

### Frontend

4. ⏳ **UI-Integration:**
   - Quality Protocol Dialog
   - Daily Price Management
   - Self-Billing Workflow-Button

---

## Dateien

### Geänderte Dateien

- ✅ `app/api/v1/endpoints/harvest_acceptance.py`

### Dokumentation

- ✅ `docs/ernte-annahme-integration-summary.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ Service-Integration abgeschlossen, bereit für Tests


