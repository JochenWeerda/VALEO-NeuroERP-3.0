/**
 * i18n (Internationalization) Support
 * Simple translation system for DE/EN
 */

type Locale = 'de' | 'en'

interface Translations {
  [key: string]: string | Translations
}

const translations: Record<Locale, Translations> = {
  de: {
    common: {
      save: 'Speichern',
      cancel: 'Abbrechen',
      delete: 'Löschen',
      edit: 'Bearbeiten',
      close: 'Schließen',
      search: 'Suchen',
      loading: 'Lädt...',
      error: 'Fehler',
      success: 'Erfolgreich',
    },
    workflow: {
      draft: 'Entwurf',
      pending: 'Ausstehend',
      approved: 'Freigegeben',
      posted: 'Gebucht',
      rejected: 'Abgelehnt',
      submit: 'Einreichen',
      approve: 'Freigeben',
      reject: 'Ablehnen',
      post: 'Buchen',
    },
    documents: {
      sales_order: 'Kundenauftrag',
      purchase_order: 'Bestellung',
      invoice: 'Rechnung',
      delivery: 'Lieferschein',
      print: 'Drucken',
      export: 'Exportieren',
      archive: 'Archiv',
    },
  },
  en: {
    common: {
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      close: 'Close',
      search: 'Search',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
    },
    workflow: {
      draft: 'Draft',
      pending: 'Pending',
      approved: 'Approved',
      posted: 'Posted',
      rejected: 'Rejected',
      submit: 'Submit',
      approve: 'Approve',
      reject: 'Reject',
      post: 'Post',
    },
    documents: {
      sales_order: 'Sales Order',
      purchase_order: 'Purchase Order',
      invoice: 'Invoice',
      delivery: 'Delivery Note',
      print: 'Print',
      export: 'Export',
      archive: 'Archive',
    },
  },
}

let currentLocale: Locale = 'de'

export function setLocale(locale: Locale): void {
  currentLocale = locale
  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}

export function getLocale(): Locale {
  const stored = localStorage.getItem('locale') as Locale | null
  return stored || currentLocale
}

export function t(key: string): string {
  const keys = key.split('.')
  let value: any = translations[currentLocale]

  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k]
    } else {
      return key // Return key if translation not found
    }
  }

  return typeof value === 'string' ? value : key
}

// Initialize locale from localStorage
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('locale') as Locale | null
  if (stored) {
    currentLocale = stored
    document.documentElement.lang = stored
  }
}

export { type Locale }

