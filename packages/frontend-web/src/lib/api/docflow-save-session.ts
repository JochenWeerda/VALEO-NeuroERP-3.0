import { apiClient } from '@/lib/api-client'

export interface DocflowSavedDraft { id: string; version: number }

/** Keep one logical save key until an unchanged attempt has a confirmed response. */
export function createDocflowSaveSession() {
  let attempt: { signature: string; key: string } | undefined
  let pending: Promise<DocflowSavedDraft> | undefined
  let pendingSignature: string | undefined
  return {
    save(id: string | null, version: number | undefined, payload: Record<string, unknown>): Promise<DocflowSavedDraft> {
      if (id && (!Number.isInteger(version) || (version ?? 0) < 1)) {
        return Promise.reject(new Error('Belegversion fehlt. Bitte den Beleg erneut laden.'))
      }
      const signature = JSON.stringify({ id, version, payload })
      if (pending) {
        return pendingSignature === signature ? pending : Promise.reject(new Error('Speichern läuft bereits.'))
      }
      if (attempt?.signature !== signature) attempt = { signature, key: crypto.randomUUID() }
      const body = { ...payload, ...(id ? { expected_version: version } : {}), idempotency_key: attempt.key }
      pendingSignature = signature
      const transport = id
        ? apiClient.put<DocflowSavedDraft>(`/api/v1/docflow/${encodeURIComponent(id)}`, body)
        : apiClient.post<DocflowSavedDraft>('/api/v1/docflow', body)
      pending = transport.then(response => {
        const saved = response.data
        if (!saved?.id || !Number.isInteger(saved.version) || saved.version < 1 || (id && saved.id !== id)) {
          throw new Error('Unvollständige Speicherbestätigung. Bitte erneut versuchen.')
        }
        return saved
      }).finally(() => { pending = undefined; pendingSignature = undefined })
      return pending
    },
  }
}
