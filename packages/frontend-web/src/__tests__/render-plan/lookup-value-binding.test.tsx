import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LookupField } from '@/components/mask-builder/renderers/LookupField'
import { apiClient } from '@/lib/api-client'
import type { RenderFieldPlan } from '@/components/mask-builder/render-plan/types'

const field: RenderFieldPlan = { key: 'customer_id', label: 'Kunde', componentKind: 'lookup',
  dataPath: 'customer_id', order: 0, required: false, readOnly: false, visible: true }

afterEach(() => { cleanup(); vi.restoreAllMocks() })

it.each(['other-record', 'reset', 'other-source'])('discards stale selection on %s', async change => {
  const user = userEvent.setup()
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [{ value: 'A', label: 'Kunde Alpha' }] } as never)
  const view = (value: string, endpoint = '/customers') => <QueryClientProvider client={client}>
    <LookupField field={field} value={value} lookupEndpoint={endpoint}
      performance={{ lookupDebounceMs: 1 }} onSelect={vi.fn()} />
  </QueryClientProvider>
  const rendered = render(view(''))
  await user.type(screen.getByLabelText('Kunde'), 'al')
  await user.click(await screen.findByRole('option', { name: 'Kunde Alpha' }))
  rendered.rerender(view('A'))
  expect(screen.getByLabelText('Kunde')).toHaveValue('Kunde Alpha')
  rendered.rerender(view(change === 'other-record' ? 'B' : change === 'reset' ? '' : 'A',
    change === 'other-source' ? '/other-tenant/customers' : '/customers'))
  expect(screen.getByLabelText('Kunde')).toHaveValue(change === 'other-record' ? 'B' : change === 'reset' ? '' : 'A')
  expect(screen.queryByDisplayValue('Kunde Alpha')).not.toBeInTheDocument()
  client.clear()
})

it('discards unfinished search when the loaded record changes', async () => {
  const user = userEvent.setup()
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const view = (value: string) => <QueryClientProvider client={client}>
    <LookupField field={field} value={value} lookupEndpoint="/customers" />
  </QueryClientProvider>
  const rendered = render(view('A'))
  await user.clear(screen.getByLabelText('Kunde'))
  await user.type(screen.getByLabelText('Kunde'), 'x')
  rendered.rerender(view('B'))
  expect(screen.getByLabelText('Kunde')).toHaveValue('B')
  client.clear()
})
