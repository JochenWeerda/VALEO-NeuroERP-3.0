# GAP-Pipeline API-Integration

## Übersicht

Die GAP-Pipeline kann über Backend-API-Endpoints ausgeführt werden, die vom Frontend aufgerufen werden können.

## API-Endpoints

### 1. Komplette Pipeline ausführen

**POST** `/api/v1/gap/pipeline/run-year`

Führt die komplette GAP-Pipeline für ein Jahr aus:
- Import (wenn CSV-Pfad angegeben)
- Aggregate
- Match
- Snapshot
- Hydrate Customers

**Request Body:**
```json
{
  "year": 2024,
  "csv_path": "data/gap/impdata2024.csv",
  "batch_id": "optional-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "GAP-Pipeline für Jahr 2024 wurde gestartet",
  "job_id": "optional-uuid"
}
```

### 2. Nur Import ausführen

**POST** `/api/v1/gap/pipeline/import`

Führt nur den GAP-Import aus.

**Request Body:**
```json
{
  "year": 2024,
  "csv_path": "data/gap/impdata2024.csv",
  "batch_id": "optional-uuid"
}
```

### 3. Einzelne Pipeline-Schritte

**POST** `/api/v1/gap/pipeline/{command}?year=2024`

Verfügbare Commands:
- `aggregate`: Aggregiert direkte Zahlungen
- `match`: Matched Kunden mit GAP-Begünstigten
- `snapshot`: Erstellt customer_potential_snapshot
- `hydrate-customers`: Aktualisiert customer analytics-Felder

### 4. Pipeline-Status prüfen

**GET** `/api/v1/gap/pipeline/status?year=2024`

Gibt zurück:
- Anzahl importierter GAP-Zahlungen
- Anzahl Snapshots
- Anzahl Kunden mit Analytics-Daten
- Ob Pipeline komplett ist

**Response:**
```json
{
  "year": 2024,
  "gap_payments_count": 1234567,
  "snapshot_count": 890,
  "customers_with_analytics_count": 450,
  "pipeline_complete": true
}
```

## Frontend-Integration

### Beispiel: React-Komponente

```typescript
import { useState } from 'react'
import { apiClient } from '@/api/client'

export function GapPipelineControl() {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<any>(null)

  const runPipeline = async (year: number, csvPath: string) => {
    setLoading(true)
    try {
      const response = await apiClient.post('/api/v1/gap/pipeline/run-year', {
        year,
        csv_path: csvPath,
      })
      console.log('Pipeline gestartet:', response.data)
      
      // Status regelmäßig prüfen
      const interval = setInterval(async () => {
        const statusResponse = await apiClient.get(
          `/api/v1/gap/pipeline/status?year=${year}`
        )
        setStatus(statusResponse.data)
        
        if (statusResponse.data.pipeline_complete) {
          clearInterval(interval)
          setLoading(false)
        }
      }, 5000)
    } catch (error) {
      console.error('Pipeline-Fehler:', error)
      setLoading(false)
    }
  }

  return (
    <div>
      <button 
        onClick={() => runPipeline(2024, 'data/gap/impdata2024.csv')}
        disabled={loading}
      >
        {loading ? 'Pipeline läuft...' : 'GAP-Pipeline starten'}
      </button>
      
      {status && (
        <div>
          <p>GAP-Zahlungen: {status.gap_payments_count}</p>
          <p>Snapshots: {status.snapshot_count}</p>
          <p>Kunden mit Analytics: {status.customers_with_analytics_count}</p>
        </div>
      )}
    </div>
  )
}
```

### Beispiel: API-Client

```typescript
// packages/frontend-web/src/api/gap.ts

export interface GapPipelineRequest {
  year: number
  csv_path?: string
  batch_id?: string
}

export interface GapPipelineResponse {
  success: boolean
  message: string
  job_id?: string
}

export interface GapPipelineStatus {
  year: number
  gap_payments_count: number
  snapshot_count: number
  customers_with_analytics_count: number
  pipeline_complete: boolean
}

export async function runGapPipeline(
  request: GapPipelineRequest
): Promise<GapPipelineResponse> {
  const response = await fetch('/api/v1/gap/pipeline/run-year', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  return response.json()
}

export async function getGapPipelineStatus(
  year: number
): Promise<GapPipelineStatus> {
  const response = await fetch(`/api/v1/gap/pipeline/status?year=${year}`)
  return response.json()
}
```

## Hinweise

1. **Hintergrund-Ausführung**: Alle Pipeline-Commands werden im Hintergrund ausgeführt, um Blocking zu vermeiden.

2. **CSV-Upload**: Für Produktivbetrieb sollte ein CSV-Upload-Endpoint hinzugefügt werden, der die Datei temporär speichert und dann an die Pipeline übergibt.

3. **Fehlerbehandlung**: Die Pipeline-Logs sollten in eine Log-Datei oder Datenbank geschrieben werden, damit Fehler nachvollziehbar sind.

4. **Berechtigungen**: Die Endpoints sollten mit entsprechenden Berechtigungen geschützt werden (z.B. nur für Administratoren).

5. **Monitoring**: Für Produktivbetrieb sollte ein Job-Queue-System (z.B. Celery) verwendet werden, um besseres Monitoring und Retry-Mechanismen zu ermöglichen.

## Testweise Ausführung im Container

Für Fehlereingrenzung kann die Pipeline auch direkt im Container ausgeführt werden:

```bash
# CSV in Container kopieren
docker cp data/gap/impdata2024.csv valeo-neuro-erp-postgres:/tmp/

# Pipeline im Container ausführen (wenn Node.js verfügbar)
docker exec -e DATABASE_URL="postgresql://valeo_dev:valeo_dev_2024@localhost:5432/valeo_neuro_erp" \
  valeo-neuro-erp-postgres \
  sh -c "cd /tmp && node gap-cli.js run-year --year 2024 --csv-path /tmp/impdata2024.csv"
```

## Nächste Schritte

1. ✅ Backend-API-Endpoints erstellt
2. ⏳ Frontend-Komponente für Pipeline-Steuerung
3. ⏳ CSV-Upload-Funktionalität
4. ⏳ Job-Queue-Integration (Celery/RQ)
5. ⏳ Logging und Monitoring

