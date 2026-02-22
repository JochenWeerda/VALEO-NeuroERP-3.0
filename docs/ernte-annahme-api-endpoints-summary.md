# Ernte-Annahme - API-Endpoints Zusammenfassung

**Datum:** 2026-02-17  
**Status:** ✅ API-Endpoints implementiert

---

## Übersicht

Drei neue API-Endpoint-Dateien für erweiterte Features der Ernte-Annahme-Erfassungsmaske wurden implementiert:

1. **Quality Protocols API** - Verwaltung von Qualitätsprotokollen
2. **Daily Prices API** - Verwaltung von Tagespreisen
3. **Self-Billing API** - Verwaltung von Self-Billing Gutschriften

---

## 1. Quality Protocols API ✅

**Datei:** `app/api/v1/endpoints/quality_protocols.py`  
**Prefix:** `/api/v1/agrar/quality-protocols`

### Endpoints

| Method | Endpoint | Beschreibung | Status |
|--------|----------|--------------|--------|
| POST | `/` | Neues Protokoll erstellen | ✅ |
| GET | `/{protocol_id}` | Protokoll abrufen | ✅ |
| GET | `/harvest-acceptance/{harvest_acceptance_id}` | Alle Protokolle für Ernte-Annahme | ✅ |
| GET | `/harvest-acceptance/{harvest_acceptance_id}/latest` | Neuestes Protokoll | ✅ |
| PUT | `/{protocol_id}` | Protokoll aktualisieren | ✅ |
| POST | `/{protocol_id}/finalize` | Protokoll finalisieren | ✅ |
| POST | `/import/csv` | Import aus CSV | ✅ |
| POST | `/import/json` | Import aus JSON | ✅ |

### Features

- ✅ Vollständiges CRUD
- ✅ Versionsverwaltung
- ✅ Import-Funktionalität (CSV/JSON)
- ✅ Finalisierung mit Freigabe
- ✅ Tenant-Isolation

---

## 2. Daily Prices API ✅

**Datei:** `app/api/v1/endpoints/daily_prices.py`  
**Prefix:** `/api/v1/agrar/daily-prices`

### Endpoints

| Method | Endpoint | Beschreibung | Status |
|--------|----------|--------------|--------|
| GET | `/` | Preise abrufen (mit Filtern) | ✅ |
| GET | `/{price_id}` | Preis abrufen | ✅ |
| POST | `/` | Neuen Preis erstellen (Admin-only) | ✅ |
| POST | `/bulk-import` | Bulk-Import (Admin-only) | ✅ |
| GET | `/{article_id}/history` | Preis-Historie | ✅ |

### Features

- ✅ Flexible Preisermittlung (Artikel/Warengruppe/Crop Code)
- ✅ Gültigkeitsprüfung
- ✅ Bulk-Import
- ✅ Preis-Historie für Charts
- ✅ Admin-only für Write-Operationen

---

## 3. Self-Billing API ✅

**Datei:** `app/api/v1/endpoints/self_billing.py`  
**Prefix:** `/api/v1/agrar/self-billing`

### Endpoints

| Method | Endpoint | Beschreibung | Status |
|--------|----------|--------------|--------|
| POST | `/harvest-acceptance/{harvest_acceptance_id}/create-credit-note` | Gutschrift erstellen | ✅ |
| GET | `/{invoice_id}` | Gutschrift abrufen | ✅ |
| GET | `/harvest-acceptance/{harvest_acceptance_id}` | Gutschrift für Ernte-Annahme | ✅ |
| POST | `/{invoice_id}/issue` | Gutschrift ausgeben | ✅ |
| POST | `/{invoice_id}/generate-einvoice` | E-Rechnung generieren | ✅ |
| POST | `/{invoice_id}/send` | E-Rechnung versenden | ✅ |
| POST | `/{invoice_id}/dispute` | Dispute erstellen | ✅ |
| GET | `/{invoice_id}/disputes` | Disputes abrufen | ✅ |

