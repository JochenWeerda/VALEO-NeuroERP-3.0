const IDENTITY_KEYS = ['id', 'entity_id', 'kunden_nr', 'probe_nr', 'nr'] as const

export function rowIdentity(row: Record<string, unknown>, index?: number): string {
  for (const key of IDENTITY_KEYS) {
    const value = row[key]
    if (value != null && String(value).length > 0) return String(value)
  }
  return index == null ? '' : `row-${index}`
}

export function resolveRowRoute(template: string | undefined, row: Record<string, unknown>): string | undefined {
  if (!template) return undefined
  const target = template.replace(/\{([^}]+)\}/g, (match, key: string) => {
    const raw = row[key]
    if (raw == null) return ''
    const value = String(raw)
    if (!value) return ''
    // Whole-template token is already a route (`{source_route}`). Encoding
    // would turn `/verkauf/auftrag/1` into `%2Fverkauf%2F...`.
    if (match === template) {
      if (!value.startsWith('/') || value.startsWith('//')) return ''
      return value
    }
    return encodeURIComponent(value)
  })
  if (!target || target.includes('{')) return undefined
  return target
}

export function navigateRowRoute(template: string | undefined, row: Record<string, unknown>): void {
  const target = resolveRowRoute(template, row)
  if (!target) return
  window.history.pushState(null, '', target)
  window.dispatchEvent(new PopStateEvent('popstate'))
}
