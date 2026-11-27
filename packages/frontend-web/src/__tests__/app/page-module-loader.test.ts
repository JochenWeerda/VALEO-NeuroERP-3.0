import { describe, expect, it } from 'vitest'
import { getPageModuleLoader } from '@/app/page-module-loader'
import routeInventory from '@/app/routing/route-inventory.gen.json'

function pageModulesFromInventory(): string[] {
  return routeInventory.routes
    .map((route) => route.module)
    .filter((module): module is string => typeof module === 'string' && module.startsWith('@/pages/'))
}

describe('page-module-loader', () => {
  it('liefert fuer denselben Modulpfad eine stabile Loader-Referenz', () => {
    const first = getPageModuleLoader('@/pages/lager/bestandsuebersicht')
    const second = getPageModuleLoader('@/pages/lager/bestandsuebersicht')

    expect(second).toBe(first)
  })

  it('registriert jedes Route-Inventar-Seitenprefix (kein unsupported page group)', () => {
    const modules = pageModulesFromInventory()
    expect(modules.length).toBeGreaterThan(100)

    const failures: string[] = []
    for (const modulePath of modules) {
      try {
        getPageModuleLoader(modulePath)
      } catch (error) {
        failures.push(`${modulePath}: ${error instanceof Error ? error.message : String(error)}`)
      }
    }

    expect(failures, failures.join('\n')).toEqual([])
  })
})

it('loads the published document pilot page through the existing page groups', async () => {
  const page = await getPageModuleLoader('@/pages/belege/beleg')()
  expect(typeof page.default).toBe('function')
}, 20000)

it('loads previously missing page-group prefixes (pricing/ops/studio/dms)', async () => {
  const modules = [
    '@/pages/konditionen/konditionssystem',
    '@/pages/dms/archiv-suche',
    '@/pages/studio/workspace-composition-preview',
    '@/pages/betrieb/maschinen-stamm',
    '@/pages/aktien/dividenden',
    '@/pages/schnittstelle/mde-inbox',
    '@/pages/analysis/WhatIfSimulator',
    '@/pages/contracts/ContractPage',
  ]
  for (const modulePath of modules) {
    const page = await getPageModuleLoader(modulePath)()
    expect(typeof page.default, modulePath).toBe('function')
  }
}, 60000)
