import { act, render } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import BankKontenStammPage from '@/pages/finance/bankkonten-stamm'

const mocks = vi.hoisted(() => ({
  saveData: vi.fn(), setData: vi.fn(),
  onLookup: undefined as undefined | ((result: { valid: boolean; bank_name: string; bic: string }) => void),
}))
vi.mock('@/components/navigation/ModuleToolbar', () => ({ ModuleToolbar: () => null }))
vi.mock('@/hooks/useUnsavedChanges', () => ({ useUnsavedChanges: () => ({ state: 'unblocked' }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }))
vi.mock('sonner', () => ({ toast: { success: vi.fn(), error: vi.fn() } }))
vi.mock('@/features/crud/utils/i18n-helpers', () => ({ getEntityTypeLabel: () => 'Bankkonto' }))
vi.mock('@/features/finance/useBankOptions', () => ({ useBankLedgerOptions: () => ({ data: [] }) }))
vi.mock('@/components/mask-builder', () => ({ ObjectPage: () => <div>Bankkonto</div> }))
vi.mock('@/components/mask-builder/hooks', () => ({
  useMaskData: () => ({ data: null, loading: false, saveData: mocks.saveData,
    updateData: mocks.saveData, setData: mocks.setData }),
  useMaskActions: (handler: unknown) => ({ handleAction: handler }),
}))
vi.mock('@/hooks/useIbanLookup', () => ({
  useIbanLookup: ({ onSuccess }: { onSuccess: typeof mocks.onLookup }) => {
    mocks.onLookup = onSuccess
    return { performLookup: vi.fn(), isLoading: false, lookupData: null }
  },
}))

it('bank lookup fills a draft locally and never implicitly saves an account', () => {
  render(<BankKontenStammPage />)
  act(() => mocks.onLookup?.({ valid: true, bank_name: 'Bank', bic: 'COBADEFFXXX' }))
  expect(mocks.setData).toHaveBeenCalledWith(expect.objectContaining({ bank_name: 'Bank', bic: 'COBADEFFXXX' }))
  expect(mocks.saveData).not.toHaveBeenCalled()
})
