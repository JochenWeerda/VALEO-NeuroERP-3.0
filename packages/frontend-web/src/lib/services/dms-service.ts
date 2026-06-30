/**
 * DMS Service
 * 
 * Frontend-Service für Kommunikation mit dem DMS-Adapter.
 * Verbindet NeuroERP Frontend mit Paperless-ngx Backend.
 */

import {
  isRecord,
  nullableNumberValue,
  numberValue,
  stringValue,
} from '@/lib/record-utils'

const DMS_API_BASE = import.meta.env.VITE_DMS_URL || 'http://localhost:8002'

// ==================== Types ====================

export interface Document {
  id: number
  paperlessId?: number
  title: string
  filename?: string
  fileType?: string
  sizeKb?: number
  tenantId?: string
  businessObjectType?: string
  businessObjectId?: string
  documentType?: string
  createdAt?: string
  downloadUrl?: string
  thumbnailUrl?: string
}

export interface DocumentListResponse {
  data: Document[]
  total: number
  page: number
  pageSize: number
}

export interface UploadOptions {
  file: File
  tenantId: string
  title?: string
  businessObjectType?: string
  businessObjectId?: string
  documentType?: string
  tags?: string[]
}

export interface LinkOptions {
  paperlessId: number
  tenantId: string
  businessObjectType: string
  businessObjectId: string
  documentType?: string
}

export interface SearchOptions {
  query: string
  tenantId: string
  page?: number
  pageSize?: number
}

// ==================== Helper Functions ====================

function snakeToCamel(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(snakeToCamel)
  }

  if (!isRecord(value)) {
    return value
  }
  
  return Object.keys(value).reduce((acc, key) => {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
    acc[camelKey] = snakeToCamel(value[key])
    return acc
  }, {} as Record<string, unknown>)
}

function getHeaders(tenantId: string): HeadersInit {
  return {
    'X-Tenant-ID': tenantId,
    'Accept': 'application/json',
  }
}

function healthFromResponse(value: unknown): { status: string; paperlessConnected: boolean } {
  const record = snakeToCamel(value)
  if (!isRecord(record)) {
    return { status: 'unavailable', paperlessConnected: false }
  }

  return {
    status: stringValue(record.status, 'unavailable'),
    paperlessConnected: typeof record.paperlessConnected === 'boolean'
      ? record.paperlessConnected
      : false,
  }
}

function documentFromResponse(value: unknown): Document {
  const record = snakeToCamel(value)
  const data = isRecord(record) ? record : {}
  return {
    id: numberValue(data.id),
    paperlessId: nullableNumberValue(data.paperlessId) ?? undefined,
    title: stringValue(data.title),
    filename: stringValue(data.filename) || undefined,
    fileType: stringValue(data.fileType) || undefined,
    sizeKb: nullableNumberValue(data.sizeKb) ?? undefined,
    tenantId: stringValue(data.tenantId) || undefined,
    businessObjectType: stringValue(data.businessObjectType) || undefined,
    businessObjectId: stringValue(data.businessObjectId) || undefined,
    documentType: stringValue(data.documentType) || undefined,
    createdAt: stringValue(data.createdAt) || undefined,
    downloadUrl: stringValue(data.downloadUrl) || undefined,
    thumbnailUrl: stringValue(data.thumbnailUrl) || undefined,
  }
}

function documentListFromResponse(value: unknown): DocumentListResponse {
  const record = snakeToCamel(value)
  const data = isRecord(record) ? record : {}
  const documents = Array.isArray(data.data)
    ? data.data.map(documentFromResponse)
    : []

  return {
    data: documents,
    total: numberValue(data.total, documents.length),
    page: numberValue(data.page, 1),
    pageSize: numberValue(data.pageSize, documents.length),
  }
}

// ==================== DMS Service ====================

