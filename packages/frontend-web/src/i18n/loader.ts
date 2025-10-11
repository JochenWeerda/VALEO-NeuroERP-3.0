import i18n from './config'

interface TranslationRecord {
  key: string
  value: string
  namespace?: string
}

interface TranslationResponse {
  language: string
  namespace?: string
  translations: TranslationRecord[]
}

const loadedLocales = new Set<string>()
const DEFAULT_NAMESPACE = 'translation'

const mapToResourceBundle = (records: TranslationRecord[]): Record<string, string> => {
  return records.reduce<Record<string, string>>((bundle, record) => {
    if (typeof record.key === 'string' && record.key.length > 0) {
      bundle[record.key] = record.value ?? ''
    }
    return bundle
  }, {})
}

export async function ensureTranslationsLoaded(locale: string): Promise<void> {
  if (loadedLocales.has(locale)) {
    return
  }

  const response = await fetch(`/api/translations/${locale}`)
  if (!response.ok) {
    throw new Error(`Failed to load translations for ${locale}`)
  }

  const payload = (await response.json()) as TranslationResponse | TranslationRecord[]

  if (Array.isArray(payload)) {
    const bundle = mapToResourceBundle(payload)
    i18n.addResources(locale, DEFAULT_NAMESPACE, bundle)
    loadedLocales.add(locale)
    return
  }

  const namespace = payload.namespace ?? DEFAULT_NAMESPACE
  const bundle = mapToResourceBundle(payload.translations ?? [])
  i18n.addResources(locale, namespace, bundle)
  loadedLocales.add(locale)
}
