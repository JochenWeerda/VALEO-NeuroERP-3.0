import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Betriebs-Listen UIX', () => {
  it('stellt Einzelfutter als Studio-Liste (Suche und 44-px-Zeilen aus dem Renderer)', () => {
    const src = read('../../../pages/futter/einzel/liste.tsx')
    expect(src).toContain("export { default } from '@/pages/futtermittel/einzelfuttermittel-liste'")
  })

  it('stellt Mischfutter als Studio-Liste (Suche und 44-px-Zeilen aus dem Renderer)', () => {
    const src = read('../../../pages/futter/misch/liste.tsx')
    expect(src).toContain("export { default } from '@/pages/futtermittel/mischfuttermittel-liste'")
  })

  it('stellt Zertifikate 44 px und blendet KPI auf Touch aus', () => {
    const src = read('../../../pages/zertifikate/liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('bg-orange-50')
  })

  it('stellt Versicherungen als Studio-Liste (Suche, 44-px-Zeilen und Export aus dem Renderer)', () => {
    const src = read('../../../pages/versicherungen/liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="versicherungen/liste"')
  })

  it('stellt Projekte als Studio-Liste (Suche, 44-px-Zeilen und Export aus dem Renderer)', () => {
    const src = read('../../../pages/projekte/liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="projekte/liste"')
  })

  it('stellt Foerderantraege als Studio-Liste (Suche, 44-px-Zeilen und Export aus dem Renderer)', () => {
    const src = read('../../../pages/foerderung/liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="foerderung/liste"')
  })

  it('stellt Schaeden als Studio-Liste (Suche, 44-px-Zeilen und Export aus dem Renderer)', () => {
    const src = read('../../../pages/schaeden/liste.tsx')
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="schaeden/liste"')
  })

  it('stellt Schlag-anlegen Zurueck beschriftet 44 px', () => {
    const src = read('../../../pages/agrar/feldbuch/schlag/neu.tsx')
    expect(src).toContain('Zurück')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
  })
})
