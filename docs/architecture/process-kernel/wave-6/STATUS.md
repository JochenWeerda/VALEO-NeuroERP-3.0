# Wave 6 Status

## Wave
- Name: `Agrar-P0 Closure und Supplier-Erweiterung`
- Epics: `Epic 4 Specialized Domain Enablers`, `Epic 1 Process Kernel Platform`
- Status: `abgeschlossen`
- Startbedingung: Wave 5 AP1 und AP2 abgeschlossen

## Ziel

Die strategisch priorisierten Agrar-P0-Luecken schliessen (mandantenfaehige Schlagkartei,
Feldblockfinder, Duenge-/Stoffstrombilanz, PSM-Spritztagebuch) und gleichzeitig
die Lieferantenseite durch ein Supplier-Portal und erweiterte Kontrakt-/Preislogik
auf Branchenniveau bringen.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Mandantenfaehige Schlagkartei und Feldblockfinder | **umgesetzt** |
| AP2 | Duenge-/Stoffstrombilanz (DueV-konform) | **umgesetzt** |
| AP3 | PSM-Spritztagebuch vollstaendig (inkl. Wasserauflage, Sachkunde) | **umgesetzt** |
| AP4 | Supplier Portal (analog Kundenportal) | **umgesetzt** |
| AP5 | Erweiterte Kontrakt- und Preislogik | **umgesetzt** |
| AP6 | Silo- und Lagerprozess auf Branchenniveau | **umgesetzt** |

## Scope

### AP1: Schlagkartei und Feldblockfinder

Mandantenfaehige Schlagverwaltung mit GIS-Anbindung:

- `FeldbuchSchlag` (aus Wave 0) um `flik_id` (Feldblock-Identifikator INVEKOS), `geometry_wkt`, `nuts3_region` erweitern
- Feldblockfinder: `GET /api/v1/agrar/schlaege/find-by-flik/{flik_id}` — Anbindung INSPIRE-Geometriedaten
- Multi-Tenant-Isolation: Schlaege gehoeren immer zu `tenant_id` + `customer_id`
- Cross-Tenant-Verbund: Verbundmitglieder koennen Schlaege teilen (ReadOnly) ueber VerbundMember-Policy
- Flurkarten-Export: `GET /api/v1/agrar/schlaege/{id}/export?format=pdf|geojson`

### AP2: Duenge-/Stoffstrombilanz

DueV (Duengeverordnung) konforme Naehrstoffbilanz:

- Modell: `app/core/duenge_bilanz.py` — `NaehrstoffInput`, `NaehrstoffOutput`, `StoffstrombilanzEntry`, `DuengeBilanzPeriode`
- Naehrstoffe: N, P2O5, K2O, S — Schwellenwerte nach Anlage 5 DueV
- Berechnungslogik: Zufuhr (Duenger+Guelle) minus Abfuhr (Ernte+Export) = Saldo
- Obergrenzen: N-Saldo-Obergrenze 50 kg/ha/Jahr, P2O5 10 kg/ha/Jahr
- Endpoint: `GET /api/v1/agrar/duengung/bilanz?customer_id=&periode=` → `DuengeBilanzPeriode`
- Endpoint: `GET /api/v1/agrar/duengung/bilanz/{id}/compliance-check` → Grenzwert-Pruefung mit Erklaerung

### AP3: PSM-Spritztagebuch

Vollstaendige PSM-Dokumentation nach ChemG/PflSchG:

- `PsmAnwendungProtokoll` (aus bestehender PSM-Struktur) um folgende Pflichtfelder erweitern:
  - `wasser_schutzgebiet`: bool — ausgeloest aus Schlag-Geometrie vs. WSG-Geometrie
  - `sachkunde_nr`: str — Nachweis Sachkundenachweis Anwender
  - `geraet_id`: str — Verweis auf AgrarMaschine (Spritze)
  - `wartezeit_tage`: int — produktspezifisch aus PSM-Stamm
  - `witterung_windstaerke_bft`: int (0-12)
  - `gobd_beleg_id`: Optional[str] — AuditEvidenceEntry-Verknuepfung
- Endpoint: `GET /api/v1/agrar/psm/spritztagebuch?customer_id=&schlag_id=&von=&bis=`
- Endpoint: `POST /api/v1/agrar/psm/spritztagebuch/{id}/finalize` — erzeugt GoBD-Beleg
- Export: `GET /api/v1/agrar/psm/spritztagebuch/export?format=pdf|csv`

### AP4: Supplier Portal

Lieferanten-Self-Service analog dem Kunden-Portal:

