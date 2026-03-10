import type { AliasGroupEntriesModule } from '@/app/route-builders/types'

const GROUP_MODULES = import.meta.glob<AliasGroupEntriesModule>('./generated/*.ts')

export const ALIAS_INDEX_MODULE = '@/pages/start-dashboard' as const

export function hasAliasRouteGroup(prefix: string): boolean {
  return Object.prototype.hasOwnProperty.call(GROUP_MODULES, `./generated/${prefix}.ts`)
}

export function loadAliasRouteGroup(prefix: string): Promise<AliasGroupEntriesModule> {
  const loader = GROUP_MODULES[`./generated/${prefix}.ts`]
  if (!loader) {
    return Promise.reject(new Error(`Unknown alias route group: ${prefix}`))
  }
  return loader()
}
