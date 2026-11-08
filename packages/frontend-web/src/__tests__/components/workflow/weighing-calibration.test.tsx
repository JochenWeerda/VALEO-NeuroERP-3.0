import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import { ScaleCalibrationPanel } from '@/components/mask-builder/specialized/weighing/scale-calibration-panel'

const api = vi.hoisted(() => ({ get: vi.fn(), patch: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: api, getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({ useDomainIdentity: () => ({ tenantId: 'tenant-a', actor: 'operator-a' }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: () => null }))

const fields = { letztes_eichdatum: 'Letztes Eichdatum', naechste_eichfaelligkeit: 'Nächste Eichfälligkeit', eichamt: 'Eichamt', zertifikat_nr: 'Zertifikat-Nr.' }
function plan(disabled = false): RenderPlan {
  return { fieldsByKey: Object.fromEntries(Object.entries(fields).map(([key, label]) => [key, { visible: true, readOnly: false, label }])), actions: [{ key: 'calibrate', label: 'Eichdaten speichern', disabled }] } as unknown as RenderPlan
}
function show(value = plan()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<QueryClientProvider client={client}><ScaleCalibrationPanel plan={value} scales={[{ id: 'scale-a', standort: 'Hof', typ: 'LKW', maxKapazitaet: 60, letzteEichung: '', naechsteEichung: '', status: 'aktiv' }]} onSaved={vi.fn()} /></QueryClientProvider>)
  fireEvent.change(screen.getByLabelText('Waage'), { target: { value: 'scale-a' } })
}
beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockResolvedValue({ data: { letztes_eichdatum: '2026-01-01', naechste_eichfaelligkeit: '2027-01-01', eichamt: 'Amt', zertifikat_nr: 'Z-1' } })
  api.patch.mockResolvedValue({ data: {} })
})
describe('Canonical scale calibration surface', () => {
  it('loads and patches only the selected scale, preserving date strings', async () => {
    show()
    await screen.findByDisplayValue('Z-1')
    expect(api.get).toHaveBeenCalledWith('/api/v1/waage/waagen/scale-a/kalibrierung')
    fireEvent.change(screen.getByLabelText('Zertifikat-Nr.'), { target: { value: 'Z-2' } })
    fireEvent.click(screen.getByRole('button', { name: 'Eichdaten speichern' }))
    await waitFor(() => expect(api.patch).toHaveBeenCalledWith('/api/v1/waage/waagen/scale-a/kalibrierung', { letztes_eichdatum: '2026-01-01', naechste_eichfaelligkeit: '2027-01-01', eichamt: 'Amt', zertifikat_nr: 'Z-2' }))
  })
  it('retains input and shows an API error without pretending success', async () => {
    api.patch.mockRejectedValue(new Error('Mandantenprüfung fehlgeschlagen'))
    show()
    await screen.findByDisplayValue('Z-1')
    fireEvent.change(screen.getByLabelText('Zertifikat-Nr.'), { target: { value: 'Z-pending' } })
    fireEvent.click(screen.getByRole('button', { name: 'Eichdaten speichern' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Mandantenprüfung fehlgeschlagen')
    expect(screen.getByLabelText('Zertifikat-Nr.')).toHaveValue('Z-pending')
    expect(screen.queryByText('Eichdaten gespeichert.')).not.toBeInTheDocument()
  })
  it('blocks a disabled compiled action including a direct form submit', async () => {
    show(plan(true))
    await screen.findByDisplayValue('Z-1')
    expect(screen.getByRole('button', { name: 'Eichdaten speichern' })).toBeDisabled()
    fireEvent.submit(screen.getByRole('button', { name: 'Eichdaten speichern' }).closest('form')!)
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('können nicht bearbeitet'))
    expect(api.patch).not.toHaveBeenCalled()
  })
  it('does not write reversed calibration dates', async () => {
    show()
    await screen.findByDisplayValue('Z-1')
    fireEvent.change(screen.getByLabelText('Nächste Eichfälligkeit'), { target: { value: '2025-01-01' } })
    fireEvent.click(screen.getByRole('button', { name: 'Eichdaten speichern' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('nicht vor der letzten')
    expect(api.patch).not.toHaveBeenCalled()
  })
})
