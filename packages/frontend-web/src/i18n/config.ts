import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'

import de from './locales/de/translation.json'
import en from './locales/en/translation.json'
import es from './locales/es/translation.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      de: { translation: de },
      en: { translation: en },
      es: { translation: es },
    },
    lng: 'de',
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

export const loadLanguage = async (lng: string): Promise<void> => {
  if (!i18n.hasResourceBundle(lng, 'translation')) {
    try {
      const response = await fetch(`/api/translations/${lng}`)
      if (response.ok) {
        const data = await response.json()
        const bundle = Array.isArray(data)
          ? data.reduce<Record<string, string>>((acc, r: { key: string; value: string }) => {
              if (r.key) acc[r.key] = r.value ?? ''
              return acc
            }, {})
          : data.translations
            ? data.translations.reduce<Record<string, string>>((acc: Record<string, string>, r: { key: string; value: string }) => {
                if (r.key) acc[r.key] = r.value ?? ''
                return acc
              }, {})
            : {}
        i18n.addResourceBundle(lng, 'translation', bundle, true, true)
      }
    } catch {
      // Backend translations not available, use bundled resources
    }
  }
  await i18n.changeLanguage(lng)
  localStorage.setItem('valeo-language', lng)
  document.documentElement.lang = lng
}