export const dmsService = {
  /**
   * Health-Check für DMS-Adapter
   */
  async healthCheck(): Promise<{ status: string; paperlessConnected: boolean }> {
    try {
      const response = await fetch(`${DMS_API_BASE}/api/dms/health`)
      if (!response.ok) {
        return { status: 'unavailable', paperlessConnected: false }
      }
      const data = await response.json()
      return healthFromResponse(data)
    } catch {
      return { status: 'unavailable', paperlessConnected: false }
    }
  },

  /**
   * Dokument hochladen und optional verknüpfen
   */
  async uploadDocument(options: UploadOptions): Promise<Document> {
    const formData = new FormData()
    formData.append('file', options.file)
    formData.append('tenant_id', options.tenantId)
    
    if (options.title) {
      formData.append('title', options.title)
    }
    if (options.businessObjectType) {
      formData.append('business_object_type', options.businessObjectType)
    }
    if (options.businessObjectId) {
      formData.append('business_object_id', options.businessObjectId)
    }
    if (options.documentType) {
      formData.append('document_type', options.documentType)
    }
    if (options.tags && options.tags.length > 0) {
      formData.append('tags', options.tags.join(','))
    }

    const response = await fetch(`${DMS_API_BASE}/api/dms/documents`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload fehlgeschlagen' }))
      throw new Error(error.detail || 'Upload fehlgeschlagen')
    }

    const data = await response.json()
    return documentFromResponse(data)
  },

  /**
   * Dokumente auflisten mit Filterung
   */
  async listDocuments(
    tenantId: string,
    options?: {
      businessObjectType?: string
      businessObjectId?: string
      query?: string
      page?: number
      pageSize?: number
    }
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams()
    
    if (options?.businessObjectType) {
      params.append('business_object_type', options.businessObjectType)
    }
    if (options?.businessObjectId) {
      params.append('business_object_id', options.businessObjectId)
    }
    if (options?.query) {
      params.append('q', options.query)
    }
    if (options?.page) {
      params.append('page', String(options.page))
    }
    if (options?.pageSize) {
      params.append('page_size', String(options.pageSize))
    }

    const url = `${DMS_API_BASE}/api/dms/documents${params.toString() ? `?${params.toString()}` : ''}`
    
    const response = await fetch(url, {
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Dokumente konnten nicht geladen werden')
    }

    const data = await response.json()
    return documentListFromResponse(data)
  },

  /**
   * Einzelnes Dokument abrufen
   */
  async getDocument(documentId: number, tenantId: string): Promise<Document> {
    const response = await fetch(`${DMS_API_BASE}/api/dms/documents/${documentId}`, {
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Dokument nicht gefunden')
    }

    const data = await response.json()
    return documentFromResponse(data)
  },

  /**
   * Dokument herunterladen
   */
  async downloadDocument(documentId: number, tenantId: string): Promise<Blob> {
    const response = await fetch(`${DMS_API_BASE}/api/dms/documents/${documentId}/download`, {
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Download fehlgeschlagen')
    }

    return response.blob()
  },

  /**
   * Dokument-Thumbnail abrufen
   */
  async getThumbnail(documentId: number, tenantId: string): Promise<Blob> {
    const response = await fetch(`${DMS_API_BASE}/api/dms/documents/${documentId}/thumbnail`, {
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Thumbnail nicht verfügbar')
    }

    return response.blob()
  },

  /**
   * Bestehendes Dokument mit Geschäftsobjekt verknüpfen
   */
  async linkDocument(options: LinkOptions): Promise<Document> {
    const response = await fetch(`${DMS_API_BASE}/api/dms/documents/${options.paperlessId}/link`, {
      method: 'POST',
      headers: {
        ...getHeaders(options.tenantId),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        business_object_type: options.businessObjectType,
        business_object_id: options.businessObjectId,
        document_type: options.documentType,
      }),
    })

    if (!response.ok) {
      throw new Error('Verknüpfung fehlgeschlagen')
    }

    const data = await response.json()
    return documentFromResponse(data)
  },

  /**
   * Dokument löschen
   */
  async deleteDocument(documentId: number, tenantId: string): Promise<void> {
    const response = await fetch(`${DMS_API_BASE}/api/dms/documents/${documentId}`, {
      method: 'DELETE',
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Löschen fehlgeschlagen')
    }
  },

  /**
   * Unzugeordnete Dokumente (Inbox) abrufen
   */
  async getInbox(
    tenantId: string,
    page = 1,
    pageSize = 25
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })

    const response = await fetch(`${DMS_API_BASE}/api/dms/inbox?${params.toString()}`, {
      headers: getHeaders(tenantId),
    })

    if (!response.ok) {
      throw new Error('Inbox konnte nicht geladen werden')
    }

    const data = await response.json()
    return documentListFromResponse(data)
  },

  /**
   * Volltextsuche in Dokumenten
   */
  async search(options: SearchOptions): Promise<DocumentListResponse> {
    const params = new URLSearchParams({
      q: options.query,
      page: String(options.page || 1),
      page_size: String(options.pageSize || 25),
    })

    const response = await fetch(`${DMS_API_BASE}/api/dms/search?${params.toString()}`, {
      headers: getHeaders(options.tenantId),
    })

    if (!response.ok) {
      throw new Error('Suche fehlgeschlagen')
    }

    const data = await response.json()
    return documentListFromResponse(data)
  },

  /**
   * Dokumente für Geschäftsobjekt abrufen
   * Convenience-Methode für häufigen Use-Case
   */
  async getDocumentsForObject(
    tenantId: string,
    businessObjectType: string,
    businessObjectId: string
  ): Promise<Document[]> {
    const result = await this.listDocuments(tenantId, {
      businessObjectType,
      businessObjectId,
    })
    return result.data
  },

  /**
   * Download-URL für Dokument erstellen
   */
  getDownloadUrl(documentId: number): string {
    return `${DMS_API_BASE}/api/dms/documents/${documentId}/download`
  },

  /**
   * Thumbnail-URL für Dokument erstellen
   */
  getThumbnailUrl(documentId: number): string {
    return `${DMS_API_BASE}/api/dms/documents/${documentId}/thumbnail`
  },
}


