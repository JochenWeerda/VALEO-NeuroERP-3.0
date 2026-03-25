import { describe, expect, it } from 'vitest'
import { getDomainPresentation, getSectionPresentation } from '@/app/navigation/dashboard-catalog'
import { loadNavSections } from '@/app/navigation/nav-runtime'

describe('dashboard-catalog', () => {
  it('liefert klare Landing-Paths fuer zentrale Starter-Karten', async () => {
    const sections = await loadNavSections()
    const byId = new Map(sections.map((section) => [section.id, section]))

    expect(getSectionPresentation(byId.get('workflow')!, 'de').landingPath).toBe('/workflow/flow-spine-studio')
    expect(getSectionPresentation(byId.get('annahme')!, 'de').landingPath).toBe('/annahme/warteschlange')
    expect(getSectionPresentation(byId.get('verkauf')!, 'de').landingPath).toBe('/dashboard/sales')
    expect(getSectionPresentation(byId.get('compliance')!, 'de').landingPath).toBe('/policies')
    expect(getSectionPresentation(byId.get('fibu')!, 'de').landingPath).toBe('/fibu-suite')
  })

  it('lokalisiert Domaenen und nutzt bereinigte Prozesslabels', async () => {
    const sections = await loadNavSections()
    const workflow = sections.find((section) => section.id === 'workflow')

    expect(getDomainPresentation('sales', 'de').label).toBe('Vertrieb')
    expect(getDomainPresentation('Vertrieb', 'de').label).toBe('Vertrieb')
    expect(workflow?.children?.find((child) => child.id === 'workflow-flow-spine-procure-to-pay')?.label).toBe(
      'Bedarf bis Zahlung',
    )
    expect(workflow?.children?.find((child) => child.id === 'workflow-flow-spine-finance-to-close')?.label).toBe(
      'Finanzen bis Abschluss',
    )
  })

  it('liefert fuer jede Dashboard-Sektion einen konkreten oeffnenden Einstiegspfad', async () => {
    const sections = await loadNavSections()

    for (const section of sections) {
      const presentation = getSectionPresentation(section, 'de')
      expect(presentation.landingPath, `${section.id} missing landingPath`).toBeTruthy()
      expect(presentation.landingPath).not.toContain(':')
      expect(presentation.landingLabel, `${section.id} missing landingLabel`).toBeTruthy()
    }
  })
})
