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
  '[data-page-surface]',
  '[data-testid*="object-page"]',
  '[data-testid*="mask-"]',
  '.object-page',
  'main [role="tabpanel"]',
  'main form',
  'main > div',
  'main',
  '[role="main"]',
  '.min-h-screen [class*="max-w-md"]',
  '.min-h-screen [class*="Card"]',
  'main section',
  '.min-h-screen',
]

const MIN_CAPTURE_W = 280
const MIN_CAPTURE_H = 150

export async function resolveCaptureLocator(page: Page): Promise<{ locator: Locator; selector: string }> {
  const selector = await page.evaluate(
    ({ candidates, minW, minH }) => {
      const isVisible = (el: Element): boolean => {
        const rect = el.getBoundingClientRect()
        const style = getComputedStyle(el)
        return (
          rect.width > 80 &&
          rect.height > 80 &&
          style.visibility !== 'hidden' &&
          style.display !== 'none' &&
          style.opacity !== '0'
        )
      }

      type Scored = { selector: string; area: number; height: number; priority: number }
      const scored: Scored[] = []
      const seen = new Set<Element>()

      for (let i = 0; i < candidates.length; i += 1) {
        const sel = candidates[i]
        document.querySelectorAll(sel).forEach((el) => {
          if (!isVisible(el) || seen.has(el)) return
          seen.add(el)
          const rect = el.getBoundingClientRect()
          scored.push({
            selector: sel,
            area: rect.width * rect.height,
            height: rect.height,
            priority: candidates.length - i,
          })
        })
      }

      if (scored.length === 0) return 'main'

      scored.sort((a, b) => {
        const aOk = a.height >= minH ? 1 : 0
        const bOk = b.height >= minH ? 1 : 0
        if (aOk !== bOk) return bOk - aOk
        if (a.priority !== b.priority) return b.priority - a.priority
        return b.area - a.area
      })

      return scored[0]?.selector ?? 'main'
    },
    { candidates: CAPTURE_SELECTORS, minW: MIN_CAPTURE_W, minH: MIN_CAPTURE_H },
  )

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

  const metrics = await page.evaluate(
    ({ candidates, minW, minH }) => {
      const isVisible = (el: Element): boolean => {
        const rect = el.getBoundingClientRect()
        const style = getComputedStyle(el)
        return (
          rect.width > 80 &&
          rect.height > 80 &&
          style.visibility !== 'hidden' &&
          style.display !== 'none' &&
          style.opacity !== '0'
        )
      }

      type Scored = { el: Element; selector: string; area: number; height: number; priority: number }
      const scored: Scored[] = []
      const seen = new Set<Element>()

      for (let i = 0; i < candidates.length; i += 1) {
        const sel = candidates[i]
        document.querySelectorAll(sel).forEach((el) => {
          if (!isVisible(el) || seen.has(el)) return
          seen.add(el)
          const rect = el.getBoundingClientRect()
          scored.push({
            el,
            selector: sel,
            area: rect.width * rect.height,
            height: rect.height,
            priority: candidates.length - i,
          })
        })
      }

      scored.sort((a, b) => {
        const aOk = a.height >= minH ? 1 : 0
        const bOk = b.height >= minH ? 1 : 0
        if (aOk !== bOk) return bOk - aOk
        if (a.priority !== b.priority) return b.priority - a.priority
        return b.area - a.area
      })

      let captureEl = scored[0]?.el ?? document.querySelector('main, [role="main"], .min-h-screen')
      if (!captureEl) return null

      let captureSelector = scored[0]?.selector ?? 'main'

      const measure = (el: Element) => {
        const rect = el.getBoundingClientRect()
        const text = ((el as HTMLElement).innerText ?? '').replace(/\s+/g, ' ').trim()
        const substantive = [
          'table tbody tr',
          'form input',
          'form select',
          'form textarea',
          '[data-testid]',
          'canvas',
          '.recharts-wrapper',
          '[role="tablist"]',
          'button',
        ].reduce((sum, sel) => sum + el.querySelectorAll(sel).length, 0)
        return { rect, text, substantive }
      }

      let { rect, text, substantive: substantiveCount } = measure(captureEl)

      if (text.length < 35 && substantiveCount < 2) {
        for (const fallbackSel of ['main', '[data-page-surface]', '.min-h-screen [class*="max-w-md"]']) {
          const alt = document.querySelector(fallbackSel)
          if (!alt || !isVisible(alt) || alt === captureEl) continue
          const altMetrics = measure(alt)
          if (altMetrics.text.length > text.length || altMetrics.substantive > substantiveCount) {
            captureEl = alt
            captureSelector = fallbackSel
            ;({ rect, text, substantive: substantiveCount } = altMetrics)
            break
          }
        }
      }

      const headingCount = captureEl.querySelectorAll('h1, h2, h3').length

      const spinners = Array.from(
        captureEl.querySelectorAll('.animate-spin, svg.animate-spin, [role="progressbar"], [aria-busy="true"]'),
      ).filter(isVisible)

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
    },
    { candidates: CAPTURE_SELECTORS, minW: MIN_CAPTURE_W, minH: MIN_CAPTURE_H },
  )

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
  const hasRichText = metrics.textLength >= 80
  const minHeight = hasRichText ? MIN_CAPTURE_H : 180

  if (metrics.width < MIN_CAPTURE_W || metrics.height < minHeight) {
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
  } else if (
    issues.length === 0 ||
    (metrics.textLength >= 40 && metrics.spinnerCount === 0) ||
    (hasRichText && metrics.substantiveCount >= 1 && metrics.spinnerCount === 0)
  ) {
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
