import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Betriebs-Listen UIX', () => {
  it('stellt Einzelfutter 44 px und filtert die Suche', () => {
    const src = read('../../../pages/futter/einzel/liste.tsx')
    expect(src).toContain('filteredFutter')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Einzelfutter')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Mischfutter 44 px und filtert die Suche', () => {
    const src = read('../../../pages/futter/misch/liste.tsx')
    expect(src).toContain('filteredMischfutter')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Mischfutter')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Zertifikate 44 px und blendet KPI auf Touch aus', () => {
    const src = read('../../../pages/zertifikate/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('bg-orange-50')
  })

  it('stellt Versicherungen 44 px und blendet Theater auf Touch aus', () => {
    const src = read('../../../pages/versicherungen/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Versicherungen')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Projekte 44 px ohne Rohblau', () => {
    const src = read('../../../pages/projekte/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('bg-blue-600')
  })

  it('stellt Foerderantraege 44 px mit wirkendem Export', () => {
    const src = read('../../../pages/foerderung/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Foerderantraege')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Schaeden 44 px und blendet KPI auf Touch aus', () => {
    const src = read('../../../pages/schaeden/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Schlag-anlegen Zurueck beschriftet 44 px', () => {
    const src = read('../../../pages/agrar/feldbuch/schlag/neu.tsx')
    expect(src).toContain('Zurück')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
  })
})
