# Ernte-Annahme - Features Implementation Plan

**Datum:** 2026-02-17  
**Status:** 🚧 In Arbeit

---

## Übersicht

Plan für die Implementierung der erweiterten Features für die Ernte-Annahme-Erfassungsmaske.

---

## Priorisierung

### Priorität 1 (Kritisch für Produktion)

1. ✅ **Qualitätsprotokoll-Tabelle** - Basis für Laborwerte
2. ✅ **Tagespreis-API** - Für dynamische Preise
3. ✅ **Mengenprüfung** - Für Vertragsmengen-Validierung
4. ✅ **Partie/Charge-Generierung** - Für Lagerbuchung

### Priorität 2 (Wichtig für Vollständigkeit)

5. ⏳ **Self-Billing Workflow** - Für Gutschrift-Erstellung
6. ⏳ **Pflichttexte / Kennzeichnung** - Für GoBD-Compliance
7. ⏳ **E-Rechnung-Erstellung** - Für E-Rechnung-Export
8. ⏳ **Dispute-Handling** - Für Widerspruch-Management

### Priorität 3 (Nice-to-have)

9. ⏳ **Import-Funktionalität** - Für Laborwerte-Import
10. ⏳ **Formeln für Zu-/Abschläge** - Für erweiterte Preislogik
11. ⏳ **Eurostat correspondence tables** - Für NUTS-2-Ableitung

---

## Implementierungs-Plan

### Phase 1: Datenbank-Modelle ✅

**Migration:** `09e3b0da2b08_add_quality_protocols_daily_prices_self_billing_dispute_nuts2_20260217.py`

#### 1.1 Qualitätsprotokoll-Tabelle

```sql
CREATE TABLE domain_inventory.quality_protocols (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    harvest_acceptance_id VARCHAR REFERENCES domain_inventory.harvest_acceptances(id),
    protocol_number VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Laborwerte
    moisture_pct DECIMAL(5,2),
    impurities_pct DECIMAL(5,2),
    hl_weight_kg_per_hl DECIMAL(6,2),
    protein_pct DECIMAL(5,2),
    mycotoxin_ppb DECIMAL(10,2),
    
    -- Quelle
    source_type VARCHAR(20), -- manual / import / lims / device
    source_device_id VARCHAR(64),
    source_file_name VARCHAR(255),
    
    -- Status
    is_final BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(64),
    approved_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(64),
    updated_at TIMESTAMP,
    updated_by VARCHAR(64)
);
```

#### 1.2 Tagespreis-Tabelle

```sql
CREATE TABLE domain_inventory.daily_prices (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    article_id VARCHAR REFERENCES domain_inventory.articles(id),
    warengruppe VARCHAR(80),
    crop_code VARCHAR(20), -- MAIZE, WHEAT, BARLEY, etc.
    
    -- Preis
    price_eur_per_ton DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Gültigkeit
    price_date DATE NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    
    -- Quelle
    source_type VARCHAR(20), -- manual / exchange / api
    source_id VARCHAR(64),
    source_name VARCHAR(255),
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(64),
    updated_at TIMESTAMP,
    updated_by VARCHAR(64)
);
```

#### 1.3 Self-Billing Invoice Tabelle

```sql
CREATE TABLE domain_finance.self_billing_invoices (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    harvest_acceptance_id VARCHAR REFERENCES domain_inventory.harvest_acceptances(id),
    
    -- Rechnungsnummern
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    provisional_invoice_number VARCHAR(50),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft / issued / paid / disputed / cancelled
    dispute_status VARCHAR(20), -- none / raised / resolved / rejected
    dispute_reason TEXT,
    dispute_date TIMESTAMP,
    dispute_user_id VARCHAR(64),
    
    -- Beträge
    total_net_amount_eur DECIMAL(15,2) NOT NULL,
    total_vat_amount_eur DECIMAL(15,2) NOT NULL,
    total_gross_amount_eur DECIMAL(15,2) NOT NULL,
    vat_rate_percent DECIMAL(5,2) NOT NULL,
    
    -- E-Rechnung
    einvoice_xml TEXT, -- XRechnung/ZUGFeRD XML
    einvoice_pdf BYTEA, -- PDF (optional)
    einvoice_sent_at TIMESTAMP,
    einvoice_received_at TIMESTAMP,
    
    -- Pflichttexte
    mandatory_texts JSONB, -- Array von Pflichttexten
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(64),
    updated_at TIMESTAMP,
    updated_by VARCHAR(64)
);
```

#### 1.4 Dispute Records Tabelle

```sql
CREATE TABLE domain_finance.dispute_records (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    invoice_id VARCHAR REFERENCES domain_finance.self_billing_invoices(id),
    
    -- Dispute-Details
    dispute_type VARCHAR(30), -- amount / quality / quantity / other
    dispute_reason TEXT NOT NULL,
    disputed_amount_eur DECIMAL(15,2),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'raised', -- raised / resolved / rejected
    resolution_notes TEXT,
    resolved_by VARCHAR(64),
    resolved_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(64),
    updated_at TIMESTAMP,
    updated_by VARCHAR(64)
);
```

#### 1.5 NUTS-2 Correspondence Table

