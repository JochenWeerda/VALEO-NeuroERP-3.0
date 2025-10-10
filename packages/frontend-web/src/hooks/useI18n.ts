import { useState, useEffect } from 'react'
import { t, getLocale, setLocale, type Locale } from '@/lib/i18n'

export function useI18n() {
  const [locale, setLocaleState] = useState<Locale>(getLocale())

  useEffect(() => {
    setLocaleState(getLocale())
  }, [])

  const changeLocale = (newLocale: Locale) => {
    setLocale(newLocale)
    setLocaleState(newLocale)
  }

  return {
    t,
    locale,
    setLocale: changeLocale,
  }
}

