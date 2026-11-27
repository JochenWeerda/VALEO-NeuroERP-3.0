import { describe, expect, it } from 'vitest'
import { getPageModuleLoader } from '@/app/page-module-loader'
import routeInventory from '@/app/routing/route-inventory.gen.json'

describe('inventory page modules load', () => {
  it('loads every unique @/pages module from route inventory', async () => {
    const modules = [...new Set(
      routeInventory.routes
        .map((r) => r.module)
        .filter((m): m is string => typeof m === 'string' && m.startsWith('@/pages/')),
    )].sort()
    const failures: string[] = []
    for (const modulePath of modules) {
      try {
        const page = await getPageModuleLoader(modulePath)()
        if (typeof page.default !== 'function') {
          failures.push(`${modulePath}: default is ${typeof page.default}`)
        }
      } catch (error) {
        failures.push(`${modulePath}: ${error instanceof Error ? error.message : String(error)}`)
      }
    }
    expect(failures, failures.slice(0, 50).join('\n')).toEqual([])
  }, 180_000)
})
