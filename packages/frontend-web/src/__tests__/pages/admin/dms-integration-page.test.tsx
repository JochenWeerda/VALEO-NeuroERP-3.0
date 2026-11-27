import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DmsIntegrationCard from '@/pages/admin/setup/dms-integration-legacy'

const apiGet = vi.hoisted(() => vi.fn())
const apiPost = vi.hoisted(() => vi.fn())
const toast = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/lib/api-client', () => ({
  apiClient: { get: (...a: unknown[]) => apiGet(...a), post: (...a: unknown[]) => apiPost(...a) },
  getAxiosErrorMessage: (e: unknown) => (e instanceof Error ? e.message : 'err'),
}))
vi.mock('@/components/workflow', () => ({
  CrudCapabilityChecklist: () => null,
  EvidenceTemplateLink: () => null,
  ManagementDecisionPanel: () => null,
  NextActionPanel: () => null,
  OperationalTaskPlan: () => null,
  RoleFocusBar: ({ onChange }: { onChange?: (id: string) => void }) => (
    <button type="button" onClick={() => onChange?.('leitung')}>Rolle</button>
  ),
}))

describe('DmsIntegrationCard page', () => {
  beforeEach(() => {
    apiGet.mockReset()
    apiPost.mockReset()
    toast.mockReset()
    apiGet.mockResolvedValue({ data: { ok: true, configured: false, base: 'http://dms.local' } })
  })

  it('lädt Status, testet Verbindung und bootstrapped DMS', async () => {
    render(<DmsIntegrationCard />)
    await waitFor(() => expect(apiGet).toHaveBeenCalledWith('/api/v1/admin/dms/status'))
    expect(screen.getByRole('region', { name: /DMS-Integration/i })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Rolle' }))

    fireEvent.click(screen.getByRole('button', { name: 'Jetzt einrichten' }))
    expect(screen.getByText('Mayan-DMS verbinden')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('API-Token'), { target: { value: 'tok-1' } })
    apiPost.mockResolvedValueOnce({ data: { ok: true } })
    fireEvent.click(screen.getByRole('button', { name: /Verbindung testen/ }))
    await waitFor(() => expect(apiPost).toHaveBeenCalledWith('/api/v1/admin/dms/test', expect.any(Object)))
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Verbindung getestet' })))

    apiPost.mockResolvedValueOnce({
      data: { ok: true, document_types: 2, metadata_types: 1, created: 3, updated: 0 },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Einrichten' }))
    await waitFor(() => expect(apiPost).toHaveBeenCalledWith('/api/v1/admin/dms/bootstrap', expect.any(Object)))
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Mayan-DMS integriert' })))
  })

  it('zeigt Status-Ladefehler und Verbindungsfehler', async () => {
    apiGet.mockRejectedValueOnce(new Error('offline'))
    render(<DmsIntegrationCard />)
    await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())
    apiGet.mockResolvedValueOnce({ data: { ok: true, configured: false, base: 'http://dms.local' } })
    fireEvent.click(screen.getByRole('button', { name: 'Erneut laden' }))
    await waitFor(() => expect(apiGet).toHaveBeenCalledTimes(2))

    fireEvent.click(screen.getByRole('button', { name: 'Jetzt einrichten' }))
    fireEvent.change(screen.getByLabelText('API-Token'), { target: { value: 'tok-x' } })
    apiPost.mockRejectedValueOnce(new Error('timeout'))
    fireEvent.click(screen.getByRole('button', { name: /Verbindung testen/ }))
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Verbindungsfehler' })))
  })

  it('zeigt konfigurierten DMS-Zustand', async () => {
    apiGet.mockResolvedValue({
      data: {
        ok: true,
        configured: true,
        base: 'http://mayan.local',
        document_types: 4,
        metadata_types: 2,
      },
    })
    render(<DmsIntegrationCard />)
    await waitFor(() => expect(screen.getByText('Aktiv')).toBeTruthy())
    expect(screen.getByText('http://mayan.local')).toBeTruthy()
    expect(screen.getByText('4')).toBeTruthy()
    expect(screen.getByRole('button', { name: /Im DMS oeffnen/ })).toBeTruthy()
    // Dialog ist nur im Nicht-konfiguriert-Zweig gemountet; Button bleibt klickbar.
    fireEvent.click(screen.getByRole('button', { name: 'Neu konfigurieren' }))
    expect(screen.getByRole('button', { name: 'Neu konfigurieren' })).toBeTruthy()
  })
})
