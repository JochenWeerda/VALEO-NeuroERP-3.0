#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { basename, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = join(__dirname, '..')
const SRC = join(ROOT, 'src')
const PAGES_DIR = join(SRC, 'pages')
const ROUTE_ALIASES_FILE = join(SRC, 'app', 'route-aliases.json')
const PAGE_MODULE_LOADER_FILE = join(SRC, 'app', 'page-module-loader.ts')
const PAGE_MODULE_GROUPS_DIR = join(SRC, 'app', 'page-module-groups')
const AUTO_GROUPS_DIR = join(SRC, 'app', 'route-builders', 'auto-groups', 'generated')
const ALIAS_GROUPS_DIR = join(SRC, 'app', 'route-builders', 'alias-groups', 'generated')

const IGNORE_PAGE_PATTERNS = [/__tests__/, /\.spec\.tsx$/, /\.test\.tsx$/, /\.stories\.tsx$/]

function walk(dir) {
  const files = []
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry)
    const stat = statSync(fullPath)
    if (stat.isDirectory()) {
      files.push(...walk(fullPath))
      continue
    }
    if (!fullPath.endsWith('.tsx')) continue
    if (IGNORE_PAGE_PATTERNS.some((pattern) => pattern.test(fullPath))) continue
    files.push(fullPath)
  }
  return files
}

function normalizeSlashes(value) {
  return value.replace(/\\/g, '/')
}

function pageFileToModule(filePath) {
  const relativePath = normalizeSlashes(relative(PAGES_DIR, filePath)).replace(/\.tsx$/, '')
  return `@/pages/${relativePath}`
}

function pageFileToModuleKey(filePath) {
  return `../../pages/${normalizeSlashes(relative(PAGES_DIR, filePath))}`
}

function extractQuotedValues(text) {
  return [...text.matchAll(/'([^']+)'/g)].map((match) => match[1])
}

function extractGroupByPrefix(text) {
  const map = new Map()
  const recordMatch = text.match(/const GROUP_BY_PREFIX: Record<string, PageModuleGroupName> = \{([\s\S]*?)\n\}/)
  if (!recordMatch) {
    throw new Error('Could not parse GROUP_BY_PREFIX from page-module-loader.ts')
  }
  for (const line of recordMatch[1].split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('//')) continue
    const match = trimmed.match(/^(?:'([^']+)'|([A-Za-z0-9_-]+)):\s*'([^']+)'/)
    if (!match) continue
    const key = match[1] ?? match[2]
    const value = match[3]
    map.set(key, value)
  }
  return map
}

function extractGroupPatterns(groupFilePath) {
  const text = readFileSync(groupFilePath, 'utf-8')
  return extractQuotedValues(text).filter((value) => value.startsWith('../../pages/'))
}

function globToRegExp(globPattern) {
  let pattern = ''

  for (let index = 0; index < globPattern.length; index += 1) {
    const char = globPattern[index]
    const next = globPattern[index + 1]
    const nextNext = globPattern[index + 2]

    if (char === '*' && next === '*' && nextNext === '/') {
      pattern += '(?:.*/)?'
      index += 2
      continue
    }

    if (char === '*' && next === '*') {
      pattern += '.*'
      index += 1
      continue
    }

    if (char === '*') {
      pattern += '[^/]*'
      continue
    }

    if (/[.+^${}()|[\]\\]/.test(char)) {
      pattern += `\\${char}`
      continue
    }

    pattern += char
  }

  return new RegExp(`^${pattern}$`)
}

function parseGeneratedEntries(filePath) {
  const text = readFileSync(filePath, 'utf-8')
  const entries = []
  for (const block of text.matchAll(/\{[\s\S]*?"module":\s*"([^"]+)"[\s\S]*?"path":\s*"([^"]*)"[\s\S]*?\}/g)) {
    entries.push({ module: block[1], path: block[2], source: basename(filePath) })
  }
  return entries
}

