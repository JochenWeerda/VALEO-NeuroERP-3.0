import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import Backend from 'i18next-http-backend'
import { initReactI18next } from 'react-i18next'

import de from './locales/de/translation.json'

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      de: { translation: de },
    },
    lng: 'de',
    fallbackLng: 'de',
    debug: false,
    supportedLngs: ['de', 'en', 'fr', 'es', 'pt', 'zh'],
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'valeo-language',
    },
    interpolation: {
      escapeValue: false,
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
      addPath: '/locales/{{lng}}/{{ns}}.json',
    },
    react: {
      useSuspense: false,
    },
  })

export default i18n

type LanguageInfo = {
  code: string
  name: string
  flag: string
  available: boolean
}

export const availableLanguages: ReadonlyArray<LanguageInfo> = [
  { code: 'de', name: 'Deutsch', flag: '????', available: true },
  { code: 'en', name: 'English', flag: '????', available: false },
  { code: 'fr', name: 'Français', flag: '????', available: false },
  { code: 'es', name: 'Español', flag: '????', available: false },
  { code: 'pt', name: 'Português', flag: '????', available: false },
  { code: 'zh', name: '??', flag: '????', available: false },
]

export const loadLanguage = async (lng: string): Promise<void> => {
  if (!i18n.hasResourceBundle(lng, 'translation')) {
    await i18n.loadLanguages(lng)
  }
  await i18n.changeLanguage(lng)
}
