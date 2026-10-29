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

  const migrated: Array<{ file: string; screenId: string; kind: 'factory' }> = [
    { file: 'finance/debitoren-stamm.tsx', screenId: 'finance/debitor', kind: 'factory' },
    { file: 'finance/kreditoren-stamm.tsx', screenId: 'finance/kreditor', kind: 'factory' },
    { file: 'finance/bankkonten-stamm.tsx', screenId: 'finance/bankkonto', kind: 'factory' },
    { file: 'futtermittel/einzelfuttermittel-stamm.tsx', screenId: 'futtermittel/einzelfuttermittel', kind: 'factory' },
    { file: 'futtermittel/mischfuttermittel-stamm.tsx', screenId: 'futtermittel/mischfuttermittel', kind: 'factory' },
    { file: 'crm/opportunity-detail.tsx', screenId: 'crm/opportunity', kind: 'factory' },
    { file: 'agrar/duenger/stamm.tsx', screenId: 'agrar/duenger', kind: 'factory' },
    { file: 'agrar/saatgut/stamm.tsx', screenId: 'agrar/saatgut', kind: 'factory' },
    { file: 'agrar/duenger-stamm.tsx', screenId: 'agrar/duenger', kind: 'factory' },
    { file: 'agrar/saatgut-stamm.tsx', screenId: 'agrar/saatgut', kind: 'factory' },
    { file: 'einkauf/anfrage-stamm.tsx', screenId: 'einkauf/anfrage', kind: 'factory' },
    { file: 'einkauf/angebot-stamm.tsx', screenId: 'einkauf/angebot', kind: 'factory' },
    { file: 'einkauf/anlieferavis.tsx', screenId: 'einkauf/anlieferavis', kind: 'factory' },
    { file: 'einkauf/auftragsbestaetigung.tsx', screenId: 'einkauf/auftragsbestaetigung', kind: 'factory' },
    { file: 'einkauf/rechnungseingang.tsx', screenId: 'finance/ap-invoice', kind: 'factory' },
    { file: 'crm/lieferanten-stamm.tsx', screenId: 'einkauf/supplier', kind: 'factory' },
    { file: 'crm/kunden-stamm.tsx', screenId: 'crm/customer-360', kind: 'factory' },
    { file: 'qualitaet/reklamation-detail.tsx', screenId: 'qualitaet/reklamation', kind: 'factory' },
    { file: 'einkauf/bestellung-stamm.tsx', screenId: 'einkauf/purchase-order', kind: 'factory' },
  ]

  it('CRM-Kunden- und Lieferanten-Listen laufen ueber NativeListPage', () => {
    expect(read('crm/kunden-liste.tsx')).toContain('screenId="crm/kunden-liste"')
    expect(read('crm/lieferanten-liste.tsx')).toContain('screenId="crm/lieferanten-liste"')
  })

  it.each(migrated)('$file bindet den aktuellen $kind-Pfad an $screenId', ({ file, screenId, kind }) => {
    const src = read(file)
    if (kind === 'factory') {
      expect(src).toContain('createStammNativeDetailPage')
      expect(src).toContain(`'${screenId}'`)
      expect(src).toContain('-legacy')
    } else {
      expect(src).toContain('<NativeListPage')
      expect(src).toContain(`screenId="${screenId}"`)
    }
  })

  it('alle 19 Page-Wrapper sind in der produktiven Routenregistry eingetragen', () => {
    const routeTree = readFileSync(resolve(__dirname, '../../app/routing/route-tree.gen.tsx'), 'utf8')
    expect(migrated).toHaveLength(19)
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
    for (const [route, page] of declaredCreateRoutes) {
      expect(routeTree).toContain(`path: "${route}"`)
      expect(routeTree).toContain(`"module":"@/pages/${page}","legacyPath":"/${route}"`)
    }
    for (const file of [
      'agrar/saatgut-stamm-legacy.tsx', 'agrar/duenger-stamm-legacy.tsx',
      'crm/opportunity-detail-legacy.tsx', 'crm/kunden-stamm-legacy.tsx',
      'einkauf/anfrage-stamm-legacy.tsx', 'einkauf/angebot-stamm-legacy.tsx',
      'einkauf/anlieferavis-legacy.tsx', 'einkauf/auftragsbestaetigung-legacy.tsx',
      'einkauf/rechnungseingang-legacy.tsx', 'einkauf/lieferanten-stamm-legacy.tsx',
      'einkauf/bestellung-stamm-legacy.tsx',
    ]) {
      expect(read(file)).toContain('isStammCreationEntityId')
    }
    for (const file of [
      'finance/debitoren-stamm-legacy.tsx', 'finance/kreditoren-stamm-legacy.tsx',
      'futtermittel/einzelfuttermittel-stamm-legacy.tsx',
      'futtermittel/mischfuttermittel-stamm-legacy.tsx', 'crm/lieferanten-stamm-legacy.tsx',
    ]) {
      expect(read(file)).not.toMatch(/id:\s*['"]new['"]/)
    }
  })
})
