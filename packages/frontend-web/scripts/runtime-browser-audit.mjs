#!/usr/bin/env node
import { chromium } from '@playwright/test'
import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const root = join(__dirname, '..')
const routesFile = resolve(root, 'tests/e2e/.generated-routes.json')
const outputDir = resolve(root, '../../artifacts/browser-runtime-audit')
const baseUrl = process.env.FRONTEND_BASE_URL ?? 'http://127.0.0.1:3000'
const routeLimit = Number(process.env.AUDIT_ROUTE_LIMIT ?? 0)
const routeStart = Math.max(0, Number(process.env.AUDIT_ROUTE_START ?? 0))
const routeEnd = Math.max(0, Number(process.env.AUDIT_ROUTE_END ?? 0))
const routePattern = process.env.AUDIT_ROUTE_PATTERN ? new RegExp(process.env.AUDIT_ROUTE_PATTERN) : null
const routeTimeoutMs = Number(process.env.AUDIT_ROUTE_TIMEOUT_MS ?? 20_000)
const slowRouteMs = Number(process.env.AUDIT_SLOW_ROUTE_MS ?? 5_000)
const slowRequestMs = Number(process.env.AUDIT_SLOW_REQUEST_MS ?? 2_000)
const dockerSampleEvery = Math.max(1, Number(process.env.AUDIT_DOCKER_SAMPLE_EVERY ?? 10))
const logMode = process.env.AUDIT_LOG_MODE ?? 'detail'
const dockerNames = (process.env.AUDIT_DOCKER_CONTAINERS ?? [
  'valeo-neuro-erp-frontend',
  'valeo-neuro-erp-bff-web',
  'valeo-neuro-erp-backend',
].join(',')).split(',').map((name) => name.trim()).filter(Boolean)

if (!existsSync(routesFile)) {
  throw new Error(`Route manifest not found: ${routesFile}. Run: node scripts/harvest-routes.mjs`)
}

mkdirSync(outputDir, { recursive: true })

const manifest = JSON.parse(readFileSync(routesFile, 'utf-8'))
let routes = manifest.routes
if (routePattern) routes = routes.filter((route) => routePattern.test(route.path))
if (routeStart > 0 || routeEnd > 0) routes = routes.slice(routeStart, routeEnd > 0 ? routeEnd : undefined)
if (routeLimit > 0) routes = routes.slice(0, routeLimit)

