import { screen } from '@testing-library/react'
import { mountDomainPage, state } from '../multi-domain-uix-harness'
import Bwa from '@/pages/fibu/bwa'
import Journal from '@/pages/fibu/buchungsjournal'
import Recurring from '@/pages/fibu/periodische-buchungen'
import RevenueCodes from '@/pages/fibu/erloeskennziffern'
import RevenueAccounts from '@/pages/fibu/erloeskontenzuordnung'
import ReceivableGroups from '@/pages/fibu/forderungsgruppen'
import Payroll from '@/pages/fibu/lohn-connector'
import Atlas from '@/pages/fibu/atlas'
import PortalOrders from '@/pages/portal/bestellungen'
import PortalInvoices from '@/pages/portal/rechnungen'
import PortalContracts from '@/pages/portal/vertraege'
import PortalRequests from '@/pages/portal/anfragen'
import PortalShop from '@/pages/portal/shop'
import PortalRecommendations from '@/pages/portal/empfehlungen'
import Terms from '@/pages/einkauf/zahlungsbedingungen'
import InvoiceCapture from '@/pages/einkauf/rechnung-eingang-erfassung'
import Reports from '@/pages/einkauf/reports'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('FIBU / Portal / NaWaRo UIX', () => {
  it('stellt BWA-Aktualisieren auf 44 px', async () => {
    await mountDomainPage(Bwa, 'fibu/bwa', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
  })

  it('stellt Journal-Storno und Abschluss-Details auf 44 px', async () => {
    await mountDomainPage(Journal, 'fibu/buchungsjournal-liste', true)
    expect.soft(screen.queryByRole('button', { name: /Storno|Stornieren/ })).toHaveClass('min-h-touch')
    // Remaining detail-page source checks are explicitly static until an entity-bound mount exists.
    expect(read('../../pages/fibu/abschluss-cockpit.tsx')).toContain('min-h-touch')
    const check = read('../../pages/fibu/abschluss-checklist-detail.tsx')
    expect(check).toContain('Erledigen')
    expect(check).not.toContain('Instanz ')
  })

  it('beschriftet FIBU-Stammaktionen 44 px', async () => {
    for (const [Page, id, label] of [
      [Recurring, 'fibu/periodische-buchungen', 'Sperren'],
      [RevenueCodes, 'fibu/erloeskennziffern', 'Bearbeiten'],
      [RevenueAccounts, 'fibu/erloeskontenzuordnung', 'Bearbeiten'],
      [ReceivableGroups, 'fibu/forderungsgruppen', 'Löschen'],
      [Payroll, 'fibu/lohn-connector', 'Löschen'],
    ] as const) {
      await mountDomainPage(Page, id, true)
      expect.soft(screen.queryByRole('button', { name: label })).toHaveClass('min-h-touch')
    }
    await mountDomainPage(Atlas, 'fibu/atlas', true)
    expect(screen.getByRole('button', { name: 'CSV-Export' })).toHaveClass('min-h-touch')
  })

  it('stellt Portal-Self-Service 44 px mit beschrifteten Zeilen', async () => {
    for (const [Page, id, label] of [
      [PortalOrders, 'portal/bestellungen', 'Details'],
      [PortalInvoices, 'portal/rechnungen', 'Download'],
      [PortalContracts, 'portal/vertraege', 'Details'],
      [PortalRequests, 'portal/anfragen', 'Details'],
    ] as const) {
      await mountDomainPage(Page, id, true)
      expect.soft(screen.queryByRole('button', { name: label })).toHaveClass('min-h-touch')
    }
    await mountDomainPage(PortalShop, 'portal/shop', true)
    expect(screen.getByRole('button', { name: 'CSV-Export' })).toHaveClass('min-h-touch')
    await mountDomainPage(PortalRecommendations, 'portal/empfehlungen', true)
    expect(screen.getByRole('button', { name: 'CSV-Export' })).not.toHaveClass('text-gray-900')
  })

  it('stellt NaWaRo-Erfassung 44 px', () => {
    expect(read('../../pages/nawaro/anbauflaechen.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/vertraege.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/mitteilung-drucken.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/anbauflaechen.tsx')).not.toMatch(/size="sm"/)
  })

  it('beschriftet Einkauf-Stamm und Rechnungs-Toolbar 44 px', async () => {
    state.roles = ['FINANCE_BEARBEITEN']
    await mountDomainPage(Terms, 'einkauf/zahlungsbedingungen', true)
    expect(screen.getByRole('button', { name: 'Zahlungsbedingung anlegen' })).toHaveClass('min-h-touch')
    await mountDomainPage(InvoiceCapture, 'einkauf/rechnung-eingang-erfassung', true)
    expect.soft(screen.queryByRole('button', { name: 'Speichern' })).toHaveClass('min-h-touch')
    expect.soft(screen.queryByRole('combobox', { name: 'Kostenstelle suchen' })).toBeInTheDocument()
    expect.soft(screen.queryByText(/Bediener:/)).toBeInTheDocument()
    expect(read('../../pages/einkauf/gutschriften-belastungen.tsx')).toContain('Entfernen')
    await mountDomainPage(Reports, 'einkauf/reports', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
  })

  it('beschriftet Stammdaten- und Partie-Aktionen 44 px', () => {
    expect(read('../../pages/stammdaten/hausbanken.tsx')).toContain('Bearbeiten')
    expect(read('../../pages/stammdaten/betriebsstaetten.tsx')).toContain('Löschen')
    expect(read('../../pages/stammdaten/mengeneinheiten.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/lager/partiestamm.tsx')).toContain('Löschen')
    expect(read('../../pages/logistik/frachttabellen.tsx')).toContain('min-h-touch')
    expect(read('../../pages/benachrichtigungen/liste.tsx')).not.toMatch(/size="sm"/)
  })
})
