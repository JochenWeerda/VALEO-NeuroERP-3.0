#!/usr/bin/env node
/**
 * Route-Harvester: Extrahiert ALLE testbaren Routen aus dem Dateisystem
 * und route-aliases.json. Gibt eine JSON-Datei aus, die der Smoke-Test konsumiert.
 *
 * Usage:  node scripts/harvest-routes.mjs
 * Output: tests/e2e/.generated-routes.json
 */
import { readdirSync, statSync, writeFileSync, readFileSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = join(__dirname, '..')
const PAGES_DIR = join(ROOT, 'src', 'pages')
const ALIASES_FILE = join(ROOT, 'src', 'app', 'route-aliases.json')
const OUTPUT = join(ROOT, 'tests', 'e2e', '.generated-routes.json')

const IGNORE = [/__tests__/, /\.spec\.tsx$/, /\.test\.tsx$/, /\.stories\.tsx$/]
const SKIP_PARAM_ROUTES = /:[\w]+/

function walkDir(dir) {
  const results = []
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) {
      results.push(...walkDir(full))
    } else if (full.endsWith('.tsx') && !IGNORE.some((p) => p.test(full))) {
      results.push(full)
    }
  }
  return results
}

function fileToRoute(filePath) {
  let rel = relative(PAGES_DIR, filePath).replace(/\\/g, '/').replace(/\.tsx$/, '')
  if (rel.endsWith('/index')) rel = rel.slice(0, -6)
  if (rel === 'index' || rel === '') return '/'
  return '/' + rel
}

// 1) Filesystem-Routen
const fsRoutes = walkDir(PAGES_DIR).map(fileToRoute)

// 2) Alias-Routen
const aliasData = JSON.parse(readFileSync(ALIASES_FILE, 'utf-8'))
const aliasRoutes = (aliasData.aliases || [])
  .filter((a) => a.path)
  .map((a) => (a.path.startsWith('/') ? a.path : '/' + a.path))

// 3) Zusammenführen, deduplizieren, Param-Routen mit Dummy-Werten füllen
const allPaths = new Set([...fsRoutes, ...aliasRoutes])

const testableRoutes = []
for (const p of allPaths) {
  if (p.includes('/auth/') || p === '/login' || p === '/auth/login') continue
  if (p.startsWith('/portal/')) continue
  if (p.startsWith('/errors/')) continue
  if (p === '/public/verify') continue

  if (SKIP_PARAM_ROUTES.test(p)) {
    const concrete = p.replace(/:[\w]+/g, 'test-123')
    testableRoutes.push({ path: concrete, source: 'param', original: p })
  } else {
    testableRoutes.push({ path: p, source: 'static' })
  }
}

testableRoutes.sort((a, b) => a.path.localeCompare(b.path))

const manifest = {
  generatedAt: new Date().toISOString(),
  totalRoutes: testableRoutes.length,
  routes: testableRoutes,
}

writeFileSync(OUTPUT, JSON.stringify(manifest, null, 2), 'utf-8')
console.log(`Harvested ${testableRoutes.length} testable routes → ${OUTPUT}`)