function parsePercent(value) {
  const n = Number(String(value ?? '').replace('%', '').replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

function dockerStats() {
  if (dockerNames.length === 0) return []
  try {
    const out = execFileSync(
      'docker',
      ['stats', '--no-stream', '--format', '{{json .}}', ...dockerNames],
      { encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] },
    )
    return out.trim().split(/\r?\n/).filter(Boolean).map((line) => {
      const row = JSON.parse(line)
      return {
        name: row.Name,
        cpuPercent: parsePercent(row.CPUPerc),
        memUsage: row.MemUsage,
      }
    })
  } catch (error) {
    return [{ name: 'docker-stats-error', cpuPercent: 0, memUsage: String(error.message ?? error) }]
  }
}

function cpuMax(stats) {
  const byContainer = {}
  for (const sample of stats.flat()) {
    if (!sample.name) continue
    byContainer[sample.name] = Math.max(byContainer[sample.name] ?? 0, sample.cpuPercent ?? 0)
  }
  return byContainer
}

function isIgnoredRequest(url, failure = '') {
  return (
    url.includes('fonts.googleapis.com') ||
    url.includes('fonts.gstatic.com') ||
    url.includes('/favicon.ico') ||
    /ERR_ABORTED|aborted/i.test(failure)
  )
}

function classify(result) {
  if (result.error) return result.error.includes('Timeout') ? 'TIMEOUT' : 'NAVIGATION_ERROR'
  if (result.renderError) return 'RENDER_ERROR'
  if (result.pageErrors.length > 0) return 'PAGE_ERROR'
  if (result.consoleErrors.some((msg) => /ReferenceError|TypeError|SyntaxError|Cannot read properties|is not defined/i.test(msg))) {
    return 'CONSOLE_ERROR'
  }
  if (result.badResponses.some((response) => response.status >= 500)) return 'HTTP_5XX'
  if (result.badResponses.some((response) => response.status >= 400)) return 'HTTP_4XX'
  if (result.failedRequests.length > 0) return 'FAILED_REQUEST'
  if (result.durationMs >= slowRouteMs) return 'SLOW_ROUTE'
  return 'OK'
}

async function auditRoute(context, route, routeIndex) {
  const page = await context.newPage()
  const consoleErrors = []
  const consoleWarnings = []
  const pageErrors = []
  const failedRequests = []
  const badResponses = []
  const slowRequests = []
  const requestStarted = new Map()
  const url = new URL(route.path, baseUrl).toString()
  const stats = []
  const sampleCpu = dockerNames.length > 0 && (routeIndex === 0 || (routeIndex + 1) % dockerSampleEvery === 0)

  const onConsole = (msg) => {
    const text = msg.text()
    const item = `${msg.type()}: ${text}`.slice(0, 500)
    if (msg.type() === 'error') consoleErrors.push(item)
    if (msg.type() === 'warning') consoleWarnings.push(item)
  }
  const onPageError = (error) => pageErrors.push(String(error.message ?? error).slice(0, 500))
  const onRequest = (request) => requestStarted.set(request, Date.now())
  const onRequestFinished = (request) => {
    const start = requestStarted.get(request)
    if (!start) return
    const duration = Date.now() - start
    if (duration >= slowRequestMs) {
      slowRequests.push({
        method: request.method(),
        url: request.url().slice(0, 300),
        durationMs: duration,
      })
    }
    requestStarted.delete(request)
  }
  const onRequestFailed = (request) => {
    const failure = request.failure()?.errorText ?? 'unknown'
    if (isIgnoredRequest(request.url(), failure)) return
    failedRequests.push({
      method: request.method(),
      url: request.url().slice(0, 300),
      failure,
    })
    requestStarted.delete(request)
  }
  const onResponse = (response) => {
    const status = response.status()
    const responseUrl = response.url()
    if (status < 400 || isIgnoredRequest(responseUrl)) return
    badResponses.push({
      status,
      url: responseUrl.slice(0, 300),
    })
  }

  page.on('console', onConsole)
  page.on('pageerror', onPageError)
  page.on('request', onRequest)
  page.on('requestfinished', onRequestFinished)
  page.on('requestfailed', onRequestFailed)
  page.on('response', onResponse)

  if (sampleCpu) stats.push(dockerStats())
  const started = Date.now()
  let status = null
  let error = null
  let renderError = false
  let title = ''
  let h1 = ''
  let perf = {}

  try {
    await page.evaluate(() => performance.clearResourceTimings()).catch(() => undefined)
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: routeTimeoutMs })
    status = response?.status() ?? null
    await page.waitForTimeout(500)
    renderError = (await page.getByText(/Fehler beim Laden der Seite|Die Seite konnte nicht gerendert werden/i).count()) > 0
    title = await page.title().catch(() => '')
    h1 = await page.locator('h1').first().textContent({ timeout: 1000 }).catch(() => '')
    perf = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0]
      const resources = performance.getEntriesByType('resource')
      const slowResources = resources
        .filter((entry) => entry.duration >= 2000)
        .slice(0, 10)
        .map((entry) => ({
          name: entry.name.slice(0, 300),
          durationMs: Math.round(entry.duration),
          initiatorType: entry.initiatorType,
        }))
      return {
        domContentLoadedMs: nav ? Math.round(nav.domContentLoadedEventEnd) : null,
        loadEventMs: nav ? Math.round(nav.loadEventEnd) : null,
        transferSize: resources.reduce((sum, entry) => sum + (entry.transferSize || 0), 0),
        resourceCount: resources.length,
        slowResources,
      }
    }).catch(() => ({}))
  } catch (err) {
    error = String(err?.message ?? err).slice(0, 500)
  }

  const durationMs = Date.now() - started
  if (sampleCpu) stats.push(dockerStats())
  page.off('console', onConsole)
  page.off('pageerror', onPageError)
  page.off('request', onRequest)
  page.off('requestfinished', onRequestFinished)
  page.off('requestfailed', onRequestFailed)
  page.off('response', onResponse)
  await page.close().catch(() => undefined)

  const filteredConsoleErrors = consoleErrors.filter(
    (msg) =>
      !msg.includes('fonts.googleapis.com') &&
      !msg.includes('fonts.gstatic.com') &&
      !msg.includes('favicon.ico') &&
      !msg.includes('net::ERR_ABORTED'),
  )

  const result = {
    path: route.path,
    source: route.source,
    status,
    title,
    h1: h1?.trim() ?? '',
    durationMs,
    category: 'OK',
    error,
    renderError,
    consoleErrors: filteredConsoleErrors,
    consoleWarnings,
    pageErrors,
    badResponses,
    failedRequests,
    slowRequests,
    performance: perf,
    cpuMaxPercent: cpuMax(stats),
  }
  result.category = classify(result)
  return result
}

