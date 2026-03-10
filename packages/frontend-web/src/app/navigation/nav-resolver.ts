import type { NavItem, RawNavItem } from '@/app/navigation/types'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

export function resolveNavItem(item: RawNavItem): NavItem {
  const moduleSpecifier = item.module ?? inferModuleFromPath(item.path)
  const resolvedPath =
    item.path ??
    (moduleSpecifier ? resolveRoutePathFromModule(moduleSpecifier, item.preferredPath) : undefined)

  return {
    ...item,
    module: moduleSpecifier,
    path: resolvedPath,
    children: item.children?.map(resolveNavItem),
  }
}

export function inferModuleFromPath(path?: string): string | undefined {
  if (!path) {
    return undefined
  }
  const normalized = path.startsWith('/') ? path.slice(1) : path
  if (!normalized) {
    return '@/pages/start-dashboard'
  }
  return `@/pages/${normalized}`
}

export function flattenNavItems(items: NavItem[]): NavItem[] {
  return items.flatMap((item) => {
    const result: NavItem[] = []
    if (item.path) {
      result.push(item)
    }
    if (item.children) {
      result.push(...flattenNavItems(item.children))
    }
    return result
  })
}
