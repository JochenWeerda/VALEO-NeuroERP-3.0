import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import BankSurface from '@/components/mask-builder/specialized/finance/bank-surface'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'

const mocks = vi.hoisted(() => ({ post: vi.fn(), toast: vi.fn(), handlers: {} as Record<string, () => void>, allowed: true }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post } }))
vi.mock('@/hooks/use-toast', () => ({ toast: mocks.toast }))
vi.mock('@/features/finance/useBankOptions', () => ({ useBankOptions: () => ({ data: [
  { id: 'bank-1', account_number: '1200', bank_name: 'Bank' }, { id: 'bank-2', account_number: '1300', bank_name: 'Andere Bank' },
] }) }))
vi.mock('@/components/mask-builder/specialized/intake/domain-runtime', () => ({
  canDomainAction: () => mocks.allowed, fieldsEditable: () => true,
  useDomainDispatch: (_plan: unknown, handlers: Record<string, () => void>) => { mocks.handlers = handlers },
}))
function Harness() {
  return <><button onClick={() => mocks.handlers.import?.()}>Import</button><button onClick={() => mocks.handlers.validate?.()}>Vergleich</button><button onClick={() => mocks.handlers.export?.()}>Export</button><BankSurface plan={{} as RenderPlan} /></>
}
const result = { statement_id: 'statement-1', imported_lines: 1, error_lines: 1, import_errors: ['Zeile 2 ungültig'], opening_balance: '10', closing_balance: '35', lines: [{ booking_date: '2026-09-28', amount: '25', reference: 'REF-1', status: 'UNMATCHED' }] }
async function importStatement() {
  await userEvent.selectOptions(screen.getByLabelText('Bankkonto'), 'bank-1')
  await userEvent.upload(screen.getByLabelText('Kontoauszug'), new File(['csv'], 'auszug.csv', { type: 'text/csv' }))
  await userEvent.click(screen.getByRole('button', { name: 'Import' }))
  await screen.findAllByText('REF-1')
}
beforeEach(() => { vi.clearAllMocks(); mocks.allowed = true; mocks.post.mockResolvedValue({ data: result }) })
describe('Bankabgleich Studio-Arbeitsbereich', () => {
  it('importiert CSV mit Zeilen und Warnungen', async () => {
    render(<Harness />); await importStatement()
    expect(mocks.post.mock.calls[0][0]).toContain('format=CSV')
    expect(screen.getByText('Zeile 2 ungültig')).toBeInTheDocument()
  })
  it.each([['auszug.xml', 'CAMT', 'text/xml'], ['auszug.940', 'MT940', 'text/plain']])('erkennt %s als %s', async (name, format, type) => {
    render(<Harness />)
    await userEvent.selectOptions(screen.getByLabelText('Bankkonto'), 'bank-1')
    await userEvent.upload(screen.getByLabelText('Kontoauszug'), new File(['data'], name, { type }))
    await userEvent.click(screen.getByRole('button', { name: 'Import' }))
    await waitFor(() => expect(mocks.post.mock.calls[0][0]).toContain(`format=${format}`))
  })
  it('exportiert die importierten Zeilen als CSV', async () => {
    const create = vi.fn().mockReturnValue('blob:test')
    const revoke = vi.fn()
    Object.assign(URL, { createObjectURL: create, revokeObjectURL: revoke })
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    render(<Harness />); await importStatement()
    await userEvent.click(screen.getByRole('button', { name: 'Export' }))
    expect(create).toHaveBeenCalledWith(expect.any(Blob)); expect(click).toHaveBeenCalledOnce(); expect(revoke).toHaveBeenCalledWith('blob:test')
    click.mockRestore()
  })
  it('führt nur einen nicht buchenden Vergleich aus und zeigt Differenzen', async () => {
    render(<Harness />); await importStatement()
    mocks.post.mockResolvedValue({ data: { comparison_state: 'DIFFERENCES', balance_comparison: { difference: '25', currency: 'EUR' }, line_counts: { matched: 0, unmatched: 1, partial: 0, unknown: 0 }, differences: [{ reason: 'unmatched' }] } })
    await userEvent.click(screen.getByRole('button', { name: 'Vergleich' }))
    await waitFor(() => expect(mocks.post.mock.calls[1][0]).toContain('auto_book=false'))
    expect(await screen.findByText('Salden weichen ab')).toBeInTheDocument()
    expect(screen.getByText(/unmatched/)).toBeInTheDocument()
  })
  it('unterscheidet fehlenden Nachweis und ausgeglichene Salden', async () => {
    render(<Harness />); await importStatement()
    mocks.post.mockResolvedValue({ data: { comparison_state: 'INCOMPLETE', balance_comparison: { difference: null, currency: 'EUR', bank_balance_state: 'CSV_SYNTHETIC' }, line_counts: { matched: 0, unmatched: 0, partial: 1, unknown: 1 }, differences: [] } })
    await userEvent.click(screen.getByRole('button', { name: 'Vergleich' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Saldennachweis unvollständig' })))
    expect(screen.getByText(/Nicht zugeordnet: 2/)).toBeInTheDocument()
    mocks.post.mockResolvedValue({ data: { comparison_state: 'BALANCES_EQUAL', balance_comparison: { difference: '0', currency: 'EUR' }, line_counts: { matched: 1, unmatched: 0, partial: 0, unknown: 0 }, differences: [] } })
    await userEvent.click(screen.getByRole('button', { name: 'Vergleich' }))
    expect(await screen.findByText('Salden stimmen überein')).toBeInTheDocument()
  })
  it('verwirft Auszug und Nachweis bei Kontowechsel', async () => {
    render(<Harness />); await importStatement(); await userEvent.selectOptions(screen.getByLabelText('Bankkonto'), 'bank-2')
    expect(screen.queryAllByText('REF-1')).toHaveLength(0)
    await userEvent.click(screen.getByRole('button', { name: 'Vergleich' }))
    expect(mocks.post).toHaveBeenCalledTimes(1)
  })
  it('verwirft den Auszug bei Dateiwechsel', async () => {
    render(<Harness />); await importStatement()
    await userEvent.upload(screen.getByLabelText('Kontoauszug'), new File(['xml'], 'neu.xml', { type: 'text/xml' }))
    expect(screen.queryAllByText('REF-1')).toHaveLength(0)
  })
  it('zeigt Fehler und behält keinen alten Saldennachweis', async () => {
    render(<Harness />); await importStatement(); mocks.post.mockRejectedValue(new Error('Offline'))
    await userEvent.click(screen.getByRole('button', { name: 'Vergleich' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Abgleich fehlgeschlagen', description: 'Offline' })))
    expect(screen.getByText('Saldennachweis unvollständig')).toBeInTheDocument()
  })
  it('führt ohne Planrecht keine Fachaktion aus', async () => {
    render(<Harness />); mocks.allowed = false
    await userEvent.click(screen.getByRole('button', { name: 'Import' }))
    expect(mocks.post).not.toHaveBeenCalled()
  })
})
