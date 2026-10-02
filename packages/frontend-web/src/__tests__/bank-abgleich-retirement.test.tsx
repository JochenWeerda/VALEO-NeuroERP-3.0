import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { MaskConfig } from '@/components/mask-builder/types'
import BankAbgleichPage from '@/pages/finance/bank-abgleich'

const mocks = vi.hoisted(() => ({ post: vi.fn(), setData: vi.fn(), toast: vi.fn(), navigate: vi.fn() }))
const data = {
  statementId: 'statement-1', kontoId: 'bank-1',
  zuordnungData: [{ datum: '2026-09-28', betrag: 25, opReferenz: 'REF-1', zugeordnet: false }],
}
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post } }))
vi.mock('@/hooks/use-toast', () => ({ toast: mocks.toast }))
vi.mock('@/features/finance/useBankOptions', () => ({ useBankOptions: () => ({ data: [{ id: 'bank-1', account_number: '1200', bank_name: 'Bank' }] }) }))
vi.mock('@/hooks/useTenant', () => ({ useTenant: () => ({ tenantId: 'tenant-1' }) }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => true }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => mocks.navigate }))
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }))
vi.mock('@/features/crud/utils/i18n-helpers', () => ({ getEntityTypeLabel: () => 'Bankabgleich' }))
vi.mock('@/components/mask-builder/hooks', () => ({
  useMaskData: () => ({ data, loading: false, setData: mocks.setData }),
  useMaskActions: (handler: unknown) => ({ handleAction: handler, loadingActionKey: null }),
}))
vi.mock('@/components/mask-builder', () => ({
  ObjectPage: ({ config, onSave, onAction }: {
    config: MaskConfig
    onSave: (form: typeof data) => Promise<void>
    onAction: (key: string, form: typeof data) => Promise<void>
  }) => <div>
    {config.actions.map(action => <button key={action.key} onClick={() => onAction(action.key, data)}>
      {action.key}
    </button>)}
    <button onClick={() => onSave(data)}>save</button>
    {config.tabs.map(tab => tab.customRender?.(data, () => undefined))}
  </div>,
}))

describe('Bankabgleich safety retirement', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.post.mockResolvedValue({ data: {
      balance_comparison: { difference: "25.00", is_balanced: false, currency: "EUR" },
      comparison_state: "DIFFERENCES",
      line_counts: { matched: 0, unmatched: 1, partial: 0, unknown: 0 }, total_differences: 1, differences: [],
    } })
  })

  it('offers comparison without direct booking or local pattern matching', () => {
    render(<BankAbgleichPage />)
    expect(screen.getByRole('button', { name: 'validate' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'book' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'auto-assign' })).not.toBeInTheDocument()
    expect(screen.getByRole('checkbox')).toBeDisabled()
  })

  it('save performs only a comparison and cannot announce a booking', async () => {
    render(<BankAbgleichPage />)
    await userEvent.click(screen.getByRole('button', { name: 'save' }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledOnce())
    const url = mocks.post.mock.calls[0][0] as string
    expect(url).toContain('/statement-1/reconcile?')
    expect(url).toContain('auto_book=false')
    expect(mocks.navigate).not.toHaveBeenCalled()
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' }))
  })

  it('missing balance evidence remains null and never becomes successful', async () => {
    mocks.post.mockResolvedValue({ data: {
      comparison_state: 'INCOMPLETE',
      balance_comparison: { difference: null, is_balanced: false, currency: 'EUR' },
      line_counts: { matched: 0, unmatched: 0, partial: 1, unknown: 1 },
      total_differences: 2, differences: [],
    } })
    render(<BankAbgleichPage />)
    await userEvent.click(screen.getByRole('button', { name: 'save' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalled())
    expect(mocks.setData).toHaveBeenCalledWith(expect.objectContaining({
      comparisonState: 'INCOMPLETE', abgleichsDifferenz: null, nichtZugeordnet: 2,
    }))
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' }))
  })

  it('a failed comparison clears previous proof', async () => {
    mocks.post.mockRejectedValue(new Error('Offline'))
    render(<BankAbgleichPage />)
    await userEvent.click(screen.getByRole('button', { name: 'save' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalled())
    expect(mocks.setData).toHaveBeenCalledWith(expect.objectContaining({
      comparisonState: 'INCOMPLETE', abgleichsDifferenz: null,
    }))
    expect(mocks.navigate).not.toHaveBeenCalled()
  })
})
