# Wave 3 Status

## Wave
- Name: `Specialized Domain Enablement`
- Epics: `Epic 4 Specialized Domain Enablers`, Restarbeiten `Epic 2`
- Status: `abgeschlossen`
- Abschlussdatum: `2026-03-11`

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | UI-Maskenklassifizierung A/B/C fuer Kernseiten | **umgesetzt** |
| AP2 | Dokument-/Audit-Evidence-Modell in DMS/OCR/Freigaben einziehen | **umgesetzt** |
| AP3 | IoT-/Telemetriepfade Waage/Silo/Lager anschliessen | **umgesetzt** |
| AP4 | Pricing-/Marktdatenquellen klassifizieren | **umgesetzt** |
| AP5 | Qualitaets-/Labordatenmodell an Charge, Preis und Freigabe anbinden | **umgesetzt** |
| AP6 | Import-/Staging-/Pruefpipelines fuer CSV, EDI, OCR standardisieren | **umgesetzt** |

## Aktueller Stand

### AP1: UI-Maskenklassifizierung A/B/C

- Modell: `app/core/mask_classification.py`
- Klassen: `A` = Kernprozess, `B` = Unterstuetzend, `C` = Reporting/Admin
- `MaskRegistry` mit 18 klassifizierten Masken
- Alle Klasse-A-Masken: `explainability=REQUIRED`, `wave1_contract=True`, `gobd_relevant=True`
- Gap-Report: `class_a_without_wave1_contract()` — zeigt technische Schulden
- Endpoints: `GET /api/v1/ui/mask-registry`, `/class/{A|B|C}`, `/domain/{domain}`, `/gap-report`

### AP2: Dokument-/Audit-Evidence-Modell

- Modell: `app/core/audit_evidence.py`
- `EvidenceReference`: Verweis auf DMS-Dokument (Paperless-ngx, OCR, Upload, EDI)
- `AuditEvidenceEntry`: Verknuepft Audit-Log-Eintrag mit Belegen, setzt `gobd_compliant`
- `DocumentEvidencePolicy`: Belegpflicht-Richtlinie (GoBD: ap_invoice.approved, payment_run.executed, ...)
- OCR-Mindestqualitaet: `ocr_min_confidence=0.75`
- Endpoints: `GET/POST /api/v1/audit-evidence`, `POST /{id}/evidence-refs`, `/policy/gobd-check/{type}/{id}`

### AP3: IoT-/Telemetriepfade

- Modell: `app/core/iot_telemetry.py`
- `DeviceType`: `weighbridge`, `silo_sensor`, `warehouse_sensor`, `moisture_sensor`, `temperature_sensor`
- `TelemetryReading`: Einzelmessung mit `quality: good|uncertain|bad`
- `DeviceManifest`: Geraete-Registrierung mit `process_context` (z.B. "harvest_acceptance")
- `TelemetryAggregation`: Voraggregierte Statistiken (min/max/avg)
- Endpoints: `GET/POST /api/v1/iot/devices`, `GET/POST /iot/devices/{id}/readings`, `/aggregation`

### AP4: Pricing-/Marktdatenquellen

- Modell: `app/core/pricing_governance.py`
- `PricingSourceType`: `exchange`, `broker`, `spot_market`, `internal_cost`, `fixed_contract`, `manual_override`
- `PricingSourceReliability`: `authoritative`, `indicative`, `estimated`, `override`
- Standard-Quellen: MATIF (Warenbörse), XONTRO, spot_daily, fixed_contract, manual_override (mit Freigabepflicht)
- Endpoints: `GET /api/v1/pricing/sources`, `GET /pricing/governance`

### AP5: Qualitaets-/Labordatenmodell

- Modell: `app/core/quality_lot_binding.py`
- `LotQualityProfile`: Charge mit Laborwerten + `price_deduction_pct` + `approval_status`
- `QualityPriceDeductionRule`: Schwellenwert-basierte Preisabzugsregeln
- `QualityReleaseDecision`: Freigabe-/Ablehnentscheidung mit Abzug
- Helper: `compute_price_deduction(profile, rules)` — berechnet Gesamtabzug mit Max-Cap
- Endpoints: `GET/POST /api/v1/agrar/quality-lots`, `POST /{id}/release-decision`

### AP6: Import-/Staging-/Pruefpipelines

- Modell: `app/core/import_pipeline.py`
- `ImportFormat`: `csv`, `edifact`, `ocr_pdf`, `json`, `xml_ubl`, `excel`
- `ImportStage`: `received` → `validated` → `staged` → `enriched` → `posted` | `failed` | `rejected`
- `ImportPipelineJob`: Zustandsmaschine mit Fortschritt und Validierungsergebnis
- `ImportPipelineConfig`: Konfiguration je Format+Domain+EntityType, Spalten-Mapping
- Standard: `require_approval_before_post=True`, `auto_post=False`
- Endpoints: `GET/POST /api/v1/import-pipeline/jobs`, `POST /{id}/validate`, `GET /configs`

## Verifikation

```bash
pytest tests/test_process_kernel_wave3_ap1_ap2.py tests/test_process_kernel_wave3_specialized.py -q
python -m py_compile \
  app/core/mask_classification.py \
  app/core/audit_evidence.py \
  app/core/iot_telemetry.py \
  app/core/pricing_governance.py \
  app/core/quality_lot_binding.py \
  app/core/import_pipeline.py
```

Ergebnis: **30 Wave-3-Tests passed** (14 AP1-AP2 + 16 AP3-AP6)

## Wave-3 Exit-Kriterien (Erfuellt)

- [x] Spezialdomaenen haengen auf gemeinsamen Plattformstandards
- [x] Dokument-, Qualitaets-, Pricing- und Telemetriepfade sind nicht mehr isoliert
- [x] Import- und Pruefpipelines sind kontrolliert und auditierbar

## Gesamtergebnis aller Waves

| Wave | Tests | Kernlieferung |
|------|-------|---------------|
| Wave 1 | 32 | Process Kernel, semantic_status, Explainability |
| Wave 2 | 37 | Events, Read-Models, Tenant Governance |
| Wave 3 | 30 | UI-Klassen, Evidence, IoT, Pricing, Qualitaet, Import |
| **Gesamt** | **99** | **alle aktuell definierten Kernarchitektur-Arbeitspakete umgesetzt** |
