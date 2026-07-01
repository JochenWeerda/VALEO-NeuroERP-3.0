import type { Locator, Page } from '@playwright/test'

import { assessPageState, type PageRenderState } from './handbuch-page-readiness'

export type QcApproval = 'approved' | 'pending' | 'rejected'

export interface ContentQcMetrics {
  captureSelector: string
  width: number
  height: number
  textLength: number
  headingCount: number
  spinnerCount: number
  clippedCount: number
  substantiveCount: number
}

export interface ContentQcResult {
  renderState: PageRenderState
  approval: QcApproval
  autoPass: boolean
  reviewRequired: boolean
  issues: string[]
  metrics: ContentQcMetrics | null
}

const CAPTURE_SELECTORS = [
  '[data-runtime="native"]',
  '[data-testid*="object-page"]',
  '[data-testid*="mask-"]',
  '.object-page',
  'main [role="tabpanel"]',
  'main form',
  'main section',
  'main',
  '[role="main"]',
]

export async function resolveCaptureLocator(page: Page): Promise<{ locator: Locator; selector: string }> {
  const selector = await page.evaluate((candidates) => {
    const isVisible = (el: Element): boolean => {
      const rect = el.getBoundingClientRect()
      const style = getComputedStyle(el)
      return (
        rect.width > 80 &&
        rect.height > 120 &&
        style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        style.opacity !== '0'
      )
    }

    for (const sel of candidates) {
      const el = document.querySelector(sel)
      if (el && isVisible(el)) return sel
    }
    return 'main'
  }, CAPTURE_SELECTORS)

  return { locator: page.locator(selector).first(), selector }
}

export async function assessContentQuality(page: Page): Promise<ContentQcResult> {
  const renderState = await assessPageState(page)

  if (renderState === 'spinner') {
    return {
      renderState,
      approval: 'rejected',
      autoPass: false,
      reviewRequired: false,
      issues: ['Seite zeigt nur Ladeindikator'],
      metrics: null,
    }
  }
  if (renderState === '404') {
    return {
      renderState,
      approval: 'rejected',
      autoPass: false,
      reviewRequired: false,
      issues: ['404-Seite'],
      metrics: null,
    }
  }
  if (renderState === 'empty') {
    return {
      renderState,
      approval: 'rejected',
      autoPass: false,
      reviewRequired: false,
      issues: ['Kein sichtbarer Hauptinhalt'],
      metrics: null,
    }
  }

  const metrics = await page.evaluate((candidates) => {
    const isVisible = (el: Element): boolean => {
      const rect = el.getBoundingClientRect()
      const style = getComputedStyle(el)
      return (
        rect.width > 80 &&
        rect.height > 120 &&
        style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        style.opacity !== '0'
      )
    }

    let captureEl: Element | null = null
    let captureSelector = 'main'
    for (const sel of candidates) {
      const el = document.querySelector(sel)
      if (el && isVisible(el)) {
        captureEl = el
        captureSelector = sel
        break
      }
    }
    if (!captureEl) {
      captureEl = document.querySelector('main, [role="main"]')
      captureSelector = 'main'
    }
    if (!captureEl) {
      return null
    }

    const rect = captureEl.getBoundingClientRect()
    const text = ((captureEl as HTMLElement).innerText ?? '').replace(/\s+/g, ' ').trim()
    const headingCount = captureEl.querySelectorAll('h1, h2, h3').length

    const spinners = Array.from(
      captureEl.querySelectorAll('.animate-spin, svg.animate-spin, [role="progressbar"], [aria-busy="true"]'),
    ).filter(isVisible)

    const substantiveCount = [
      'table tbody tr',
      'form input',
      'form select',
      'form textarea',
      '[data-testid]',
      'canvas',
      '.recharts-wrapper',
      '[role="tablist"]',
      'button',
    ].reduce((sum, sel) => sum + (captureEl?.querySelectorAll(sel).length ?? 0), 0)

    const viewportH = window.innerHeight
    let clippedCount = 0
    captureEl.querySelectorAll('table, form, section, [role="tabpanel"], .object-page').forEach((el) => {
      const node = el as HTMLElement
      if (!isVisible(node)) return
      const r = node.getBoundingClientRect()
      const overflowY = node.scrollHeight - node.clientHeight
      const nearBottom = r.bottom >= viewportH - 8
      if (overflowY > 24 && nearBottom) clippedCount += 1
    })

    return {
      captureSelector,
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      textLength: text.length,
      headingCount,
      spinnerCount: spinners.length,
      clippedCount,
      substantiveCount,
    }
  }, CAPTURE_SELECTORS)

  if (!metrics) {
    return {
      renderState: 'empty',
      approval: 'rejected',
      autoPass: false,
      reviewRequired: false,
      issues: ['Capture-Ziel nicht gefunden'],
      metrics: null,
    }
  }

  const issues: string[] = []

  if (metrics.width < 280 || metrics.height < 180) {
    issues.push(`Capture-Bereich zu klein (${metrics.width}×${metrics.height})`)
  }
  if (metrics.textLength < 35 && metrics.substantiveCount < 2) {
    issues.push('Zu wenig sichtbarer Maskeninhalt')
  }
  if (metrics.spinnerCount > 0) {
    issues.push('Ladeindikator im Capture-Bereich')
  }
  if (metrics.clippedCount > 0) {
    issues.push(`${metrics.clippedCount} Bereich(e) am unteren Rand abgeschnitten`)
  }

  const reviewRequired = metrics.clippedCount > 0 || metrics.spinnerCount > 0
  const autoPass =
    issues.length === 0 &&
    metrics.width >= 320 &&
    metrics.height >= 200 &&
    (metrics.textLength >= 50 || metrics.substantiveCount >= 2)

  let approval: QcApproval = 'rejected'
  if (autoPass && !reviewRequired) {
    approval = 'approved'
  } else if (issues.length === 0 || (metrics.textLength >= 40 && metrics.spinnerCount === 0)) {
    approval = 'pending'
  }

  return {
    renderState: 'ready',
    approval,
    autoPass,
    reviewRequired,
    issues,
    metrics,
  }
}
