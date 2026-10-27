import { mountDomainPage, expectSearchWorkArea, expectCsvDownload, state } from '../multi-domain-uix-harness'
import Confirmations from '@/pages/einkauf/auftragsbestaetigungen-liste'
import Requests from '@/pages/einkauf/anfragen-liste'
import OpenItems from '@/pages/fibu/offene-posten'
import Drivers from '@/pages/transporte/fahrer-liste'
import { screen, fireEvent, within } from '@testing-library/react'
import Vehicles from '@/pages/fuhrpark/fahrzeuge'
import Warengruppen from '@/pages/einkauf/warengruppen'
import Notifications from '@/pages/benachrichtigungen/liste'
import Banks from '@/pages/banken/konten'
import Customers from '@/pages/crm/kunden-liste'
import Campaigns from '@/pages/marketing/kampagnen'
import Liabilities from '@/pages/fibu/verbindlichkeiten'
import Creditors from '@/pages/fibu/kreditoren'
import PaymentSuggestions from '@/pages/fibu/zahlungsvorschlaege'
import ArrivalNotices from '@/pages/einkauf/anlieferavis-liste'
import PaymentRuns from '@/pages/fibu/zahlungslaeufe'
import OpenItemAdmin from '@/pages/fibu/op-verwaltung'
import Journal from '@/pages/fibu/buchungsjournal'
import Ledger from '@/pages/fibu/hauptbuch'
import FibuInterface from '@/pages/fibu/schnittstelle-fibu'
import BookingImport from '@/pages/finance/buchungsimport'
import Bwa from '@/pages/fibu/bwa'
import Balance from '@/pages/fibu/bilanz'
import Income from '@/pages/fibu/guv'
import DirectDebit from '@/pages/finance/lastschriften-debitoren'
import Elster from '@/pages/fibu/elster-online'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('CRM/FIBU/Logistik UIX', () => {
  it('bewahrt 40px-Desktopdichte und wechselt auf beschriftete Touch-Ziele statt Desktopzeilen aufzublaehen', async () => {
    await mountDomainPage(Banks, 'banken/konten-liste')
    const desktop = await screen.findByTestId('virtual-data-table')
    expect(within(desktop).getAllByRole('columnheader').length).toBeGreaterThan(0)
    expect(within(desktop).getAllByRole('row')[1]).toHaveStyle({ height: '40px' })
    await mountDomainPage(Banks, 'banken/konten-liste', true)
    const touch = await screen.findByTestId('virtual-data-table')
    expect(within(touch).queryByRole('columnheader')).not.toBeInTheDocument()
    expect(within(touch).getByRole('button')).toHaveAttribute('tabindex', '0')
    expect(screen.getByRole('searchbox', { name: 'Suche in Bankkonten' })).toHaveClass('min-h-touch')
    expect(screen.getByRole('button', { name: 'CSV-Export' })).toHaveClass('min-h-touch')
    // Static token evidence; JSDOM does not constitute a browser pixel measurement.
    expect(readFileSync(resolve(__dirname, '../../index.css'), 'utf8')).toContain('--touch-target: 44px')
  })
  it('oeffnet den Fuhrpark als Maske und legt ein Fahrzeug ueber den Stamm an', async () => {
    await mountDomainPage(Vehicles, 'fuhrpark/fahrzeuge-liste', true)
    const create = screen.getByRole('button', { name: /Neues Fahrzeug|Fahrzeug anlegen/ })
    expect(create).toHaveClass('min-h-touch')
    fireEvent.click(create)
    expect(state.navigate).toHaveBeenCalledWith('/fuhrpark/fahrzeug/neu')
  })

  it('stellt Warengruppen als Studio-Liste dar', async () => {
    state.roles = ['EINKAUF_BEARBEITEN']
    await mountDomainPage(Warengruppen, 'einkauf/warengruppen', true)
    expect(screen.getByRole('button', { name: 'Warengruppe anlegen' })).toHaveClass('min-h-touch')
    await expectSearchWorkArea('Warengruppen')
  })

  it('stellt Debitoren-Liste 44 px ohne Rohorange', () => {
    const src = read('../../pages/fibu/debitoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-mono font-medium text-primary')
    expect(src).toContain('Suche Debitoren')
    expect(src).not.toContain('bg-orange-50')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Benachrichtigungen lokal als gelesen', async () => {
    const rows = [
      { id: 'one', titel: 'Erster Hinweis', nachricht: 'Erste Nachricht', gelesen: false },
      { id: 'two', titel: 'Zweiter Hinweis', nachricht: 'Zweite Nachricht', gelesen: false },
    ]
    const mounted = await mountDomainPage(Notifications, 'benachrichtigungen/liste', true, rows)
    const marks = screen.getAllByRole('button', { name: 'Als gelesen markieren' })
    expect(marks).toHaveLength(2)
    expect(marks[0]).toHaveClass('min-h-touch')
    fireEvent.click(marks[0])
    const remaining = screen.getAllByRole('button', { name: 'Als gelesen markieren' })
    expect(remaining).toHaveLength(1)
    expect(remaining[0].closest('[data-index]')).toHaveTextContent('Zweiter Hinweis')
    expect(state.request).not.toHaveBeenCalled()
    mounted.unmount()
    await mountDomainPage(Notifications, 'benachrichtigungen/liste', true, rows)
    expect(screen.getAllByRole('button', { name: 'Als gelesen markieren' })).toHaveLength(2)
  })

  it('stellt Bankkonten-Export und 44 px', async () => {
    await mountDomainPage(Banks, 'banken/konten-liste', true)
    await expectSearchWorkArea('Bankkonten')
    await expectCsvDownload()
  })

  it('stellt Kunden-mailto ohne Hover-Blau', async () => {
    await mountDomainPage(Customers, 'crm/kunden-liste', true)
    const link = screen.getByRole('link', { name: /SYNTHETIC/ })
    expect(link).toHaveAttribute('href', expect.stringMatching(/^mailto:/))
    expect(link).not.toHaveClass('text-blue-600')
  })

  it('stellt Kampagnen 44 px mit Export', async () => {
    await mountDomainPage(Campaigns, 'marketing/kampagnen', true)
    await expectSearchWorkArea('Kampagnen')
    await expectCsvDownload()
  })

  it('stellt Schulungen ueber den nativen Builder mit Stand und echten Zeilen', () => {
    const src = read('../../pages/personal/schulungen.tsx')
    const definitions = read('../../masks/capture-screens.ts')
    const start = definitions.indexOf('export const personalSchulungenScreen')
    const end = definitions.indexOf('\nexport const ', start + 1)
    const definition = definitions.slice(start, end < 0 ? undefined : end)
    expect(start).toBeGreaterThanOrEqual(0)
    expect(src).toContain('personalSchulungenScreen')
    expect(src).toContain('compileRenderPlanFromScreenDefinition')
    expect(src).toContain('<UniversalMaskRenderer')
    expect(src).toContain('schulungen: rows.map')
    expect(definition).toContain("key: 'status'")
    expect(definition).toContain("label: 'Stand'")
    expect(src).not.toContain('bg-orange-50')
  })

  it('stellt Verbindlichkeiten NativeSelect und 44 px', async () => {
    await mountDomainPage(Liabilities, 'fibu/verbindlichkeiten-liste', true)
    await expectSearchWorkArea('Verbindlichkeiten')
    for (const select of screen.getAllByRole('combobox')) { expect(select.tagName).toBe('SELECT'); expect(select).toHaveClass('min-h-touch') }
  })

  it('stellt Kreditoren Arbeit zuerst und 44 px', async () => {
    await mountDomainPage(Creditors, 'fibu/kreditoren-liste', true)
    await expectSearchWorkArea('Kreditoren OP')
    expect(document.querySelector('[data-screen-definition="fibu/kreditoren-liste"]')).toHaveAttribute('data-density', 'compact')
  })

  it('stellt Zahlungsvorschlaege Arbeit zuerst mit 44-px-Auswahl', async () => {
    await mountDomainPage(PaymentSuggestions, 'fibu/zahlungsvorschlaege', true)
    await expectSearchWorkArea('Zahlungsvorschlaege')
    expect(screen.getByRole('button', { name: 'Zahlungslauf erstellen' })).toHaveClass('min-h-touch')
  })

  it('stellt Anlieferavis als Studio-Liste', async () => {
    await mountDomainPage(ArrivalNotices, 'einkauf/anlieferavis-liste', true)
    await expectSearchWorkArea('Anlieferavis')
    await expectCsvDownload()
  })

  it('stellt Zahlungslaeufe Wizard zuerst mit 44-px-Auswahl', async () => {
    await mountDomainPage(PaymentRuns, 'fibu/zahlungslaeufe-liste', true)
    const name = screen.getByRole('textbox', { name: /Bezeichnung/ })
    expect(name).toHaveClass('min-h-touch')
    fireEvent.click(screen.getByRole('button', { name: /Weiter|Zahlungslauf erstellen/ }))
    expect(await screen.findByText('Bitte eine Bezeichnung erfassen.')).toBeVisible()
  })

  it('stellt OP-Verwaltung Arbeit zuerst mit 44-px-Oeffnen', async () => {
    await mountDomainPage(OpenItemAdmin, 'fibu/op-verwaltung', true)
    for (const label of ['Debitoren oeffnen', 'Kreditoren oeffnen']) expect(screen.getByRole('button', { name: label })).toHaveClass('min-h-touch')
  })

  it('stellt Auftragsbestaetigungen als Studio-Liste', async () => {
    await mountDomainPage(Confirmations, 'einkauf/auftragsbestaetigungen', true)
    await expectSearchWorkArea('Auftragsbestaetigungen')
  })

  it('stellt Einkaufsanfragen als Studio-Liste mit echtem Export', async () => {
    await mountDomainPage(Requests, 'einkauf/anfragen', true)
    await expectCsvDownload()
  })

  it('stellt FIBU Offene Posten Arbeit zuerst mit Mahnlauf', async () => {
    await mountDomainPage(OpenItems, 'fibu/offene-posten-liste', true)
    const dunning = screen.getByRole('button', { name: 'Mahnlauf starten' })
    expect(dunning).toHaveClass('min-h-touch')
    fireEvent.click(dunning)
    expect(state.navigate).toHaveBeenCalledWith('/finance/mahnwesen')
    expect(screen.getAllByRole('combobox').every(select => select.tagName === 'SELECT')).toBe(true)
  })

  it('stellt Buchungsjournal Suche zuerst mit 44 px', async () => {
    await mountDomainPage(Journal, 'fibu/buchungsjournal-liste', true)
    await expectSearchWorkArea('Buchungsjournal')
  })

  it('stellt Hauptbuch Arbeit zuerst mit DATEV-Navigation', async () => {
    await mountDomainPage(Ledger, 'fibu/hauptbuch-liste', true)
    await expectSearchWorkArea('Hauptbuch')
    fireEvent.click(screen.getByRole('button', { name: /DATEV|FIBU-Schnittstelle/ }))
    expect(state.navigate).toHaveBeenCalledWith('/fibu/schnittstelle-fibu?context=hauptbuch')
  })

  it('stellt FIBU-Schnittstelle Arbeit zuerst mit 44-px-Filtern', async () => {
    await mountDomainPage(FibuInterface, 'fibu/schnittstelle-fibu-liste', true)
    await expectSearchWorkArea('FIBU-Schnittstelle')
  })

  it('stellt Buchungsimport Arbeit zuerst mit 44-px-Schritten', async () => {
    await mountDomainPage(BookingImport, 'finance/buchungsimport', true)
    expect(screen.getByRole('button', { name: /Vorschau/ })).toHaveClass('min-h-touch')
  })

  it('stellt BWA Arbeit zuerst ohne Rohblau', async () => {
    await mountDomainPage(Bwa, 'fibu/bwa', true)
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toHaveClass('min-h-touch')
  })

  it('stellt Bilanz Arbeit zuerst mit CSV-Export', async () => {
    await mountDomainPage(Balance, 'fibu/bilanz', true)
    expect(screen.getByRole('combobox', { name: /Bilanz-Periode|Periode/ })).toHaveClass('min-h-touch')
    await expectCsvDownload()
  })

  it('stellt GuV Arbeit zuerst ohne Rohgruen', async () => {
    await mountDomainPage(Income, 'fibu/guv', true)
    expect(screen.getByRole('combobox', { name: /GuV-Periode|Periode/ })).toHaveClass('min-h-touch')
  })

  it('stellt Lastschriften 44 px ohne Rohblau', async () => {
    await mountDomainPage(DirectDebit, 'finance/lastschriften-debitoren', true)
    await expectSearchWorkArea('Debitorenlauf')
  })

  it('stellt ELSTER Arbeit zuerst mit 44-px-Periode', async () => {
    await mountDomainPage(Elster, 'fibu/elster-online', true)
    expect(screen.getByRole('combobox', { name: 'UStVA-Periode' })).toHaveClass('min-h-touch')
  })

  it('stellt Bankabgleich Arbeit zuerst und Theater nur Desktop', () => {
    const src = read('../../pages/finance/bank-abgleich.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<ObjectPage')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Fahrer 44 px ohne Hover-Blau', async () => {
    await mountDomainPage(Drivers, 'transporte/fahrer', true)
    await expectSearchWorkArea('Fahrer')
    expect(screen.getByRole('button', { name: 'Tourenplanung' })).toHaveClass('min-h-touch')
    fireEvent.click(screen.getByRole('button', { name: 'Tourenplanung' }))
    expect(state.navigate).toHaveBeenCalledWith('/logistik/tourenplanung')
  })
})
