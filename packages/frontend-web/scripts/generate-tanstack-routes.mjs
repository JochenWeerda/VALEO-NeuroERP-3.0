#!/usr/bin/env node
import { readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs'
import { basename, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const root = join(__dirname, '..')
const aliasesFile = join(root, 'src', 'app', 'route-aliases.json')
const legacyRedirectsFile = join(root, 'src', 'app', 'routing', 'legacy-redirects.json')
const navigationRoutesFile = join(root, 'src', 'app', 'routing', 'navigation-routes.json')
const autoGroupsDir = join(root, 'src', 'app', 'route-builders', 'auto-groups', 'generated')
const outputFile = join(root, 'src', 'app', 'routing', 'route-tree.gen.tsx')
const inventoryFile = join(root, 'src', 'app', 'routing', 'route-inventory.gen.json')
const sourceDir = join(root, 'src')

function normalizePath(value) {
  return String(value ?? '').replace(/^\/+|\/+$/g, '')
}

function toTanStackPath(value) {
  return normalizePath(value)
    .split('/')
    .map((segment) => (segment.startsWith(':') ? `$${segment.slice(1)}` : segment))
    .join('/')
}

function parseAutoEntries() {
  const entries = []
  for (const name of readdirSync(autoGroupsDir).filter((entry) => entry.endsWith('.ts'))) {
    const prefix = basename(name, '.ts')
    const text = readFileSync(join(autoGroupsDir, name), 'utf8')
    for (const match of text.matchAll(/"module":\s*"([^"]+)"[\s\S]*?"path":\s*"([^"]*)"/g)) {
      entries.push({
        module: match[1],
        path: normalizePath(`${prefix}/${match[2]}`),
        source: 'auto',
      })
    }
  }
  return entries
}

function collectSearchKeys(directory) {
  const keys = new Set()
  for (const name of readdirSync(directory)) {
    const file = join(directory, name)
    if (statSync(file).isDirectory()) {
      for (const key of collectSearchKeys(file)) keys.add(key)
      continue
    }
    if (!/\.(?:ts|tsx)$/.test(name) || name === 'route-tree.gen.tsx') continue
    const text = readFileSync(file, 'utf8')
    for (const match of text.matchAll(/searchParams\.get\(['"]([A-Za-z0-9_-]+)['"]\)/g)) {
      keys.add(match[1])
    }
  }
  return keys
}

function routeLabel(path) {
  const segment = normalizePath(path).split('/').filter(Boolean).at(-1) ?? 'Start'
  if (segment.startsWith(':')) return 'Detail'
  return segment
    .split('-')
    .map((part) => part ? `${part[0].toUpperCase()}${part.slice(1)}` : part)
    .join(' ')
}

const aliases = JSON.parse(readFileSync(aliasesFile, 'utf8')).aliases ?? []
const legacyRedirects = JSON.parse(readFileSync(legacyRedirectsFile, 'utf8'))
const navigationRoutes = JSON.parse(readFileSync(navigationRoutesFile, 'utf8'))
const candidates = [
  ...aliases
    .filter((entry) => typeof entry.path === 'string')
    .map((entry) => ({ module: entry.module, path: normalizePath(entry.path), source: 'alias' })),
  ...parseAutoEntries(),
  ...navigationRoutes.map((entry) => ({
    module: entry.module,
    path: normalizePath(entry.path),
    source: 'navigation',
  })),
]

// Native mask aliases are the rollout switch for UniversalMaskRuntime pages and
// must win over legacy auto detail routes on the same URL.
const byPath = new Map()
function candidatePriority(entry) {
  if (entry.source === 'alias' && entry.module?.endsWith('-native')) return -1
  return { auto: 0, alias: 1, navigation: 2 }[entry.source] ?? 3
}
for (const entry of candidates.sort(
  (a, b) => candidatePriority(a) - candidatePriority(b),
)) {
  if (entry.path && !byPath.has(entry.path)) byPath.set(entry.path, entry)
}

byPath.set('', { module: '@/pages/start-dashboard', path: '', source: 'system' })
byPath.set('login', { module: '@/pages/auth/Login', path: 'login', source: 'system' })
byPath.set('auth/login', { module: '@/pages/auth/Login', path: 'auth/login', source: 'system' })
byPath.set('auth/callback', { module: '@/pages/auth/Callback', path: 'auth/callback', source: 'system' })
byPath.set('fibu-suite/$', { module: '@runtime/fibu-suite', path: 'fibu-suite/$', source: 'system' })

const entries = [...byPath.values()].sort((a, b) => a.path.localeCompare(b.path))
const searchKeys = [...collectSearchKeys(sourceDir)].sort()
const paramKeys = [
  ...new Set(
    entries.flatMap((entry) =>
      [...entry.path.matchAll(/:([A-Za-z0-9_]+)/g)].map((match) => match[1]),
    ),
  ),
].sort()
const publicPaths = new Set(['login', 'auth/login', 'auth/callback'])
const publicEntries = entries.filter((entry) => publicPaths.has(entry.path))
const appEntries = entries.filter(
  (entry) =>
    !publicPaths.has(entry.path) &&
    !entry.path.startsWith('verify/') &&
    !entry.path.startsWith('portal/') &&
    entry.path !== 'portal',
)
const portalEntries = entries.filter((entry) => entry.path.startsWith('portal/') || entry.path === 'portal')
publicEntries.push(...entries.filter((entry) => entry.path.startsWith('verify/')))

function identifier(index, prefix) {
  return `${prefix}Route${String(index).padStart(4, '0')}`
}

function emitRoute(entry, index, parent, prefix, relativePath = entry.path) {
  const id = identifier(index, prefix)
  const routePath = toTanStackPath(relativePath) || '/'
  const staticData = {
    breadcrumb: routeLabel(entry.path),
    module: entry.module,
    legacyPath: `/${entry.path}`,
  }
  const redirectTarget = legacyRedirects[entry.path]
  const beforeLoad = redirectTarget
    ? `  beforeLoad: ({ params }) => {
    throw redirect({ href: buildLegacyRedirect(${JSON.stringify(redirectTarget)}, params) })
  },
`
    : ''
  return `const ${id} = createRoute({
  getParentRoute: () => ${parent},
  path: ${JSON.stringify(routePath)},
${beforeLoad}\
  component: () => renderPage(${JSON.stringify(entry.module)}),
  staticData: ${JSON.stringify(staticData)},
})`
}

const appRoutes = appEntries.map((entry, index) => emitRoute(entry, index, 'appLayoutRoute', 'app'))
const publicRoutes = publicEntries.map((entry, index) => emitRoute(entry, index, 'rootRoute', 'public'))
const portalRoutes = portalEntries.map((entry, index) => {
  const relative = entry.path === 'portal' ? '/' : entry.path.slice('portal/'.length)
  return emitRoute(entry, index, 'portalLayoutRoute', 'portal', relative)
})

const content = `// Generated by scripts/generate-tanstack-routes.mjs. Do not edit manually.
import { createRootRoute, createRoute, redirect } from '@tanstack/react-router'
import { RootRouteLayout, AppRouteLayout, PortalRouteLayout, renderPage } from '@/app/routing/route-layouts'

function buildLegacyRedirect(target: string, params: Record<string, string>): string {
  return \`/\${target.replace(/:([A-Za-z0-9_]+)/g, (_match, name: string) => encodeURIComponent(params[name] ?? ''))}\`
}

export const rootRoute = createRootRoute({
  component: RootRouteLayout,
  notFoundComponent: () => renderPage('@/pages/errors/NotFound'),
})

export const appLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: '_app',
  component: AppRouteLayout,
})

export const portalLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'portal',
  component: PortalRouteLayout,
})

${appRoutes.join('\n\n')}

${publicRoutes.join('\n\n')}

${portalRoutes.join('\n\n')}

export const routeTree = rootRoute.addChildren([
  appLayoutRoute.addChildren([
    ${appEntries.map((_, index) => identifier(index, 'app')).join(',\n    ')}
  ]),
  portalLayoutRoute.addChildren([
    ${portalEntries.map((_, index) => identifier(index, 'portal')).join(',\n    ')}
  ]),
  ${publicEntries.map((_, index) => identifier(index, 'public')).join(',\n  ')}
])

export const generatedRouteInventory = ${JSON.stringify(entries, null, 2)} as const
export const generatedSearchKeys = ${JSON.stringify(searchKeys, null, 2)} as const
export const generatedParamKeys = ${JSON.stringify(paramKeys, null, 2)} as const
`

writeFileSync(outputFile, content)
writeFileSync(
  inventoryFile,
  `${JSON.stringify({ routes: entries, searchKeys, paramKeys }, null, 2)}\n`,
)
console.log(`Generated ${entries.length} TanStack routes in ${outputFile}`)
