import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('UIX zentrale Runtime und Restmasken', () => {
  it('stellt Mask-Builder-Tabelle und ObjectPage auf 44 px', () => {
    const table = read('../../components/mask-builder/renderers/FastTableRenderer.tsx')
    expect(table).toContain('min-h-touch')
    expect(table).toContain('disabled={(page ?? 1) >= totalPages}')
    expect(table).not.toMatch(/size="sm"/)
    expect(table).not.toMatch(/className="h-7/)
    const page = read('../../components/mask-builder/ObjectPage.tsx')
    expect(page).toContain('Wiederherstellen')
    expect(page).toContain('Verwerfen')
    expect(page).not.toMatch(/size="sm"/)
    expect(read('../../components/list/AdvancedFilters.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../components/mask-builder/ListReport.tsx')).toContain('data-global-button-handler="ignore"')
  })

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('stellt Start, Dokumente, Wissen und Leads 44 px', () => {
    expect(read('../../pages/start-dashboard.tsx')).toContain('Oeffnen')
    expect(read('../../pages/start-dashboard.tsx')).not.toMatch(/size="sm"/)
    const ablage = read('../../pages/dokumente/ablage.tsx')
    expect(ablage).toContain('Download')
    expect(ablage).toContain('useTouchDevice')
    expect(ablage).toContain('{!isTouch ? (')
    expect(ablage).toContain('handleExport')
    expect(ablage).toContain('data-global-button-handler="ignore"')
    expect(ablage).toContain('handleDownload')
    expect(ablage).toContain('min-h-touch')
    expect(ablage).not.toMatch(/size="sm"/)
    expect(ablage).toContain('<h1 className="text-2xl font-bold md:text-3xl">Dokumenten-Ablage</h1>')
    expect(read('../../pages/wissen/wissensbasis.tsx')).toContain('min-h-touch')
    expect(read('../../pages/prospecting/LeadExplorer.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/prospecting/LeadExplorer.tsx')).not.toContain('h-6 text-xs')
  })

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('stellt Agenten-Integration und Vordruck 44 px mit deutschen Elementtypen', () => {
    expect(read('../../pages/admin/agenten-integration.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/admin/agenten-integration.tsx')).toContain('Freigeben')
    const vordruck = read('../../pages/admin/vordruck-editor.tsx')
    expect(vordruck).toContain('ELEMENT_TYP_LABELS')
    expect(vordruck).toContain('Löschen')
    expect(vordruck).not.toMatch(/size="sm"/)
    expect(read('../../pages/portal/whatsapp-simulator.tsx')).not.toMatch(/size="sm"/)
  })

  // Der fruehere Fall zu Auftrag/Rechnung/Lieferschein-Editor entfiel 09.11.2026: die Seiten oeffnen die Belegmaske.
})
