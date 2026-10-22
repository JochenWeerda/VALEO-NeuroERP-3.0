import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('MASK-PRIMARY-NAV-NATIVE-20261022 & UIX-STAMM-OBJECTPAGE-ALL-20261022', () => {
  it('Saatgut-Liste oeffnet bestehende Saetze auf der nativen Detailroute', () => {
    const src = read('agrar/saatgut-liste.tsx')
    expect(src).toContain('`/agrar/saatgut/${itemId}`')
    expect(src).not.toContain('`/agrar/saatgut-stamm/${itemId}`')
    // Neuanlage bleibt Legacy-Stamm
    expect(src).toContain("navigate('/agrar/saatgut-stamm')")
  })

  it('Duenger-Liste oeffnet bestehende Saetze auf der nativen Detailroute', () => {
    const src = read('agrar/duenger-liste.tsx')
    expect(src).toContain('`/agrar/duenger/${item.id}`')
    expect(src).not.toMatch(/navigate\(`\/agrar\/duenger-stamm\/\$\{item\.id\}`\)/)
    expect(src).toContain("navigate('/agrar/duenger-stamm')")
  })

  it('Duenger- und Saatgut-Unterpfad-Listen re-exportieren die kanonische Liste', () => {
    expect(read('agrar/duenger/liste.tsx')).toContain("export { default } from '../duenger-liste'")
    expect(read('agrar/saatgut/liste.tsx')).toContain("export { default } from '@/pages/agrar/saatgut-liste'")
  })

  it('Lieferanten-Liste oeffnet bestehende Saetze auf der nativen Supplier-Route', () => {
    const src = read('einkauf/lieferanten-liste.tsx')
    expect(src).toContain('`/einkauf/lieferanten/${l.id}`')
    expect(src).not.toContain('`/einkauf/lieferant/${l.id}`')
    expect(src).toContain("navigate('/einkauf/lieferant/neu')")
  })

  it('Bankkonten-Liste oeffnet bestehende Konten auf der nativen Bankkonto-Route', () => {
    const src = read('banken/konten.tsx')
    expect(src).toContain('`/finance/bankkonto/${k.id}`')
    expect(src).not.toContain('`/banken/konto/${k.id}`')
    expect(src).toContain("navigate('/banken/konto/neu')")
  })

  it('Debitoren-, Kreditoren-, Artikel-, Opportunity- und Futtermittel-Listen laufen ueber NativeListPage', () => {
    expect(read('finance/debitoren-liste.tsx')).toContain('screenId="finance/debitoren-liste"')
    expect(read('finance/kreditoren-liste.tsx')).toContain('screenId="finance/kreditoren-liste"')
    expect(read('artikel/liste.tsx')).toContain('screenId="artikel/liste"')
    expect(read('crm/opportunities-liste.tsx')).toContain('screenId="crm/opportunities-liste"')
    expect(read('futtermittel/mischfuttermittel-liste.tsx')).toContain('screenId="futtermittel/mischfuttermittel-liste"')
    expect(read('futtermittel/einzelfuttermittel-liste.tsx')).toContain('screenId="futtermittel/einzelfuttermittel-liste"')
    expect(read('futter/misch/liste.tsx')).toContain("export { default } from '@/pages/futtermittel/mischfuttermittel-liste'")
    expect(read('futter/einzel/liste.tsx')).toContain("export { default } from '@/pages/futtermittel/einzelfuttermittel-liste'")
  })
})
