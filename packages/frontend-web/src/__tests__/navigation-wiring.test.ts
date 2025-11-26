import { describe, it, expect } from 'vitest'
import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'
import routeAliases from '@/app/route-aliases.json'
import {
  NAV_SECTIONS,
  NAV_LINKS,
  ACTION_SHORTCUTS,
  AI_SHORTCUTS,
  type NavItem,
} from '@/app/navigation/manifest'

type AliasInfo = { paths: Set<string>; hasIndex: boolean }

const aliasMap = buildAliasMap()
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const SRC_DIR = path.resolve(__dirname, '..')

describe('navigation wiring', () => {
  it('every sidebar item references an existing module file', () => {
    for (const item of collectNavItems(NAV_SECTIONS)) {
      if (!item.module) {
        continue
      }
      const resolvedPath = resolveModuleToFile(item.module)
      expect(resolvedPath, `Module ${item.module} not found on disk`).toBeTruthy()
    }
  })

  it('sidebar routes have matching router entries (default or alias)', () => {
    for (const link of NAV_LINKS) {
      if (!link.module || !link.path) {
        continue
      }
      const normalized = normalizePath(link.path)
      const defaultPath = normalizePath(defaultPathFromModule(link.module))
      if (normalized === defaultPath) {
        continue
      }
      const aliasInfo = aliasMap.get(normalizeModule(link.module))
      if (normalized === '' || normalized === '/') {
        expect(aliasInfo?.hasIndex).toBe(true)
        continue
      }
      expect(aliasInfo?.paths.has(normalized)).toBe(true)
    }
  })

  it('command palette shortcuts resolve to valid routes', () => {
    for (const shortcut of ACTION_SHORTCUTS) {
      const normalized = normalizePath(shortcut.path)
      expect(normalized.length).toBeGreaterThan(0)
    }
    for (const shortcut of AI_SHORTCUTS) {
      if (shortcut.type === 'navigate') {
        const normalized = normalizePath(shortcut.path)
        expect(normalized.length).toBeGreaterThan(0)
      }
    }
  })
})

function collectNavItems(items: NavItem[]): NavItem[] {
  const result: NavItem[] = []
  const stack = [...items]
  while (stack.length) {
    const current = stack.pop()
    if (!current) continue
    result.push(current)
    if (current.children) {
      stack.push(...current.children)
    }
  }
  return result
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

function defaultPathFromModule(moduleSpecifier: string): string {
  let relative = normalizeModule(moduleSpecifier).replace(/^@\//, '')
  if (relative.startsWith('pages/')) {
    relative = relative.slice('pages/'.length)
  }
  if (relative.endsWith('/index')) {
    relative = relative.slice(0, -'/index'.length)
  }
  return relative || '/'
}

function normalizePath(routePath: string): string {
  if (!routePath) {
    return ''
  }
  if (routePath === '/') {
    return '/'
  }
  return routePath.startsWith('/') ? routePath.slice(1) : routePath
}

function buildAliasMap(): Map<string, AliasInfo> {
  const map = new Map<string, AliasInfo>()
  for (const alias of routeAliases.aliases ?? []) {
    const module = normalizeModule(alias.module)
    const entry = map.get(module) ?? { paths: new Set<string>(), hasIndex: false }
    if (alias.path) {
      entry.paths.add(normalizePath(alias.path))
    }
    if (alias.index) {
      entry.hasIndex = true
    }
    map.set(module, entry)
  }
  return map
}
