# GAP-Pipeline End-to-End Test Report

## Test-Datum
2025-01-17

## Voraussetzungen
- ✅ PostgreSQL läuft (Port 5432)
- ✅ Backend läuft (Port 8000)
- ✅ Frontend läuft (Port 3000)
- ✅ CSV-Datei vorhanden: `data/gap/impdata2024.csv` (113.29 MB)
- ✅ Feature-Flag aktiv: `VITE_ENABLE_PROSPECTING_UI=true`

## Test-Schritte

### 1. UI-Zugriff
- **URL**: `http://localhost:3000/admin/gap-pipeline`
- **Status**: ✅ Seite lädt korrekt
- **Bemerkung**: Route `/admin/gap-pipeline` ist registriert und funktional

### 2. CSV-Upload (optional, da bereits vorhanden)
- **Datei**: `data/gap/impdata2024.csv`
- **Größe**: 113.29 MB
- **Status**: ⏳ Noch nicht getestet (Datei bereits vorhanden)

### 3. "Nur Import" Test
- **Status**: ⏳ Noch nicht ausgeführt
- **Erwartung**: 
  - Status → "running" → "success"
  - DB-Check: `SELECT COUNT(*) FROM gap_payments WHERE ref_year = 2024;`
  - Erwartung: Signifikant mehr als 2 Zeilen (aktuell nur Test-Daten)

### 4. "Komplette Pipeline" Test
- **Status**: ⏳ Noch nicht ausgeführt
- **Erwartung**:
  - Steps: Import → Aggregate → Match → Snapshot → Hydrate
  - Status → "success"
  - DB-Checks:
    - `gap_payments`: Viele Zeilen für 2024
    - `customer_potential_snapshot`: Snapshots erstellt
    - `customers.analytics_*`: Felder gefüllt

### 5. Frontend-Tests
- **Kundenmaske - Tab "Potential & Leaddaten"**: ⏳ Noch nicht getestet
- **LeadExplorer (`/prospecting/leads`)**: ⏳ Noch nicht getestet

## Aktuelle Datenlage (vor Test)
```sql
-- gap_payments
ref_year | count 
---------+-------
    2024 |     2  (nur Test-Daten)

-- customer_potential_snapshot
ref_year | count 
---------+-------
    2024 |     1  (nur Test-Daten)

-- customers mit Analytics
customers_with_analytics: 0
```

## Nächste Schritte
1. Backend-API-Verbindung prüfen
2. "Nur Import" ausführen
3. DB-Check nach Import
4. "Komplette Pipeline" ausführen
5. DB-Checks nach Pipeline
6. Frontend-Tests (Kundenmaske, LeadExplorer)

## Bekannte Probleme
- API-Endpoint `/api/v1/gap/pipeline/status` gibt möglicherweise HTML statt JSON zurück (CORS/Proxy-Problem?)
- Status-Anzeige zeigt "Status wird geladen…" - möglicherweise API-Verbindungsproblem

