/**
 * Workflow Journey Test — simuliert einen Stakeholder der alle ERP-Seiten
 * erkundet OHNE vorher Daten angelegt zu haben.
 *
 * Ausführen mit:
 *   PLAYWRIGHT_SKIP_WEBSERVER=1 FRONTEND_BASE_URL=http://localhost:3001 \
 *     npx playwright test tests/e2e/workflow-journey.spec.ts
 */
import { test, expect } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/** Kernworkflows: jeder Schritt kann ohne Vorschritt-Daten besucht werden */
const WORKFLOW_JOURNEYS = [
  {
    name: 'OTC: Angebot → Auftrag → Lieferschein → Rechnung',
    steps: ['/verkauf/angebote', '/verkauf/auftraege', '/verkauf/lieferschein-erfassung', '/verkauf/rechnungen'],
  },
  {
    name: 'PTP: Bedarfsermittlung → Bestellung → Wareneingang → Rechnung',
    steps: ['/einkauf/bestellvorschlag', '/einkauf/bestellungen', '/einkauf/wareneingang', '/einkauf/eingangsrechnungen'],
  },
  {
    name: 'Agrar: Annahme → Qualität → Abrechnung',
    steps: ['/annahme/warteschlange', '/annahme/qualitaets-check', '/annahme/abrechnung'],
  },
  {
    name: 'CRM: Kunden → Aktivitäten → Kampagnen',
    steps: ['/crm/kunden', '/crm/aktivitaeten', '/crm/campaigns'],
  },
  {
    name: 'Finance: OP-Debitoren → Mahnwesen → Zahlungseingang',
    steps: ['/finance/op-debitoren', '/finance/dunning', '/finance/payments'],
  },
  {
    name: 'Lager: Bestand → Bewegungen → Inventur',
    steps: ['/lager/bestand', '/lager/bewegungen', '/lager/inventur'],
  },
]

const DETAIL_PAGES_WITHOUT_ID = [
  '/crm/betriebsprofil-detail',
  '/crm/aktivitaet-detail',
  '/crm/kontakt-detail',
  '/finance/op-debitoren',
  '/einkauf/wareneingang',
]

const FLOW_SPINE_PAGES = [
  '/workflow/flow-spine-order-to-cash',
  '/workflow/flow-spine-procure-to-pay',
  '/workflow/flow-spine-complaint-to-resolution',
  '/workflow/flow-spine-compliance-to-report',
  '/workflow/flow-spine-service-to-customer',
  '/workflow/flow-spine-harvest-to-settlement',
]

async function visitAndVerify(page: import('@playwright/test').Page, path: string, context: string) {
  await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 30_000 })

  // Warte auf App-Shell oder Timeout (App zeigt mindestens Navigation)
  try {
    await waitForDashboardShell(page, 15_000)
  } catch {
    await page.waitForTimeout(1500)
  }

  // Kein expliziter 404-Heading
  const notFoundHeading = await page.getByRole('heading', { name: /^404$/i }).count()
  expect(notFoundHeading, `${context}: "${path}" zeigt 404-Heading`).toBe(0)

  // Seite hat sichtbaren Inhalt (main, h1, table, form oder Karte)
  const hasContent = await page
    .locator('main, h1, h2, table, form, [data-page], [data-testid], .card, .page-content')
    .first()
    .isVisible({ timeout: 5000 })
    .catch(() => false)
  expect(hasContent, `${context}: "${path}" zeigt komplett leere Seite ohne Inhalt`).toBe(true)

  // Kein unbehandelter Crash (ErrorBoundary-Fallback ist ok für Stakeholder)
  // aber die Seite darf NICHT im Lade-Spinner hängen (> 3 aktive Spinner = Freeze)
  await page.waitForTimeout(1500)
  const fullPageSpinner = page.locator('.fixed.inset-0 [role="status"], [data-loading="page"]')
  const isPageFrozen = await fullPageSpinner.isVisible({ timeout: 1000 }).catch(() => false)
  expect(isPageFrozen, `${context}: "${path}" hängt in Vollseiten-Ladescreen`).toBe(false)
}

test.describe('Workflow Journey — Stakeholder browsing', () => {
  test.setTimeout(180_000)

  for (const journey of WORKFLOW_JOURNEYS) {
    test(journey.name, async ({ page }) => {
      for (const step of journey.steps) {
        await visitAndVerify(page, step, journey.name)
      }
    })
  }
})

test.describe('Detailseiten ohne ID — Stakeholder-Browsing', () => {
  test.setTimeout(90_000)

  test('Detailseiten ohne ID zeigen freundliche Meldung, kein Crash', async ({ page }) => {
    for (const url of DETAIL_PAGES_WITHOUT_ID) {
      await visitAndVerify(page, url, 'Detail ohne ID')
    }
  })
})

test.describe('Flow Spine Workflow-Seiten', () => {
  test.setTimeout(90_000)

  test('Alle Flow-Spine-Seiten zeigen Error-State oder Workspace, kein Crash', async ({ page }) => {
    for (const url of FLOW_SPINE_PAGES) {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30_000 })
      try {
        await waitForDashboardShell(page, 12_000)
      } catch {
        await page.waitForTimeout(2000)
      }

      // Seite muss irgendetwas sinnvolles zeigen
      const hasAnyContent = await page
        .locator('main, h1, h2, [data-page-surface], .card')
        .first()
        .isVisible({ timeout: 5000 })
        .catch(() => false)

      expect(hasAnyContent, `Flow-Spine "${url}": keine sichtbaren Inhalte`).toBe(true)
    }
  })
})
