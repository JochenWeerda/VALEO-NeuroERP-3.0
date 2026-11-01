import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import { ScaleImportPanel } from '@/components/mask-builder/specialized/weighing/scale-import-panel'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), delete: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: api, getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({ useDomainIdentity: () => ({ tenantId: 'tenant-a', actor: 'operator-a' }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: () => null }))

function plan(disabled = false): RenderPlan {
  return { fieldsByKey: Object.fromEntries(['importScaleId', 'importFile', 'fehlerToleranz'].map(key => [key, { label: key, visible: true, readOnly: false }])),
    actions: ['import', 'retryImport', 'dismissImport'].map(key => ({ key, label: key === 'import' ? 'Datei importieren' : key, disabled })) } as unknown as RenderPlan
}
function show(value = plan()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<QueryClientProvider client={client}><ScaleImportPanel plan={value} scales={[{ id: 'scale-a', standort: 'Hof', typ: 'LKW', maxKapazitaet: 60, letzteEichung: '', naechsteEichung: '', status: 'aktiv' }]} onImported={vi.fn()} /></QueryClientProvider>)
}
function selectFile(bytes = new TextEncoder().encode('W;123')): File {
  const file = new File([bytes], 'scale.asc', { type: 'text/plain' })
  Object.defineProperty(file, 'arrayBuffer', { value: async () => bytes.buffer })
  fireEvent.change(screen.getByLabelText('importScaleId'), { target: { value: 'scale-a' } })
  fireEvent.change(screen.getByLabelText('importFile'), { target: { files: [file] } })
  return file
}
beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue({ data: [] })
  api.post.mockResolvedValue({ data: { imported: 1, skipped: 0, errors: [], wiegung_ids: ['ticket-a'], replayed: false } })
  api.delete.mockResolvedValue({ data: { deleted: true } })
})
describe('Guarded scale import and tenant error queue', () => {
  it('requires explicit own scale, sends bounded UTF-8 file and strict default', async () => {
    show()
    expect(screen.getByRole('button', { name: 'Datei importieren' })).toBeDisabled()
    const file = selectFile()
    fireEvent.click(screen.getByRole('button', { name: 'Datei importieren' }))
    await screen.findByText('1 importiert, 0 übersprungen, 0 Fehler.')
    expect(api.post).toHaveBeenCalledTimes(1)
    const [endpoint, body] = api.post.mock.calls[0]
    expect(endpoint).toBe('/api/v1/waage/waagen/import/ascii')
    expect(body.get('waage_id')).toBe('scale-a')
    expect(body.get('fehler_toleranz')).toBe('false')
    expect(body.get('file').name).toBe(file.name)
  })
  it('rejects an oversized file before any import request', async () => {
    show()
    selectFile(new Uint8Array(1048577))
    expect(screen.getByRole('alert')).toHaveTextContent('größer als 1 MB')
    expect(screen.getByRole('button', { name: 'Datei importieren' })).toBeDisabled()
    expect(api.post).not.toHaveBeenCalled()
  })
  it('preserves selected file and scale after an API failure for retry', async () => {
    api.post.mockRejectedValueOnce(new Error('Artikel nicht freigegeben'))
    show()
    selectFile()
    fireEvent.click(screen.getByRole('button', { name: 'Datei importieren' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Artikel nicht freigegeben')
    expect(screen.getByLabelText('importScaleId')).toHaveValue('scale-a')
    expect(screen.getByRole('button', { name: 'Datei importieren' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Datei importieren' }))
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(2))
    expect(api.post.mock.calls[1][1].get('file').name).toBe('scale.asc')
  })
  it('retains a replay receipt without claiming a second import', async () => {
    api.post.mockResolvedValue({ data: { imported: 0, skipped: 1, errors: [], wiegung_ids: ['ticket-a'], replayed: true } })
    show()
    selectFile()
    fireEvent.click(screen.getByRole('button', { name: 'Datei importieren' }))
    await screen.findByText(/Bereits verarbeitete Datei; keine Doppelanlage/)
  })
  it('requires confirmation before dismissing a returned queue entry', async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 'error-a', waage_id: 'scale-a', rohdaten: 'W;bad', fehler_beschreibung: 'Artikel fehlt', retry_count: 0, status: 'error', timestamp: '2026-10-30', ticket_id: null }] })
    show()
    await screen.findByText('Artikel fehlt')
    fireEvent.click(screen.getByRole('button', { name: 'Verwerfen' }))
    expect(api.delete).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Verwerfen bestätigen' }))
    await waitFor(() => expect(api.delete).toHaveBeenCalledWith('/api/v1/waage/waagen/import/fehlerqueue/error-a'))
  })
})