```sql
CREATE TABLE domain_shared.nuts2_postal_codes (
    id VARCHAR PRIMARY KEY,
    postal_code VARCHAR(10) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL DEFAULT 'DE',
    nuts2_code VARCHAR(10) NOT NULL,
    nuts_version VARCHAR(20) NOT NULL DEFAULT 'NUTS 2024',
    
    -- Gültigkeit
    valid_from DATE NOT NULL,
    valid_to DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

---

### Phase 2: Backend-Services

#### 2.1 Quality Protocol Service

**Datei:** `modules/agrar/services/quality_protocol_service.py`

**Funktionen:**
- `create_quality_protocol()` - Neues Qualitätsprotokoll erstellen
- `update_quality_protocol()` - Qualitätsprotokoll aktualisieren
- `finalize_quality_protocol()` - Qualitätsprotokoll finalisieren
- `import_from_file()` - Import aus CSV/JSON/XML
- `get_latest_protocol()` - Neuestes Protokoll für Ernte-Annahme

#### 2.2 Daily Price Service

**Datei:** `modules/agrar/services/daily_price_service.py`

**Funktionen:**
- `get_price_for_date()` - Preis für Datum abrufen
- `create_daily_price()` - Neuen Tagespreis erstellen
- `bulk_import_prices()` - Bulk-Import von Preisen
- `get_price_history()` - Preis-Historie abrufen

#### 2.3 Self-Billing Service

**Datei:** `modules/agrar/services/self_billing_service.py`

**Funktionen:**
- `create_credit_note()` - Gutschrift erstellen
- `generate_einvoice()` - E-Rechnung generieren (XRechnung/ZUGFeRD)
- `add_mandatory_texts()` - Pflichttexte hinzufügen
- `send_einvoice()` - E-Rechnung versenden
- `handle_dispute()` - Dispute verarbeiten

#### 2.4 Lot/Charge Generation Service

**Datei:** `modules/agrar/services/lot_generation_service.py`

**Funktionen:**
- `generate_lot_number()` - Partie/Charge-Nummer generieren
- `create_lot_from_acceptance()` - Partie aus Ernte-Annahme erstellen
- `allocate_to_silos()` - Auf Silo/Partie aufteilen

#### 2.5 Price Adjustment Service

**Datei:** `modules/agrar/services/price_adjustment_service.py`

**Funktionen:**
- `calculate_adjustments()` - Zu-/Abschläge berechnen
- `apply_hl_weight_adjustment()` - HL-Gewicht-Anpassung
- `apply_impurity_adjustment()` - Besatz-Anpassung
- `apply_mycotoxin_adjustment()` - Mykotoxin-Anpassung

---

### Phase 3: API-Endpoints

#### 3.1 Quality Protocol API

**Datei:** `app/api/v1/endpoints/quality_protocols.py`

**Endpoints:**
- `POST /api/v1/agrar/quality-protocols` - Neues Protokoll erstellen
- `GET /api/v1/agrar/quality-protocols/{id}` - Protokoll abrufen
- `PUT /api/v1/agrar/quality-protocols/{id}` - Protokoll aktualisieren
- `POST /api/v1/agrar/quality-protocols/{id}/finalize` - Protokoll finalisieren
- `POST /api/v1/agrar/quality-protocols/import` - Import aus Datei

#### 3.2 Daily Price API

**Datei:** `app/api/v1/endpoints/daily_prices.py`

**Endpoints:**
- `GET /api/v1/agrar/daily-prices` - Preise abrufen (mit Filtern)
- `POST /api/v1/agrar/daily-prices` - Neuen Preis erstellen
- `GET /api/v1/agrar/daily-prices/{article_id}/history` - Preis-Historie
- `POST /api/v1/agrar/daily-prices/bulk-import` - Bulk-Import

#### 3.3 Self-Billing API

**Datei:** `app/api/v1/endpoints/self_billing.py`

**Endpoints:**
- `POST /api/v1/agrar/harvest-acceptance/{id}/create-credit-note` - Gutschrift erstellen
- `GET /api/v1/agrar/self-billing-invoices/{id}` - Gutschrift abrufen
- `POST /api/v1/agrar/self-billing-invoices/{id}/generate-einvoice` - E-Rechnung generieren
- `POST /api/v1/agrar/self-billing-invoices/{id}/send` - E-Rechnung versenden
- `POST /api/v1/agrar/self-billing-invoices/{id}/dispute` - Dispute erstellen
- `GET /api/v1/agrar/self-billing-invoices/{id}/disputes` - Disputes abrufen

#### 3.4 Lot Generation API

**Datei:** `app/api/v1/endpoints/lot_generation.py`

**Endpoints:**
- `POST /api/v1/agrar/harvest-acceptance/{id}/generate-lot` - Partie generieren
- `POST /api/v1/agrar/harvest-acceptance/{id}/allocate-to-silos` - Auf Silo aufteilen

---

### Phase 4: Frontend-Integration

#### 4.1 Quality Protocol Dialog

**Datei:** `packages/frontend-web/src/components/agrar/QualityProtocolDialog.tsx`

**Features:**
- Laborwerte eingeben
- Import aus Datei (CSV/JSON/XML)
- Protokoll finalisieren
- Versionshistorie anzeigen

#### 4.2 Daily Price Management

**Datei:** `packages/frontend-web/src/pages/agrar/daily-prices.tsx`

**Features:**
- Tagespreise verwalten
- Bulk-Import
- Preis-Historie anzeigen
- Preis-Charts

#### 4.3 Self-Billing Workflow

**Erweiterung:** `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`

**Features:**
- Button "Endabrechnung / Gutschrift erzeugen"
- Gutschrift-Vorschau
- E-Rechnung generieren
- E-Rechnung versenden
- Dispute erstellen

---

## Nächste Schritte

1. ✅ Migration erstellen und ausführen
2. ⏳ Backend-Services implementieren
3. ⏳ API-Endpoints implementieren
4. ⏳ Frontend-Integration
5. ⏳ Tests schreiben

---

**Stand:** 2026-02-17  
**Status:** 🚧 In Arbeit


