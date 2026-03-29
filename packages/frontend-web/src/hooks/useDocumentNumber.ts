import { apiClient } from '@/lib/api/client'

let _fallbackCounter = 0

/**
 * Generates a document number via the backend numbering service.
 * Falls back to a deterministic client-side counter if the API is unavailable.
 */
export async function fetchDocumentNumber(
  domain: string,
  tenantId = 'default',
): Promise<string> {
  try {
    const res = await apiClient.post<{ ok: boolean; number: string }>(
      '/api/numbering/next',
      { domain, tenant_id: tenantId },
    )
    if (res.data?.ok && res.data.number) {
      return res.data.number
    }
  } catch {
    // Backend unavailable — fall through to client-side fallback
  }

  _fallbackCounter += 1
  const year = new Date().getFullYear()
  const seq = String(_fallbackCounter).padStart(6, '0')
  return `${domain.toUpperCase().slice(0, 3)}-${year}-${seq}`
}
