/**
 * Am Kunden laesst sich eine Bankverbindung hinterlegen — und sie bleibt.
 *
 * Die Maske schickte `banking` als festen Rumpf aus lauter `null` und reichte
 * beim Bearbeiten nur durch, was schon dastand. Ein Eingabefeld gab es nicht.
 * Spalten (iban, bic, bank_name, sepa_mandate_*) und Schreibpfad im Backend
 * existierten die ganze Zeit — es fehlte allein die Maske.
 *
 * Ohne Bankverbindung hat der Lastschrifteinzug keine Grundlage. Das ist kein
 * Schoenheitsfehler, sondern ein fehlender Stammdatensatz.
 */
import { test, expect } from '@playwright/test'

const IBAN = 'DE02120300000000202051'
const BIC = 'BYLADEM1001'

test('IBAN, BIC und Mandat lassen sich eintragen und werden gespeichert', async ({ page }) => {
  await page.goto('/verkauf/kunden-stamm', { waitUntil: 'domcontentloaded' })
  await page.locator('main').first().waitFor({ state: 'visible', timeout: 20_000 })

  // Pflichtfeld, sonst speichert die Maske nicht.
  const name = `Testhof Bankverbindung ${Date.now()}`
  await page.getByLabel('Firmenname (Zeile 1)').fill(name)

  // Die Bankverbindung steht bei Zahlungsziel und Kreditlimit im Reiter
  // „Konditionen" — dort gehoert sie fachlich hin.
  await page.getByRole('tab', { name: 'Konditionen' }).click()

  await page.getByLabel('IBAN').fill(IBAN)
  await page.getByLabel('BIC').fill(BIC)
  await page.getByLabel('Kreditinstitut').fill('Testbank eG')
  await page.getByLabel('SEPA-Mandatsreferenz').fill('MND-TEST-0001')
  await page.getByLabel('Mandat unterschrieben am').fill('2026-01-15')

  // Was geht wirklich zum Server?
  const anfrage = page.waitForRequest(
    (r) => r.url().includes('/crm/business-partners') && ['POST', 'PUT'].includes(r.method()),
    { timeout: 20_000 },
  )
  await page.getByRole('button', { name: /speichern/i }).first().click()
  const gesendet = await anfrage

  const rumpf = JSON.parse(gesendet.postData() ?? '{}')
  const banking = rumpf?.business_partner?.banking ?? rumpf?.banking
  expect(banking, 'Die Maske schickt keinen Bank-Block').toBeTruthy()
  expect(banking.iban, 'IBAN kommt nicht am Server an').toBe(IBAN)
  expect(banking.bic).toBe(BIC)
  expect(banking.bank_name).toBe('Testbank eG')
  expect(banking.sepa_mandate_reference).toBe('MND-TEST-0001')
})

test('die Maske bietet die Felder ueberhaupt an', async ({ page }) => {
  /**
   * Der eigentliche Fehler war nicht ein falscher Wert, sondern ein fehlendes
   * Feld — und ein fehlendes Feld faellt in keinem Vertragstest auf.
   */
  await page.goto('/verkauf/kunden-stamm', { waitUntil: 'domcontentloaded' })
  await page.locator('main').first().waitFor({ state: 'visible', timeout: 20_000 })
  await page.getByRole('tab', { name: 'Konditionen' }).click()

  for (const feld of ['IBAN', 'BIC', 'Kreditinstitut', 'SEPA-Mandatsreferenz']) {
    await expect(page.getByLabel(feld), `Feld ${feld} fehlt in der Kundenmaske`).toBeVisible()
  }
})
