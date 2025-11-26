# 🎯 Plan: Eliminierung ALLER Mock-Daten - 100% Production Ready

**Datum:** 2025-10-16  
**Ziel:** Keine Mock-Daten mehr - ALLES produktiv & realistisch!

---

## Current Status (BACKEND-STATUS.yml)

### ✅ Real (bereits produktiv)
- **Sales:** Order, Delivery, Invoice (Phase O komplett)
- **Inventory:** Articles, Movements, Stock

### 🔧 Partial (teilweise Mock)
- **Agrar:** PSM real, Saatgut/Dünger mock
- **Finance:** Bookings real, DATEV/SEPA mock

### ❌ Mock (komplett Frontend-Only)
- **CRM:** Keine Persistenz

---

## 🎯 Implementierungs-Plan (3 Phasen)

### Phase 1: CRM Backend (KRITISCH - 2-3 Stunden)

**Tabellen:**
```sql
CREATE TABLE crm_contacts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    type TEXT CHECK(type IN ('customer', 'supplier', 'lead')),
    address_street TEXT,
    address_zip TEXT,
    address_city TEXT,
    address_country TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);

CREATE TABLE crm_leads (
    id TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    source TEXT,
    potential REAL DEFAULT 0,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
    status TEXT CHECK(status IN ('new', 'qualified', 'converted', 'lost')),
    assigned_to TEXT,
    expected_close_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);

CREATE TABLE crm_activities (
    id TEXT PRIMARY KEY,
    contact_id TEXT REFERENCES crm_contacts(id),
    type TEXT CHECK(type IN ('call', 'email', 'meeting', 'visit')),
    date TIMESTAMP NOT NULL,
    subject TEXT,
    notes TEXT,
    status TEXT CHECK(status IN ('planned', 'completed', 'cancelled')),
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);

CREATE TABLE crm_betriebsprofile (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    betriebsform TEXT,
    flaeche_ha REAL,
    tierbestand INTEGER,
    contact_id TEXT REFERENCES crm_contacts(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);
```

**FastAPI-Router:**
```python
# app/crm/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import models, schemas

router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])

@router.post("/contacts", response_model=schemas.Contact)
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    # ... Implementation

@router.get("/contacts", response_model=list[schemas.Contact])
async def list_contacts(db: Session = Depends(get_db)):
    # ... Implementation

@router.get("/contacts/{id}", response_model=schemas.Contact)
async def get_contact(id: str, db: Session = Depends(get_db)):
    # ... Implementation

@router.put("/contacts/{id}", response_model=schemas.Contact)
async def update_contact(id: str, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    # ... Implementation

@router.delete("/contacts/{id}")
async def delete_contact(id: str, db: Session = Depends(get_db)):
    # ... Implementation

# Analog für Leads, Activities, Betriebsprofile
```

---

### Phase 2: Agrar Backend (Saatgut & Dünger - 1-2 Stunden)

**Tabellen:**
```sql
CREATE TABLE agrar_saatgut (
    id TEXT PRIMARY KEY,
    artikelnummer TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sorte TEXT,
    art TEXT,
    zuechter TEXT,
    zulassungsnummer TEXT,
    bsa_zulassung BOOLEAN DEFAULT FALSE,
    eu_zulassung BOOLEAN DEFAULT FALSE,
    ablauf_zulassung DATE,
    tkm REAL,
    keimfaehigkeit REAL,
    aussaatstaerke REAL,
    ek_preis REAL,
    vk_preis REAL,
    waehrung TEXT DEFAULT 'EUR',
    lagerbestand REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);

CREATE TABLE agrar_duenger (
    id TEXT PRIMARY KEY,
    artikelnummer TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    typ TEXT,
    hersteller TEXT,
    n_gehalt REAL,
    p_gehalt REAL,
    k_gehalt REAL,
    s_gehalt REAL,
    mg_gehalt REAL,
    dmv_nummer TEXT,
    eu_zulassung TEXT,
    ablauf_zulassung DATE,
    gefahrstoff_klasse TEXT,
    wassergefaehrdend BOOLEAN DEFAULT FALSE,
    lagerklasse TEXT,
    ek_preis REAL,
    vk_preis REAL,
    lagerbestand REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id TEXT NOT NULL
);
```

