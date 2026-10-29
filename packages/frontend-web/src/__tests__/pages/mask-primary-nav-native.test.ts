import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import definitions from '../fixtures/native-stamm-route-builder-contracts.json'

const pages = resolve(__dirname, '../../pages')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('MASK-PRIMARY-NAV-NATIVE-20261022 & UIX-STAMM-OBJECTPAGE-ALL-20261022', () => {
  it('Saatgut-Liste oeffnet bestehende Saetze auf der nativen Detailroute', () => {
    const src = read('agrar/saatgut-liste.tsx')
    expect(src).toContain('screenId="agrar/saatgut-liste"')
    expect(definitions['agrar/saatgut-liste'].tables[0].rowRouteTemplate).toBe('/agrar/saatgut/{id}')
    expect(definitions['agrar/saatgut-liste'].actions.find(action => action.key === 'neu')?.navigationRoute).toBe('/agrar/saatgut-stamm')
  })

  it('Duenger-Liste oeffnet bestehende Saetze auf der nativen Detailroute', () => {
    const src = read('agrar/duenger-liste.tsx')
    expect(src).toContain('screenId="agrar/duenger-liste"')
    expect(definitions['agrar/duenger-liste'].tables[0].rowRouteTemplate).toBe('/agrar/duenger/{id}')
    expect(definitions['agrar/duenger-liste'].actions.find(action => action.key === 'neu')?.navigationRoute).toBe('/agrar/duenger-stamm')
  })

  it('Duenger- und Saatgut-Unterpfad-Listen binden die registrierten Screen-IDs', () => {
    expect(read('agrar/duenger/liste.tsx')).toContain('screenId="agrar/duenger-liste"')
    expect(read('agrar/saatgut/liste.tsx')).toContain('screenId="agrar/saatgut/liste"')
  })

  it('Lieferanten-Liste oeffnet bestehende Saetze auf der nativen Supplier-Route', () => {
    const src = read('einkauf/lieferanten-liste.tsx')
    expect(src).toContain('screenId="einkauf/lieferanten"')
    expect(definitions['einkauf/lieferanten'].tables[0].rowRouteTemplate).toBe('/einkauf/lieferanten/{id}')
    expect(definitions['einkauf/lieferanten'].actions.find(action => action.key === 'neu')?.navigationRoute).toBe('/einkauf/lieferant/neu')
  })

  it('Bankkonten-Liste oeffnet bestehende Konten auf der nativen Bankkonto-Route', () => {
    const src = read('banken/konten.tsx')
    expect(src).toContain('screenId="banken/konten-liste"')
    expect(definitions['banken/konten-liste'].tables[0].rowRouteTemplate).toBe('/finance/bankkonto/{id}')
    // A create action is not declared in this list builder; its route remains a separate gap.
    expect(definitions['banken/konten-liste'].actions.some(action => action.key === 'neu')).toBe(false)
  })

  it('Debitoren-, Kreditoren-, Artikel-, Opportunity- und Futtermittel-Listen laufen ueber NativeListPage', () => {
    expect(read('finance/debitoren-liste.tsx')).toContain('screenId="finance/debitoren-liste"')
    expect(read('finance/kreditoren-liste.tsx')).toContain('screenId="finance/kreditoren-liste"')
    expect(read('artikel/liste.tsx')).toContain('screenId="artikel/liste"')
    expect(read('crm/opportunities-liste.tsx')).toContain('screenId="crm/opportunities-liste"')
    expect(read('futtermittel/mischfuttermittel-liste.tsx')).toContain('screenId="futtermittel/mischfuttermittel/liste"')
    expect(read('futtermittel/einzelfuttermittel-liste.tsx')).toContain('screenId="futtermittel/einzelfuttermittel/liste"')
    expect(read('futter/misch/liste.tsx')).toContain('screenId="futter/misch/liste"')
    expect(read('futter/einzel/liste.tsx')).toContain('screenId="futter/einzel/liste"')
  })
})