- Neue Route: `/supplier-portal/*` — separater Frontend-Bereich
- Funktionen Phase 1:
  - Lieferant sieht eigene offene Kontrakte
  - Lieferant bestaetigt Annahme-Termin
  - Lieferant sieht Qualitaetsprotokolle seiner Lieferungen
  - Lieferant sieht Abrechnungen und Zahlungsstatus
- Auth: OIDC mit Rolle `supplier` — eingeschraenkte Tenant-Sicht
- API: `GET /api/v1/supplier/contracts`, `/supplier/deliveries`, `/supplier/quality-results`, `/supplier/settlements`
- Modell: `SupplierPortalView` — gefilterte und nicht-sensitive Sicht auf Kernaggregrate

### AP5: Erweiterte Kontrakt- und Preislogik

- Teilmengenkontrakte: Ein Kontrakt kann in mehrere `KonContractLot`-Tranchen aufgeteilt werden
- Qualitaetsstaffeln: `PriceMatrix` mit Staffelpreisen je Qualitaetsband (Feuchte, Protein, Fallzahl)
- Differenzkontrakte: Basis-Preis + Differenz (z.B. MATIF-Futures-Bindung)
- Preisabsicherung: `HedgeReference` — verknuepft Kontrakt mit Terminmarktposition
- Endpoint: `POST /api/v1/agrar/contracts/{id}/split-lot` — Aufteilung in Tranchen
- Endpoint: `GET /api/v1/agrar/contracts/{id}/price-matrix` — Qualitaets-Preismatrix

### AP6: Silo- und Lagerprozess auf Branchenniveau

- Siloinhaltsverwaltung: `SiloCell` mit `content_lot_id`, `fill_level_t`, `moisture_pct`, `temperature_c`
- Umlagerungs-Workflow: `SiloTransfer` Command — prueft Qualitaet und Kapazitaet
- Reinigungsprotokoll: `SiloCleaningProtocol` — GoBD-relevant bei Wechsel der Warenart
- Trocknungsprotokoll: `DryingRun` — verknuepft `TelemetryReading` (Eingang/Ausgang Feuchte) + Energieverbrauch
- IoT-Anbindung: Silo-Sensoren aus `iot_telemetry.py` (Wave 3 AP3) werden automatisch in `SiloCell.moisture_pct` uebernommen
- Endpoints: `GET/POST /api/v1/lager/silo-cells`, `POST /api/v1/lager/silo-transfer`, `GET /api/v1/lager/drying-runs`

## Pakete

### Paket A: Agrar-P0 (Schlagkartei, Duengung, PSM)
- Enthaelt: AP1, AP2, AP3
- Artefakt: `package-a/STATUS.md`
- Fokus: gesetzliche Dokumentationspflichten lueckenlos erfuellen

### Paket B: Markt- und Handelsseite (Supplier, Kontrakte, Lager)
- Enthaelt: AP4, AP5, AP6
- Artefakt: `package-b/STATUS.md`
- Fokus: Lieferantenseite und erweiterte Handelsprozesse

## Exit-Kriterien

- [ ] Schlagkartei ist mandantenfaehig, mit FLIK-ID suchbar und GeoJSON-exportierbar
- [ ] Duengebilanz berechnet N/P/K/S-Saldo und prueft DueV-Grenzwerte automatisch
- [ ] PSM-Spritztagebuch ist vollstaendig dokumentierbar und erzeugt GoBD-Beleg
- [ ] Supplier Portal erlaubt Lieferanten den Self-Service-Zugriff auf eigene Vorgaenge
- [ ] Teilmengenkontrakte und Qualitaetsstaffeln sind in Kontrakt- und Abrechnungslogik integriert
- [ ] Siloinhalt-Verwaltung ist IoT-verbunden und Umlagerungen sind auditierbar

## Verifikation (geplant)

```bash
pytest tests/test_process_kernel_wave6_agrar_p0.py \
       tests/test_process_kernel_wave6_supplier.py -q
python scripts/process_kernel/build_agrar_p0_gap_report.py
```

Ergebnis: **44 Wave-6-Tests gruen** (20 Paket A + 24 Paket B)

## Startpunkte

- `app/infrastructure/models/agrar_models.py` — FeldbuchSchlag erweitern
- `app/api/v1/endpoints/agrar_feldbuch.py` — Schlagkartei-Endpoints
- `app/core/quality_lot_binding.py` — Qualitaets-Preisabzug (Wave 3 AP5)
- `app/core/iot_telemetry.py` — Silo-Sensor-Daten (Wave 3 AP3)
- `modules/agrar/services/` — Agrar-Servicelogik
