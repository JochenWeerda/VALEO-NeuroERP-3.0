import { afterEach, describe, expect, it, vi } from 'vitest'
import i18n from '@/i18n/config'
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
})
