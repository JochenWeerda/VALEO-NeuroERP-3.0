import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as exportUtils from '@/lib/export-utils'
import { mountList, transport } from '../native-list-contract-harness'
import definitions from '../fixtures/native-final-list-builder-contracts.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import Biostimulanzien from '@/pages/agrar/biostimulanzien-liste'
import Sachkunde from '@/pages/agrar/psm/sachkunde-register'
import Sorten from '@/pages/agrar/saatgut/sortenregister'
import Einzel from '@/pages/futter/einzel/liste'
import Misch from '@/pages/futter/misch/liste'
import Zertifikate from '@/pages/zertifikate/liste'

const cases = [
  { page: <Biostimulanzien />, id: 'agrar/biostimulanzien-liste', title: 'Biostimulanzien', row: { id: 'synthetic', name: 'SYNTHETIC-BIO' }, label: 'SYNTHETIC-BIO', path: '/agrar/biostimulanzien-stamm/synthetic' },
  { page: <Sachkunde />, id: 'agrar/psm-sachkunde-register-liste', title: 'PSM Sachkunde', row: { id: 'synthetic', kunde: 'SYNTHETIC-KUNDE', nachweisNr: 'N-1' }, label: 'SYNTHETIC-KUNDE', path: '/agrar/psm/sachkunde/synthetic/edit' },
  { page: <Sorten />, id: 'agrar/saatgut-sortenregister-liste', title: 'Sortenregister', row: { id: 'synthetic', name: 'SYNTHETIC-SORTE', crop_type: 'Weizen' }, label: 'SYNTHETIC-SORTE', path: '/agrar/saatgut/sorte/synthetic' },
  { page: <Einzel />, id: 'futter/einzel/liste', title: 'Einzelfuttermittel', row: { id: 'synthetic', name: 'SYNTHETIC-EINZEL', verfuegbar_t: 2 }, label: 'SYNTHETIC-EINZEL', path: '/futter/einzel/synthetic' },
  { page: <Misch />, id: 'futtermittel/mischfuttermittel-liste', title: 'Mischfuttermittel', row: { id: 'synthetic', name: 'SYNTHETIC-MISCH', tierart: 'Rind', aktiv: true }, label: 'SYNTHETIC-MISCH', path: '/futtermittel/mischfuttermittel/synthetic' },
]

describe('Studio-Listen mit fachlicher Zeilennavigation', () => {
  it.each(cases)('$title: Daten, Suche und deklarierter Zeilenweg', async ({ page, id, title, row, label, path }) => {
    mountList(page, id, row, (definitions as unknown as Record<string, ScreenDefinition>)[id])
    const table = await screen.findByTestId('virtual-data-table')
    expect(await within(table).findByText(label)).toBeVisible()
    const search = screen.getByRole('searchbox', { name: `Suche in ${title}` })
    expect(search).toHaveClass('min-h-touch')
    fireEvent.change(search, { target: { value: 'SYNTHETIC' } })
    await waitFor(() => expect(transport.get.mock.calls.some(([url]) => String(url).includes('q=SYNTHETIC'))).toBe(true))
    fireEvent.click(within(table).getByText(label).closest('[role="row"]')!)
    const open = await screen.findByRole('button', { name: 'In Vollansicht öffnen' })
    expect(open).toHaveClass('min-h-touch')
    fireEvent.click(open)
    expect(window.location.pathname).toBe(path)
    expect(transport.request).not.toHaveBeenCalled()
  })
})

it('zeigt Zertifikate aus dem Register statt der Neuanlage', async () => {
  const id = 'zertifikate/liste'
  mountList(<Zertifikate />, id, { id: 'synthetic', nummer: 'SYNTHETIC-ZERT', standard: 'QS' }, (definitions as unknown as Record<string, ScreenDefinition>)[id])
  expect(await screen.findByText('SYNTHETIC-ZERT')).toBeVisible()
  expect(screen.getByRole('searchbox', { name: 'Suche in Zertifikate' })).toHaveClass('min-h-touch')
  expect(transport.request).not.toHaveBeenCalled()
})


it.each([
  { page: <Einzel />, id: 'futter/einzel/liste', row: { id: 'e1', name: 'Soja' } },
  { page: <Misch />, id: 'futtermittel/mischfuttermittel-liste', row: { id: 'm1', name: 'Rinderfutter' } },
  { page: <Zertifikate />, id: 'zertifikate/liste', row: { id: 'z1', nummer: 'QS-123' } },
])('$id exportiert die geladenen Fachdatensaetze', async ({ page, id, row }) => {
  const exporter = vi.spyOn(exportUtils, 'exportToCSV').mockImplementation(() => undefined)
  mountList(page, id, row, (definitions as unknown as Record<string, ScreenDefinition>)[id])
  await screen.findByTestId('virtual-data-table')
  fireEvent.click(screen.getByRole('button', { name: 'CSV-Export' }))
  await waitFor(() => expect(exporter).toHaveBeenCalledWith([row], expect.stringMatching(/\.csv$/), expect.any(Array)))
  expect(transport.request).not.toHaveBeenCalled()
})

it('verweigert Mischfutter-Deaktivierung ohne Fachrecht', async () => {
  const id = 'futtermittel/mischfuttermittel-liste'
  mountList(<Misch />, id, { id: 'm1', name: 'Rinderfutter', aktiv: true }, (definitions as unknown as Record<string, ScreenDefinition>)[id])
  expect(await screen.findByText('Rinderfutter')).toBeVisible()
  expect(screen.queryByRole('button', { name: 'Deaktivieren' })).not.toBeInTheDocument()
  expect(transport.request).not.toHaveBeenCalled()
})
