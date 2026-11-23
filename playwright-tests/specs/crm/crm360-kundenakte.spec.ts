/**
 * Kundenakte (CRM 360) gegen den echten Stack: Liste, Neuanlage, Register, Bearbeiten, Aktivitaet.
 *
 * Kanonisch ist die native Akte `/crm/kunden/{id}` (ScreenDefinition `crm/customer-360`). Das fruehere Cockpit mit
 * Schnellaktionen (Drucken, Telefon/TAPI, KI-Zusammenfassung, Belegmenue, Uebergabe in die Belegkette) ist bei der
 * Studio-Umstellung entfallen. Diese Vertraege bleiben als `test.fixme` mit der Luecke M4-CRM-KUNDENAKTE-PARITAET
 * stehen und werden scharf, sobald die Akte die Aktion wieder anbietet.
 */
import { expect, test, type APIRequestContext, type Page } from '@playwright/test'
import { apiToken, E2E_MANDANT } from '../../helpers/anmeldung'
import { InteractionGuard } from '../../helpers/interactionGuard'

const LUECKE = 'M4-CRM-KUNDENAKTE-PARITAET'

interface Kunde {
  id: string
  customer_number: string
  company_name: string
  city?: string | null
}

function kopf(): Record<string, string> {
  return { Authorization: `Bearer ${apiToken()}`, 'X-Tenant-ID': E2E_MANDANT }
}

// Nur Buchstaben: der InteractionGuard wertet Ziffernfolgen wie "404" im Seitentext als Fehlerseite.
function laufKennung(): string {
  return Array.from({ length: 8 }, () => String.fromCharCode(65 + Math.floor(Math.random() * 26))).join('')
}

async function legeKundeAn(request: APIRequestContext, lauf: string): Promise<Kunde> {
  const antwort = await request.post('/api/v1/crm/customers/', {
    headers: kopf(),
    data: { customer_number: `E2E-${lauf}`, company_name: `E2E Musterhof ${lauf}` },
  })
  expect(antwort.status(), await antwort.text()).toBe(201)
  return antwort.json()
}

async function leseKunde(request: APIRequestContext, id: string): Promise<Kunde> {
  const antwort = await request.get(`/api/v1/crm/customers/${id}`, { headers: kopf() })
  expect(antwort.status(), await antwort.text()).toBe(200)
  return antwort.json()
}

async function oeffneAkte(page: Page, kunde: Kunde): Promise<void> {
  await page.goto(`/crm/kunden/${kunde.id}`)
  await expect(page.getByText(kunde.company_name).first()).toBeVisible()
  await expect(page.getByTestId('action-bearbeiten')).toBeVisible()
}

