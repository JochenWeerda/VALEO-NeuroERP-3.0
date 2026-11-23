/**
 * Bankabgleich und Zahlungszuordnung (FIBU-BNK-02, FIBU-AR-03) gegen den echten Stack.
 *
 * Kanonische Maske ist die Workbench `finance/bank-abgleich` (Kontoauszug importieren, Salden vergleichen). Die
 * frueheren handgebauten Seiten unter /fibu/zahlungseingaenge sind durch generische Studio-Listen ersetzt; die
 * Zuordnung einzelner Umsaetze fehlt dort wie in der Workbench. Die Tests dafuer bleiben als `test.fixme` mit der
 * Luecke M3-BANK-ZUORDNUNG-UI stehen und beschreiben den Sollvertrag; sie werden scharf, sobald die Aktion existiert.
 */
import { expect, test, type APIRequestContext } from '@playwright/test'
import { apiToken, E2E_MANDANT } from '../../helpers/anmeldung'

const LUECKE_ZUORDNUNG =
  'M3-BANK-ZUORDNUNG-UI: Die Workbench finance/bank-abgleich zeigt Umsatzzeilen nur an; Zuordnen, Vorschlaege ' +
  '(POST /api/v1/finance/auto-matching/match, /match/{line_id}/apply) und Kennzahlen fehlen in der Maske.'

function kopf(): Record<string, string> {
  return { Authorization: `Bearer ${apiToken()}`, 'X-Tenant-ID': E2E_MANDANT }
}

async function legeBankkontoAn(request: APIRequestContext, lauf: string): Promise<{ id: string; account_number: string }> {
  const antwort = await request.post('/api/v1/finance/bank-accounts', {
    headers: kopf(),
    data: { account_number: `E2E-${lauf}`, bank_name: 'E2E Raiffeisenbank', currency: 'EUR' },
  })
  expect(antwort.status(), await antwort.text()).toBe(201)
  return antwort.json()
}

function kontoauszugCsv(lauf: string): Buffer {
  return Buffer.from(
    [
      'date,amount,reference,remittance_info,debtor_name',
      `2026-11-02,1190.00,E2E-${lauf}-1,RE-${lauf}-1 Saatgut,Musterhof Nord GmbH`,
      `2026-11-03,-250.50,E2E-${lauf}-2,Lieferant Duenger,Agrarhandel Sued`,
    ].join('\n'),
    'utf-8',
  )
}

test.describe('Bankabgleich @full', () => {
  test('Kontoauszug importieren und Salden vergleichen', async ({ page, request }) => {
    const lauf = `${Date.now()}`
    const konto = await legeBankkontoAn(request, lauf)

    await page.goto('/finance/bank-abgleich')
    const arbeitsbereich = page.getByRole('region', { name: 'Bankabgleich Arbeitsbereich' })
    await expect(arbeitsbereich).toBeVisible()

    await arbeitsbereich.getByLabel('Bankkonto').selectOption(konto.id)
    await arbeitsbereich.getByLabel('Kontoauszug').setInputFiles({
      name: `kontoauszug-${lauf}.csv`,
      mimeType: 'text/csv',
      buffer: kontoauszugCsv(lauf),
    })
    await page.getByRole('button', { name: 'Kontoauszug importieren' }).click()

    await expect(page.getByText('2 Zeilen importiert')).toBeVisible()
    const zeilen = arbeitsbereich.locator('tbody tr')
    await expect(zeilen).toHaveCount(2)
    await expect(zeilen.filter({ hasText: `E2E-${lauf}-1` })).toContainText('1190.00 EUR')
    await expect(zeilen.filter({ hasText: `E2E-${lauf}-2` })).toContainText('-250.50 EUR')
    await expect(arbeitsbereich.getByText('Umsatzsumme: 939.50 EUR')).toBeVisible()

    // Eine CSV-Datei traegt keinen Bank-Saldonachweis, das neue Konto keine Hauptbuchzuordnung: der Abgleich muss
    // das als unvollstaendig melden statt "Salden stimmen ueberein".
    await page.getByRole('button', { name: 'Salden vergleichen' }).click()
    await expect(page.getByText('CSV-Dateien enthalten keinen Bank-Saldonachweis.')).toBeVisible()
    await expect(arbeitsbereich.getByText('Salden stimmen überein')).toHaveCount(0)
    await expect(page.getByText('Abgleich fehlgeschlagen')).toHaveCount(0)
  })

  test('Umsatz manuell einem offenen Posten zuordnen', async ({ page }) => {
    test.fixme(true, LUECKE_ZUORDNUNG)
    await page.goto('/finance/bank-abgleich')
    const zeile = page.getByRole('region', { name: 'Bankabgleich Arbeitsbereich' }).locator('tbody tr').first()
    await zeile.getByRole('button', { name: 'Zuordnen' }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByRole('table')).toBeVisible()
    await dialog.getByRole('button', { name: 'Zuordnen' }).first().click()
    await expect(zeile).toContainText('MATCHED')
  })

  test('Zuordnungsvorschlaege je Umsatz', async ({ page }) => {
    test.fixme(true, LUECKE_ZUORDNUNG)
    await page.goto('/finance/bank-abgleich')
    const zeile = page.getByRole('region', { name: 'Bankabgleich Arbeitsbereich' }).locator('tbody tr').first()
    await zeile.getByRole('button', { name: 'Zuordnen' }).click()
    await expect(page.getByRole('dialog').getByText(/Vorschlag/)).toBeVisible()
  })

  test('Kennzahlen offene Zuordnungen und Auto-Match-Quote', async ({ page }) => {
    test.fixme(true, LUECKE_ZUORDNUNG)
    await page.goto('/finance/bank-abgleich')
    await expect(page.getByText('Offene Zuordnungen')).toBeVisible()
    await expect(page.getByText('Auto-Match-Rate')).toBeVisible()
  })
})
