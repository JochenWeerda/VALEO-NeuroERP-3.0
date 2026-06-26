/** CRM-Listenantworten: Backend liefert `{ items, total }` oder legacy `{ data, total }`. */
export type CrmListEnvelope<T> = {
  items?: T[]
  data?: T[]
  total?: number
}

/** Entpackt den HTTP-Body (nicht den apiClient-Proxy — dafür zuerst `response.data` übergeben). */
export function unwrapCrmListPage<T>(
  body: CrmListEnvelope<T> | T[] | null | undefined,
): { items: T[]; total: number } {
  if (Array.isArray(body)) {
    return { items: body, total: body.length }
  }
  if (!body || typeof body !== 'object') {
    return { items: [], total: 0 }
  }
  const items = body.items ?? body.data ?? []
  return { items, total: body.total ?? items.length }
}
