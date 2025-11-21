import routeAliases from '@/app/route-aliases.json'

type AliasEntry = {
  module: string
  path?: string
}

const aliasMap = new Map<string, string[]>()
for (const alias of (routeAliases.aliases ?? []) as AliasEntry[]) {
  const moduleKey = normalizeModule(alias.module)
  if (!aliasMap.has(moduleKey)) {
    aliasMap.set(moduleKey, [])
  }
  if (alias.path) {
    aliasMap.get(moduleKey)?.push(alias.path)
  }
}

export function resolveRoutePathFromModule(moduleSpecifier: string, fallbackPath?: string): string {
  const moduleKey = normalizeModule(moduleSpecifier)
  if (fallbackPath) {
    return toAbsolutePath(fallbackPath)
  }

  const aliasPath = aliasMap.get(moduleKey)?.[0]
  if (aliasPath) {
    return toAbsolutePath(aliasPath)
  }

  const defaultPath = computeDefaultPath(moduleKey)
  return toAbsolutePath(defaultPath)
}

function normalizeModule(moduleSpecifier: string): string {
  if (moduleSpecifier.startsWith('@/')) {
    return moduleSpecifier
  }
  if (moduleSpecifier.startsWith('./')) {
    return moduleSpecifier.replace('./', '@/')
  }
  return moduleSpecifier.startsWith('pages/')
    ? `@/${moduleSpecifier}`
    : moduleSpecifier
}

function computeDefaultPath(moduleSpecifier: string): string {
  let path = moduleSpecifier.replace(/^@\//, '')
  if (path.startsWith('pages/')) {
    path = path.slice('pages/'.length)
  }
  if (path.endsWith('/index')) {
    path = path.slice(0, -'/index'.length)
  }
  return path || '/'
}

function toAbsolutePath(routePath: string): string {
  if (!routePath || routePath === '/') {
    return '/'
  }
  return routePath.startsWith('/') ? routePath : `/${routePath}`
}
