#!/usr/bin/env node
/**
 * Route-Harvester: Sammelt testbare Routen aus derselben Konfiguration wie AppRouteRuntime
 * (route-aliases.json + auto-groups/generated + alias-groups/generated).
 * Kein Dateisystem-Walk unter src/pages — verhindert 404 durch Chart-/Hilfs-Komponenten-Pfade.
 *
 * Usage:  node scripts/harvest-routes.mjs
 * Output: tests/e2e/.generated-routes.json
 */
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join, basename } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = join(__dirname, '..')
const ALIASES_FILE = join(ROOT, 'src', 'app', 'route-aliases.json')
const AUTO_GEN = join(ROOT, 'src', 'app', 'route-builders', 'auto-groups', 'generated')
const ALIAS_GEN = join(ROOT, 'src', 'app', 'route-builders', 'alias-groups', 'generated')
const OUTPUT = join(ROOT, 'tests', 'e2e', '.generated-routes.json')
const ENV_FILE = join(ROOT, '.env')

/** Ersetzt :param durch test-123 (wie bisher im Smoke). */
function toConcretePath(path) {
  return path.replace(/:[\w]+/g, 'test-123')
}

/** Einheitlich mit führendem Slash, ohne doppelte Slashes. */
function normalizeUrlPath(p) {
  const trimmed = p.replace(/^\/+/, '').replace(/\/+$/, '')
  if (!trimmed) return '/'
  const withSlashes = '/' + trimmed.replace(/\/+/g, '/')
  return toConcretePath(withSlashes)
}

function loadProspectingEnabled() {
  if (!existsSync(ENV_FILE)) return false
  try {
    const raw = readFileSync(ENV_FILE, 'utf-8')
    const m = raw.match(/^\s*VITE_ENABLE_PROSPECTING_UI\s*=\s*(\S+)/m)
    return m ? m[1] === 'true' : false
  } catch {
    return false
  }
}

const PROSPECTING_ENABLED = loadProspectingEnabled()

function skipProspectingModule(modulePath) {
  if (PROSPECTING_ENABLED) return false
  return typeof modulePath === 'string' && modulePath.includes('/prospecting/')
}

const seen = new Map() // path -> { source, original? }

function addRoute(pathKey, meta) {
  if (seen.has(pathKey)) return
  seen.set(pathKey, meta)
}

// ── 1) route-aliases.json (globale Aliase, vollständige Pfade ohne führenden Slash in JSON) ──
const aliasData = JSON.parse(readFileSync(ALIASES_FILE, 'utf-8'))
for (const a of aliasData.aliases || []) {
  if (!a.path || skipProspectingModule(a.module)) continue
  const pathKey = normalizeUrlPath(a.path)
  const original = /:[\w]+/.test(a.path) ? `alias:${a.path}` : undefined
  addRoute(pathKey, { source: 'alias-json', original })
}

// ── 2) Generierte Gruppen (Prefix = Dateiname ohne .ts) ──
const entryRe = /\{\s*"module":\s*"([^"]+)",\s*"path":\s*"([^"]*)"\s*\}/g

function harvestGeneratedDir(dir, label) {
  if (!existsSync(dir)) return
  for (const file of readdirSync(dir).filter((f) => f.endsWith('.ts'))) {
    const prefix = basename(file, '.ts')
    const content = readFileSync(join(dir, file), 'utf-8')
    let m
    entryRe.lastIndex = 0
    while ((m = entryRe.exec(content)) !== null) {
      const modulePath = m[1]
      const rel = m[2]
      if (skipProspectingModule(modulePath)) continue

      let full
      if (rel === '' || rel === undefined) {
        full = `/${prefix}`
      } else {
        full = `/${prefix}/${rel}`.replace(/\/+/g, '/')
      }
      const pathKey = normalizeUrlPath(full)
      const original =
        /:[\w]+/.test(rel) || /:[\w]+/.test(prefix) ? `${label}:${prefix}/${rel}` : undefined
      addRoute(pathKey, { source: label, original })
    }
  }
}

harvestGeneratedDir(AUTO_GEN, 'auto-group')
harvestGeneratedDir(ALIAS_GEN, 'alias-group')

// ── 3) Explizit: Startseite (nicht immer als Datei-Prefix abgebildet) ──
addRoute('/', { source: 'explicit' })

// ── Filter: Smoke-Regeln wie zuvor ──
const skipPrefixes = [
  (p) => p.includes('/auth/') || p === '/login' || p === '/auth/login',
  (p) => p.startsWith('/portal/'),
  (p) => p.startsWith('/errors/'),
  (p) => p === '/public/verify',
]

const testableRoutes = []
for (const [pathKey, meta] of seen) {
  if (skipPrefixes.some((fn) => fn(pathKey))) continue
  const entry = { path: pathKey, source: meta.source }
  if (meta.original) entry.original = meta.original
  testableRoutes.push(entry)
}

testableRoutes.sort((a, b) => a.path.localeCompare(b.path))

const manifest = {
  generatedAt: new Date().toISOString(),
  totalRoutes: testableRoutes.length,
  routes: testableRoutes,
}

writeFileSync(OUTPUT, JSON.stringify(manifest, null, 2), 'utf-8')
console.log(`Harvested ${testableRoutes.length} testable routes (runtime-aligned) → ${OUTPUT}`)
