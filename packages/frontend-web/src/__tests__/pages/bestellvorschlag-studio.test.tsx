import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { beforeAll, describe, expect, it, vi } from 'vitest'
import { initI18n } from '@/i18n/config'
import { mountList, transport } from '../native-list-contract-harness'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import Lager from '@/pages/einkauf/bestellvorschlag-lager'
import Rohware from '@/pages/einkauf/bestellvorschlag-rohware'
import Verkauf from '@/pages/einkauf/bestellvorschlag-verkauf'
import fixtures from '../fixtures/bestellvorschlag-family.json'

const toast = vi.hoisted(() => vi.fn())
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }), toast }))
const cases = [
  { name: 'lager', page: <Lager />, link: 'Bestellvorschlag Verkauf', route: '/einkauf/bestellvorschlaege/ansicht/verkauf' },
  { name: 'rohware', page: <Rohware />, link: 'Bestellvorschlag Lager', route: '/einkauf/bestellvorschlaege/ansicht/lager' },
  { name: 'verkauf', page: <Verkauf />, link: 'Bestellvorschlag Rohware', route: '/einkauf/bestellvorschlaege/ansicht/rohware' },
] as const
const row = { artikel_nr: 'TEST-4711', artikel_bezeichnung: 'Testweizen', ist_bestand: 4, vorschlag_menge: 8, einheit: 'kg' }
function mount(c: typeof cases[number], permitted = true) {
  transport.roles = permitted ? ['EINKAUF_BEARBEITEN'] : []
  mountList(c.page, `bestellvorschlag/${c.name}`, row, fixtures[c.name] as unknown as ScreenDefinition)
}
async function openSave() {
  fireEvent.click(await screen.findByRole('button', { name: 'Als Vorschlag speichern' }, { timeout: 10000 }))
  expect(screen.getByRole('dialog')).toHaveAccessibleDescription('Angaben für diese Aktion. Pflichtfelder sind markiert.')
  fireEvent.change(screen.getByLabelText('Bezeichnung'), { target: { value: 'Testvorschlag' } })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  const confirmation = await screen.findByRole('dialog')
  expect(confirmation).toHaveAccessibleDescription('Aktion fuer den gewaehlten Eintrag ausfuehren?')
  return within(confirmation).getByRole('button', { name: 'Als Vorschlag speichern' })
}

beforeAll(async () => { await initI18n() })

describe('Bestellvorschlag Studio-Familie', () => {
  it.each(cases)('$name: Daten und Variantenwechsel', async c => {
    mount(c)
    expect(await screen.findByText('Testweizen', {}, { timeout: 10000 })).toBeVisible()
    expect(transport.get.mock.calls.some(([url]) => String(url).includes(`/masks/bestellvorschlag%2F${c.name}/data/list?`))).toBe(true)
    expect(fixtures[c.name].dataSources[0].endpoint).toBe(`/api/v1/einkauf/bestellvorschlaege/${c.name}`)
    fireEvent.click(screen.getByRole('button', { name: c.link }))
    expect(transport.navigate).toHaveBeenCalledWith(c.route)
    expect(transport.request).not.toHaveBeenCalled()
  })
  it.each(cases)('$name: Speichern sendet den richtigen Command', async c => {
    transport.request.mockResolvedValueOnce({ data: { success: true } })
    mount(c)
    fireEvent.click(await openSave())
    await waitFor(() => expect(transport.request).toHaveBeenCalledWith(expect.objectContaining({ method: 'POST', url: `/api/v1/einkauf/bestellvorschlaege/berechnung/${c.name}/actions/speichern`, data: expect.objectContaining({ bezeichnung: 'Testvorschlag' }) })))
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Als Vorschlag speichern' })))
  })
  it.each(cases)('$name: ohne Recht kein Speichern', async c => {
    mount(c, false)
    await screen.findByText('Testweizen', {}, { timeout: 10000 })
    expect(screen.queryByRole('button', { name: 'Als Vorschlag speichern' })).not.toBeInTheDocument()
    expect(transport.request).not.toHaveBeenCalled()
  })
  it.each([403, 409])('HTTP %s zeigt Fehler und keinen Erfolg', async status => {
    transport.request.mockRejectedValueOnce(Object.assign(new Error(`HTTP ${status}`), { response: { status } }))
    mount(cases[0])
    fireEvent.click(await openSave())
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Als Vorschlag speichern fehlgeschlagen', variant: 'destructive' })))
    expect(toast).not.toHaveBeenCalledWith(expect.objectContaining({ title: 'Als Vorschlag speichern' }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })
  it('verhindert Doppelaufruf waehrend Speichern laeuft', async () => {
    let finish!: (value: unknown) => void
    transport.request.mockReturnValueOnce(new Promise(resolve => { finish = resolve }))
    mount(cases[0])
    const button = await openSave()
    fireEvent.click(button)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Wird ausgefuehrt…' })).toBeDisabled())
    fireEvent.click(screen.getByRole('button', { name: 'Wird ausgefuehrt…' }))
    expect(transport.request).toHaveBeenCalledTimes(1)
    finish({ data: { success: true } })
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })
})
