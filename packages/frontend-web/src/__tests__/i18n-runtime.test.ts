import { expect, it } from 'vitest'
import i18n, { initI18n, loadLanguage } from '@/i18n/config'

it('loads and switches the bundled ERP translations with the installed i18next runtime', async () => {
  const previousLanguage = localStorage.getItem('valeo-language')
  try {
    localStorage.setItem('valeo-language', 'de')
    await initI18n()
    expect(i18n.t('common.save')).toBe('Speichern')

    await loadLanguage('en')
    expect(i18n.t('common.save')).toBe('Save')
    expect(localStorage.getItem('valeo-language')).toBe('en')

    await loadLanguage('es')
    expect(i18n.t('common.save')).toBe('Guardar')
    expect(localStorage.getItem('valeo-language')).toBe('es')
  } finally {
    await i18n.changeLanguage('de')
    if (previousLanguage === null) localStorage.removeItem('valeo-language')
    else localStorage.setItem('valeo-language', previousLanguage)
  }
})
