/**
 * Verträge zur Nutzermeldung vom 17.07.2026 — jetzt für alle Fächer.
 *
 * Gemeldet war: „Ackerschlagkartei zeigte initial weder Schläge noch Maßnahmen —
 * erst nach einer Mutation erschienen die Seed-Daten." Ursache:
 *
 *   `initialData: []` + `staleTime` ließ React Query den Platzhalter als **frisch
 *   geladen** werten — der Mount-Fetch entfiel.
 *
 * `initialData` schreibt den Wert in den Cache, als wäre er vom Server gekommen.
 * Ohne `initialDataUpdatedAt: 0` gilt er für die Dauer von `staleTime` als frisch,
 * und die Abfrage fragt in dieser Zeit **gar nicht**. Die Maske zeigt „keine
 * Einträge", und niemand sieht, dass nie gefragt wurde.
 *
 * Behoben war das für zwei Hooks in `portal.ts`. Diese Verträge halten fest, dass es
 * jetzt für die ganze Breite gilt — Hooks aus sechs Fächern, darunter die
 * `makeHook`-Fabrik aus `betrieb.ts`, hinter der allein über zwanzig Hooks stehen.
 *
 * Kein Backend nötig: `apiClient` ist gemockt.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock, post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { useVersicherungen } from '@/lib/api/schaeden'
import { useSchaeden } from '@/lib/api/betrieb'
import { usePortalAnfragen } from '@/lib/api/portal'
import { useCustomers } from '@/lib/api/crm'
import { useSalesDashboard } from '@/lib/api/dashboard'

function wrapper({ children }: { children: ReactNode }): JSX.Element {
  // `retry: false`, damit ein Fehlschlag sofort sichtbar wird und nicht wartet.
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe('Platzhalter verhindern den Mount-Fetch nicht (Nutzermeldung 17.07.2026)', () => {
  beforeEach(() => {
    getMock.mockReset()
  })

  it('useVersicherungen fragt trotz Platzhalter beim Mount', async () => {
    getMock.mockResolvedValue({ data: [{ id: 'v-1', bezeichnung: 'Hagel' }] })

    const { result } = renderHook(() => useVersicherungen(), { wrapper })

    await waitFor(() => {
      expect(getMock).toHaveBeenCalledWith('/api/v1/schaeden/versicherungen')
    })
    await waitFor(() => {
      expect(result.current.data).toEqual([{ id: 'v-1', bezeichnung: 'Hagel' }])
    })
  })

  it('useSchaeden (makeHook mit staleTime) fragt beim Mount', async () => {
    // `makeHook` setzt `staleTime: 2 * 60 * 1000`. Genau diese Kombination ließ den
    // Mount-Fetch entfallen — hinter der Fabrik stehen über zwanzig Hooks.
    getMock.mockResolvedValue({ data: [{ id: 's-1', meldungsnummer: 'SM-1' }] })

    const { result } = renderHook(() => useSchaeden(), { wrapper })

    await waitFor(() => {
      expect(getMock).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(result.current.data).toEqual([{ id: 's-1', meldungsnummer: 'SM-1' }])
    })
  })

  it('usePortalAnfragen fragt beim Mount', async () => {
    getMock.mockResolvedValue({ data: [{ id: 'a-1' }] })

    const { result } = renderHook(() => usePortalAnfragen(), { wrapper })

    await waitFor(() => expect(getMock).toHaveBeenCalled())
    await waitFor(() => expect(result.current.data).toEqual([{ id: 'a-1' }]))
  })

  it('useCustomers fragt beim Mount', async () => {
    getMock.mockResolvedValue({ data: { items: [{ id: 'k-1' }], total: 1 } })

    renderHook(() => useCustomers(), { wrapper })

    await waitFor(() => expect(getMock).toHaveBeenCalled())
  })

  it('useSalesDashboard fragt beim Mount', async () => {
    getMock.mockResolvedValue({ data: { umsatz: 1 } })

    renderHook(() => useSalesDashboard(), { wrapper })

    await waitFor(() => expect(getMock).toHaveBeenCalled())
  })

  it('ein Fehlschlag bleibt ein Fehlschlag — der Platzhalter verdeckt ihn nicht', async () => {
    // Die zweite Hälfte des Fehlers ist **nicht** behoben: `data` bleibt im
    // Fehlerfall der Platzhalter, weil `initialData` im Cache steht. Dieser Vertrag
    // hält genau das fest, damit es nicht als behoben gilt — eine Maske, die
    // `isError` nicht liest, zeigt weiterhin eine Attrappe.
    getMock.mockRejectedValue(new Error('500'))

    const { result } = renderHook(() => useVersicherungen(), { wrapper })

    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(getMock).toHaveBeenCalled()
    expect(result.current.data).toEqual([])
  })
})
