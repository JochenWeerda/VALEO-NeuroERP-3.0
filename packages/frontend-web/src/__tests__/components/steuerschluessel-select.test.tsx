import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { SteuerschluesselSelect } from '@/components/finance/SteuerschluesselSelect'
import { satzVon, schluesselText } from '@/lib/api/steuerschluessel-auswahl'

const mocks = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get } }))

const VERKAUF = [
  { code: '2', bezeichnung: 'Umsatzsteuer 7 %', steuersatz: '7.00' },
  { code: '3', bezeichnung: 'Umsatzsteuer 19 %', steuersatz: '19.00' },
]

function zeichnen(value: string | null, onChange = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <SteuerschluesselSelect richtung="verkauf" value={value} onChange={onChange} />
    </QueryClientProvider>,
  )
  return onChange
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockResolvedValue({ data: VERKAUF })
})

// Das Feld, das in Belegen und Stammdaten an die Stelle des Prozentsatzes tritt.
describe('SteuerschluesselSelect', () => {
  it('fragt die Auswahl der Richtung ab und waehlt nichts vor', async () => {
    zeichnen(null)
    const feld = await screen.findByLabelText('Steuerschlüssel')
    await waitFor(() => expect(within(feld).getByRole('option', { name: '3 – Umsatzsteuer 19 % (19 %)' })).toBeInTheDocument())
    expect(mocks.get).toHaveBeenCalledWith('/api/v1/finance/tax-keys/auswahl', { params: { richtung: 'verkauf' } })
    expect(feld).toHaveValue('')
  })

  it('meldet den Schluessel mit seinem Satz und eine leere Auswahl als leer', async () => {
    const onChange = zeichnen(null)
    const feld = await screen.findByLabelText('Steuerschlüssel')
    await waitFor(() => expect(within(feld).getAllByRole('option').length).toBeGreaterThan(2))
    fireEvent.change(feld, { target: { value: '2' } })
    expect(onChange).toHaveBeenLastCalledWith('2', VERKAUF[0])
    fireEvent.change(feld, { target: { value: '' } })
    expect(onChange).toHaveBeenLastCalledWith(null, null)
  })

  it('zeigt einen hinterlegten Schluessel, der nicht mehr gilt', async () => {
    zeichnen('6')
    const feld = await screen.findByLabelText('Steuerschlüssel')
    await waitFor(() => expect(within(feld).getByRole('option', { name: '6 – nicht (mehr) gültig' })).toBeInTheDocument())
    expect(feld).toHaveValue('6')
  })

  it('sagt, wenn die Auswahl nicht geladen werden konnte', async () => {
    mocks.get.mockRejectedValue(new Error('weg'))
    zeichnen(null)
    expect(await screen.findByRole('alert')).toHaveTextContent('Steuerschlüssel konnten nicht geladen werden.')
  })

  it('leitet den Satz nur aus einem gueltigen Schluessel ab', () => {
    expect(satzVon(VERKAUF, '3')).toBe(19)
    expect(satzVon(VERKAUF, '9')).toBeNull()
    expect(satzVon(VERKAUF, null)).toBeNull()
    expect(schluesselText(VERKAUF, '')).toBe('kein Steuerschlüssel')
  })
})
