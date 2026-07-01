/**
 * Handbook screenshot capture — ~832 Endnutzer-Routen mit QC + Zuschnitt auf Maskeninhalt.
 *
 * Nach dem Lauf:
 *   python scripts/handbuch_screenshot_qc.py process
 *   python scripts/handbuch_screenshot_qc.py review-html
 *   python scripts/generate_benutzerhandbuch_full.py
 */
import { test, expect } from '@playwright/test'
import * as fs from 'node:fs'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  imgOutputPaths,
  loadCaptureRoutes,
  type CaptureRoute,
} from './handbuch-screenshot-utils'
import { waitUntilRenderable } from './handbuch-page-readiness'
import {
  assessContentQuality,
  resolveCaptureLocator,
  type ContentQcResult,
  type QcApproval,
} from './handbuch-screenshot-qc'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(__dirname, '../../../..')
const MANIFEST_PATH = path.join(REPO_ROOT, 'docs/benutzerhandbuch/screenshot-manifest.json')
const ROUTES = loadCaptureRoutes()

interface ManifestEntry {
  path: string
  slug: string
  module: string
  status: 'ok' | 'empty' | 'error' | 'skipped' | 'rejected'
  approval: QcApproval
  detail?: string
  qc?: ContentQcResult
  capturedAt?: string
}

function safeUnlink(filePath: string): void {
  try {
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath)
  } catch {
    // non-critical cleanup
  }
}

function loadExistingManifest(): ManifestEntry[] {
  if (!fs.existsSync(MANIFEST_PATH)) return []
  try {
    const data = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8')) as { entries?: ManifestEntry[] }
    return data.entries ?? []
  } catch {
    return []
  }
}

function writeManifest(entries: ManifestEntry[]): void {
  fs.mkdirSync(path.dirname(MANIFEST_PATH), { recursive: true })
  fs.writeFileSync(
    MANIFEST_PATH,
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        routeCount: ROUTES.length,
        policy: {
          crop: 'main-content-element',
          approvalRequired: 'approved-only in handbook',
          reviewHtml: 'docs/benutzerhandbuch/screenshot-review.html',
        },
        entries,
      },
      null,
      2,
    ),
    'utf-8',
  )
}

async function captureRoute(
  page: import('@playwright/test').Page,
  route: CaptureRoute,
  skipExisting: boolean,
): Promise<ManifestEntry> {
  const { png, webp } = imgOutputPaths(REPO_ROOT, route.slug)
  if (skipExisting && fs.existsSync(webp)) {
    return {
      path: route.path,
      slug: route.slug,
      module: route.module,
      status: 'skipped',
      approval: 'approved',
    }
  }

  const url = route.urlPath ? `/${route.urlPath}` : '/'
  try {
    await page.setExtraHTTPHeaders({
      Authorization: 'Bearer dev-token',
      'X-Tenant-ID': '00000000-0000-0000-0000-000000000001',
    })
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45_000 })

    const renderState = await waitUntilRenderable(
      page,
      Number(process.env.HANDBUCH_RENDER_TIMEOUT_MS ?? 45_000),
    )
    if (renderState !== 'ready') {
      safeUnlink(png)
      safeUnlink(webp)
      return {
        path: route.path,
        slug: route.slug,
        module: route.module,
        status: 'rejected',
        approval: 'rejected',
        detail: renderState,
      }
    }

    const qc = await assessContentQuality(page)
    if (qc.approval === 'rejected') {
      safeUnlink(png)
      safeUnlink(webp)
      return {
        path: route.path,
        slug: route.slug,
        module: route.module,
        status: 'rejected',
        approval: 'rejected',
        detail: qc.issues.join('; ') || qc.renderState,
        qc,
      }
    }

    const { locator } = await resolveCaptureLocator(page)
    fs.mkdirSync(path.dirname(png), { recursive: true })
    await locator.screenshot({ path: png, animations: 'disabled', timeout: 30_000 })

    const postQc = await assessContentQuality(page)
    if (postQc.approval === 'rejected' || postQc.metrics?.spinnerCount) {
      safeUnlink(png)
      return {
        path: route.path,
        slug: route.slug,
        module: route.module,
        status: 'rejected',
        approval: 'rejected',
        detail: 'Nach Capture ungeeignet (Spinner/leer)',
        qc: postQc,
      }
    }

    const finalApproval: QcApproval =
      qc.approval === 'approved' && postQc.approval === 'approved' ? 'approved' : 'pending'

    return {
      path: route.path,
      slug: route.slug,
      module: route.module,
      status: 'ok',
      approval: finalApproval,
      qc: { ...qc, approval: finalApproval, issues: [...qc.issues, ...postQc.issues] },
      capturedAt: new Date().toISOString(),
    }
  } catch (error) {
    safeUnlink(png)
    safeUnlink(webp)
    return {
      path: route.path,
      slug: route.slug,
      module: route.module,
      status: 'error',
      approval: 'rejected',
      detail: error instanceof Error ? error.message.slice(0, 200) : String(error),
    }
  }
}

test.describe.configure({ mode: 'serial' })

test('Handbuch-Screenshots für alle App-Routen', async ({ page }) => {
  test.setTimeout(Math.max(ROUTES.length * 15_000, 3_600_000))

  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'dev-token')
    localStorage.setItem('tenant_id', '00000000-0000-0000-0000-000000000001')
  })

  const skipExisting = process.env.HANDBUCH_SKIP_EXISTING !== '0'
  const slugFilter = process.env.HANDBUCH_SLUGS?.split(',').map((s) => s.trim()).filter(Boolean)
  const limit = process.env.HANDBUCH_SCREENSHOT_LIMIT
    ? Number(process.env.HANDBUCH_SCREENSHOT_LIMIT)
    : ROUTES.length

  let batch = ROUTES
  if (slugFilter?.length) {
    const allowed = new Set(slugFilter)
    batch = ROUTES.filter((r) => allowed.has(r.slug))
  }
  batch = batch.slice(0, limit)

  const manifest: ManifestEntry[] = slugFilter?.length
    ? loadExistingManifest().filter((e) => !slugFilter.includes(e.slug))
    : []
  let ok = 0
  let approved = 0
  let pending = 0
  let rejected = 0
  let errors = 0
  let skipped = 0

  for (const [index, route] of batch.entries()) {
    const entry = await captureRoute(page, route, skipExisting)
    manifest.push(entry)
    if (entry.status === 'ok') ok += 1
    if (entry.approval === 'approved') approved += 1
    else if (entry.approval === 'pending') pending += 1
    else if (entry.approval === 'rejected') rejected += 1
    if (entry.status === 'error') errors += 1
    if (entry.status === 'skipped') skipped += 1

    if ((index + 1) % 25 === 0) {
      writeManifest(manifest)
      console.log(
        `[handbuch] ${index + 1}/${batch.length} ok=${ok} approved=${approved} pending=${pending} rejected=${rejected} err=${errors} skip=${skipped}`,
      )
    }
  }

  writeManifest(manifest)
  console.log(
    `[handbuch] done — ok=${ok} approved=${approved} pending=${pending} rejected=${rejected} errors=${errors} skipped=${skipped}`,
  )

  expect(ok + skipped).toBeGreaterThan(0)
})
