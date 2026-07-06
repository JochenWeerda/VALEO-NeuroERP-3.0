import type { Page } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

export type PageRenderState = 'ready' | 'spinner' | '404' | 'empty'

export async function assessPageState(page: Page): Promise<PageRenderState> {
  return page.evaluate(() => {
    const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    if (
      headings.some((h) =>
        /^\s*(404|Seite nicht gefunden|Not Found|Page Not Found)\s*$/i.test(
          (h as HTMLElement).innerText ?? '',
        ),
      )
    ) {
      return '404'
    }

    const isVisible = (el: Element): boolean => {
      const rect = el.getBoundingClientRect()
      const style = getComputedStyle(el)
      return (
        rect.width > 2 &&
        rect.height > 2 &&
        style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        style.opacity !== '0'
      )
    }

    const spinners = Array.from(
      document.querySelectorAll(
        '.animate-spin, svg.animate-spin, [role="progressbar"], [aria-busy="true"]',
      ),
    ).filter(isVisible)

    const bodyText = (document.body.innerText ?? '').replace(/\s+/g, ' ').trim()
    const loadingText = /wird geladen|loading\.{0,3}|lädt\.{0,3}|bitte warten|daten werden geladen|summary wird geladen/i.test(
      bodyText,
    )

    const main =
      document.querySelector('main, [role="main"]') ??
      document.querySelector('[data-page-surface], .min-h-screen')
    const mainText = ((main as HTMLElement | null)?.innerText ?? '').replace(/\s+/g, ' ').trim()

    const substantiveSelectors = [
      'table tbody tr',
      'form input',
      'form select',
      'form textarea',
      '[data-testid]',
      'canvas',
      '.recharts-wrapper',
      'h1',
      'h2',
      '[role="tablist"]',
      '.object-page',
      '[data-runtime="native"]',
    ]
    const substantiveCount = substantiveSelectors.reduce(
      (sum, selector) => sum + document.querySelectorAll(selector).length,
      0,
    )

    const contentText = mainText || bodyText
    const hasSubstantiveContent =
      substantiveCount >= 2 ||
      contentText.length > 160 ||
      (contentText.length > 80 && !loadingText)

    if ((spinners.length > 0 || loadingText) && !hasSubstantiveContent) {
      return 'spinner'
    }

    if (!main || !isVisible(main)) {
      const bodyTextLen = bodyText.length
      if (bodyTextLen < 50) {
        return 'empty'
      }
    }

    if (!hasSubstantiveContent && contentText.length < 50) {
      return 'empty'
    }

    return 'ready'
  }) as Promise<PageRenderState>
}

export async function waitUntilRenderable(
  page: Page,
  maxMs = 45_000,
): Promise<PageRenderState> {
  await page.waitForLoadState('domcontentloaded')
  await waitForDashboardShell(page, Math.min(maxMs, 60_000)).catch(() => {})

  const deadline = Date.now() + maxMs
  while (Date.now() < deadline) {
    const state = await assessPageState(page)
    if (state === 'ready' || state === '404' || state === 'empty') {
      return state
    }
    await page.waitForTimeout(750)
  }

  return assessPageState(page)
}
