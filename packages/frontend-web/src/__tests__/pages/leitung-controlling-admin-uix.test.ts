import { screen } from '@testing-library/react'
import { mountDomainPage } from '../multi-domain-uix-harness'
import Kpi from '@/pages/controlling/kpi-verwaltung'
import Measures from '@/pages/controlling/massnahmen'
import Timeseries from '@/pages/controlling/timeseries-erfassung'
import Benchmark from '@/pages/controlling/benchmark-cockpit'
import Quarantine from '@/pages/admin/integrationen-quarantaene'
import Compliance from '@/pages/admin/compliance-dashboard'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Leitung Controlling Admin Compliance UIX', () => {
  it('stellt Controlling-Stammaktionen beschriftet 44 px', async () => {
    await mountDomainPage(Kpi, 'controlling/kpi-verwaltung', true)
    expect.soft(screen.queryByRole('button', { name: 'Bearbeiten' })).toHaveClass('min-h-touch')
    expect.soft(screen.queryByRole('button', { name: 'Löschen' })).toHaveClass('min-h-touch')
    await mountDomainPage(Timeseries, 'controlling/timeseries-erfassung', true)
    expect.soft(screen.queryByRole('button', { name: 'Löschen' })).toHaveClass('min-h-touch')
    await mountDomainPage(Measures, 'controlling/massnahmen', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
    await mountDomainPage(Benchmark, 'controlling/benchmark-cockpit', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
  })

  it('stellt Leitungs-Admin und Vorfälle auf Deutsch 44 px', async () => {
    // The ControlCenter source contract remains explicitly static; quarantine is mounted below.
    const cc = read('../../pages/admin/control-center/index.tsx')
    expect(cc).toContain('PLANNING_FILTER_LABELS')
    expect(cc).toContain('Erledigen')
    expect(cc).toContain('Erneut versuchen')
    await mountDomainPage(Quarantine, 'admin/integrationen-quarantaene', true)
    expect.soft(screen.queryByRole('button', { name: 'Erneut versuchen' })).toHaveClass('min-h-touch')
    await mountDomainPage(Compliance, 'admin/compliance-dashboard', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
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
