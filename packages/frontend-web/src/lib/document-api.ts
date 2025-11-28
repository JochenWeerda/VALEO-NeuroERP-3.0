/**
 * Document API Utilities
 * Zentrale Funktionen für den Zugriff auf Dokument-APIs
 */

export type DocumentType = 
  | 'sales_offer' 
  | 'sales_order' 
  | 'sales_delivery' 
  | 'sales_invoice'
  | 'purchase_request'
  | 'purchase_offer'
  | 'purchase_order'
  | 'customer_inquiry'

export interface DocumentListResponse {
  ok: boolean
  data: any[]
  total: number
  skip: number
  limit: number
}

export interface DocumentResponse {
  ok: boolean
  data?: any
  number?: string
  error?: string
}

/**
 * Lädt eine Liste von Dokumenten eines Typs
 */
export async function listDocuments(
  docType: DocumentType,
  skip: number = 0,
  limit: number = 100,
  filters?: Record<string, any>
): Promise<DocumentListResponse> {
  try {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...(filters?.status && { status: filters.status }),
    })
    
    const response = await fetch(`/api/mcp/documents/${docType}?${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const result = await response.json()
    return result as DocumentListResponse
  } catch (_error) {
    // API nicht erreichbar - stille Fehlerbehandlung, da Fallback-Objekt zurückgegeben wird
    return {
      ok: false,
      data: [],
      total: 0,
      skip,
      limit,
    }
  }
}

/**
 * Lädt ein einzelnes Dokument
 */
export async function getDocument(
  docType: DocumentType,
  docNumber: string
): Promise<DocumentResponse> {
  try {
    const response = await fetch(`/api/mcp/documents/${docType}/${docNumber}`)
    
    if (!response.ok) {
      if (response.status === 404) {
        return { ok: false, error: 'Document not found' }
      }
      throw new Error(`HTTP ${response.status}`)
    }
    
    return await response.json() as DocumentResponse
  } catch (error) {
    // API nicht erreichbar - Fehler wird im Response-Objekt zurückgegeben
    return { ok: false, error: String(error) }
  }
}

/**
 * Speichert oder aktualisiert ein Dokument
 */
export async function saveDocument(
  docType: DocumentType,
  document: any
): Promise<DocumentResponse> {
  try {
    const response = await fetch(`/api/mcp/documents/${docType}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(document),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.json() as DocumentResponse
  } catch (error) {
    // API nicht erreichbar - Fehler wird im Response-Objekt zurückgegeben
    return { ok: false, error: String(error) }
  }
}

/**
 * Aktualisiert ein Dokument
 */
export async function updateDocument(
  docType: DocumentType,
  docNumber: string,
  updates: any
): Promise<DocumentResponse> {
  try {
    const response = await fetch(`/api/mcp/documents/${docType}/${docNumber}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.json() as DocumentResponse
  } catch (error) {
    // API nicht erreichbar - Fehler wird im Response-Objekt zurückgegeben
    return { ok: false, error: String(error) }
  }
}

/**
 * Löscht ein Dokument
 */
export async function deleteDocument(
  docType: DocumentType,
  docNumber: string
): Promise<DocumentResponse> {
  try {
    const response = await fetch(`/api/mcp/documents/${docType}/${docNumber}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.json() as DocumentResponse
  } catch (error) {
    // API nicht erreichbar - Fehler wird im Response-Objekt zurückgegeben
    return { ok: false, error: String(error) }
  }
}

/**
 * Löscht mehrere Dokumente gleichzeitig
 */
export interface BulkDeleteResponse extends DocumentResponse {
  deleted?: string[]
  failed?: Array<{ number: string; error: string }>
  total?: number
  deleted_count?: number
  failed_count?: number
}

export async function bulkDeleteDocuments(
  docType: DocumentType,
  docNumbers: string[]
): Promise<BulkDeleteResponse> {
  try {
    const params = new URLSearchParams()
    docNumbers.forEach(num => params.append('numbers', num))
    
    const response = await fetch(`/api/mcp/documents/${docType}?${params}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.json() as BulkDeleteResponse
  } catch (error) {
    // API nicht erreichbar - Fehler wird im Response-Objekt zurückgegeben
    return { ok: false, error: String(error) }
  }
}

