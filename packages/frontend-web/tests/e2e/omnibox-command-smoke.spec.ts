import { test, expect } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * UIX-070 Command-Smoke: NL mit Aktions-Verb erzeugt einen sicheren
 * Command-/Prefill-Plan in der Omnibox (kein Auto-Submit). Der Omnibox-Katalog
 * wird deterministisch gemockt (Backend separat via pytest getestet) — hier zaehlt
 * die UI-Verdrahtung: Verb-Erkennung → "Aktion vorbereiten" → Navigation.
 */
const CATALOG = [
  {
    screen_id: 'crm/customer-360',
    title: 'Kundenstamm',
    domain: 'crm',
    floorplan: 'cockpit',
    route: '/verkauf/kunden-liste',
    synonyms: ['kunde', 'kundenakte', 'kunden-360'],
    example_prompts: [],
    filterable_fields: [],
    actions: [
      {
        key: 'create_activity',
        label: 'Aktivitaet anlegen',
        dangerLevel: 'safe',
        requiresConfirmation: false,
        forbiddenForAgents: false,
        verbs: ['aktivitaet', 'anlegen', 'create', 'activity'],
        fields: [{ key: 'betreff', type: 'text', required: true }],
      },
    ],
  },
]

test('NL mit Aktions-Verb zeigt "Aktion vorbereiten" und navigiert (formPrefill)', async ({ page }) => {
  await page.route('**/ui/mask-registry/omnibox-catalog', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(CATALOG) }),
  )

  await page.goto('/', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)
  await page.getByRole('button', { name: /Suche/ }).click()
  await expect(page.getByPlaceholder(/Aktion suchen/)).toBeVisible()

  await page.getByPlaceholder(/Aktion suchen/).fill('kunde folkerts aktivität anlegen')

  const commandItem = page.locator('[data-mcp-action^="omnibox-command:"]').first()
  await expect(commandItem).toBeVisible()
  // safe ohne Confirmation → formPrefill (nichts wird armiert)
  await expect(commandItem).toHaveAttribute('data-omnibox-command-kind', 'formPrefill')

  await commandItem.click()
  await expect(page).toHaveURL(/\/verkauf\/kunden-liste\?.*omniboxAction=create_activity/)
})