**FastAPI-Router:**
```python
# app/agrar/router.py
router = APIRouter(prefix="/api/v1/agrar", tags=["Agrar"])

# Saatgut Endpoints
@router.post("/saatgut")
@router.get("/saatgut")
@router.get("/saatgut/{id}")
@router.put("/saatgut/{id}")
@router.delete("/saatgut/{id}")

# Dünger Endpoints
@router.post("/duenger")
@router.get("/duenger")
@router.get("/duenger/{id}")
@router.put("/duenger/{id}")
@router.delete("/duenger/{id}")
```

---

### Phase 3: Finance Export (DATEV & SEPA - 1 Stunde)

**DATEV-Export (CSV):**
```python
@router.get("/finance/export/datev")
async def export_datev(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    # Hole Buchungen aus DB
    bookings = db.query(Booking).filter(
        Booking.date >= start_date,
        Booking.date <= end_date
    ).all()
    
    # DATEV CSV Format (Standard-Kontenrahmen SKR03/SKR04)
    csv_data = generate_datev_csv(bookings)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=datev-export-{start_date}-{end_date}.csv"}
    )
```

**SEPA-Export (XML pain.001):**
```python
@router.post("/finance/zahlungslaeufe/{id}/sepa")
async def generate_sepa_xml(id: str, db: Session = Depends(get_db)):
    # Hole Zahlungslauf
    run = db.query(PaymentRun).filter(PaymentRun.id == id).first()
    
    # Generiere SEPA pain.001.003.03 XML
    sepa_xml = generate_sepa_pain001(run)
    
    return Response(
        content=sepa_xml,
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=sepa-{id}.xml"}
    )
```

---

## 📋 Datei-Struktur

### Neue Dateien (pro Domain)

**CRM:**
```
app/crm/
├── __init__.py
├── models.py          # SQLAlchemy Models
├── schemas.py         # Pydantic Schemas
├── router.py          # FastAPI Router
├── services.py        # Business Logic
└── seed.py            # Seed-Daten (10+ Kontakte, Leads, etc.)
```

**Agrar:**
```
app/agrar/
├── models.py          # Saatgut, Dünger Models
├── schemas.py         # Pydantic Schemas
├── router.py          # Erweitern um Saatgut/Dünger
└── seed.py            # Seed-Daten
```

**Finance:**
```
app/finance/
├── exports/
│   ├── datev.py       # DATEV-Export-Logik
│   └── sepa.py        # SEPA-XML-Generator
└── router.py          # Erweitern um Export-Endpoints
```

---

## Migration-Script

```sql
-- migrations/002_crm_agrar_finance_real.sql

-- CRM Tables
CREATE TABLE IF NOT EXISTS crm_contacts (...);
CREATE TABLE IF NOT EXISTS crm_leads (...);
CREATE TABLE IF NOT EXISTS crm_activities (...);
CREATE TABLE IF NOT EXISTS crm_betriebsprofile (...);

-- Agrar Tables
CREATE TABLE IF NOT EXISTS agrar_saatgut (...);
CREATE TABLE IF NOT EXISTS agrar_duenger (...);

-- Finance Tables (bereits vorhanden, nur Indizes)
CREATE INDEX IF NOT EXISTS idx_bookings_date ON finance_bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_account ON finance_bookings(account_id);

-- Seed-Daten
INSERT INTO crm_contacts (...) VALUES (...); -- 10+ Kontakte
INSERT INTO crm_leads (...) VALUES (...);    -- 10+ Leads
INSERT INTO agrar_saatgut (...) VALUES (...); -- 10+ Saatgut
INSERT INTO agrar_duenger (...) VALUES (...); -- 10+ Dünger
```

---

## Integration in main.py

```python
# main.py
from app.crm import router as crm_router
from app.agrar import router as agrar_router
from app.finance import router as finance_router

app.include_router(crm_router)
app.include_router(agrar_router)
app.include_router(finance_router)
```

---

## Zeitplan

| Phase | Aufwand | Priorität |
|-------|---------|-----------|
| CRM Backend | 2-3h | KRITISCH |
| Agrar (Saatgut/Dünger) | 1-2h | HOCH |
| Finance Export (DATEV/SEPA) | 1h | MITTEL |
| **GESAMT** | **4-6h** | - |

---

## Abnahme-Kriterien

- [ ] Alle API-Endpoints funktional (200 OK)
- [ ] CRUD vollständig (Create, Read, Update, Delete)
- [ ] Daten persistiert in DB
- [ ] Seed-Daten vorhanden (10+ pro Entität)
- [ ] Frontend nutzt echte APIs (keine Fallbacks)
- [ ] BACKEND-STATUS.yml: Alle Domains = "real"

---

**Soll ich jetzt sofort mit Phase 1 (CRM Backend) starten?** 🚀

