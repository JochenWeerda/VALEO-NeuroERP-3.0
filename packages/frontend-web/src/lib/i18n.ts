/**
 * Minimal i18n helper with German and English defaults.
 */

type Locale = 'de' | 'en'

type TranslationNode = string | TranslationRecord

interface TranslationRecord {
  [key: string]: TranslationNode
}

const translations: Record<Locale, TranslationRecord> = {
  de: {
    common: {
      save: 'Speichern',
      cancel: 'Abbrechen',
      delete: 'Loeschen',
      edit: 'Bearbeiten',
      close: 'Schliessen',
      search: 'Suchen',
      loading: 'Laedt...',
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

const LOCAL_STORAGE_KEY = 'locale'

type TranslationPath = string

type LookupResult = string | TranslationRecord | undefined

export function setLocale(locale: Locale): void {
  currentLocale = locale
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(LOCAL_STORAGE_KEY, locale)
    document.documentElement.lang = locale
  }
}

export function getLocale(): Locale {
  if (typeof window === 'undefined') {
    return currentLocale
  }
  const stored = window.localStorage.getItem(LOCAL_STORAGE_KEY) as Locale | null
  return stored ?? currentLocale
}

function resolveTranslation(locale: Locale, path: TranslationPath): LookupResult {
  const segments = path.split('.')
  let cursor: TranslationNode = translations[locale]

  for (const segment of segments) {
    if (typeof cursor === 'string') {
      return cursor
    }
    const record = cursor
    const next: TranslationNode | undefined = record[segment]
    if (next === undefined) {
      return undefined
    }
    cursor = next
  }

  return cursor
}

export function t(path: TranslationPath): string {
  const value = resolveTranslation(currentLocale, path)
  if (typeof value === 'string') {
    return value
  }
  return path
}

if (typeof window !== 'undefined') {
  const stored = window.localStorage.getItem(LOCAL_STORAGE_KEY) as Locale | null
  if (stored) {
    currentLocale = stored
    document.documentElement.lang = stored
  }
}

export type { Locale }