function summarize(results) {
  const byCategory = {}
  for (const result of results) byCategory[result.category] = (byCategory[result.category] ?? 0) + 1
  const slowest = [...results].sort((a, b) => b.durationMs - a.durationMs).slice(0, 25)
  const failed = results.filter((result) => result.category !== 'OK')
  const cpuObservedMaxPercent = cpuMax(results.map((result) => (
    Object.entries(result.cpuMaxPercent ?? {}).map(([name, cpuPercent]) => ({ name, cpuPercent }))
  )))
  return {
    generatedAt: new Date().toISOString(),
    baseUrl,
    dockerSampleEvery,
    totalRoutes: results.length,
    byCategory,
    failedCount: failed.length,
    cpuObservedMaxPercent,
    slowest,
    failures: failed,
  }
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  ignoreHTTPSErrors: true,
})
const results = []

for (let i = 0; i < routes.length; i += 1) {
  const route = routes[i]
  const result = await auditRoute(context, route, i)
  results.push(result)
  const marker = result.category === 'OK' ? 'OK' : 'ISSUE'
  if (logMode !== 'summary' || result.category !== 'OK') {
    console.log(`${String(i + 1).padStart(4, ' ')}/${routes.length} ${marker} ${result.category} ${result.durationMs}ms ${route.path}`)
  } else if ((i + 1) % 50 === 0 || i + 1 === routes.length) {
    console.log(`${String(i + 1).padStart(4, ' ')}/${routes.length} OK`)
  }
}

await browser.close()

const report = summarize(results)
const jsonPath = join(outputDir, 'runtime-browser-audit.json')
const mdPath = join(outputDir, 'runtime-browser-audit.md')
writeFileSync(jsonPath, JSON.stringify(report, null, 2), 'utf-8')
writeFileSync(
  mdPath,
  [
    '# Browser Runtime Audit',
    '',
    `- Base URL: ${report.baseUrl}`,
    `- Generated: ${report.generatedAt}`,
    `- Routes: ${report.totalRoutes}`,
    `- Failures: ${report.failedCount}`,
    `- Docker CPU sample interval: every ${report.dockerSampleEvery} route(s)`,
    '',
    '## Categories',
    '',
    ...Object.entries(report.byCategory)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, value]) => `- ${key}: ${value}`),
    '',
    '## CPU Observed Max',
    '',
    ...Object.entries(report.cpuObservedMaxPercent)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, value]) => `- ${key}: ${value}%`),
    '',
    '## Slowest Routes',
    '',
    ...report.slowest.map((r) => `- ${r.durationMs}ms ${r.category} ${r.path}`),
    '',
    '## Failures',
    '',
    ...report.failures.slice(0, 100).map((r) => `- ${r.category} ${r.durationMs}ms ${r.path}: ${r.error ?? r.consoleErrors[0] ?? r.failedRequests[0]?.failure ?? ''}`),
    '',
  ].join('\n'),
  'utf-8',
)

console.log(`Wrote ${jsonPath}`)
console.log(`Wrote ${mdPath}`)
