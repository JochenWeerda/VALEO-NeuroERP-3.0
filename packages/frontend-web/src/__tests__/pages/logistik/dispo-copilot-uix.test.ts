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

  it('stellt Mahnwesen-Theater nur am Desktop', () => {
    const src = read('../../../pages/finance/mahnwesen.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ObjectPage')
  })
})