### Features

- ✅ Gutschrift-Erstellung mit automatischer Nummer
- ✅ Status-Workflow (draft → issued → paid/disputed)
- ✅ E-Rechnung-Generierung (XRechnung)
- ✅ Dispute-Handling
- ✅ Automatische Pflichttexte

---

## Integration

### API-Router

Die neuen Endpoints wurden in `app/api/v1/api.py` integriert:

```python
api_router.include_router(
    quality_protocols.router,
    prefix="/agrar/quality-protocols",
    tags=["agrar", "quality", "protocols", "labor"]
)

api_router.include_router(
    daily_prices.router,
    prefix="/agrar/daily-prices",
    tags=["agrar", "pricing", "daily-prices"]
)

api_router.include_router(
    self_billing.router,
    prefix="/agrar/self-billing",
    tags=["agrar", "self-billing", "invoices", "e-invoice"]
)
```

### Endpoints-Export

Die neuen Endpoints wurden in `app/api/v1/endpoints/__init__.py` exportiert:

```python
from . import quality_protocols
from . import daily_prices
from . import self_billing
```

---

## Pydantic Models

### Quality Protocols

- `QualityProtocolOut` - Output-Model
- `QualityProtocolCreateIn` - Input für Erstellung
- `QualityProtocolUpdateIn` - Input für Update
- `QualityProtocolFinalizeIn` - Input für Finalisierung

### Daily Prices

- `DailyPriceOut` - Output-Model
- `DailyPriceCreateIn` - Input für Erstellung
- `DailyPriceBulkCreateIn` - Input für Bulk-Import

### Self-Billing

- `SelfBillingInvoiceOut` - Output-Model
- `CreditNoteCreateIn` - Input für Gutschrift-Erstellung
- `DisputeCreateIn` - Input für Dispute-Erstellung
- `EinvoiceGenerateIn` - Input für E-Rechnung-Generierung

---

## Sicherheit

### Authentifizierung

- ✅ Alle Endpoints erfordern Authentifizierung
- ✅ Tenant-Isolation über `get_tenant_id` Dependency

### Autorisierung

- ✅ Daily Prices: Admin-only für Write-Operationen (`require_inventory_admin`)
- ✅ Quality Protocols: Alle Benutzer können lesen, nur finale Protokolle sind geschützt
- ✅ Self-Billing: Alle Benutzer können lesen, Write-Operationen erfordern Berechtigung

---

## Fehlerbehandlung

- ✅ 404 für nicht gefundene Ressourcen
- ✅ 403 für Zugriffsverweigerung
- ✅ 400 für Validierungsfehler
- ✅ 500 für Server-Fehler

---

## Nächste Schritte

### Backend

1. ⏳ **Integration in Harvest Acceptance API:**
   - Quality Protocol beim Erstellen/Laden von Ernte-Annahme
   - Daily Price bei Preisermittlung
   - Self-Billing bei Freigabe

2. ⏳ **Weitere Features:**
   - Partie/Charge-Generierung
   - Mengenprüfung (Vertragsmengen-Validierung)
   - Formeln für Zu-/Abschläge

### Frontend

3. ⏳ **UI-Komponenten:**
   - Quality Protocol Dialog
   - Daily Price Management
   - Self-Billing Workflow

---

## Dateien

### API-Endpoints

- ✅ `app/api/v1/endpoints/quality_protocols.py`
- ✅ `app/api/v1/endpoints/daily_prices.py`
- ✅ `app/api/v1/endpoints/self_billing.py`
- ✅ `app/api/v1/endpoints/__init__.py` (aktualisiert)
- ✅ `app/api/v1/api.py` (aktualisiert)

### Dokumentation

- ✅ `docs/ernte-annahme-api-endpoints-summary.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ API-Endpoints implementiert, bereit für Integration und Tests


