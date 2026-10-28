import { afterEach, describe, expect, it, vi } from 'vitest'
import i18n from '@/i18n/config'
import { apiClient } from '@/lib/api-client'
import {
  getFlowSpineWorkspaceQueryKey,
  prefetchFlowSpineWorkspace,
  warmFlowSpineCache,
} from '@/lib/api/flow-spines'

describe('flow spine query keys', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('builds workspace keys with language and instance id', () => {
    expect(getFlowSpineWorkspaceQueryKey('order-to-cash', undefined, 'de')).toEqual([
      'workflow',
      'flow-spine',
      'order-to-cash',
      'default',
      'de',
    ])

    expect(getFlowSpineWorkspaceQueryKey('order-to-cash', 'instance-7', 'en')).toEqual([
      'workflow',
      'flow-spine',
      'order-to-cash',
      'instance-7',
      'en',
    ])
  })

  it('prefetches with the same language-aware workspace key', async () => {
    Object.defineProperty(i18n, 'resolvedLanguage', {
      value: 'de',
      configurable: true,
    })

    const prefetchQuery = vi.fn().mockResolvedValue(undefined)
    const queryClient = { prefetchQuery } as never

    await prefetchFlowSpineWorkspace(queryClient, 'order-to-cash', 'instance-7')

    expect(prefetchQuery).toHaveBeenCalledTimes(1)
    expect(prefetchQuery.mock.calls[0][0].queryKey).toEqual([
      'workflow',
      'flow-spine',
      'order-to-cash',
      'instance-7',
      'de',
    ])
  })

  it('warms all workspaces with the same language-aware key pattern', () => {
    vi.useFakeTimers()
    Object.defineProperty(i18n, 'resolvedLanguage', {
      value: 'de',
      configurable: true,
    })

    const prefetchQuery = vi.fn().mockResolvedValue(undefined)
    const queryClient = { prefetchQuery } as never

    warmFlowSpineCache(queryClient)
    vi.runAllTimers()

    expect(prefetchQuery).toHaveBeenCalledTimes(9)
    expect(prefetchQuery.mock.calls[0][0].queryKey).toEqual([
      'workflow',
      'flow-spine',
      'order-to-cash',
      'default',
      'de',
    ])
    expect(prefetchQuery.mock.calls[8][0].queryKey).toEqual([
      'workflow',
      'flow-spine',
      'compliance-to-report',
      'default',
      'de',
    ])
  })
  it('cancels pending warmup on unmount and keeps staggered reads bounded', () => {
    vi.useFakeTimers()
    const prefetchQuery = vi.fn().mockResolvedValue(undefined)
    const cancel = warmFlowSpineCache({ prefetchQuery } as never)
    vi.advanceTimersByTime(299)
    expect(prefetchQuery).toHaveBeenCalledTimes(1)
    cancel()
    vi.runAllTimers()
    expect(prefetchQuery).toHaveBeenCalledTimes(1)
  })
  it('uses the same captured language for delayed requests and cache keys', async () => {
    vi.useFakeTimers()
    const read = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { nodes: [] } })
    const prefetchQuery = vi.fn().mockResolvedValue(undefined)
    const cancel = warmFlowSpineCache({ prefetchQuery } as never, 'de')
    Object.defineProperty(i18n, 'resolvedLanguage', { value: 'en', configurable: true })
    vi.advanceTimersByTime(301)
    await prefetchQuery.mock.calls[1][0].queryFn()
    expect(prefetchQuery.mock.calls[1][0].queryKey.at(-1)).toBe('de')
    expect(read).toHaveBeenCalledWith('/api/v1/process/flow-spines/procure-to-pay?lang=de')
    cancel()
  })

})
