import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Leitung Controlling Admin Compliance UIX', () => {
  it('stellt Controlling-Stammaktionen beschriftet 44 px', () => {
    const kpi = read('../../pages/controlling/kpi-verwaltung.tsx')
    expect(kpi).toContain('min-h-touch')
    expect(kpi).toContain('Bearbeiten')
    expect(kpi).toContain('Löschen')
    expect(kpi).not.toMatch(/size="sm"/)
    expect(read('../../pages/controlling/massnahmen.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/controlling/timeseries-erfassung.tsx')).toContain('Löschen')
    expect(read('../../pages/controlling/benchmark-cockpit.tsx')).toContain('min-h-touch')
  })

  it('stellt Leitungs-Admin und Vorfälle auf Deutsch 44 px', () => {
    const cc = read('../../pages/admin/control-center/index.tsx')
    expect(cc).toContain('PLANNING_FILTER_LABELS')
    expect(cc).toContain('Erledigen')
    expect(cc).toContain('Erneut versuchen')
    expect(cc).not.toMatch(/size="sm"/)
    expect(read('../../pages/admin/integrationen-quarantaene.tsx')).toContain('Erneut versuchen')
    expect(read('../../pages/admin/compliance-dashboard.tsx')).toContain('min-h-touch')
    expect(read('../../pages/admin-suite/setup.tsx')).not.toMatch(/size="sm"/)
  })

  it('stellt Compliance- und Docflow-Aktionen 44 px', () => {
    expect(read('../../pages/compliance/intrastat.tsx')).toContain('min-h-touch')
    expect(read('../../pages/compliance/datenpannen.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/compliance/verarbeitungsverzeichnis.tsx')).toContain('ropa-add-btn')
    expect(read('../../pages/docflow/artefakt-freigabe.tsx')).toContain('Freigeben')
    expect(read('../../pages/workflow/workflow-regeln.tsx')).toContain('min-h-touch')
  })

  it('beschriftet Preis- und Konditions-Löschen 44 px', () => {
    expect(read('../../pages/preise/rabattgruppen.tsx')).toContain('Löschen')
    expect(read('../../pages/preise/rabattgruppen.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/preise/individualpreise.tsx')).toContain('Löschen')
    expect(read('../../pages/konditionen/konditionssystem.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/fuhrpark/fahrzeug-vertiefung.tsx')).toContain('min-h-touch')
  })
})
