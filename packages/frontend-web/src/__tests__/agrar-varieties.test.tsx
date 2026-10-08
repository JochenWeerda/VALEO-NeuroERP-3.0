import { afterEach, describe, expect, it, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useSorten, varietyCropLabel, type AgrarVariety } from '@/lib/api/agrar'
import type { ReactNode } from 'react'

afterEach(() => vi.restoreAllMocks())
function wrapper() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
describe('canonical crop variety register query', () => {
  it('keeps crop selection labels compatible without rewriting canonical codes', () => {
    expect(varietyCropLabel('WHEAT').toLowerCase()).toBe('weizen')
    expect(varietyCropLabel('CUSTOM_CROP')).toBe('CUSTOM_CROP')
    expect(varietyCropLabel(null)).toBe('')
  })
  it('loads real canonical nullable and inactive fields without invented attributes', async () => {
    const variety: AgrarVariety = { id: 'variety-1', variety_number: '245', name: 'CI Weizen',
      description: null, crop_type: 'WHEAT', zuechter: null, zulassungsjahr: 2025,
      reifezahl: null, qualitaetsgruppe: 'A', aktiv: false }
    const get = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [variety] })
    const { result } = renderHook(() => useSorten(), { wrapper: wrapper() })
    await waitFor(() => expect(get).toHaveBeenCalled())
    await waitFor(() => expect(result.current.data).toEqual([variety]))
    expect(get.mock.calls[0][0]).toBe('/api/v1/agrar/varieties/?aktiv=false')
    expect(result.current.data?.[0]).not.toHaveProperty('eigenschaft')
  })
  it('retains a genuinely empty response', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] })
    const { result } = renderHook(() => useSorten(), { wrapper: wrapper() })
    await waitFor(() => expect(result.current.isFetching).toBe(false))
    expect(result.current.data).toEqual([])
  })
  it('exposes backend failure rather than reporting a successful empty register', async () => {
    vi.spyOn(apiClient, 'get').mockRejectedValue(new Error('API unavailable'))
    const { result } = renderHook(() => useSorten(), { wrapper: wrapper() })
    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(result.current.error?.message).toBe('API unavailable')
  })
})
