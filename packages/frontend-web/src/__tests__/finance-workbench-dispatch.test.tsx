import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BankPage from '@/pages/finance/bank-abgleich'
import DunningPage from '@/pages/finance/mahnlauf'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import fixtures from './fixtures/finance-workbenches.json'

const state = vi.hoisted(() => ({ schema: undefined as unknown, get: vi.fn(), post: vi.fn(), put: vi.fn(), toast: vi.fn() }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: state.schema }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['studio.finance-workbench.import', 'studio.finance-workbench.validate', 'studio.finance-workbench.run', 'studio.finance-workbench.sendEmail', 'studio.finance-workbench.sendPost'] }))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({ useDomainIdentity: () => ({ tenantId: 't1', actor: 'u1' }) }))
vi.mock('@/features/finance/useBankOptions', () => ({ useBankOptions: () => ({ data: [{ id: 'b1', account_number: '1200', bank_name: 'Bank' }] }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: state.get, post: state.post, put: state.put } }))
vi.mock('@/hooks/use-toast', () => ({ toast: state.toast }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ permissions, onAction }: { permissions: string[]; onAction: (key: string, payload: Record<string, unknown>) => void }) =>
    <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(state.schema as ScreenDefinition, { permissions, roleHash: 'flow-test' })} onAction={onAction} />,
}))
const schemas = fixtures as unknown as ScreenDefinition[]
const page = (node: JSX.Element) => <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>{node}</QueryClientProvider>
beforeEach(() => { vi.clearAllMocks() })

describe('Finance-Aktionen über die gemeinsame Studio-Aktionsleiste', () => {
  it('importiert im Bankarbeitsbereich über den verdrahteten Dispatcher', async () => {
    state.schema = schemas[0]
    state.post.mockResolvedValue({ data: { statement_id: 's1', imported_lines: 1, error_lines: 0, import_errors: [], opening_balance: '0', closing_balance: '5', lines: [{ booking_date: '2026-10-30', amount: '5', reference: 'R-1', status: 'UNMATCHED' }] } })
    render(page(<BankPage />))
    await userEvent.selectOptions(screen.getByLabelText('Bankkonto'), 'b1')
    await userEvent.upload(screen.getByLabelText('Kontoauszug'), new File(['csv'], 's.csv', { type: 'text/csv' }))
    await userEvent.click(screen.getByRole('button', { name: 'Kontoauszug importieren' }))
    await waitFor(() => expect(state.post).toHaveBeenCalledWith(expect.stringContaining('format=CSV'), expect.any(FormData), expect.any(Object)))
    expect(await screen.findAllByText('R-1')).not.toHaveLength(0)
  })
  it('führt die ausgewählte Mahnmenge über den verdrahteten Dispatcher aus', async () => {
    state.schema = schemas[1]
    state.get.mockImplementation((url: string) => Promise.resolve({ data: { items: url.endsWith('/candidates') ? [
      { op_id: '1', rechnungsnr: 'R1', partner: 'A', tage_ueberfaellig: 10, offen: 10, aktuelle_stufe: 0, naechste_stufe: 1, dunning_fee: 0, interest: 0, total_amount: 10 },
      { op_id: '2', rechnungsnr: 'R2', partner: 'B', tage_ueberfaellig: 10, offen: 10, aktuelle_stufe: 0, naechste_stufe: 1, dunning_fee: 0, interest: 0, total_amount: 10 },
    ] : [] } }))
    state.post.mockResolvedValue({ data: { ok: true, erzeugt: 1 } })
    render(page(<DunningPage />))
    await userEvent.click(await screen.findByRole('checkbox', { name: 'R2 von B in diesem Lauf mahnen' }))
    await userEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen' }))
    await waitFor(() => expect(state.post).toHaveBeenCalledWith('/api/v1/finance/mahnlauf/run', { rechnungsnrn: ['R1'] }))
  })
})
