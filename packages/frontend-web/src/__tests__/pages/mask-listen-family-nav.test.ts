import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

describe('Listenfamilien: aktuelles Routeninventar (Quellnachweis)', () => {
  it('Batch-3-Listen nutzen NativeListPage mit ScreenDefinition-IDs', () => {
    const batch3: Array<[string, string]> = [
      ['agrar/biostimulanzien-liste.tsx', 'agrar/biostimulanzien-liste'],
      ['agrar/ernte/liste.tsx', 'agrar/ernte-liste'],
      ['sales/auftraege-liste.tsx', 'verkauf/auftraege'],
      ['service/anfragen.tsx', 'service/anfragen'],
    ]
    for (const [file, screenId] of batch3) {
      const src = read(file)
      expect(src).toContain('NativeListPage')
      expect(src).toContain(`screenId="${screenId}"`)
    }
    const rekl = read('qualitaet/reklamationen.tsx')
    expect(rekl).toContain('useReklamationen')
    expect(rekl).toContain('saveFlowSpineResumeCheckpoint')
  })

  it('Debitoren-, Mischfuttermittel-, Auftragsbestaetigungen- und Artikel-Listen nutzen NativeListPage', () => {
    expect(read('finance/debitoren-liste.tsx')).toContain('NativeListPage')
    expect(read('finance/debitoren-liste.tsx')).toContain('screenId="finance/debitoren-liste"')
    expect(read('futtermittel/mischfuttermittel-liste.tsx')).toContain('screenId="futtermittel/mischfuttermittel/liste"')
    expect(read('einkauf/auftragsbestaetigungen-liste.tsx')).toContain('screenId="einkauf/auftragsbestaetigungen-liste"')
    expect(read('artikel/liste.tsx')).toContain('screenId="artikel/liste"')
  })

  it('CRM-Lieferanten-Liste nutzt NativeListPage und kanonische row_route in ScreenDefinition', () => {
    expect(read('crm/lieferanten-liste.tsx')).toContain('screenId="crm/lieferanten-liste"')
    const listen = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions_listen.py'),
      'utf8',
    )
    expect(listen).toContain('row_route="/crm/lieferanten/{id}"')
    expect(listen).not.toContain('row_route="/crm/lieferanten/stamm/{id}"')
  })

  it('CRM-Kunden-Liste nutzt NativeListPage und Customer-360 row_route', () => {
    expect(read('crm/kunden-liste.tsx')).toContain('screenId="crm/kunden-liste"')
    const listen = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions_listen.py'),
      'utf8',
    )
    expect(listen).toContain('row_route="/crm/kunden/{id}"')
    expect(listen).toContain('"/verkauf/kunde/neu"')
  })

  it('Verkauf-Kunden-Liste bindet ihre eigene aktuelle ScreenDefinition', () => {
    expect(read('verkauf/kunden-liste.tsx')).toContain('screenId="verkauf/kunden-liste"')
  })

  it('Sales-Auftraege- und Lieferungen-Listen nutzen NativeListPage', () => {
    expect(read('sales/auftraege-liste.tsx')).toContain('screenId="verkauf/auftraege"')
    const lieferungen = read('sales/lieferungen-liste.tsx')
    expect(lieferungen).toContain('useLieferungen')
    expect(lieferungen).toContain('RoleFocusBar')
    const listen = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions_listen.py'),
      'utf8',
    )
    expect(listen).toContain('row_route="/sales/sales-order/{id}"')
    expect(listen).toContain('row_route="/sales/delivery-note/{id}"')
  })

  it('Rechnungseingaenge-Liste nutzt NativeListPage und Beleg-Zeilenroute', () => {
    expect(read('einkauf/rechnungseingaenge-liste.tsx')).toContain('screenId="einkauf/rechnungseingaenge-liste"')
    const listen = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions_listen.py'),
      'utf8',
    )
    expect(listen).toContain('row_route="/belege/purchase_invoice/{id}"')
  })

  it('Batch-11-Listen nutzen NativeListPage mit ScreenDefinition-IDs', () => {
    const batch11: Array<[string, string]> = [
      ['admin/audit-log.tsx', 'admin/audit-log'],
      ['agrar/bodenproben/liste.tsx', 'agrar/bodenproben-liste'],
      ['fibu/zahlungslaeufe.tsx', 'fibu/zahlungslaeufe-liste'],
      ['einkauf/bestellvorschlaege.tsx', 'einkauf/bestellvorschlaege-liste'],
      ['compliance/qs-checkliste.tsx', 'compliance/qs-checkliste-liste'],
      ['controlling/plan-ist.tsx', 'controlling/plan-ist-liste'],
      ['dokumente/ablage.tsx', 'dokumente/ablage-liste'],
    ]
    for (const [file, screenId] of batch11) {
      const src = read(file)
      expect(src).toContain('NativeListPage')
      expect(src).toContain(`screenId="${screenId}"`)
    }
    const debitoren = read('fibu/debitoren.tsx')
    expect(debitoren).toContain('useDebitorenOP')
    expect(debitoren).toContain('exportToCSV')
  })

  it('Ausgangsrechnungen-Worklist (sales/invoices) zeigt auf Beleg-Detailroute', () => {
    const sd = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions.py'),
      'utf8',
    )
    expect(sd).toContain('"rowRouteTemplate": "/belege/sales_invoice/{id}"')
    expect(sd).not.toContain('"rowRouteTemplate": "/verkauf/rechnung/{id}"')
  })
})