test.describe('Kundenakte @full', () => {
  test('Neuer Kunde aus der Kundenliste fuehrt nach dem Speichern in die Akte', async ({ page, request }) => {
    const lauf = laufKennung()
    await page.goto('/crm')
    await page.getByRole('button', { name: 'Neuer Kunde' }).click()
    await expect(page).toHaveURL(/\/crm\/kunden\/neu$/)

    await page.getByLabel('Kunden-Nr.', { exact: true }).fill(`E2E-${lauf}`)
    await page.getByLabel('Firma', { exact: true }).fill(`E2E Neukunde ${lauf}`)
    await page.getByRole('button', { name: 'Speichern' }).click()

    await expect(page).toHaveURL(/\/crm\/kunden\/(?!neu$)[^/?#]+$/)
    await expect(page.getByText(`E2E Neukunde ${lauf}`).first()).toBeVisible()
    const id = new URL(page.url()).pathname.split('/').pop() ?? ''
    const gespeichert = await leseKunde(request, decodeURIComponent(id))
    expect(gespeichert.customer_number).toBe(`E2E-${lauf}`)
    expect(gespeichert.company_name).toBe(`E2E Neukunde ${lauf}`)
  })

  test('Abschnitte der Akte laden ohne Fehler', async ({ page, request }) => {
    const kunde = await legeKundeAn(request, laufKennung())
    const guard = new InteractionGuard(page)
    await oeffneAkte(page, kunde)
    const checkpoint = guard.checkpoint()

    await expect(page.getByRole('region', { name: 'Stammdaten', exact: true }).getByLabel('Kundennummer'))
      .toHaveValue(kunde.customer_number)
    const abschnitte: Array<[string, string]> = [
      ['Ansprechpartner', 'table-contacts'],
      ['Finanzen', 'table-finance'],
      ['Belege', 'table-auftraege'],
      ['Aktivitaeten', 'table-aktivitaeten'],
      ['Aufgaben', 'table-aufgaben'],
      ['Kontrakte', 'table-kontrakte'],
      ['Praesente', 'table-praesente'],
      ['Chef-Anweisung', 'table-chefanweisungen'],
    ]
    const navigation = page.getByRole('navigation', { name: 'Abschnitte' })
    for (const [name, tabelle] of abschnitte) {
      await navigation.getByRole('link', { name, exact: true }).click()
      const abschnitt = page.getByRole('region', { name, exact: true })
      await expect(abschnitt).toBeInViewport()
      await expect(abschnitt.getByTestId(tabelle)).toBeVisible()
    }
    await guard.expectNoNewErrors(checkpoint)
  })

  test('Bearbeiten speichert den Ort ueber den Aktionsweg', async ({ page, request }) => {
    const lauf = laufKennung()
    const kunde = await legeKundeAn(request, lauf)
    await oeffneAkte(page, kunde)

    await page.getByTestId('action-bearbeiten').click()
    const dialog = page.getByRole('dialog', { name: 'Bearbeiten' })
    await expect(dialog).toBeVisible()
    await expect(dialog.getByLabel('Firma', { exact: true })).toHaveValue(kunde.company_name)
    await dialog.getByLabel('Ort', { exact: true }).fill(`Aurich ${lauf}`)
    await dialog.getByRole('button', { name: 'Weiter' }).click()

    await expect(page.getByText('Bearbeiten erfolgreich').first()).toBeVisible()
    await expect(dialog).toBeHidden()
    expect((await leseKunde(request, kunde.id)).city).toBe(`Aurich ${lauf}`)
  })

  test('Aktivitaet anlegen erscheint im Abschnitt Aktivitaeten', async ({ page, request }) => {
    test.fixme(true, 'CRM-ACTIVITY-CANONICAL-20261029 (Codex): die Maske sendet den Datensatzkontext mit, '
      + 'POST /crm/customers/{id}/actions/create_activity weist jedes Feld ausser den fuenf Eingaben mit 422 ab')
    const lauf = laufKennung()
    const kunde = await legeKundeAn(request, lauf)
    await oeffneAkte(page, kunde)

    await page.getByTestId('action-create_activity').click()
    const dialog = page.getByRole('dialog', { name: 'Aktivitaet anlegen' })
    await dialog.getByLabel('Betreff', { exact: true }).fill(`Erntegespraech ${lauf}`)
    await dialog.getByLabel('Typ', { exact: true }).selectOption('Anruf')
    await dialog.getByLabel('Notiz', { exact: true }).fill('Lieferfenster und Menge abgestimmt.')
    await dialog.getByRole('button', { name: 'Weiter' }).click()

    await expect(page.getByText('Aktivitaet anlegen erfolgreich').first()).toBeVisible()
    await page.getByRole('navigation', { name: 'Abschnitte' }).getByRole('link', { name: 'Aktivitaeten', exact: true }).click()
    await expect(page.getByTestId('table-aktivitaeten')).toContainText(`Erntegespraech ${lauf}`)
  })

  test('Aktivitaet ohne Betreff wird nicht abgeschickt', async ({ page, request }) => {
    const kunde = await legeKundeAn(request, laufKennung())
    await oeffneAkte(page, kunde)
    const anlagen: string[] = []
    page.on('request', (anfrage) => {
      if (anfrage.method() === 'POST' && anfrage.url().includes('/actions/create_activity')) anlagen.push(anfrage.url())
    })

    await page.getByTestId('action-create_activity').click()
    const dialog = page.getByRole('dialog', { name: 'Aktivitaet anlegen' })
    await dialog.getByLabel('Typ', { exact: true }).selectOption('Besuch')
    await dialog.getByRole('button', { name: 'Weiter' }).click()

    await expect(dialog.getByRole('alert').first()).toBeVisible()
    await expect(dialog).toBeVisible()
    expect(anlagen).toEqual([])
  })

  test('Kundenakte drucken', async ({ page }) => {
    test.fixme(true, `${LUECKE}: keine Druckaktion und keine Druckansicht in crm/customer-360`)
    await page.getByRole('button', { name: 'Drucken' }).click()
  })

  test('Telefonat mit Ansprechpartner waehlen und protokollieren', async ({ page }) => {
    test.fixme(true, `${LUECKE}: kein Waehl-/TAPI-Kommando; Anrufe nur als generische Aktivitaet Typ "Anruf"`)
    await page.getByRole('button', { name: 'Anrufen' }).click()
  })

  test('Ansprechpartner im Detail oeffnen', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Tabelle Ansprechpartner hat nur Aendern/Entfernen, keinen Detaildialog`)
    await page.getByTestId('table-contacts').getByRole('row').nth(1).click()
  })

  test('KI-Zusammenfassung zum Kunden', async ({ page }) => {
    test.fixme(true, `${LUECKE}: keine Zusammenfassungsaktion in der Akte`)
    await page.getByRole('button', { name: 'Zusammenfassung' }).click()
  })

  test('Angebot aus der Akte mit Kundenkontext anlegen', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Register Angebote und Belege sind lesend, keine Anlageaktion mit Kundenkontext`)
    await page.getByRole('button', { name: 'Angebot anlegen' }).click()
  })

  test('Beleg aus dem Register Belege oeffnen', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Belegtabellen der Akte haben keine Zeilenroute in die Belegmaske`)
    await page.getByTestId('table-auftraege').getByRole('row').nth(1).click()
  })

  test('Offene Posten des Kunden in der OP-Verwaltung oeffnen', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Register Finanzen fuehrt nicht nach finance/op-debitoren mit Kundenfilter`)
    await page.getByRole('button', { name: 'Offene Posten' }).click()
  })

  test('Belegkette Auftrag, Lieferschein, Rechnung aus der Akte', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Uebergabe aus der Akte in die Belegkette fehlt; Belegkette selbst: Verkauf VK-01..VK-05`)
    await page.getByRole('button', { name: 'Auftrag anlegen' }).click()
  })

  test('Leads und Geodaten des Kunden', async ({ page }) => {
    test.fixme(true, `${LUECKE}: kein Lead-Register und keine Karte, Geodaten nur als Felder`)
    await page.getByRole('region', { name: 'Leads' }).scrollIntoViewIfNeeded()
  })

  test('Unterlagen ablegen, ansehen und entfernen', async ({ page }) => {
    test.fixme(true, `${LUECKE}: Register Dokumente zeigt offene Posten, keine Ablage ueber DocFlow`)
    await page.getByRole('region', { name: 'Dokumente' }).getByRole('button', { name: 'Unterlage ablegen' }).click()
  })
})
