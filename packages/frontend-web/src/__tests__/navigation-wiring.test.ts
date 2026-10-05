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
import { getDocumentEntryPolicy } from '@/lib/workflow/document-entry-policy'

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

  it('exposes article master data where users expect to maintain articles', () => {
    const masterDataSection = findNavItemById(NAV_SECTIONS, 'artikel-stammdaten')
    expect(masterDataSection, 'Artikel-Stammdaten section missing').toBeTruthy()

    const articleMaster = findNavItemById(masterDataSection?.children ?? [], 'artikelstamm')
    expect(articleMaster?.path).toBe('/artikel')
    expect(articleMaster?.module).toBe('@/pages/artikel/liste')

    const newArticle = findNavItemById(masterDataSection?.children ?? [], 'artikel-neu')
    expect(newArticle?.path).toBe('/artikel/neu')
    expect(aliasMap.get('@/pages/artikel/stamm')?.paths.has('artikel/:id')).toBe(true)
    expect(aliasMap.get('@/pages/artikel/stamm')?.paths.has('artikel/neu')).toBe(true)

    const salesArticle = findNavItemById(NAV_SECTIONS, 'artikel')
    expect(salesArticle?.path).toBe('/artikel')
  })

  it('exposes document entry shortcuts with workflow policy routes', () => {
    const outgoingDocuments = findNavItemById(NAV_SECTIONS, 'ausgehende-belege')
    const incomingDocuments = findNavItemById(NAV_SECTIONS, 'eingehende-belege')
    expect(outgoingDocuments, 'Ausgehende Belege section missing').toBeTruthy()
    expect(incomingDocuments, 'Eingehende Belege section missing').toBeTruthy()

    expect(findNavItemById(NAV_SECTIONS, 'ausgehend-lieferschein')?.path).toBe(
      getDocumentEntryPolicy('outgoing-delivery-note').targetRoute,
    )
    expect(findNavItemById(NAV_SECTIONS, 'eingehend-lieferschein')?.path).toBe(
      getDocumentEntryPolicy('incoming-delivery-note').targetRoute,
    )
    expect(findNavItemById(NAV_SECTIONS, 'eingehend-wareneingang')?.path).toBe(
      getDocumentEntryPolicy('incoming-goods-receipt').targetRoute,
    )
    expect(findNavItemById(NAV_SECTIONS, 'eingehend-rechnung')?.path).toBe(
      getDocumentEntryPolicy('incoming-supplier-invoice').targetRoute,
    )

    const immediateDeliveryShortcut = ACTION_SHORTCUTS.find((shortcut) => shortcut.id === 'action-outgoing-delivery-note')
    expect(immediateDeliveryShortcut?.path).toBe('/verkauf/lieferschein-erfassung')
    expect(immediateDeliveryShortcut?.keywords).toContain('sofort-lieferschein')

    const incomingShortcut = ACTION_SHORTCUTS.find((shortcut) => shortcut.id === 'action-incoming-documents')
    expect(incomingShortcut?.keywords).toContain('rechnungseingang')
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

function findNavItemById(items: NavItem[], id: string): NavItem | undefined {
  return collectNavItems(items).find((item) => item.id === id)
}

function resolveModuleToFile(moduleSpecifier: string): string | undefined {
  const normalized = normalizeModule(moduleSpecifier)
  const relativePath = normalized.replace(/^@\//, '')
  const candidates = [
    path.join(SRC_DIR, `${relativePath}.tsx`),
    path.join(SRC_DIR, `${relativePath}.ts`),
    path.join(SRC_DIR, relativePath, 'index.tsx'),
    path.join(SRC_DIR, relativePath, 'index.ts'),
  ]

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate
    }
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
