import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Copilot und Dispo-UIX', () => {
  it('schliesst das Copilot-Dock bei Navigation', () => {
    const src = read('../../../features/copilot/AdvisorDock.tsx')
    expect(src).toContain('useLocation')
    expect(src).toContain('setOpen(false)')
    expect(src).toContain('[pathname]')
    expect(read('../../../features/copilot/CopilotDockPanel.tsx')).toContain('hidden={!open}')
  })

  it('zeichnet Frachtbriefe ueber den Masken-Builder ohne freie Neuanlage', () => {
    const src = read('../../../pages/logistik/frachtbriefe.tsx')
    expect(src).toContain('CaptureScreenHost')
    expect(src).toContain('logistik/frachtbrief')
    expect(src).toContain("navigate('/verladung')")
    expect(src).not.toContain('Neuer Frachtbrief')
  })

  it('stellt Tourenplanung ohne tote Neue-Tour-CTA', () => {
    const src = read('../../../pages/logistik/tourenplanung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Dispo-Arbeitsraum')
    expect(src).toContain('/logistik/tour-fracht-arbeitsraum')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('<Button className="gap-2">\n          <Truck')
  })

  // Die Einzelmaske Mahnwesen ist am 11.10.2026 abgeloest: drei erfundene Debitoren, nie eine
  // geladene Mahnung, Felder ohne Gegenstueck im Backend. Die Wege dorthin zeigen den Mahnlauf.
  it('fuehrt Mahnwesen und Dunning zum Mahnlauf', () => {
    const { aliases } = JSON.parse(read('../../../app/route-aliases.json')) as { aliases: Array<{ module: string; path: string }> }
    const ziel = (pfad: string) => aliases.filter((e) => e.path === pfad).map((e) => e.module)
    expect(ziel('finance/mahnwesen')).toEqual(['@/pages/finance/mahnlauf'])
    expect(ziel('finance/dunning')).toEqual(['@/pages/finance/mahnlauf'])
    expect(() => read('../../../pages/finance/mahnwesen.tsx')).toThrow()
    expect(read('../../../app/routing/route-tree.gen.tsx')).not.toContain('@/pages/finance/mahnwesen')
  })
})
