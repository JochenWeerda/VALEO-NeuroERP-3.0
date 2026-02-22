import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import routeAliases from '../src/app/route-aliases.json' assert { type: 'json' }
import { NAV_SECTIONS, type NavItem } from '../src/app/navigation/manifest'

type AliasInfo = { paths: Set<string>; hasIndex: boolean }

type NavAuditEntry = {
  id: string
  label: string
  depth: number
  module?: string
  path?: string
  fileExists: boolean
  routeLinked: boolean
}

type PageEntry = {
  pagePath: string
  moduleSpecifier: string
  assignedInNav: boolean
}

type CardEntry = {
  id: string
  label: string
  path: string
  module?: string
  featureKey?: string
}

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT_DIR = path.resolve(__dirname, '..')
const SRC_DIR = path.join(ROOT_DIR, 'src')
const OUTPUT_DIR = path.join(ROOT_DIR, 'artifacts')
const REPORT_PATH = path.join(OUTPUT_DIR, 'navigation-audit.md')
const JSON_PATH = path.join(OUTPUT_DIR, 'navigation-audit.json')

const aliasMap = buildAliasMap()

const pageEntries = listPages()
const navEntries = collectNavEntries(NAV_SECTIONS)
const cardEntries = collectCards(NAV_SECTIONS)

const missingModules = navEntries.filter((entry) => entry.module && !entry.fileExists)
const missingRoutes = navEntries.filter((entry) => entry.path && !entry.routeLinked)
const unassignedPages = pageEntries.filter((entry) => !entry.assignedInNav)

const reportLines: string[] = []
reportLines.push('# Navigation Audit')
reportLines.push('')
reportLines.push(`Generated: ${new Date().toISOString()}`)
reportLines.push('')
reportLines.push('## Summary')
reportLines.push('')
reportLines.push(`- Pages total: ${pageEntries.length}`)
reportLines.push(`- Sidebar menu points total: ${navEntries.length}`)
reportLines.push(`- Starter cards total: ${cardEntries.length}`)
reportLines.push(`- Missing module files: ${missingModules.length}`)
reportLines.push(`- Missing route links: ${missingRoutes.length}`)
reportLines.push(`- Unassigned pages (not referenced in sidebar modules): ${unassignedPages.length}`)
reportLines.push('')

reportLines.push('## Starter Cards')
reportLines.push('')
for (const card of cardEntries) {
  reportLines.push(`- ${card.id} | ${card.label} | path: \`${card.path}\` | module: \`${card.module ?? '-'}\``)
}
reportLines.push('')

reportLines.push('## Sidebar Menu Points')
reportLines.push('')
for (const entry of navEntries) {
  const indent = '  '.repeat(entry.depth)
  const status = `${entry.fileExists ? 'file:ok' : 'file:missing'}, ${entry.routeLinked ? 'route:ok' : 'route:missing'}`
  reportLines.push(
    `${indent}- ${entry.id} | ${entry.label} | module: \`${entry.module ?? '-'}\` | path: \`${entry.path ?? '-'}\` | ${status}`,
  )
}
reportLines.push('')

reportLines.push('## All Pages')
reportLines.push('')
for (const page of pageEntries) {
  reportLines.push(`- \`${page.pagePath}\` | module: \`${page.moduleSpecifier}\` | assigned: ${page.assignedInNav ? 'yes' : 'no'}`)
}
reportLines.push('')

if (missingModules.length > 0) {
  reportLines.push('## Missing Module Files')
  reportLines.push('')
  for (const entry of missingModules) {
    reportLines.push(`- ${entry.id} | ${entry.module}`)
  }
  reportLines.push('')
}

if (missingRoutes.length > 0) {
  reportLines.push('## Missing Route Links')
  reportLines.push('')
  for (const entry of missingRoutes) {
    reportLines.push(`- ${entry.id} | ${entry.path} | module: ${entry.module ?? '-'}`)
  }
  reportLines.push('')
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true })
fs.writeFileSync(REPORT_PATH, `${reportLines.join('\n')}\n`, 'utf8')
fs.writeFileSync(
  JSON_PATH,
  JSON.stringify(
    {
      summary: {
        pagesTotal: pageEntries.length,
        menuPointsTotal: navEntries.length,
        starterCardsTotal: cardEntries.length,
        missingModules: missingModules.length,
        missingRoutes: missingRoutes.length,
        unassignedPages: unassignedPages.length,
      },
      cards: cardEntries,
      menuPoints: navEntries,
      pages: pageEntries,
      missingModules,
      missingRoutes,
      unassignedPages,
    },
    null,
    2,
  ),
  'utf8',
)

console.log(`Navigation audit written:`)
console.log(`- ${REPORT_PATH}`)
console.log(`- ${JSON_PATH}`)

function buildAliasMap(): Map<string, AliasInfo> {
  const map = new Map<string, AliasInfo>()
  for (const alias of routeAliases.aliases ?? []) {
    const module = normalizeModule(alias.module)
    const current = map.get(module) ?? { paths: new Set<string>(), hasIndex: false }
    if (alias.path) {
      current.paths.add(normalizePath(alias.path))
    }
    if (alias.index) {
      current.hasIndex = true
    }
    map.set(module, current)
  }
  return map
}

