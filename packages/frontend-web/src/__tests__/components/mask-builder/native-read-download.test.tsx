import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { readDownload } from '@/components/mask-builder/runtime/read-download'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const { get, request, toast, state } = vi.hoisted(() => ({
  get: vi.fn(), request: vi.fn(), toast: vi.fn(), state: { allowed: true },
}))
const action = { key: 'export_erstellen', label: 'Export erstellen', permission: 'finance.datev.export',
  download: { endpoint: '/api/v1/finance/datev-export', contentField: 'csv', filenameField: 'filename', mediaType: 'text/csv;charset=utf-8' as const },
  inputFields: [{ key: 'typ', label: 'Buchungsstapel-Typ', type: 'select' as const, required: true,
    options: [{ value: 'alle', label: 'Alle' }, { value: 'debitor', label: 'Debitoren' }, { value: 'kreditor', label: 'Kreditoren' }] }],
}
const definition: ScreenDefinition = { schemaVersion: 1, id: 'finance/datev-export', domain: 'finance', mode: 'list', title: 'DATEV-Export', actions: [action] }
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => state.allowed ? ['finance.datev.export'] : [] }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get, request }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction }: { onAction: (key: string, row: object) => void }) =>
    <button onClick={() => onAction('export_erstellen', {})}>Export erstellen</button>,
}))

beforeEach(() => { vi.clearAllMocks(); state.allowed = true })
function mount() {
  render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="finance/datev-export" /></QueryClientProvider>)
}
async function selectExport() {
  fireEvent.click(screen.getByRole('button', { name: 'Export erstellen' }))
  fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'kreditor' } })
  fireEvent.click(screen.getAllByRole('button', { name: 'Export erstellen' }).at(-1)!)
}

it('preserves type selection, the real GET API, CSV preview and the server filename', async () => {
  get.mockResolvedValue({ data: { filename: 'datev-kreditor.csv', csv: 'Konto;Betrag\n1600;25,00', zeilen: 1, summe: 25 } })
  mount(); await selectExport()
  expect(await screen.findByText('datev-kreditor.csv')).toBeVisible()
  expect(screen.getByText(/1600;25,00/)).toBeVisible()
  expect(get).toHaveBeenCalledWith('/api/v1/finance/datev-export', { params: { typ: 'kreditor' } })
  expect(request).not.toHaveBeenCalled()
  const create = vi.fn(() => 'blob:synthetic'), revoke = vi.fn(), click = vi.fn()
  vi.stubGlobal('URL', class extends URL { static createObjectURL = create; static revokeObjectURL = revoke })
  const spy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(click)
  fireEvent.click(screen.getByRole('button', { name: 'Datei herunterladen' }))
  expect(create.mock.calls[0][0]).toBeInstanceOf(Blob)
  expect(click).toHaveBeenCalledTimes(1)
  expect(revoke).toHaveBeenCalledWith('blob:synthetic')
  spy.mockRestore(); vi.unstubAllGlobals()
})

it('keeps selected inputs on server rejection and retries without a domain mutation', async () => {
  get.mockRejectedValueOnce(new Error('Kein Finanzleserecht')).mockResolvedValueOnce({ data: { filename: 'datev.csv', csv: '' } })
  mount(); await selectExport()
  await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })))
  expect(screen.getByRole('combobox')).toHaveValue('kreditor')
  fireEvent.click(screen.getAllByRole('button', { name: 'Export erstellen' }).at(-1)!)
  expect(await screen.findByText('datev.csv')).toBeVisible()
  expect(request).not.toHaveBeenCalled()
})

it('does not dispatch even a direct UI callback without its projected permission', () => {
  state.allowed = false; mount()
  fireEvent.click(screen.getByRole('button', { name: 'Export erstellen' }))
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(get).not.toHaveBeenCalled()
})

it.each(['https://external.invalid/api', '//external.invalid/api', '/api/v1/x?tenant_id=other'])('rejects an unsafe endpoint %s before HTTP', async endpoint => {
  await expect(readDownload({ ...action, download: { ...action.download, endpoint } }, { typ: 'alle' })).rejects.toThrow()
  expect(get).not.toHaveBeenCalled()
})

it.each([{}, { typ: 'invalid' }, { typ: ['alle'] }])('rejects invalid selection %j before HTTP', async values => {
  await expect(readDownload(action, values)).rejects.toThrow()
  expect(get).not.toHaveBeenCalled()
})

it.each([{ filename: '../data.csv', csv: 'data' }, { filename: 'data.csv', csv: null }, { filename: 'data.csv' }])('does not invent a file from a malformed response %j', async data => {
  get.mockResolvedValue({ data })
  await expect(readDownload(action, { typ: 'alle' })).rejects.toThrow()
})
