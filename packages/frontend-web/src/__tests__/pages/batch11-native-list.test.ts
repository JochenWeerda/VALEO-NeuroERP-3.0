import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { createElement } from 'react'
import { fireEvent, screen } from '@testing-library/react'
import { mountBatchList, transport } from '../native-batch11-12-contract-harness'
import KundenListePage from '@/pages/crm/kunden-liste'
import debitorenDefinition from '../fixtures/fibu-debitoren-builder-contract.json'

const pages = resolve(__dirname, '../../pages')
const listenPy = readFileSync(
  resolve(__dirname, '../../../../../app/core/screen_definitions_listen.py'),
  'utf8',
)

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

/** Historical Batch 11 route set (59 pages). Exceptions below retain their operational paths. */
const BATCH11: Array<[string, string]> = [
  ['admin/audit-log.tsx', 'admin/audit-log-liste'],
  ['agrar/bodenproben/liste.tsx', 'agrar/bodenproben-liste'],
  ['agrar/ernte-annahme-energiemais.tsx', 'agrar/ernte-annahme-energiemais-liste'],
  ['agrar/feldbuch/ackerschlagkartei.tsx', 'agrar/feldbuch-schlagkartei-liste'],
  ['agrar/feldbuch/flurstueck-kataster.tsx', 'agrar/feldbuch-flurstueck-kataster-liste'],
  ['agrar/kultur-stamm.tsx', 'agrar/kultur-stamm-liste'],
  ['agrar/maschinen-auslastung.tsx', 'agrar/maschinen-auslastung-liste'],
  ['agrar/nachhaltigkeit-eudr.tsx', 'agrar/nachhaltigkeit-eudr-liste'],
  ['agrar/pflanzenschutz-applikationen.tsx', 'agrar/pflanzenschutz-applikationen-liste'],
  ['agrar/psm/abgabedokumentation.tsx', 'agrar/psm-abgabedokumentation-liste'],
  ['agrar/psm/beratung.tsx', 'agrar/psm-beratung-liste'],
  ['agrar/psm/sachkunde-register.tsx', 'agrar/psm-sachkunde-register-liste'],
  ['agrar/psm/wasserschutz.tsx', 'agrar/psm-wasserschutz-liste'],
  ['agrar/saatgut/bestellungen.tsx', 'agrar/saatgut-bestellungen-liste'],
  ['agrar/saatgut/sortenregister.tsx', 'agrar/saatgut-sortenregister-liste'],
  ['agrar/schlaege/index.tsx', 'agrar/schlaege-liste'],
  ['agrar/schlaege/karte.tsx', 'agrar/schlaege-karte-liste'],
  ['agrar/schlaege/kulturhistorie.tsx', 'agrar/schlaege-kulturhistorie-liste'],
  ['agrar/vertrag-kontingente.tsx', 'agrar/vertrag-kontingente-liste'],
  ['charge/wareneingang.tsx', 'charge/wareneingang-liste'],
  ['compliance/bvl-umsatzmeldung.tsx', 'compliance/bvl-umsatzmeldung-liste'],
  ['compliance/CrossCompliancePage.tsx', 'compliance/cross-compliance-liste'],
  ['compliance/eudr-compliance.tsx', 'compliance/eudr-compliance-liste'],
  ['compliance/export-pruefung.tsx', 'compliance/export-pruefung-liste'],
  ['compliance/gefahrstoff-doku.tsx', 'compliance/gefahrstoff-doku-liste'],
  ['compliance/qs-checkliste.tsx', 'compliance/qs-checkliste-liste'],
  ['compliance/sachkunde-register.tsx', 'compliance/sachkunde-liste'],
  ['compliance/vvvo-register.tsx', 'compliance/vvvo-liste'],
  ['compliance/zulassungen-register.tsx', 'compliance/zulassungen-liste'],
  ['controlling/plan-ist.tsx', 'controlling/plan-ist-liste'],
  ['crm/contact-detail.tsx', 'crm/contact-detail-liste'],
  ['crm/kontakt-management.tsx', 'crm/kontakt-management-liste'],
  ['crm/kunden-liste.tsx', 'crm/kunden-liste'],
  ['crm/lead-detail.tsx', 'crm/leads-liste'],
  ['crm/lieferanten-liste.tsx', 'crm/lieferanten-liste'],
  ['dokumente/ablage.tsx', 'dokumente/ablage-liste'],
  ['einkauf/anfragen-create.tsx', 'einkauf/anfragen-create-liste'],
  ['einkauf/angebote-vergleich.tsx', 'einkauf/angebote-vergleich-liste'],
  ['einkauf/bestellvorschlaege.tsx', 'einkauf/bestellvorschlaege-liste'],
  ['einkauf/dienstleistungen-haltung.tsx', 'einkauf/dienstleistungen-haltung-liste'],
  ['einkauf/EinkaufVorgangPage.tsx', 'einkauf/einkauf-vorgang-liste'],
  ['einkauf/kontrakte-service.tsx', 'einkauf/kontrakte-service-liste'],
  ['einkauf/rechnung-abgleich.tsx', 'einkauf/rechnung-abgleich-liste'],
  ['einkauf/rechnungseingaenge-liste.tsx', 'einkauf/rechnungseingaenge-liste'],
  ['einkauf/retouren.tsx', 'einkauf/retouren-liste'],
  ['etiketten/druck.tsx', 'etiketten/druck-liste'],
  ['export/intrastat-meldung.tsx', 'export/intrastat-meldung-liste'],
  ['export/umsatzsteuer-voranmeldung.tsx', 'export/umsatzsteuer-voranmeldung-liste'],
  ['fibu/anlagen.tsx', 'fibu/anlagen-liste'],
  ['fibu/buchungsjournal.tsx', 'fibu/buchungsjournal-liste'],
  ['fibu/debitoren.tsx', 'fibu/debitoren-liste'],
  ['fibu/hauptbuch.tsx', 'fibu/hauptbuch-liste'],
  ['fibu/kassenbuch.tsx', 'fibu/kassenbuch-liste'],
  ['fibu/kostenstellenrechnung.tsx', 'fibu/kostenstellen-liste'],
  ['fibu/kreditoren.tsx', 'fibu/kreditoren-liste'],
  ['fibu/offene-posten.tsx', 'fibu/offene-posten-liste'],
  ['fibu/schnittstelle-fibu.tsx', 'fibu/schnittstelle-fibu-liste'],
  ['fibu/verbindlichkeiten.tsx', 'fibu/verbindlichkeiten-liste'],
  ['fibu/zahlungslaeufe.tsx', 'fibu/zahlungslaeufe-liste'],
]

