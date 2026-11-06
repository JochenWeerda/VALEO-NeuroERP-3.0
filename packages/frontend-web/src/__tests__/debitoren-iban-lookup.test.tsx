import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import Debitoren from '@/pages/finance/debitoren-stamm-legacy'

const mocks = vi.hoisted(() => ({ save: vi.fn(), lookup: vi.fn(), changes: 0 }))
vi.mock('@/lib/utils/iban-validator', () => ({
  validateIBAN: () => true, formatIBAN: (s: string) => s, lookupIBAN: mocks.lookup,
}))
vi.mock('@/hooks/useTenant', () => ({ useTenant: () => ({ tenantId: 't' }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (s: string) => s }) }))
vi.mock('@/components/navigation/ModuleToolbar', () => ({ ModuleToolbar: () => null }))
vi.mock('@/components/LeaveConfirmDialog', () => ({ LeaveConfirmDialog: () => null }))
vi.mock('@/hooks/useUnsavedChanges', () => ({ useUnsavedChanges: () => ({ state: 'unblocked' }) }))
vi.mock('@/components/mask-builder/hooks', () => ({
  useMaskData: () => ({ data: null, loading: false, saveData: mocks.save, updateData: mocks.save }),
  useMaskActions: (handler: unknown) => ({ handleAction: handler }),
}))
vi.mock('@/components/mask-builder', () => ({
  ObjectPage: ({ data, onChange, onSave }: { data: Record<string, unknown>; onChange: (d: object) => void; onSave: (d: object) => void }) => {
    mocks.changes++
    return <><button onClick={() => onChange({ iban: 'DE89370400440532013000', company_name: 'Firma', debtor_number: '123456', street: 'Weg', postal_code: '12345', city: 'Ort' })}>IBAN</button>
      <button onClick={() => onChange({ iban: 'DE02370400440532013001', company_name: 'Neu' })}>Andere IBAN</button><button onClick={() => onChange({ ...data, bic: 'MANUELL', bank_name: 'Manuell' })}>Manuell</button><button onClick={() => onChange({ ...data, iban: 'DE02370400440532013001', bic: 'ALT', bank_name: 'Alt' })}>Wechsel</button><button onClick={() => onSave(data)}>Speichern</button><output data-testid="draft">{JSON.stringify(data)}</output></>
  },
}))

it('enriches the draft once without saving it', async () => {
  mocks.lookup.mockResolvedValue({ valid: true, bank_name: 'Bank', bic: 'BIC123' })
  render(<Debitoren />)
  fireEvent.click(screen.getByRole('button', { name: 'IBAN' }))
  await waitFor(() => expect(screen.getByTestId('draft').textContent).toContain('BIC123'), { timeout: 3000 })
  expect(screen.getByTestId('draft').textContent).toContain('Bank')
  expect(mocks.lookup).toHaveBeenCalledTimes(1)
  expect(mocks.save).not.toHaveBeenCalled()
  expect(mocks.changes).toBeLessThan(10)
  mocks.save.mockResolvedValue({})
  fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
  await waitFor(() => expect(mocks.save).toHaveBeenCalledWith(expect.objectContaining({ bank_name: 'Bank', bic: 'BIC123' })))
})


it('ignores a late result for the previous IBAN', async () => {
  let resolveOld!: (result: { valid: boolean; bank_name: string; bic: string }) => void
  mocks.lookup.mockReset().mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve }))
    .mockResolvedValue({ valid: true, bank_name: 'Neue Bank', bic: 'NEU' })
  render(<Debitoren />)
  fireEvent.click(screen.getByRole('button', { name: 'IBAN' }))
  await waitFor(() => expect(mocks.lookup).toHaveBeenCalledTimes(1), { timeout: 3000 })
  fireEvent.click(screen.getByRole('button', { name: 'Andere IBAN' }))
  await waitFor(() => expect(screen.getByTestId('draft').textContent).toContain('NEU'), { timeout: 3000 })
  resolveOld({ valid: true, bank_name: 'Alte Bank', bic: 'ALT' })
  await new Promise(resolve => setTimeout(resolve, 0))
  expect(screen.getByTestId('draft').textContent).toContain('NEU')
  expect(screen.getByTestId('draft').textContent).not.toContain('Alte Bank')
})


it.each([false, true])('replaces unchanged bank data but preserves edits during lookup: %s', async manual => {
  let finish!: (result: { valid: boolean; bank_name: string; bic: string }) => void
  mocks.lookup.mockReset().mockImplementation(() => new Promise(resolve => { finish = resolve }))
  render(<Debitoren />)
  fireEvent.click(screen.getByRole('button', { name: 'Wechsel' }))
  await waitFor(() => expect(mocks.lookup).toHaveBeenCalledTimes(1), { timeout: 3000 })
  if (manual) fireEvent.click(screen.getByRole('button', { name: 'Manuell' }))
  await act(async () => { finish({ valid: true, bank_name: 'Neue Bank', bic: 'NEU' }) })
  await waitFor(() => expect(screen.getByTestId('draft').textContent).toContain(manual ? 'MANUELL' : 'NEU'))
  expect(screen.getByTestId('draft').textContent).toContain(manual ? 'Manuell' : 'Neue Bank')
})
