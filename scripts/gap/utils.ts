export function normalizeName(raw: string | undefined | null): string {
  if (!raw) return ''
  let s = raw.toUpperCase().trim()
  s = s.replace(/\b(GMBH|MBH|KG|GMBH & CO\. KG|E G|E\.G\.|EG|E\. G\.)\b/g, '')
  s = s.replace(/\s+/g, ' ')
  return s.trim()
}

export function parseAmount(value: string | undefined | null): number | null {
  if (!value) return null
  const normalized = value.replace(/\./g, '').replace(',', '.')
  const amount = Number(normalized)
  return Number.isFinite(amount) ? amount : null
}

export function assertYear(year: number): void {
  if (!Number.isInteger(year) || year < 2000 || year > 3000) {
    throw new Error(`Invalid reference year: ${year}`)
  }
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
