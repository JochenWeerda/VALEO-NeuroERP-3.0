import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('WCAG 2.2 AA Audit', () => {
  const routes = ['/', '/agrar', '/einkauf/bestellungen', '/finance', '/lager']

  for (const route of routes) {
    test(`Keine axe-Fehler auf ${route}`, async ({ page }) => {
      await page.goto(route)
      await page.waitForLoadState('networkidle')
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze()
      expect(results.violations).toEqual([])
    })
  }
})
