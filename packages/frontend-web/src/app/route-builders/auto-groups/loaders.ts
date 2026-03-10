import type { AutoGroupEntriesModule } from '@/app/route-builders/types'

const GROUP_MODULES = import.meta.glob<AutoGroupEntriesModule>('./generated/*.ts')

export function hasAutoRouteGroup(prefix: string): boolean {
  return Object.prototype.hasOwnProperty.call(GROUP_MODULES, `./generated/${prefix}.ts`)
}

export function loadAutoRouteGroup(prefix: string): Promise<AutoGroupEntriesModule> {
  const loader = GROUP_MODULES[`./generated/${prefix}.ts`]
  if (!loader) {
    return Promise.reject(new Error(`Unknown auto route group: ${prefix}`))
  }
  return loader()
}
