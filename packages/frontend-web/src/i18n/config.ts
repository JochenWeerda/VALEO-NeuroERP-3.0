import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import de from './locales/de/translation.json'

type TranslationBundle = Record<string, unknown>

const bundledLanguageLoaders: Record<string, () => Promise<TranslationBundle>> = {
  en: async () => (await import('./locales/en/translation.json')).default as TranslationBundle,
  es: async () => (await import('./locales/es/translation.json')).default as TranslationBundle,
}

let initPromise: Promise<void> | null = null

export default i18n

export type LanguageInfo = {
  code: string
  name: string
  flag: string
  available: boolean
}

export const availableLanguages: ReadonlyArray<LanguageInfo> = [
  { code: 'de', name: 'Deutsch', flag: '\uD83C\uDDE9\uD83C\uDDEA', available: true },
  { code: 'en', name: 'English', flag: '\uD83C\uDDEC\uD83C\uDDE7', available: true },
  { code: 'es', name: 'Espa\u00f1ol', flag: '\uD83C\uDDEA\uD83C\uDDF8', available: true },
  { code: 'fr', name: 'Fran\u00e7ais', flag: '\uD83C\uDDEB\uD83C\uDDF7', available: false },
  { code: 'pt', name: 'Portugu\u00eas', flag: '\uD83C\uDDE7\uD83C\uDDF7', available: false },
  { code: 'zh', name: '\u4e2d\u6587', flag: '\uD83C\uDDE8\uD83C\uDDF3', available: false },
]

function getInitialLanguage(): string {
  try {
    return localStorage.getItem('valeo-language') ?? 'de'
  } catch {
    return 'de'
  }
}

export const initI18n = async (): Promise<void> => {
  if (i18n.isInitialized) {
    return
  }
  if (initPromise) {
    return initPromise
  }

  initPromise = (async () => {
    const { default: LanguageDetector } = await import('i18next-browser-languagedetector')

    await i18n
      .use(LanguageDetector)
      .use(initReactI18next)
      .init({
        resources: {
          de: { translation: de },
        },
        lng: getInitialLanguage(),
        fallbackLng: 'de',
        debug: false,
        supportedLngs: ['de', 'en', 'es', 'fr', 'pt', 'zh'],
        detection: {
          order: ['localStorage', 'navigator'],
          caches: ['localStorage'],
          lookupLocalStorage: 'valeo-language',
        },
        interpolation: {
          escapeValue: false,
        },
        react: {
          useSuspense: false,
        },
      })
  })()

  await initPromise
}

export const loadLanguage = async (lng: string): Promise<void> => {
  await initI18n()

  if (!i18n.hasResourceBundle(lng, 'translation')) {
    const bundledLoader = bundledLanguageLoaders[lng]
    if (bundledLoader) {
      const bundle = await bundledLoader()
      i18n.addResourceBundle(lng, 'translation', bundle, true, true)
    }

    try {
      if (!i18n.hasResourceBundle(lng, 'translation')) {
        const response = await fetch(`/api/translations/${lng}`)
        if (response.ok) {
          const data: unknown = await response.json()
          const toBundle = (rows: Array<{ key: string; value: string }>): Record<string, string> => {
            return rows.reduce((acc: Record<string, string>, r) => {
              if (r.key) acc[r.key] = r.value ?? ''
              return acc
            }, {})
          }

          const bundle = Array.isArray(data)
            ? toBundle(data as Array<{ key: string; value: string }>)
            : data && typeof data === 'object' && Array.isArray((data as { translations?: unknown }).translations)
              ? toBundle((data as { translations: Array<{ key: string; value: string }> }).translations)
              : {}
          i18n.addResourceBundle(lng, 'translation', bundle, true, true)
        }
      }
    } catch {
      // Backend translations not available, use bundled resources
    }
  }
  await i18n.changeLanguage(lng)
  localStorage.setItem('valeo-language', lng)
  document.documentElement.lang = lng
}
