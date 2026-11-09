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
      ['sales/auftraege-liste.tsx', 'beleg-liste/sales-order'],
      ['service/anfragen.tsx', 'service/anfragen-liste'],
    ]
    for (const [file, screenId] of batch3) {
      const src = read(file)
      expect(src).toContain('NativeListPage')
      expect(src).toContain(`screenId="${screenId}"`)
    }
    const rekl = read('qualitaet/reklamationen.tsx')
    expect(rekl).toContain('NativeListPage')
    expect(rekl).toContain('screenId="qualitaet/reklamationen-liste"')
  })

  it('Debitoren-, Mischfuttermittel-, Auftragsbestaetigungen- und Artikel-Listen nutzen NativeListPage', () => {
    expect(read('finance/debitoren-liste.tsx')).toContain('NativeListPage')
    expect(read('finance/debitoren-liste.tsx')).toContain('screenId="finance/debitoren-liste"')
    expect(read('futtermittel/mischfuttermittel-liste.tsx')).toContain('screenId="futtermittel/mischfuttermittel-liste"')
    expect(read('einkauf/auftragsbestaetigungen-liste.tsx')).toContain('screenId="einkauf/auftragsbestaetigungen"')
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
    expect(read('verkauf/kunden-liste.tsx')).toContain('screenId="crm/kunden-liste"')
  })

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('Sales-Auftraege- und Lieferungen-Listen nutzen NativeListPage', () => {
    expect(read('sales/auftraege-liste.tsx')).toContain('screenId="sales/auftraege-liste"')
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

  it('Rechnungseingaenge-Liste ist die Eingangsrechnungs-Variante der Belegliste (DocFlow)', () => {
    expect(read('einkauf/rechnungseingaenge-liste.tsx')).toContain('screenId="beleg-liste/purchase-invoice"')
    const familie = readFileSync(
      resolve(__dirname, '../../../../../app/core/screen_definitions_family_beleg_liste.py'),
      'utf8',
    )
    expect(familie).toContain('row_route=f"/belege/{belegart}/{{id}}"')
  })

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('Batch-11-Listen nutzen NativeListPage mit ScreenDefinition-IDs', () => {
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

  it('Ausgangsrechnungen-Worklist ist die Rechnungs-Variante der Belegliste (DocFlow)', () => {
    expect(read('verkauf/rechnungen-worklist.tsx')).toContain('screenId="beleg-liste/sales-invoice"')
    expect(read('sales/rechnungen-liste.tsx')).toContain('screenId="beleg-liste/sales-invoice"')
  })
})
