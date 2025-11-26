/**
 * GAP Pipeline API Client
 * Client für die Ausführung und Überwachung der GAP-Pipeline
 */

// Verwende VITE_API_BASE_URL falls gesetzt (für direkte Backend-Verbindung),
// sonst relativen Pfad für Vite-Proxy
const API_BASE = import.meta.env.VITE_API_BASE_URL 
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : '/api/v1'

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

export interface GapPipelineJobStatus {
  state: 'idle' | 'running' | 'success' | 'error'
  currentStep?: string
  refYear?: number
  startedAt?: string
  finishedAt?: string
  message?: string
}

/**
 * Führt die komplette GAP-Pipeline für ein Jahr aus
 */
export async function runGapYearPipeline(
  refYear: number,
  csvPath?: string
): Promise<GapPipelineResponse> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  const response = await fetch(`${API_BASE}/gap/pipeline/run-year`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      year: refYear,
      csv_path: csvPath,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Pipeline run-year failed (${response.status})`)
  }

  return response.json()
}

/**
 * Führt nur den GAP-Import aus
 */
export async function runGapImport(
  refYear: number,
  csvPath: string
): Promise<GapPipelineResponse> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  const response = await fetch(`${API_BASE}/gap/pipeline/import`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      year: refYear,
      csv_path: csvPath,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Pipeline import failed (${response.status})`)
  }

  return response.json()
}

/**
 * Führt einen einzelnen Pipeline-Schritt aus
 */
export async function runGapCommand(
  command: 'aggregate' | 'match' | 'snapshot' | 'hydrate-customers',
  refYear: number
): Promise<GapPipelineResponse> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  const response = await fetch(`${API_BASE}/gap/pipeline/${command}?year=${refYear}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Pipeline ${command} failed (${response.status})`)
  }

  return response.json()
}

/**
 * Startet den externen Download der GAP-Daten
 */
export async function fetchGapExternal(
  refYear: number
): Promise<GapPipelineResponse> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  const response = await fetch(`${API_BASE}/gap/pipeline/fetch-external?year=${refYear}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `External fetch failed (${response.status})`)
  }

  return response.json()
}

/**
 * Ruft den Status der GAP-Pipeline für ein Jahr ab
 * Mit Retry-Logik für instabile Verbindungen
 */
export async function getGapPipelineStatus(refYear: number, retries = 2): Promise<GapPipelineStatus> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Timeout mit AbortController (kompatibler als AbortSignal.timeout)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 Sekunden Timeout
      
      try {
        const response = await fetch(`${API_BASE}/gap/pipeline/status?year=${refYear}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          if (attempt < retries && (response.status === 0 || response.status >= 500)) {
            // Retry bei Server-Fehlern
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)))
            continue
          }
          throw new Error(`Failed to fetch GAP pipeline status (${response.status})`)
        }

        return response.json()
      } catch (fetchError: any) {
        clearTimeout(timeoutId)
        throw fetchError
      }
    } catch (error: any) {
      if (attempt < retries && (error.name === 'TypeError' || error.name === 'AbortError' || error.message?.includes('Failed to fetch'))) {
        // Retry bei Netzwerkfehlern oder Timeouts
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)))
        continue
      }
      throw error
    }
  }
  
  throw new Error('Failed to fetch GAP pipeline status after retries')
}

/**
 * Lädt eine GAP-CSV-Datei hoch
 */
export async function uploadGapCsv(
  file: File,
  year?: number
): Promise<{ success: boolean; stored_path: string; year: number; filename: string; size_bytes: number; message: string }> {
  const token = import.meta.env.VITE_API_DEV_TOKEN || 'dev-token'
  const formData = new FormData()
  formData.append('file', file)
  
  const url = year 
    ? `${API_BASE}/gap/pipeline/upload?year=${year}`
    : `${API_BASE}/gap/pipeline/upload`
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `CSV-Upload fehlgeschlagen (${response.status})`)
  }

  return response.json()
}
