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

  const migrated: Array<{ file: string; screenId: string }> = [
    { file: 'finance/debitoren-stamm.tsx', screenId: 'finance/debitor' },
    { file: 'finance/kreditoren-stamm.tsx', screenId: 'finance/kreditor' },
    { file: 'finance/bankkonten-stamm.tsx', screenId: 'finance/bankkonto' },
    { file: 'futtermittel/einzelfuttermittel-stamm.tsx', screenId: 'futtermittel/einzelfuttermittel' },
    { file: 'futtermittel/mischfuttermittel-stamm.tsx', screenId: 'futtermittel/mischfuttermittel' },
    { file: 'crm/opportunity-detail.tsx', screenId: 'crm/opportunity' },
    { file: 'agrar/duenger/stamm.tsx', screenId: 'agrar/duenger' },
    { file: 'agrar/saatgut/stamm.tsx', screenId: 'agrar/saatgut' },
    { file: 'agrar/duenger-stamm.tsx', screenId: 'agrar/duenger' },
    { file: 'agrar/saatgut-stamm.tsx', screenId: 'agrar/saatgut' },
    { file: 'einkauf/anfrage-stamm.tsx', screenId: 'einkauf/anfrage' },
    { file: 'einkauf/angebot-stamm.tsx', screenId: 'einkauf/angebot' },
    { file: 'einkauf/anlieferavis.tsx', screenId: 'einkauf/anlieferavis' },
    { file: 'einkauf/auftragsbestaetigung.tsx', screenId: 'einkauf/auftragsbestaetigung' },
    { file: 'einkauf/rechnungseingang.tsx', screenId: 'finance/ap-invoice' },
    { file: 'crm/lieferanten-stamm.tsx', screenId: 'einkauf/supplier' },
    { file: 'crm/kunden-stamm.tsx', screenId: 'crm/customer-360' },
    { file: 'qualitaet/reklamation-detail.tsx', screenId: 'qualitaet/reklamation' },
    { file: 'einkauf/bestellung-stamm.tsx', screenId: 'einkauf/purchase-order' },
  ]

  it('CRM-Kunden- und Lieferanten-Listen laufen ueber NativeListPage', () => {
    expect(read('crm/kunden-liste.tsx')).toContain('screenId="crm/kunden-liste"')
    expect(read('crm/lieferanten-liste.tsx')).toContain('screenId="crm/lieferanten-liste"')
  })

  it.each(migrated)('$file nutzt createStammNativeDetailPage mit $screenId', ({ file, screenId }) => {
    const src = read(file)
    expect(src).toContain('createStammNativeDetailPage')
    expect(src).toContain(`'${screenId}'`)
    expect(src).toContain('-legacy')
  })
})
