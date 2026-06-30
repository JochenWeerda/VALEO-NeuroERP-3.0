export type UnknownRecord = Record<string, unknown>

export function isRecord(value: unknown): value is UnknownRecord {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

export function stringValue(value: unknown, fallback = ''): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return fallback
}

export function inputValue(value: unknown): string | number {
  return typeof value === 'string' || typeof value === 'number' ? value : ''
}

export function renderValue(value: unknown, fallback = ''): string {
  if (value == null) return fallback
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  return fallback
}

export function nullableStringValue(value: unknown): string | null {
  const result = stringValue(value)
  return result ? result : null
}

export function numberValue(value: unknown, fallback = 0): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const parsed = Number(value)
    if (Number.isFinite(parsed)) return parsed
  }
  return fallback
}

export function nullableNumberValue(value: unknown): number | null {
  if (value == null || value === '') return null
  return numberValue(value)
}

export function literalValue<T extends string>(
  value: unknown,
  allowed: readonly T[],
  fallback: T,
): T {
  return typeof value === 'string' && allowed.includes(value as T) ? value as T : fallback
}

export function recordArrayFromResponse(value: unknown): UnknownRecord[] {
  if (Array.isArray(value)) return value.filter(isRecord)
  if (!isRecord(value)) return []
  if (Array.isArray(value.items)) return value.items.filter(isRecord)
  if (Array.isArray(value.data)) return value.data.filter(isRecord)
  if (isRecord(value.data) && Array.isArray(value.data.items)) {
    return value.data.items.filter(isRecord)
  }
  return []
}

export function apiErrorDetail(error: unknown): string | null {
  if (!isRecord(error)) return null
  const response = error.response
  if (!isRecord(response)) return null
  const data = response.data
  if (!isRecord(data)) return null
  return nullableStringValue(data.detail)
}

export function errorMessage(error: unknown, fallback = 'Unbekannter Fehler'): string {
  return apiErrorDetail(error) ?? (error instanceof Error ? error.message : fallback)
}
