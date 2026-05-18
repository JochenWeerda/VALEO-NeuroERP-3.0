import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Smoke tests for 15 new frontend masks.
 * Each test:
 *  - navigates to the route
 *  - waits for the AppShell <main> to appear
 *  - asserts the URL is retained (no silent redirect to dashboard)
 *  - asserts a visible heading / key UI element
 *  - asserts no TypeError or ReferenceError in the browser console
 */

type MaskCheck = {
  path: string
  /** Substring / regex that should appear in an h1 or [role="heading"] */
  heading: RegExp
  /** Optional: an additional visible element (e.g. a table, button) */
  extraLocator?: string
}

const MASKS: MaskCheck[] = [
  {
    path: '/waage/vorlagen',
    heading: /waagenvorlage/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/kontrakte/kontraktklassen',
    heading: /kontraktklasse/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/agrar/sammelabrechnung',
    heading: /sammelabrechnung/i,
    extraLocator: 'button, form, [data-testid]',
  },
  {
    path: '/preise/kalkulation',
    heading: /kalkulation|preis/i,
    extraLocator: 'table, [role="grid"], input, button',
  },
  {
    path: '/compliance/gelangensbestaetigung',
    heading: /gelangensbestätigung|gelangensbestaetigung/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/compliance/sanktionspruefung',
    heading: /sanktionsprüfung|sanktionspruefung/i,
    extraLocator: 'table, [role="grid"], input, button',
  },
  {
    path: '/compliance/lksg',
    heading: /lksg/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/compliance/intrastat',
    heading: /intrastat/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/genossenschaft/mitglieder',
    heading: /genossenschaftsmitglied|mitglied/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/admin/webshop',
    heading: /webshop/i,
    extraLocator: 'table, form, button, input',
  },
  {
    path: '/agrar/saatzucht',
    heading: /saatzucht/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/pos/promotionen',
    heading: /promotion/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/admin/webhooks',
    heading: /webhook/i,
    extraLocator: 'table, [role="grid"], button',
  },
  {
    path: '/personal/organigramm',
    heading: /organigramm/i,
    extraLocator: 'svg, canvas, [role="tree"], button',
  },
  {
    path: '/personal/bewerbungen',
    heading: /bewerbung/i,
    extraLocator: 'table, [role="grid"], button',
  },
]

test.describe('Neue Masken — Smoke Tests', () => {
  for (const mask of MASKS) {
    test(`${mask.path} renders without errors`, async ({ page }) => {
      // Collect console errors before navigation
      const consoleErrors: string[] = []
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          const text = msg.text()
          if (/TypeError|ReferenceError/.test(text)) {
            consoleErrors.push(text)
          }
        }
      })

      await page.goto(mask.path, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)

      // URL must not silently redirect away from the requested path
      await expect(page).toHaveURL(
        new RegExp(`${mask.path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|\\?)`)
      )

      // Page must not show a generic load-error fallback
      await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)

      // Heading must be visible
      await expect(
        page.locator('h1, [role="heading"]').filter({ hasText: mask.heading }).first()
      ).toBeVisible()

      // At least one key UI element must be present
      if (mask.extraLocator) {
        await expect(page.locator(mask.extraLocator).first()).toBeVisible()
      }

      // No TypeError / ReferenceError in console
      expect(
        consoleErrors,
        `Console errors on ${mask.path}: ${consoleErrors.join(' | ')}`
      ).toHaveLength(0)
    })
  }
})
