/**
 * Regressionstest (User-Meldung 2026-07-17): Ackerschlagkartei zeigte initial
 * weder Schlaege noch Massnahmen — erst nach einer Mutation erschienen die
 * Seed-Daten. Ursache: `initialData: []` + `staleTime` liess React Query die
 * leere Liste als frische Daten werten, der Mount-Fetch entfiel.
 * Vertrag: die Feldbuch-Hooks MUESSEN beim Mount vom Server laden.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock },
}))

import {
  usePortalFeldbuchMassnahmen,
  usePortalFeldbuchSchlaege,
} from '@/lib/api/portal'

function wrapper({ children }: { children: ReactNode }): JSX.Element {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe('Portal-Feldbuch-Hooks laden beim Mount (Seed-Sichtbarkeit)', () => {
  beforeEach(() => {
    getMock.mockReset()
  })

  it('usePortalFeldbuchSchlaege fetcht sofort und liefert die Serverdaten', async () => {
    getMock.mockResolvedValue({ data: [{ id: 's-1', name: 'Seed-Schlag' }] })

    const { result } = renderHook(() => usePortalFeldbuchSchlaege(), { wrapper })

    await waitFor(() => {
      expect(getMock).toHaveBeenCalledWith('/api/v1/portal/feldbuch/schlaege')
    })
    await waitFor(() => {
      expect(result.current.data).toEqual([{ id: 's-1', name: 'Seed-Schlag' }])
    })
  })

  it('usePortalFeldbuchMassnahmen fetcht sofort (leere Liste ist kein Datenersatz)', async () => {
    getMock.mockResolvedValue({ data: [{ id: 'm-1', typ: 'duengung' }] })

    const { result } = renderHook(() => usePortalFeldbuchMassnahmen(), { wrapper })

    await waitFor(() => {
      expect(getMock).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(result.current.data).toEqual([{ id: 'm-1', typ: 'duengung' }])
    })
  })
})