describe('Batch 11 route inventory (source-level evidence only)', () => {
  it.each(BATCH11)('%s → %s', (file, screenId) => {
    const src = read(file)
    if (file === 'admin/audit-log.tsx') {
      // This route was consolidated onto the Batch 12 audit screen.
      expect(src).toContain('screenId="admin/audit-log"')
      expect(src).toContain('testId="screen-admin/audit-log"')
      return
    }
    if (file === 'crm/lead-detail.tsx') {
      // Entity and create paths are distinct; the former uses the Party native detail runtime.
      expect(src).toContain('<PartyNativePage kind="lead" entityId={entityId} />')
      expect(src).toContain('LeadMaskDetailPage')
      expect(src).toContain('LegacyLeadDetailPage')
      return
    }
    if (file === 'fibu/debitoren.tsx') {
      // The canonical route delegates to the real builder/runtime; runtime evidence lives in
      // debitoren-native.test.tsx and the prior list behavior is exercised in debitoren.test.tsx.
      expect(src).toContain('NativeListPage')
      expect(src).toContain(`screenId="${screenId}"`)
      expect(src).toContain(`testId="screen-${screenId}"`)
      expect(src).not.toContain('useDebitorenOP')
      expect(listenPy).toContain(`"${screenId}"`)
      expect(debitorenDefinition.id).toBe(screenId)
      expect(debitorenDefinition.dataSources[0].endpoint).toBe(
        '/api/v1/finance/open-items?konto_typ=debitoren&only_open=true',
      )
      return
    }
    expect(src).toContain('NativeListPage')
    expect(src).toContain(`screenId="${screenId}"`)
    expect(src).toContain(`testId="screen-${screenId}"`)
    expect(listenPy).toContain(`"${screenId}"`)
  })

  it('mounts the routed Kundenliste through its real builder, runtime and table renderer', async () => {
    mountBatchList(createElement(KundenListePage), 'crm/kunden-liste', {
      id: 'synthetic-customer', name: 'SYNTHETIC-CUSTOMER', kunden_nr: 'K-001', ort: 'Bremen',
    })
    expect(await screen.findByText('SYNTHETIC-CUSTOMER')).toBeTruthy()
    expect(transport.get).toHaveBeenCalledWith('/api/v1/masks/crm__kunden-liste/screen-definition', expect.anything())
    fireEvent.click(screen.getByRole('button', { name: 'SYNTHETIC-CUSTOMER' }))
    fireEvent.click(screen.getByRole('button', { name: 'In Vollansicht öffnen' }))
    expect(window.location.pathname).toBe('/crm/kunden/synthetic-customer')
    expect(transport.request).not.toHaveBeenCalled()
  })

  it('CRM- und Rechnungseingangs-Zeilenrouten in screen_definitions_listen', () => {
    expect(listenPy).toContain('row_route="/crm/kunden/{id}"')
    expect(listenPy).toContain('row_route="/crm/lieferanten/{id}"')
    expect(listenPy).toContain('row_route="/belege/purchase_invoice/{id}"')
  })
})
