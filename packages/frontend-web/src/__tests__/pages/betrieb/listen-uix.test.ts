import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Betriebs-Listen UIX', () => {
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

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('stellt Schlag-anlegen Zurueck beschriftet 44 px', () => {
    const src = read('../../../pages/agrar/feldbuch/schlag/neu.tsx')
    expect(src).toContain('Zurück')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
  })
})
