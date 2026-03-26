import { describe, expect, it } from 'vitest'
import routeAliases from '@/app/route-aliases.json'
import { findMatchingAliasModuleFromRouteAliases } from '@/app/route-builders/alias-matching'

describe('alias-matching', () => {
  it('findet Workflow-Routen auch dann aus der zentralen Alias-Tabelle, wenn die Gruppendatei veraltet ist', () => {
    const result = findMatchingAliasModuleFromRouteAliases(
      (routeAliases.aliases ?? []) as Array<{ module: string; path?: string; index?: boolean }>,
      'workflow',
      'flow-spine-studio',
    )

    expect(result).toBe('@/pages/workflow/flow-spine-studio')
  })
})
