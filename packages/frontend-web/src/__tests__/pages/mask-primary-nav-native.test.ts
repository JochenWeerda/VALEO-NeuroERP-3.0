import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('MASK-PRIMARY-NAV-NATIVE-20261022', () => {
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

  it('Lieferanten-Liste oeffnet bestehende Saetze auf der nativen Supplier-Route', () => {
    const src = read('einkauf/lieferanten-liste.tsx')
    expect(src).toContain('`/einkauf/lieferanten/${l.id}`')
    expect(src).not.toContain('`/einkauf/lieferant/${l.id}`')
    expect(src).toContain("navigate('/einkauf/lieferant/neu')")
  })
})