function resolveModuleCandidates(modulePath) {
  const normalized = modulePath.replace(/^@\//, '')
  return [
    join(SRC, `${normalized}.tsx`),
    join(SRC, normalized, 'index.tsx'),
  ]
}

function moduleExists(modulePath) {
  return resolveModuleCandidates(modulePath).some((candidate) => {
    try {
      return statSync(candidate).isFile()
    } catch {
      return false
    }
  })
}

function resolveModuleKey(modulePath) {
  let resolved = modulePath.replace(/^@\//, '../../')
  if (!resolved.startsWith('../../')) {
    resolved = `../../${resolved.replace(/^\.\.\//, '')}`
  }
  if (!resolved.endsWith('.tsx')) {
    resolved = `${resolved}.tsx`
  }
  return resolved
}

function modulePrefix(modulePath) {
  const normalized = modulePath.replace(/^@\//, '').replace(/^pages\//, '')
  return normalized.split('/')[0] ?? normalized
}

function listGeneratedEntries(dir) {
  return readdirSync(dir)
    .filter((name) => name.endsWith('.ts'))
    .flatMap((name) => parseGeneratedEntries(join(dir, name)))
}

const pageFiles = walk(PAGES_DIR)
const knownModules = new Set(pageFiles.map(pageFileToModule))
const knownModuleKeys = new Set(pageFiles.map(pageFileToModuleKey))
const aliases = JSON.parse(readFileSync(ROUTE_ALIASES_FILE, 'utf-8')).aliases ?? []
const loaderText = readFileSync(PAGE_MODULE_LOADER_FILE, 'utf-8')
const groupByPrefix = extractGroupByPrefix(loaderText)

const groupPatterns = new Map(
  readdirSync(PAGE_MODULE_GROUPS_DIR)
    .filter((name) => name.endsWith('.ts') && name !== 'types.ts')
    .map((name) => [basename(name, '.ts'), extractGroupPatterns(join(PAGE_MODULE_GROUPS_DIR, name))]),
)

const generatedEntries = [
  ...listGeneratedEntries(AUTO_GROUPS_DIR),
  ...listGeneratedEntries(ALIAS_GROUPS_DIR),
]

const issues = []

for (const alias of aliases) {
  if (!alias.module?.startsWith('@/pages/')) continue
  if (!moduleExists(alias.module)) {
    issues.push(`Alias references missing page module: ${alias.module} (${alias.path ?? 'index'})`)
  }
}

for (const entry of generatedEntries) {
  if (!entry.module.startsWith('@/pages/')) continue

  if (!knownModules.has(entry.module) && !moduleExists(entry.module)) {
    issues.push(`Generated route entry references unknown page module: ${entry.module} (${entry.source})`)
    continue
  }

  const prefix = modulePrefix(entry.module)
  const groupName = groupByPrefix.get(prefix)
  if (!groupName) {
    issues.push(`No page-module group mapping for prefix '${prefix}' (${entry.module})`)
    continue
  }

  const moduleKey = resolveModuleKey(entry.module)
  const patterns = groupPatterns.get(groupName) ?? []
  const matchesPattern = patterns.some((pattern) => globToRegExp(pattern).test(moduleKey))
  if (!matchesPattern) {
    issues.push(`Page module group '${groupName}' does not cover ${entry.module} -> ${moduleKey}`)
  }

  if (!knownModuleKeys.has(moduleKey)) {
    const candidates = resolveModuleCandidates(entry.module)
    const hasIndexRoute = candidates.some((candidate) => {
      try {
        return statSync(candidate).isFile()
      } catch {
        return false
      }
    })
    if (!hasIndexRoute) {
      issues.push(`Resolved module key does not map to a known page file: ${entry.module} -> ${moduleKey}`)
    }
  }
}

const portalAliases = aliases.filter((alias) => alias.module?.startsWith('@/pages/portal/'))
const portalPages = pageFiles
  .filter((filePath) => normalizeSlashes(relative(PAGES_DIR, filePath)).startsWith('portal/'))
  .map(pageFileToModule)
const portalAliasModules = new Set(portalAliases.map((alias) => alias.module))

for (const modulePath of portalPages) {
  if (!portalAliasModules.has(modulePath)) {
    issues.push(`Portal page is missing alias entry: ${modulePath}`)
  }
}

if (issues.length > 0) {
  console.error(`Routing integrity check failed with ${issues.length} issue(s):`)
  for (const issue of issues) {
    console.error(`- ${issue}`)
  }
  process.exit(1)
}

console.log('Routing integrity check passed.')
console.log(`- page modules: ${knownModules.size}`)
console.log(`- aliases: ${aliases.length}`)
console.log(`- generated route entries: ${generatedEntries.length}`)
console.log(`- portal aliases: ${portalAliases.length}`)
