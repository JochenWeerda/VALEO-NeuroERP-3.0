import { apiClient } from '@/lib/api-client'
import type { ScreenActionDefinition } from '../schema'

export type ReadDownloadResult = { filename: string; content: string; mediaType: string; encoding?: 'base64' }

/** Read-only file transport. No cross-origin URL, identity selector or invented CSV. */
export async function readDownload(
  action: ScreenActionDefinition,
  values: Record<string, unknown>,
  entityId?: string,
): Promise<ReadDownloadResult> {
  const binding = action.download
  if (!binding || !/^\/api\/v1\/[a-zA-Z0-9_/-]+(\{entity_id\}[a-zA-Z0-9_/-]*)?$/.test(binding.endpoint)) {
    throw new Error('Der Downloadweg ist nicht gültig.')
  }
  const needsEntity = binding.endpoint.includes('{entity_id}')
  if (needsEntity && !entityId) throw new Error('Zum Download fehlt die Kennung des Datensatzes.')
  const endpoint = needsEntity ? binding.endpoint.replace('{entity_id}', encodeURIComponent(entityId ?? '')) : binding.endpoint
  const params: Record<string, string | number | boolean> = {}
  for (const field of action.inputFields ?? []) {
    if (/tenant|mandant|actor|user|agent/i.test(field.key)) throw new Error('Identitätsfelder sind im Download nicht zulässig.')
    const value = values[field.key]
    if (value === undefined || value === null || value === '') {
      if (field.required) throw new Error(`${field.label} fehlt.`)
      continue
    }
    if (!['string', 'number', 'boolean'].includes(typeof value)) throw new Error(`${field.label} ist nicht gültig.`)
    if (field.options && !field.options.some(option => option.value === value)) throw new Error(`${field.label} ist nicht gültig.`)
    params[field.key] = value as string | number | boolean
  }
  const { data } = await apiClient.get<Record<string, unknown>>(endpoint, { params })
  const content = data?.[binding.contentField]
  const filename = data?.[binding.filenameField]
  if (typeof content !== 'string' || typeof filename !== 'string' || !filename || ((filename.includes('/') || filename.includes('\\')) || Array.from(filename).some(character => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127))) {
    throw new Error('Der Server hat keine gültige Exportdatei geliefert.')
  }
  return { content, filename, mediaType: binding.mediaType, encoding: binding.contentEncoding }
}

export function saveReadDownload(result: ReadDownloadResult): void {
  const body = result.encoding === 'base64'
    ? Uint8Array.from(atob(result.content), character => character.charCodeAt(0))
    : result.content
  const url = URL.createObjectURL(new Blob([body], { type: result.mediaType }))
  try {
    const link = document.createElement('a')
    link.href = url
    link.download = result.filename
    link.click()
  } finally {
    URL.revokeObjectURL(url)
  }
}
