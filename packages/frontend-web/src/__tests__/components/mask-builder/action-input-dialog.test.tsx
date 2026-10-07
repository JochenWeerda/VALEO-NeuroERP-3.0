import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'

const mocks = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get } }))

// Die Eingaben einer Aktion stehen in der Screen Definition; der Mask-Builder
// zeichnet sie. Keine handgebaute Eingabemaske je Aktion.
const WARENEINGANG: ScreenActionDefinition = {
  key: 'wareneingang',
  label: 'Wareneingang buchen',
  commandEndpoint: '/api/v1/einkauf/anlieferavis/{entity_id}/actions/wareneingang',
  inputFields: [
    { key: 'lieferschein_nr', label: 'Lieferschein-Nr.', type: 'text', required: true },
    {
      key: 'lager_id',
      label: 'Lager',
      type: 'select',
      required: true,
      optionsSource: { endpoint: '/api/v1/inventory/warehouses', valueKey: 'id', labelKey: 'name' },
    },
    { key: 'bemerkung', label: 'Bemerkung', type: 'textarea' },
  ],
}

function mitAbfragen(kind: ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{kind}</QueryClientProvider>
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockResolvedValue({ data: { items: [{ id: 'l-1', name: 'Silo Nord' }, { id: 'l-2', name: 'Halle 2' }] } })
})

describe('ActionInputDialog', () => {
  it('zeichnet die Felder der Aktion aus der Screen Definition', async () => {
    render(mitAbfragen(<ActionInputDialog action={WARENEINGANG} open onCancel={vi.fn()} onSubmit={vi.fn()} />))
    expect(screen.getByRole('dialog', { name: 'Wareneingang buchen' })).toBeInTheDocument()
    expect(screen.getByLabelText(/Lieferschein-Nr\./)).toBeInTheDocument()
    expect(screen.getByLabelText(/Bemerkung/)).toBeInTheDocument()
    // Optionen aus der deklarierten Quelle, nicht fest verdrahtet.
    await waitFor(() => expect(screen.getByRole('option', { name: 'Silo Nord' })).toBeInTheDocument())
    expect(mocks.get).toHaveBeenCalledWith('/api/v1/inventory/warehouses')
  })

  it('haelt bei fehlenden Pflichtfeldern an und zeigt, was fehlt', async () => {
    const onSubmit = vi.fn()
    render(mitAbfragen(<ActionInputDialog action={WARENEINGANG} open onCancel={vi.fn()} onSubmit={onSubmit} />))
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    expect(onSubmit).not.toHaveBeenCalled()
    expect(await screen.findAllByText(/ist ein Pflichtfeld/)).not.toHaveLength(0)
  })

  it('gibt die Eingaben weiter', async () => {
    const onSubmit = vi.fn()
    render(mitAbfragen(<ActionInputDialog action={WARENEINGANG} open onCancel={vi.fn()} onSubmit={onSubmit} />))
    await screen.findByRole('option', { name: 'Halle 2' })
    fireEvent.change(screen.getByLabelText(/Lieferschein-Nr\./), { target: { value: 'LS-4711' } })
    fireEvent.change(screen.getByRole('combobox', { name: 'Lager' }), { target: { value: 'l-2' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    expect(onSubmit).toHaveBeenCalledWith({ lieferschein_nr: 'LS-4711', lager_id: 'l-2' })
  })

  it('Abbrechen gibt nichts weiter', () => {
    const onSubmit = vi.fn()
    const onCancel = vi.fn()
    render(mitAbfragen(<ActionInputDialog action={WARENEINGANG} open onCancel={onCancel} onSubmit={onSubmit} />))
    fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
    expect(onCancel).toHaveBeenCalled()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('meldet, wenn die Optionsquelle nicht laedt', async () => {
    mocks.get.mockRejectedValue(new Error('503'))
    render(mitAbfragen(<ActionInputDialog action={WARENEINGANG} open onCancel={vi.fn()} onSubmit={vi.fn()} />))
    expect(await screen.findByText(/Lager: Auswahl nicht geladen/)).toBeInTheDocument()
  })
})
