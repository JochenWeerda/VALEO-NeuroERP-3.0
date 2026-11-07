import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import Versandprofile from '@/pages/logistik/versandprofile'

const { mutate, toast } = vi.hoisted(() => ({ mutate: vi.fn(), toast: { success: vi.fn(), error: vi.fn() } }))
vi.mock('@/lib/api/versandprofile', () => ({
  useVersandprofile: () => ({ data: [{ id: 'uuid-1', profil_nr: 'P1', aktiv: true }], isLoading: false }),
  useLieferavise: () => ({ data: [], isLoading: false }),
  useDeleteVersandprofil: () => ({ mutateAsync: mutate }),
  useCreateVersandprofil: () => ({ mutateAsync: vi.fn() }), useCreateLieferavis: () => ({ mutateAsync: vi.fn() }),
}))
vi.mock('sonner', () => ({ toast }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/components/mask-builder/made-by-studio-runtime-wire', () => ({ MadeByStudioListRuntimeWire: () => null }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => [] }))
vi.mock('@/components/mask-builder/render-plan/schema-compiler', () => ({ compileRenderPlanFromScreenDefinition: () => ({}) }))
vi.mock('@/components/mask-builder/runtime/useUniversalFormState', () => ({ useUniversalFormState: () => ({ values: {}, setValue: vi.fn() }) }))
vi.mock('@/components/mask-builder/UniversalMaskRenderer', () => ({
  UniversalMaskRenderer: ({ tables, screenContext }: { tables: Record<string, Record<string, unknown>[]>; screenContext: { actions: Record<string, (row: Record<string, unknown>) => void> } }) =>
    <button onClick={() => screenContext.actions['versand.deleteProfile'](tables.profile[0])}>Deaktivieren</button>,
}))
beforeEach(() => { vi.clearAllMocks() })
afterEach(cleanup)
function mount() { render(<QueryClientProvider client={new QueryClient()}><Versandprofile /></QueryClientProvider>) }

it('requires confirmation, uses stable ID and reuses the key after an uncertain result', async () => {
  mutate.mockRejectedValueOnce(new Error('network')).mockResolvedValueOnce(undefined)
  mount(); fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  expect(mutate).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren bestätigen' }))
  await waitFor(() => expect(toast.error).toHaveBeenCalled())
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren bestätigen' }))
  await waitFor(() => expect(mutate).toHaveBeenCalledTimes(2))
  expect(mutate.mock.calls[0][0]).toEqual({ id: 'uuid-1', key: expect.any(String) })
  expect(mutate.mock.calls[1][0]).toEqual(mutate.mock.calls[0][0])
})

it('cancelling does not submit', async () => {
  mount(); fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
  expect(mutate).not.toHaveBeenCalled()
  await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
})
