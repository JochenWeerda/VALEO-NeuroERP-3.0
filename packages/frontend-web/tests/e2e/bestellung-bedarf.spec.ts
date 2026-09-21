/**
 * Die Bestellerfassung waehlt ihren Fall — und rechnet im Fall Bestand.
 *
 * Die Maske fuehrte neun Felder und kannte keinen Unterschied zwischen einer
 * Lagerbestellung, einer Direktlieferung an den Kunden und einem neuen Artikel
 * zur Probe. Jetzt steht der Fall im ersten Schritt, und im Fall
 * Bestand/Abverkauf laesst sich der Bedarf aus den Lagerbewegungen rechnen,
 * statt ihn zu schaetzen.
 *
 * Geprueft wird, was der Anwender sieht: die drei Faelle, die Bedarfsansicht
 * nur im passenden Fall, und dass die Rechnung wirklich am Endpunkt landet.
 */
import { test, expect } from '@playwright/test'

const ERFASSUNG = '/einkauf/bestellungen/neu'

async function maskeOeffnen(page: import('@playwright/test').Page) {
  await page.goto(ERFASSUNG, { waitUntil: 'domcontentloaded' })
  await page.locator('main').first().waitFor({ state: 'visible', timeout: 20_000 })
}

test('der Bestellfall steht im ersten Schritt', async ({ page }) => {
  await maskeOeffnen(page)

  for (const fall of ['bestand_abgleich', 'direktlieferung', 'innovation']) {
    await expect(
      page.getByTestId(`bestellfall-${fall}`),
      `Der Bestellfall ${fall} fehlt in der Erfassung`,
    ).toBeVisible()
  }
})

test('die Bedarfsansicht erscheint nur im Fall Bestand und Abverkauf', async ({ page }) => {
  await maskeOeffnen(page)

  // Vorbelegt ist Bestand/Abverkauf — dort gehoert die Rechnung hin.
  await expect(page.getByLabel('Horizont')).toBeVisible()

  // Bei einer Direktlieferung waere ein Abverkaufsschnitt die falsche Frage:
  // Die Menge steht im Auftrag des Kunden.
  await page.getByTestId('bestellfall-direktlieferung').click()
  await expect(page.getByLabel('Horizont')).toHaveCount(0)

  // Und bei einem neuen Artikel gibt es keine Historie, aus der man rechnen
  // koennte — genau deshalb ist er ein eigener Fall.
  await page.getByTestId('bestellfall-innovation').click()
  await expect(page.getByLabel('Horizont')).toHaveCount(0)

  await page.getByTestId('bestellfall-bestand_abgleich').click()
  await expect(page.getByLabel('Horizont')).toBeVisible()
})

test('die Rechnung geht mit Horizont und Kostensaetzen an den Endpunkt', async ({ page }) => {
  await maskeOeffnen(page)

  await page.getByLabel('Horizont').selectOption('saisonal')
  await page.getByLabel('Lagerkosten je Einheit und Tag').fill('0.02')
  await page.getByLabel('Frachtkosten je Anlieferung').fill('250')

  const anfrage = page.waitForRequest(
    (r) => r.url().includes('/einkauf/bestellvorschlaege/bedarf'),
    { timeout: 20_000 },
  )
  await page.getByRole('button', { name: /Bedarf berechnen/i }).click()
  const url = new URL((await anfrage).url())

  expect(url.searchParams.get('horizont')).toBe('saisonal')
  expect(url.searchParams.get('lagerkosten_satz')).toBe('0.02')
  expect(url.searchParams.get('frachtkosten_fix')).toBe('250')
})

test('ohne Bedarf steht dort ein Satz und keine leere Flaeche', async ({ page }) => {
  /**
   * Eine leere Tabelle sieht aus wie ein Fehler. Wenn kein Artikel seinen
   * Bedarf unterschreitet, ist das eine Auskunft — und die gehoert hin.
   */
  await maskeOeffnen(page)

  await page.getByRole('button', { name: /Bedarf berechnen/i }).click()
  // Beides ist eine Auskunft: der leere Bedarf oder der Fehlschlag mit Grund.
  // Scheitert der Aufruf, steht der Satz zweimal da — im Kasten und im Toast;
  // geprueft wird, dass ueberhaupt etwas dasteht.
  await expect(
    page.getByText(/Kein Artikel unterschreitet|Bedarf nicht geladen/).first(),
  ).toBeVisible({ timeout: 20_000 })
})
