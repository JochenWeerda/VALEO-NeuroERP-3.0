import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import Zahlungslauf from '@/pages/finance/zahlungslauf-kreditoren-legacy'

const mocks = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn(), get: vi.fn(), lookup: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post, put: mocks.put, get: mocks.get }, getAxiosErrorMessage: () => 'Fehler' }))
vi.mock('@/lib/utils/iban-validator', () => ({ validateIBAN: () => true, formatIBAN: (s: string) => s, lookupIBAN: mocks.lookup }))
vi.mock('@/components/mask-builder/validation', () => ({ getFieldsFromMaskConfig: () => [], validateFields: () => ({}) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (s: string) => s }) }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => true }))
vi.mock('@/hooks/useUnsavedChanges', () => ({ useUnsavedChanges: () => ({ state: 'unblocked' }) }))
vi.mock('@/features/workflow/useApprovalDensityProfile', () => ({ useApprovalDensityProfile: () => undefined }))
vi.mock('@/components/navigation/ModuleToolbar', () => ({ ModuleToolbar: () => null }))
vi.mock('@/components/LeaveConfirmDialog', () => ({ LeaveConfirmDialog: () => null }))
vi.mock('@/components/mask-builder', () => ({
  ObjectPage: ({ data, onChange, onSave }: { data: Record<string, unknown>; onChange: (d: object) => void; onSave: (d: object) => void }) => <>
    <button onClick={() => onChange({ auftraggeberIban: 'DE89370400440532013000', notizen: 'Entwurf' })}>IBAN</button>
    <button onClick={() => onChange({ ...data, auftraggeberBic: 'MANUELL' })}>Manuell</button><button onClick={() => onChange({ ...data, auftraggeberIban: 'DE02370400440532013001', auftraggeberBic: 'ALT' })}>Wechsel</button><button onClick={() => onSave(data)}>Speichern</button><output data-testid="draft">{JSON.stringify(data)}</output></>,
}))

it('enriches locally and creates only on explicit save', async () => {
  mocks.lookup.mockResolvedValue({ valid: true, bic: 'BIC123' })
  mocks.post.mockResolvedValue({ data: {} })
  render(<Zahlungslauf />)
  fireEvent.click(screen.getByRole('button', { name: 'IBAN' }))
  await waitFor(() => expect(screen.getByTestId('draft').textContent).toContain('BIC123'), { timeout: 3000 })
  expect(mocks.lookup).toHaveBeenCalledTimes(1)
  expect(mocks.post).not.toHaveBeenCalled()
  expect(mocks.put).not.toHaveBeenCalled()
  expect(mocks.get).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
  await waitFor(() => expect(mocks.post).toHaveBeenCalledWith('/api/v1/finance/payment-runs', expect.objectContaining({ auftraggeberBic: 'BIC123' })))
  expect(mocks.put).not.toHaveBeenCalled()
})


it.each([false, true])('replaces unchanged BIC and preserves manual edits during lookup: %s', async manual => {
  let finish!: (result: { valid: boolean; bic: string }) => void
  mocks.lookup.mockReset().mockImplementation(() => new Promise(resolve => { finish = resolve }))
  render(<Zahlungslauf />)
  fireEvent.click(screen.getByRole('button', { name: 'Wechsel' }))
  await waitFor(() => expect(mocks.lookup).toHaveBeenCalledTimes(1), { timeout: 3000 })
  if (manual) fireEvent.click(screen.getByRole('button', { name: 'Manuell' }))
  await act(async () => { finish({ valid: true, bic: 'NEU' }) })
  await waitFor(() => expect(screen.getByTestId('draft').textContent).toContain(manual ? 'MANUELL' : 'NEU'))
})
