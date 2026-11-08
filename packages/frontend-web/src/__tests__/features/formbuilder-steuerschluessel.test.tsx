import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { FormBuilder, type FormSchema } from '@/features/forms/FormBuilder'
import invoiceSchema from '@/domain-schemas/sales_invoice.schema.json'

const mocks = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get } }))
vi.mock('@/components/ui/toast-provider', () => ({ useToast: () => ({ push: vi.fn() }) }))

const VERKAUF = [
  { code: '2', bezeichnung: 'Umsatzsteuer 7 %', steuersatz: '7.00' },
  { code: '3', bezeichnung: 'Umsatzsteuer 19 %', steuersatz: '19.00' },
]

beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockResolvedValue({ data: VERKAUF })
})

// Die Rechnungsmaske der Navigation (sales/invoice-editor) zeichnet ihre Positionen aus diesem Schema.
// Bis zum 13.10.2026 stand dort die Spalte „MwSt %“, in der Maske vorbelegt mit 19.
describe('Rechnungspositionen: Steuerschluessel statt Prozentspalte', () => {
  it('das Schema nennt den Steuerschluessel und keinen Satz', () => {
    const spalten = invoiceSchema.lines.columns.map((c) => c.name)
    expect(spalten).toContain('taxCode')
    expect(spalten).not.toContain('vatRate')
  })

  it('zeichnet eine Auswahl, waehlt nichts vor und meldet den gewaehlten Schluessel', async () => {
    const onChange = vi.fn()
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={client}>
        <FormBuilder
          schema={invoiceSchema as unknown as FormSchema}
          data={{ lines: [{ article: 'A-1', qty: 1, price: 100, taxCode: '' }] }}
          onChange={onChange}
          onSubmit={vi.fn()}
        />
      </QueryClientProvider>,
    )
    const feld = await screen.findByLabelText('Steuerschlüssel Position 1')
    await waitFor(() => expect(within(feld).getByRole('option', { name: '3 – Umsatzsteuer 19 % (19 %)' })).toBeInTheDocument())
    expect(feld).toHaveValue('')
    expect(screen.queryByText('MwSt %')).toBeNull()
    fireEvent.change(feld, { target: { value: '3' } })
    await waitFor(() => expect(onChange).toHaveBeenCalled())
    const letzte = onChange.mock.calls.at(-1)?.[0] as { lines: Array<{ taxCode: string }> }
    expect(letzte.lines[0].taxCode).toBe('3')
  })
})
