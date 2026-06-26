# Ernte-Annahme - Backend-Services Implementation

**Datum:** 2026-02-17  
**Status:** ✅ Services implementiert

---

## Übersicht

Drei Backend-Services für erweiterte Features der Ernte-Annahme-Erfassungsmaske wurden implementiert:

1. **Quality Protocol Service** - Verwaltung von Qualitätsprotokollen
2. **Daily Price Service** - Verwaltung von Tagespreisen
3. **Self-Billing Service** - Verwaltung von Self-Billing Gutschriften

---

## 1. Quality Protocol Service ✅

**Datei:** `modules/agrar/services/quality_protocol_service.py`

### Funktionen

- ✅ `create_quality_protocol()` - Neues Qualitätsprotokoll erstellen
- ✅ `update_quality_protocol()` - Protokoll aktualisieren (nur wenn nicht final)
- ✅ `finalize_quality_protocol()` - Protokoll finalisieren
- ✅ `import_from_csv()` - Import aus CSV
- ✅ `import_from_json()` - Import aus JSON
- ✅ `get_latest_protocol()` - Neuestes Protokoll abrufen

### Features

- **Automatische Versionsnummer:** Wird basierend auf bestehenden Protokollen erhöht
- **Automatische Protokoll-Nummer:** Format: `QP-{acceptance_id}-V{version}`
- **Import-Funktionalität:** CSV und JSON werden unterstützt
- **Finalisierung:** Nach Finalisierung keine Änderungen mehr möglich
- **Audit-Trail:** Vollständige Nachverfolgbarkeit

### Datenstrukturen

```python
@dataclass
class QualityProtocol:
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str]
    protocol_number: str
    version: int
    moisture_pct: Optional[Decimal]
    impurities_pct: Optional[Decimal]
    hl_weight_kg_per_hl: Optional[Decimal]
    protein_pct: Optional[Decimal]
    mycotoxin_ppb: Optional[Decimal]
    other_values: Optional[dict]  # JSONB
    source_type: Optional[SourceType]  # manual / import / lims / device
    is_final: bool
    # ... Audit-Felder
```

---

## 2. Daily Price Service ✅

**Datei:** `modules/agrar/services/daily_price_service.py`

### Funktionen

- ✅ `get_price_for_date()` - Preis für Datum abrufen
- ✅ `create_daily_price()` - Neuen Tagespreis erstellen
- ✅ `bulk_import_prices()` - Bulk-Import von Preisen
- ✅ `get_price_history()` - Preis-Historie abrufen

### Features

- **Flexible Preisermittlung:** Artikel, Warengruppe oder Crop Code
- **Gültigkeitszeitraum:** `valid_from` und `valid_to` für Preis-Gültigkeit
- **Quellen-Tracking:** Manual, Exchange oder API
- **Bulk-Import:** Für Massenimporte aus Excel/CSV
- **Preis-Historie:** Für Charts und Trend-Analysen

### Datenstrukturen

```python
@dataclass
class DailyPrice:
    id: str
    tenant_id: str
    article_id: Optional[str]
    warengruppe: Optional[str]
    crop_code: Optional[str]
    price_eur_per_ton: Decimal
    currency: str
    price_date: date
    valid_from: datetime
    valid_to: Optional[datetime]
    source_type: Optional[SourceType]  # manual / exchange / api
    # ... Audit-Felder
```

### Priorität

Preisermittlung erfolgt nach Priorität:
1. `article_id` (falls vorhanden)
2. `warengruppe` (falls vorhanden)
3. `crop_code` (falls vorhanden)

---

## 3. Self-Billing Service ✅

**Datei:** `modules/agrar/services/self_billing_service.py`

### Funktionen

- ✅ `create_credit_note()` - Gutschrift erstellen
- ✅ `issue_invoice()` - Gutschrift ausgeben (draft → issued)
- ✅ `generate_einvoice()` - E-Rechnung generieren (XRechnung/ZUGFeRD)
- ✅ `send_einvoice()` - E-Rechnung versenden
- ✅ `create_dispute()` - Dispute erstellen
- ✅ `resolve_dispute()` - Dispute auflösen

### Features

- **Automatische Rechnungsnummer:** Format: `GS-{year}-{acceptance_id}-{sequence}`
- **Pflichttexte:** Automatische Generierung basierend auf Besteuerungsart
- **E-Rechnung:** XRechnung XML-Generierung (EN16931)
- **Dispute-Handling:** Vollständiges Dispute-Management
- **Status-Workflow:** draft → issued → paid / disputed → cancelled

### Datenstrukturen

```python
@dataclass
class SelfBillingInvoice:
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str]
    invoice_number: str
    status: InvoiceStatus  # draft / issued / paid / disputed / cancelled
    dispute_status: DisputeStatus  # none / raised / resolved / rejected
    total_net_amount_eur: Decimal
    total_vat_amount_eur: Decimal
    total_gross_amount_eur: Decimal
    vat_rate_percent: Decimal
    einvoice_xml: Optional[str]
    einvoice_pdf: Optional[bytes]
    mandatory_texts: Optional[list[dict]]  # JSONB
    # ... Audit-Felder
```

### Pflichttexte

Automatische Generierung basierend auf Besteuerungsart:

- **§24-Pauschalierung:** "Rechnung nach §24 UStG (Pauschalierung)"
- **Kleinunternehmer:** "Kleinunternehmerregelung nach §19 UStG"
- **Self-Billing:** "Diese Rechnung wurde im Rahmen des Self-Billing-Verfahrens erstellt."

### E-Rechnung

- **XRechnung:** Vollständige XML-Generierung (EN16931)
- **ZUGFeRD:** TODO (noch nicht implementiert)
- **Versand:** TODO (E-Mail-Service oder Portal-Integration)

---

## Repository Pattern

Alle Services verwenden das **Protocol-basierte Repository Pattern**:

```python
class QualityProtocolRepository(Protocol):
    def create(self, protocol: QualityProtocol) -> QualityProtocol: ...
    def get_by_id(self, protocol_id: str) -> Optional[QualityProtocol]: ...
    # ...
```

Dies ermöglicht:
- **Testbarkeit:** Einfache Mock-Implementierungen
- **Flexibilität:** Verschiedene Datenbank-Implementierungen
- **Dependency Injection:** Services sind unabhängig von konkreten Implementierungen

---

## Nächste Schritte

### Backend

1. ⏳ **Repository-Implementierungen:** SQLAlchemy-Repositories für alle Services
2. ⏳ **API-Endpoints:** FastAPI-Endpoints für alle Services
3. ⏳ **Integration:** Integration in bestehende Harvest Acceptance API

### Frontend

4. ⏳ **Quality Protocol Dialog:** UI für Protokoll-Verwaltung
5. ⏳ **Daily Price Management:** UI für Preis-Verwaltung
6. ⏳ **Self-Billing Workflow:** UI für Gutschrift-Erstellung

---

## Dateien

### Services

- ✅ `modules/agrar/services/quality_protocol_service.py`
- ✅ `modules/agrar/services/daily_price_service.py`
- ✅ `modules/agrar/services/self_billing_service.py`
- ✅ `modules/agrar/services/__init__.py` (aktualisiert)

### Dokumentation

- ✅ `docs/ernte-annahme-features-implementation-plan.md`
- ✅ `docs/ernte-annahme-services-implementation.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ Backend-Services implementiert, bereit für Repository-Implementierungen und API-Endpoints


