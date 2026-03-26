import { describe, expect, it } from 'vitest'
import { getPageModuleLoader } from '@/app/page-module-loader'

describe('page-module-loader', () => {
  it('liefert fuer denselben Modulpfad eine stabile Loader-Referenz', () => {
    const first = getPageModuleLoader('@/pages/lager/bestandsuebersicht')
    const second = getPageModuleLoader('@/pages/lager/bestandsuebersicht')

    expect(second).toBe(first)
  })
})
