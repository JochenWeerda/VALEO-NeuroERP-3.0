/**
 * i18n Configuration für VALEO NeuroERP
 * 
 * Aktuell verfügbar: DE (Deutsch)
 * Geplant für Lazy-Loading: EN, FR, ES, PT, ZH
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

import de from './locales/de/translation.json';

i18n
  .use(Backend) // Für zukünftiges Nachladen
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      de: { translation: de },
      // EN, FR, ES, PT, ZH werden später nachgeladen
    },
    
    lng: 'de', // Standard: Deutsch
    fallbackLng: 'de',
    debug: false,
    
    // Alle geplanten Sprachen (für UI-Auswahl)
    supportedLngs: ['de', 'en', 'fr', 'es', 'pt', 'zh'],
    
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'valeo-language',
    },
    
    interpolation: {
      escapeValue: false,
    },
    
    // Backend für Lazy-Loading
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
      addPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    react: {
      useSuspense: false, // Wichtig für lazy-loading
    },
  });

export default i18n;

// Verfügbare Sprachen
export const availableLanguages = [
  { code: 'de', name: 'Deutsch', flag: '🇩🇪', available: true },
  { code: 'en', name: 'English', flag: '🇬🇧', available: false },
  { code: 'fr', name: 'Français', flag: '🇫🇷', available: false },
  { code: 'es', name: 'Español', flag: '🇪🇸', available: false },
  { code: 'pt', name: 'Português', flag: '🇵🇹', available: false },
  { code: 'zh', name: '中文', flag: '🇨🇳', available: false },
] as const;

// Helper: Sprache dynamisch nachladen
export const loadLanguage = async (lng: string) => {
  if (!i18n.hasResourceBundle(lng, 'translation')) {
    await i18n.loadLanguages(lng);
  }
  await i18n.changeLanguage(lng);
};
