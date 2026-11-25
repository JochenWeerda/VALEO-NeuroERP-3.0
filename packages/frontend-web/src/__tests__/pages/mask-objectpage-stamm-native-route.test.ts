import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { isStammCreationEntityId } from '@/components/mask-builder'

const pages = resolve(__dirname, '../../pages')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('Batch 5–6: Legacy-ObjectPage-Stamm → UniversalMaskRuntime', () => {
  it('isStammCreationEntityId erkennt Anlage-Routen', () => {
    expect(isStammCreationEntityId(undefined)).toBe(true)
    expect(isStammCreationEntityId('')).toBe(true)
    expect(isStammCreationEntityId('new')).toBe(true)
    expect(isStammCreationEntityId('neu')).toBe(true)
    expect(isStammCreationEntityId('42')).toBe(false)
    expect(isStammCreationEntityId('DEB-001')).toBe(false)
  })

  const migrated: Array<{ file: string; screenId: string; kind: 'factory' | 'native-create' | 'native' | 'create-capture' }> = [
    { file: 'finance/debitoren-stamm.tsx', screenId: 'finance/debitor', kind: 'create-capture' },
    { file: 'finance/kreditoren-stamm.tsx', screenId: 'finance/kreditor', kind: 'native' },
    { file: 'finance/bankkonten-stamm.tsx', screenId: 'finance/bankkonto', kind: 'native' },
    { file: 'futtermittel/einzelfuttermittel-stamm.tsx', screenId: 'futtermittel/einzelfuttermittel', kind: 'native-create' },
    { file: 'futtermittel/mischfuttermittel-stamm.tsx', screenId: 'futtermittel/mischfuttermittel', kind: 'native-create' },
    { file: 'crm/opportunity-detail.tsx', screenId: 'crm/opportunity', kind: 'native' },
    { file: 'agrar/duenger/stamm.tsx', screenId: 'agrar/duenger', kind: 'native' },
    { file: 'agrar/saatgut/stamm.tsx', screenId: 'agrar/saatgut', kind: 'native' },
    { file: 'agrar/duenger-stamm.tsx', screenId: 'agrar/duenger', kind: 'native' },
    { file: 'agrar/saatgut-stamm.tsx', screenId: 'agrar/saatgut', kind: 'native' },
    { file: 'einkauf/anfrage-stamm.tsx', screenId: 'einkauf/anfrage', kind: 'native' },
    { file: 'einkauf/angebot-stamm.tsx', screenId: 'einkauf/angebot', kind: 'native' },
    { file: 'einkauf/anlieferavis.tsx', screenId: 'einkauf/anlieferavis', kind: 'native' },
    { file: 'einkauf/auftragsbestaetigung.tsx', screenId: 'einkauf/auftragsbestaetigung', kind: 'native' },
    { file: 'crm/lieferanten-stamm.tsx', screenId: 'einkauf/supplier', kind: 'native' },
    { file: 'crm/kunden-stamm.tsx', screenId: 'crm/customer-360', kind: 'native' },
    { file: 'qualitaet/reklamation-detail.tsx', screenId: 'qualitaet/reklamation', kind: 'native' },
    { file: 'stammdaten/artikelbestandteile.tsx', screenId: 'stammdaten/artikelbestandteile', kind: 'native' },
    { file: 'stammdaten/artikelverpackung.tsx', screenId: 'stammdaten/artikelverpackung', kind: 'native' },
    { file: 'stammdaten/artikel-stoffstrom.tsx', screenId: 'stammdaten/artikel-stoffstrom', kind: 'native' },
    { file: 'stammdaten/individuelle-artikelnummern.tsx', screenId: 'stammdaten/individuelle-artikelnummern', kind: 'native' },
    { file: 'verkauf/kunde-neu.tsx', screenId: 'verkauf/kunde-neu', kind: 'native' },
    { file: 'verkauf/kunden-stamm-enhanced.tsx', screenId: 'verkauf/kunden-stamm-enhanced', kind: 'native' },
    { file: 'preise/individualpreise.tsx', screenId: 'preise/individualpreise', kind: 'native' },
    { file: 'preise/rabattgruppen.tsx', screenId: 'preise/rabattgruppen', kind: 'native' },
    { file: 'preise/zu-abschlaggruppen.tsx', screenId: 'preise/zu-abschlaggruppen', kind: 'native' },
    { file: 'verkauf/dauerauftraege.tsx', screenId: 'verkauf/dauerauftraege', kind: 'native' },
    { file: 'produktion/rezepturgruppen.tsx', screenId: 'produktion/rezepturgruppen', kind: 'native' },
    { file: 'fibu/geschaeftsjahre.tsx', screenId: 'fibu/geschaeftsjahre', kind: 'native' },
    { file: 'lager/massebilanz.tsx', screenId: 'lager/massebilanz', kind: 'native' },
    { file: 'lager/permanente-inventur.tsx', screenId: 'lager/permanente-inventur', kind: 'native' },
    { file: 'fibu/zahlungsmeldungen.tsx', screenId: 'fibu/zahlungsmeldungen', kind: 'native' },
    { file: 'fibu/op-skonto-auszifferung.tsx', screenId: 'fibu/op-skonto-auszifferung', kind: 'native' },
    { file: 'fibu/stammdaten.tsx', screenId: 'fibu/stammdaten', kind: 'native' },
    { file: 'finance/bank-stamm.tsx', screenId: 'finance/bankkonto', kind: 'native' },
    { file: 'agribusiness/field-service-task-neu.tsx', screenId: 'agribusiness/field-service-tasks/neu', kind: 'native' },
    { file: 'personal/schulung-neu.tsx', screenId: 'personal/schulung-neu', kind: 'native' },
    { file: 'agrar/rohwarengruppen.tsx', screenId: 'agrar/rohwarengruppen', kind: 'native' },
    { file: 'agrar/vermehrungsvertraege.tsx', screenId: 'agrar/vermehrungsvertraege', kind: 'native' },
    { file: 'fibu/abschluss-checklist-detail.tsx', screenId: 'fibu/abschluss-checklist-detail', kind: 'native' },
  ]

  it('CRM-Kunden- und Lieferanten-Listen laufen ueber NativeListPage', () => {
    expect(read('crm/kunden-liste.tsx')).toContain('screenId="crm/kunden-liste"')
    expect(read('crm/lieferanten-liste.tsx')).toContain('screenId="crm/lieferanten-liste"')
  })

  it.each(migrated)('$file bindet den aktuellen $kind-Pfad an $screenId', ({ file, screenId, kind }) => {
    const src = read(file)
    if (kind === 'native') {
      expect(src).toContain('createStammNativeDetailPage')
      expect(src).toContain(`'${screenId}'`)
      expect(src).not.toContain('-legacy')
    } else if (kind === 'factory') {
      expect(src).toContain('createStammNativeDetailPage')
      expect(src).toContain(`'${screenId}'`)
      expect(src).toContain('-legacy')
    } else if (kind === 'create-capture') {
      expect(src).toContain('createStammNativeDetailPage')
      expect(src).toContain(`'${screenId}'`)
      expect(src).toContain('<UniversalNativeCreatePage')
      expect(src).toContain('finance/debitoren/new')
      expect(src).not.toContain('-legacy')
    } else {
      expect(src).toContain('<UniversalNativeCreatePage')
      expect(src).toContain('<UniversalNativeDetailPage')
      expect(src).toContain(`screenId="${screenId}"`)
    }
  })

  it('alle 40 Page-Wrapper sind in der produktiven Routenregistry eingetragen (Bestellung und Eingangsrechnung seit BELEG-052 in der Belegmaske)', () => {
    const routeTree = readFileSync(resolve(__dirname, '../../app/routing/route-tree.gen.tsx'), 'utf8')
    expect(migrated).toHaveLength(40)
    for (const { file } of migrated) {
      expect(routeTree).toContain(`renderPage("@/pages/${file.replace(/\.tsx$/, '')}")`)
    }
  })

  it('deklarierte Anlagepfade behalten ihre Create-Formulare ohne neu/new als Detail-ID', () => {
    const routeTree = readFileSync(resolve(__dirname, '../../app/routing/route-tree.gen.tsx'), 'utf8')
    const declaredCreateRoutes = [
      ['einkauf/anfrage/neu', 'einkauf/anfrage-stamm'],
      ['einkauf/angebot/neu', 'einkauf/angebot-stamm'],
      ['einkauf/anlieferavis/neu', 'einkauf/anlieferavis'],
      ['einkauf/auftragsbestaetigung/neu', 'einkauf/auftragsbestaetigung'],
      ['einkauf/lieferant/neu', 'einkauf/lieferanten-stamm'],
      ['einkauf/rechnungseingang/neu', 'einkauf/rechnungseingang'],
    ] as const
    // Eingangsrechnung und Bestellung legen seit BELEG-052 (08.11.2026) ueber die Belegmaske an (DocFlow).
    expect(read('einkauf/rechnungseingang.tsx')).toContain("belegSeite('purchase_invoice')")
    expect(read('einkauf/bestellung-stamm.tsx')).toContain("belegSeite('purchase_order')")
    for (const [route, page] of declaredCreateRoutes) {
      expect(routeTree).toContain(`path: "${route}"`)
      expect(routeTree).toContain(`"module":"@/pages/${page}","legacyPath":"/${route}"`)
    }
    // Saatgut/Duenger: Create laeuft native; Legacy-Dateien bleiben nur als Rollback-Artefakt.
    for (const file of [
      'crm/opportunity-detail-legacy.tsx',
      'einkauf/anfrage-stamm-legacy.tsx', 'einkauf/angebot-stamm-legacy.tsx',
      'einkauf/anlieferavis-legacy.tsx',
    ]) {
      expect(read(file)).toContain('isStammCreationEntityId')
    }
    for (const file of [
      'finance/debitoren-stamm-legacy.tsx', 'finance/kreditoren-stamm-legacy.tsx',
    ]) {
      expect(read(file)).not.toMatch(/id:\s*['"]new['"]/)
    }
  })
})
