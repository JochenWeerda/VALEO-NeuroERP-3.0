***REMOVED*** GAP-Pipeline Test-Guide

***REMOVED******REMOVED*** Quick Start - "Happy Path" Test

***REMOVED******REMOVED******REMOVED*** 1. Voraussetzungen prüfen

✅ **PostgreSQL läuft**: `docker ps | grep postgres`
✅ **Backend läuft**: `http://localhost:8000`
✅ **Frontend läuft**: `http://localhost:3000`
✅ **Feature-Flag aktiv**: `VITE_ENABLE_PROSPECTING_UI=true` in `.env`

***REMOVED******REMOVED******REMOVED*** 2. CSV-Datei besorgen

1. Öffne: https://www.agrarzahlungen.de/agrarfonds/bs
2. Lade "Gesamtliste der Begünstigten - Download 2024" herunter
3. Datei lokal speichern (z.B. `impdata2024.csv`)

***REMOVED******REMOVED******REMOVED*** 3. Pipeline im Browser starten

1. **Frontend öffnen**: `http://localhost:3000/admin/gap-pipeline`
2. **CSV hochladen**:
   - Klicke auf "Datei auswählen"
   - Wähle die heruntergeladene `impdata2024.csv`
   - Jahr wird automatisch aus Dateiname extrahiert
   - Pfad wird automatisch gesetzt
3. **Pipeline starten**:
   - Option A: "Nur Import" → testet nur den Import
   - Option B: "Komplette Pipeline starten" → vollständiger Durchlauf
4. **Status beobachten**:
   - Status wird alle 5 Sekunden aktualisiert
   - Zeigt: GAP-Zahlungen, Snapshots, Kunden mit Analytics

***REMOVED******REMOVED******REMOVED*** 4. Daten prüfen (SQL)

```sql
-- GAP-Zahlungen
SELECT ref_year, COUNT(*) 
FROM gap_payments 
GROUP BY ref_year;

-- Snapshots
SELECT ref_year, COUNT(*) 
FROM customer_potential_snapshot 
GROUP BY ref_year;

-- Kunden mit Analytics
SELECT 
  id,
  name,
  analytics_gap_ref_year,
  analytics_potential_total_eur,
  analytics_segment
FROM customers
WHERE analytics_gap_ref_year IS NOT NULL
LIMIT 20;
```

***REMOVED******REMOVED*** Verfügbare API-Endpoints

***REMOVED******REMOVED******REMOVED*** CSV-Upload
```http
POST /api/v1/gap/pipeline/upload
Content-Type: multipart/form-data
Body: file=<impdata2024.csv>
```

***REMOVED******REMOVED******REMOVED*** Pipeline starten
```http
POST /api/v1/gap/pipeline/run-year
Content-Type: application/json
Body: {
  "year": 2024,
  "csv_path": "data/gap/impdata2024.csv"
}
```

***REMOVED******REMOVED******REMOVED*** Status prüfen
```http
GET /api/v1/gap/pipeline/status?year=2024
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Pipeline startet nicht
- Prüfe Backend-Logs: `docker logs valeo-neuro-erp-backend`
- Prüfe ob CSV-Datei existiert: `ls -lh data/gap/impdata2024.csv`
- Prüfe Datenbankverbindung im Backend

***REMOVED******REMOVED******REMOVED*** CSV-Upload schlägt fehl
- Prüfe ob `data/gap/` Verzeichnis existiert
- Prüfe Dateigröße (sollte < 200MB sein)
- Prüfe Backend-Logs für Fehlerdetails

***REMOVED******REMOVED******REMOVED*** Keine Daten nach Pipeline
- Prüfe Backend-Logs für Fehler
- Prüfe ob `customers`-Tabelle existiert
- Prüfe ob GAP-Tabellen existieren: `\dt gap_*`

***REMOVED******REMOVED*** Workflow für Produktivbetrieb

1. **Jährlicher Ablauf** (z.B. Januar):
   - CSV von agrarzahlungen.de herunterladen
   - Im Admin-UI hochladen (`/admin/gap-pipeline`)
   - Pipeline für neues Jahr starten
   - Status prüfen
   - Leads im LeadExplorer prüfen (`/prospecting/leads`)

2. **Außendienst-Steuerung**:
   - LeadExplorer öffnen
   - Filter setzen (Segment A, minPotential, Region)
   - Leads an Außendienst zuweisen
   - Aktivitäten planen

***REMOVED******REMOVED*** Nächste Schritte

- ✅ CSV-Upload implementiert
- ✅ Pipeline-UI erstellt
- ⏳ Job-Queue für besseres Monitoring (optional)
- ⏳ E-Mail-Benachrichtigungen bei Pipeline-Fertigstellung (optional)