function listPages(): PageEntry[] {
  const pageFiles = walkFiles(path.join(SRC_DIR, 'pages'))
    .filter((file) => file.endsWith('.tsx'))
    .map((file) => path.relative(SRC_DIR, file).replaceAll('\\', '/'))
    .sort((a, b) => a.localeCompare(b))

  const moduleSet = new Set<string>()
  for (const nav of collectNavEntries(NAV_SECTIONS)) {
    if (nav.module) {
      moduleSet.add(normalizeModule(nav.module))
    }
  }

  return pageFiles.map((pagePath) => {
    const moduleSpecifier = `@/${pagePath.replace(/\.tsx$/, '')}`
    return {
      pagePath,
      moduleSpecifier,
      assignedInNav: moduleSet.has(moduleSpecifier),
    }
  })
}

function collectCards(sections: NavItem[]): CardEntry[] {
  return sections
    .map((section) => {
      const pathValue = resolveEffectivePath(section)
      if (!pathValue) {
        return null
      }
      return {
        id: section.id,
        label: section.label,
        path: pathValue,
        module: section.module,
        featureKey: section.featureKey,
      }
    })
    .filter((entry): entry is CardEntry => Boolean(entry))
}

function collectNavEntries(items: NavItem[], depth = 0): NavAuditEntry[] {
  const entries: NavAuditEntry[] = []

  for (const item of items) {
    const module = item.module ? normalizeModule(item.module) : undefined
    const resolvedFile = module ? resolveModuleToFile(module) : undefined
    const pathValue = item.path
    const routeLinked = pathValue ? isPathLinked(item) : true

    entries.push({
      id: item.id,
      label: item.label,
      depth,
      module,
      path: pathValue,
      fileExists: Boolean(!module || resolvedFile),
      routeLinked,
    })

    if (item.children && item.children.length > 0) {
      entries.push(...collectNavEntries(item.children, depth + 1))
    }
  }

  return entries
}

function resolveModuleToFile(moduleSpecifier: string): string | undefined {
  const normalized = normalizeModule(moduleSpecifier)
  const relativePath = normalized.replace(/^@\//, '')
  const tsxPath = path.join(SRC_DIR, `${relativePath}.tsx`)
  if (fs.existsSync(tsxPath)) {
    return tsxPath
  }
  const tsPath = path.join(SRC_DIR, `${relativePath}.ts`)
  if (fs.existsSync(tsPath)) {
    return tsPath
  }
  return undefined
}

function normalizeModule(moduleSpecifier: string): string {
  if (moduleSpecifier.startsWith('@/')) {
    return moduleSpecifier
  }
  if (moduleSpecifier.startsWith('./')) {
    return moduleSpecifier.replace('./', '@/')
  }
  if (moduleSpecifier.startsWith('pages/')) {
    return `@/${moduleSpecifier}`
  }
  return moduleSpecifier
}

function normalizePath(routePath: string): string {
  if (!routePath || routePath === '/') {
    return '/'
  }
  return routePath.startsWith('/') ? routePath : `/${routePath}`
}

function defaultPathFromModule(moduleSpecifier: string): string {
  let pathValue = normalizeModule(moduleSpecifier).replace(/^@\//, '')
  if (pathValue.startsWith('pages/')) {
    pathValue = pathValue.slice('pages/'.length)
  }
  if (pathValue.endsWith('/index')) {
    pathValue = pathValue.slice(0, -'/index'.length)
  }
  return normalizePath(pathValue || '/')
}

function isPathLinked(item: NavItem): boolean {
  if (!item.path) {
    return true
  }
  if (!item.module) {
    return true
  }

  const normalizedPath = normalizePath(item.path)
  const defaultPath = defaultPathFromModule(item.module)
  if (normalizedPath === defaultPath) {
    return true
  }

  const aliasInfo = aliasMap.get(normalizeModule(item.module))
  if (!aliasInfo) {
    return false
  }

  if (normalizedPath === '/' && aliasInfo.hasIndex) {
    return true
  }

  return aliasInfo.paths.has(normalizedPath)
}

function resolveEffectivePath(item: NavItem): string | null {
  if (item.path && !item.path.includes(':')) {
    return item.path
  }
  if (!item.children || item.children.length === 0) {
    return null
  }
  for (const child of item.children) {
    const found = resolveEffectivePath(child)
    if (found) {
      return found
    }
  }
  return null
}

function walkFiles(root: string): string[] {
  const results: string[] = []
  const stack: string[] = [root]

  while (stack.length > 0) {
    const current = stack.pop()
    if (!current || !fs.existsSync(current)) {
      continue
    }
    const stat = fs.statSync(current)
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(current)) {
        stack.push(path.join(current, entry))
      }
    } else if (stat.isFile()) {
      results.push(current)
    }
  }

  return results
}
