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

  it('stellt Start, Dokumente, Wissen und Leads 44 px', () => {
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

  it('stellt Agenten-Integration und Vordruck 44 px mit deutschen Elementtypen', () => {
    expect(read('../../pages/admin/agenten-integration.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/admin/agenten-integration.tsx')).toContain('Freigeben')
    const vordruck = read('../../pages/admin/vordruck-editor.tsx')
    expect(vordruck).toContain('ELEMENT_TYP_LABELS')
    expect(vordruck).toContain('Löschen')
    expect(vordruck).not.toMatch(/size="sm"/)
    expect(read('../../pages/portal/whatsapp-simulator.tsx')).not.toMatch(/size="sm"/)
  })

  it('stellt KIM, Auftrag, Rechnung und Lieferschein ohne size=sm', () => {
    const files = [
      '../../pages/crm/kim/index.tsx',
      '../../pages/crm/kim/components/CustomerActionBar.tsx',
      '../../pages/crm/kim/components/ContactPersonsTable.tsx',
      '../../pages/crm/kim/components/DocumentPanel.tsx',
      '../../pages/crm/kim/components/CustomerGiftsTab.tsx',
      '../../pages/sales/OrderEditorLegacyPage.tsx',
      '../../pages/sales/invoice-editor.tsx',
      '../../pages/sales/delivery-editor.tsx',
      '../../pages/sales/delivery-editor-new.tsx',
      '../../pages/sales/auftragskette.tsx',
      '../../pages/sales/auftrag-lieferschein-abgleich.tsx',
    ]
    for (const file of files) {
      expect(read(file), file).not.toMatch(/size="sm"/)
    }
    expect(read('../../pages/crm/kim/components/DocumentPanel.tsx')).toContain('Löschen')
    expect(read('../../pages/crm/kim/index.tsx')).not.toMatch(/h-6 px-2/)
    expect(read('../../pages/sales/OrderEditorLegacyPage.tsx')).toContain('min-h-touch')
    expect(read('../../pages/sales/OrderEditorLegacyPage.tsx')).not.toMatch(/h-8 w-8/)
    expect(read('../../pages/sales/invoice-editor.tsx')).toContain('XRechnung')
  })
})
