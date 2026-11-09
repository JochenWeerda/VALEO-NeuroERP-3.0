import { fireEvent, screen, waitFor } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import AngeboteListePage from '@/pages/sales/angebote-liste'
import LieferungenListePage from '@/pages/sales/lieferungen-liste'
import RechnungenWorklistPage from '@/pages/verkauf/rechnungen-worklist'
import definitions from '../../fixtures/beleg-liste-contracts.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

// Belegliste je Belegart (Familie beleg-liste, DocFlow einziger Belegspeicher seit 08.11.2026).
// Fixture = unveraenderte, versionierte Ausgabe des Python-Registers (get_screen_definition).
const defs = definitions as unknown as Record<string, ScreenDefinition>

it('Angebote: liest DocFlow, sucht, filtert nach Belegstatus und legt ueber die Belegmaske an', async () => {
  mountList(<AngeboteListePage />, 'beleg-liste/sales-offer',
    { id: 'A-1', beleg_id: 'A-1', belegart: 'sales_offer', bezeichnung: 'Angebot', beleg_nr: 'ANG-1001',
      partner_name: 'Hof Beispiel', partner_nummer: 'K-7', status: 'draft', belegdatum: '2026-11-08',
      netto: 1000, steuer: 190, brutto: 1190, waehrung: 'EUR', version: 1 },
    defs['beleg-liste/sales-offer'])
  expect(await screen.findByRole('gridcell', { name: 'ANG-1001' })).toBeInTheDocument()
  expect(screen.getByRole('combobox', { name: 'Arbeitsfokus' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Drucken' })).toBeInTheDocument()
  fireEvent.change(screen.getByRole('combobox', { name: 'Belegstatus' }), { target: { value: 'posted' } })
  await waitFor(() => expect(screen.queryByRole('gridcell', { name: 'ANG-1001' })).not.toBeInTheDocument())
  fireEvent.change(screen.getByRole('combobox', { name: 'Belegstatus' }), { target: { value: 'all' } })
  expect(await screen.findByRole('gridcell', { name: 'ANG-1001' })).toBeInTheDocument()
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'kein Treffer' } })
  await waitFor(() => expect(screen.queryByRole('gridcell', { name: 'ANG-1001' })).not.toBeInTheDocument())
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'Hof Beispiel' } })
  expect(await screen.findByRole('gridcell', { name: 'ANG-1001' })).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Angebot anlegen' }))
  expect(transport.navigate).toHaveBeenCalledWith('/belege/sales_offer/neu')
})

it('Lieferscheine: Mengenbeleg ohne Betragsspalten, Anlage ueber die Belegmaske', async () => {
  mountList(<LieferungenListePage />, 'beleg-liste/sales-delivery',
    { id: 'L-1', beleg_id: 'L-1', belegart: 'sales_delivery', bezeichnung: 'Lieferschein', beleg_nr: 'LS-1001',
      partner_name: 'Hof Beispiel', status: 'released', belegdatum: '2026-11-08', version: 1,
      netto: null, steuer: null, brutto: null, waehrung: null },
    defs['beleg-liste/sales-delivery'])
  expect(await screen.findByRole('gridcell', { name: 'LS-1001' })).toBeInTheDocument()
  expect(screen.queryByRole('columnheader', { name: /Brutto/ })).not.toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Lieferschein anlegen' }))
  expect(transport.navigate).toHaveBeenCalledWith('/belege/sales_delivery/neu')
})

it('Ausgangsrechnungen: die Faktura-Seite ist dieselbe Familie, Zeile oeffnet die Belegmaske', async () => {
  mountList(<RechnungenWorklistPage />, 'beleg-liste/sales-invoice',
    { id: 'R-1', beleg_id: 'R-1', belegart: 'sales_invoice', bezeichnung: 'Rechnung', beleg_nr: 'RE-1001',
      partner_name: 'Hof Beispiel', status: 'posted', belegdatum: '2026-11-08', buchungsdatum: '2026-11-08',
      netto: 100, steuer: 19, brutto: 119, waehrung: 'EUR', version: 2 },
    defs['beleg-liste/sales-invoice'])
  expect(await screen.findByRole('gridcell', { name: 'RE-1001' })).toBeInTheDocument()
  expect(defs['beleg-liste/sales-invoice'].tables?.[0]?.rowRouteTemplate).toBe('/belege/sales_invoice/{id}')
})
