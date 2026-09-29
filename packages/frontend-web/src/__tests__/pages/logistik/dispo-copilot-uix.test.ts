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

  it('stellt Frachtbriefe Arbeit zuerst und filtert die Suche', () => {
    const src = read('../../../pages/logistik/frachtbriefe.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('filtered')
    expect(src).toContain('Suche Frachtbriefe')
    expect(src).toContain('min-h-11 font-medium font-mono text-primary')
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Tourenplanung ohne tote Neue-Tour-CTA', () => {
    const src = read('../../../pages/logistik/tourenplanung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Dispo-Arbeitsraum')
    expect(src).toContain('/logistik/tour-fracht-arbeitsraum')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('<Button className="gap-2">\n          <Truck')
  })

  it('stellt Mahnwesen-Theater nur am Desktop', () => {
    const src = read('../../../pages/finance/mahnwesen.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ObjectPage')
  })
})
