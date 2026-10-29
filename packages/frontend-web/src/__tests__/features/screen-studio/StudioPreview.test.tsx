import { act, fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { StudioPreview } from '@/features/screen-studio/StudioPreview'
import type { HarvestPreviewResult } from '@/lib/api/studio'

const calculate = vi.hoisted(() => vi.fn())
vi.mock('@/lib/api/studio', () => ({ calculateStudioHarvest: calculate }))
vi.stubGlobal('ResizeObserver', class { observe() {} unobserve() {} disconnect() {} })

afterEach(() => vi.useRealTimers())

describe('interactive Domain-Service preview', () => {
  it('preserves compatible inputs and removes values of deselected optional fields', async () => {
    vi.useFakeTimers()
    calculate.mockReset().mockResolvedValue({ positions: [], total_net_amount_eur: '1', total_vat_amount_eur: '0', total_gross_amount_eur: '1', warnings: [] })
    const definition = {
      schemaVersion: 1, id: 'tenant/preview-fields', title: 'Feldprobe', domain: 'agrar', mode: 'detail',
      layout: { floorplan: 'objectPage', density: 'compact', contextRail: 'audit' },
      fields: [{ key: 'delivered_quantity_kg', label: 'Nettomenge', type: 'number', required: true },
        { key: 'hl_weight_kg_per_hl', label: 'Hektolitergewicht', type: 'number' }],
      studioSemantic: { contract: 'agrar.harvest.manual-preview.v1' },
    } as ScreenDefinition
    const client = new QueryClient()
    const page = (current: ScreenDefinition) => <MemoryRouter><QueryClientProvider client={client}><StudioPreview definition={current} /></QueryClientProvider></MemoryRouter>
    const view = render(page(definition))
    fireEvent.click(screen.getByRole('button', { name: 'Synthetische Beispieldaten laden' }))
    expect(screen.getByRole('spinbutton', { name: 'Nettomenge' })).toHaveValue(25000)
    view.rerender(page({ ...definition, fields: definition.fields?.slice(0, 1) }))
    expect(screen.getByRole('spinbutton', { name: 'Nettomenge' })).toHaveValue(25000)
    expect(screen.queryByRole('spinbutton', { name: 'Hektolitergewicht' })).not.toBeInTheDocument()
    await act(async () => { await vi.advanceTimersByTimeAsync(500) })
    expect(calculate.mock.calls.at(-1)?.[0]).toEqual({ delivered_quantity_kg: 25000 })
  })

  it('uses the central form and discards a late result after the input changes', async () => {
    vi.useFakeTimers()
    calculate.mockReset()
    let finish: (_result: HarvestPreviewResult) => void = () => undefined
    calculate.mockImplementationOnce(() => new Promise<HarvestPreviewResult>(resolve => { finish = resolve }))
    calculate.mockRejectedValueOnce(new Error('Menge unzulaessig'))
    const definition = {
      schemaVersion: 1, id: 'tenant/preview-race', title: 'Kalkulationsprobe', domain: 'agrar', mode: 'detail',
      layout: { floorplan: 'objectPage', density: 'compact', contextRail: 'audit' },
      fields: [{ key: 'delivered_quantity_kg', label: 'Nettomenge', type: 'number', required: true }],
      studioSemantic: { contract: 'agrar.harvest.manual-preview.v1' },
    } as ScreenDefinition
    render(<MemoryRouter><QueryClientProvider client={new QueryClient()}><StudioPreview definition={definition} /></QueryClientProvider></MemoryRouter>)
    fireEvent.click(screen.getByRole('button', { name: 'Synthetische Beispieldaten laden' }))
    await act(async () => { await vi.advanceTimersByTimeAsync(500) })
    expect(calculate.mock.calls[0][0].delivered_quantity_kg).toBe(25000)
    fireEvent.change(screen.getByRole('spinbutton', { name: 'Nettomenge' }), { target: { value: '-1' } })
    await act(async () => finish({ contract: 'agrar.harvest.manual-preview.v1', business_effect: 'none', external_effect: 'none', positions: [], total_net_amount_eur: '999', total_vat_amount_eur: '0', total_gross_amount_eur: '999', warnings: [] }))
    expect(screen.queryByTestId('studio-calculation-result')).not.toBeInTheDocument()
    await act(async () => { await vi.advanceTimersByTimeAsync(500) })
    expect(screen.getByRole('alert')).toHaveTextContent('Menge unzulaessig')
    expect(screen.queryByText('999')).not.toBeInTheDocument()
  })
})
