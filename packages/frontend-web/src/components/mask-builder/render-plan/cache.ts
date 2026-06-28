import type { RenderPlan } from './types'

const DEFAULT_MAX_ENTRIES = 50

type CacheEntry = {
  plan: RenderPlan
}

export class RenderPlanCache {
  private readonly maxEntries: number
  private readonly store = new Map<string, CacheEntry>()

  constructor(maxEntries = DEFAULT_MAX_ENTRIES) {
    this.maxEntries = maxEntries
  }

  get(cacheKey: string): RenderPlan | undefined {
    const entry = this.store.get(cacheKey)
    if (!entry) return undefined
    this.store.delete(cacheKey)
    this.store.set(cacheKey, entry)
    return entry.plan
  }

  set(cacheKey: string, plan: RenderPlan): void {
    if (this.store.has(cacheKey)) {
      this.store.delete(cacheKey)
    }
    this.store.set(cacheKey, { plan })
    while (this.store.size > this.maxEntries) {
      const oldest = this.store.keys().next().value
      if (oldest === undefined) break
      this.store.delete(oldest)
    }
  }

  invalidate(cacheKey?: string): void {
    if (cacheKey) {
      this.store.delete(cacheKey)
      return
    }
    this.store.clear()
  }

  size(): number {
    return this.store.size
  }
}

export const globalRenderPlanCache = new RenderPlanCache()
