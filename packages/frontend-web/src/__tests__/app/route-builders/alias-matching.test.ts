import { describe, expect, it } from 'vitest'
import routeAliases from '@/app/route-aliases.json'
import {
  findMatchingAliasModule,
  findMatchingAliasModuleFromRouteAliases,
} from '@/app/route-builders/alias-matching'

describe('alias-matching', () => {
  it('findMatchingAliasModule: dynamische Segmente (relativePath ohne führenden Slash)', () => {
    const entries = [{ module: '@/pages/crm/lead-detail', path: 'lead/:id' }]
    expect(findMatchingAliasModule(entries, 'lead/test-123')).toBe('@/pages/crm/lead-detail')
  })

  it('findet Workflow-Routen auch dann aus der zentralen Alias-Tabelle, wenn die Gruppendatei veraltet ist', () => {
    const result = findMatchingAliasModuleFromRouteAliases(
      (routeAliases.aliases ?? []) as Array<{ module: string; path?: string; index?: boolean }>,
      'workflow',
      'flow-spine-studio',
    )

    expect(result).toBe('@/pages/workflow/flow-spine-studio')
  })
})
