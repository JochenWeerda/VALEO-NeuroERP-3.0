import fs from 'node:fs'
import path from 'node:path'
import { chromium } from 'playwright'
import { ACTION_SHORTCUTS, NAV_LINKS } from '../src/app/navigation/manifest'

type RouteResult = {
  path: string
  ok: boolean
  title: string
  consoleErrors: string[]
  failedRequests: string[]
  mockHints: string[]
}

const BASE_URL = process.env.AUDIT_BASE_URL ?? 'http://localhost:3000'
const OUTPUT_DIR = path.resolve(process.cwd(), 'artifacts')
const OUTPUT_JSON = path.join(OUTPUT_DIR, 'route-click-audit.json')
const OUTPUT_MD = path.join(OUTPUT_DIR, 'route-click-audit.md')

const MOCK_PATTERNS = [
  /\bmock\b/i,
  /\bplaceholder\b/i,
  /\bcoming soon\b/i,
  /\bnot implemented\b/i,
  /\btodo\b/i,
  /\bfallback\b/i,
  /\bdemo data\b/i,
]

const routes = collectRoutes()

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage()

const results: RouteResult[] = []

for (const routePath of routes) {
  const consoleErrors: string[] = []
  const failedRequests: string[] = []

  page.removeAllListeners('console')
  page.removeAllListeners('requestfailed')
  page.removeAllListeners('response')

  page.on('console', (message) => {
    if (message.type() === 'error') {
      consoleErrors.push(message.text())
    }
  })
  page.on('requestfailed', (request) => {
    const reason = request.failure()?.errorText ?? 'failed'
    const url = request.url()
    if (reason.includes('ERR_ABORTED')) {
      return
    }
    if (url.includes('/api/events?stream=')) {
      return
    }
    failedRequests.push(`${request.method()} ${url} :: ${reason}`)
  })
  page.on('response', (response) => {
    if (response.status() >= 400) {
      failedRequests.push(`${response.status()} ${response.url()}`)
    }
  })

  const url = `${BASE_URL}${routePath}`
  let ok = true
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 })
    await page.waitForTimeout(250)
  } catch (error) {
    ok = false
    consoleErrors.push(`Navigation failed: ${String(error)}`)
  }

  const title = await page.title().catch(() => '')
  const bodyText = await page.textContent('body').catch(() => '') ?? ''
  const mockHints = MOCK_PATTERNS.filter((pattern) => pattern.test(bodyText)).map((pattern) => pattern.source)

  const criticalConsoleErrors = consoleErrors.filter((entry) => !entry.includes('[vite]'))
  if (criticalConsoleErrors.length > 0 || failedRequests.length > 0) {
    ok = false
  }

  results.push({
    path: routePath,
    ok,
    title,
    consoleErrors: unique(criticalConsoleErrors),
    failedRequests: unique(failedRequests),
    mockHints: unique(mockHints),
  })
}

await browser.close()

const failed = results.filter((entry) => !entry.ok)
const withMocks = results.filter((entry) => entry.mockHints.length > 0)

const markdown: string[] = []
markdown.push('# Route Click Audit')
markdown.push('')
markdown.push(`Base URL: ${BASE_URL}`)
markdown.push(`Routes checked: ${results.length}`)
markdown.push(`Failed routes: ${failed.length}`)
markdown.push(`Mock-hint routes: ${withMocks.length}`)
markdown.push('')
markdown.push('## Results')
markdown.push('')
for (const result of results) {
  markdown.push(`- ${result.ok ? 'OK' : 'FAIL'} \`${result.path}\` | title: ${result.title || '-'} | mocks: ${result.mockHints.length}`)
}
markdown.push('')

if (failed.length > 0) {
  markdown.push('## Failed Details')
  markdown.push('')
  for (const entry of failed) {
    markdown.push(`### ${entry.path}`)
    if (entry.consoleErrors.length > 0) {
      markdown.push('- Console errors:')
      for (const message of entry.consoleErrors.slice(0, 10)) {
        markdown.push(`  - ${message}`)
      }
    }
    if (entry.failedRequests.length > 0) {
      markdown.push('- Failed requests:')
      for (const message of entry.failedRequests.slice(0, 10)) {
        markdown.push(`  - ${message}`)
      }
    }
    markdown.push('')
  }
}

if (withMocks.length > 0) {
  markdown.push('## Mock Hints')
  markdown.push('')
  for (const entry of withMocks) {
    markdown.push(`- \`${entry.path}\` -> ${entry.mockHints.join(', ')}`)
  }
  markdown.push('')
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true })
fs.writeFileSync(OUTPUT_JSON, JSON.stringify({ baseUrl: BASE_URL, results }, null, 2), 'utf8')
fs.writeFileSync(OUTPUT_MD, `${markdown.join('\n')}\n`, 'utf8')

console.log(`Route click audit written:`)
console.log(`- ${OUTPUT_MD}`)
console.log(`- ${OUTPUT_JSON}`)

function collectRoutes(): string[] {
  const routeSet = new Set<string>()
  for (const entry of NAV_LINKS) {
    if (!entry.path || entry.path.includes(':')) {
      continue
    }
    routeSet.add(normalizePath(entry.path))
  }
  for (const shortcut of ACTION_SHORTCUTS) {
    if (!shortcut.path || shortcut.path.includes(':')) {
      continue
    }
    routeSet.add(normalizePath(shortcut.path))
  }
  return [...routeSet].sort((a, b) => a.localeCompare(b))
}

function normalizePath(routePath: string): string {
  if (!routePath || routePath === '/') {
    return '/'
  }
  return routePath.startsWith('/') ? routePath : `/${routePath}`
}

function unique(values: string[]): string[] {
  return [...new Set(values)]
}
