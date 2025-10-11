import { useEffect, useState } from 'react'
import { ensureTranslationsLoaded } from '@/i18n/loader'
import { type Locale, getLocale, setLocale, t } from '@/lib/i18n'

interface I18nHook {
  t: typeof t
  locale: Locale
  loading: boolean
  setLocale: (locale: Locale) => Promise<void>
}

export function useI18n(): I18nHook {
  const [locale, setLocaleState] = useState<Locale>(getLocale())
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    let isMounted = true
    const bootstrap = async (): Promise<void> => {
      const currentLocale = getLocale()
      setLocaleState(currentLocale)
      try {
        setLoading(true)
        await ensureTranslationsLoaded(currentLocale)
      } catch {
        // ignore missing translations during bootstrap
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    void bootstrap()

    return () => {
      isMounted = false
    }
  }, [])

  const changeLocale = async (newLocale: Locale): Promise<void> => {
    setLoading(true)
    try {
      await ensureTranslationsLoaded(newLocale)
      setLocale(newLocale)
      setLocaleState(newLocale)
    } finally {
      setLoading(false)
    }
  }

  return {
    t,
    locale,
    loading,
    setLocale: changeLocale,
  }
}
