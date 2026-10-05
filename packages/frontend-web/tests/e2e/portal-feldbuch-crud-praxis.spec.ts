/**
 * Praxis-Simulation Portal-Ackerschlagkartei: alle CRUD- und Sonderaktionen.
 * Speichert Screenshots nach docs/benutzerhandbuch/img/ für Handbuch-Nachzug.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect, test, type Page } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const SHOT_DIR = path.resolve(__dirname, '../../../../docs/benutzerhandbuch/img')
const PROTOCOL_PATH = path.resolve(__dirname, '../../../../artifacts/portal-feldbuch-crud-praxis.json')

const protocol: {
  startedAt: string
  steps: { step: string; ok: boolean; detail?: string }[]
  screenshots: string[]
} = { startedAt: new Date().toISOString(), steps: [], screenshots: [] }

function log(step: string, ok: boolean, detail?: string) {
  protocol.steps.push({ step, ok, detail })
}

async function shot(page: Page, name: string) {
  fs.mkdirSync(SHOT_DIR, { recursive: true })
  const png = path.join(SHOT_DIR, `${name}.png`)
  await page.screenshot({ path: png, fullPage: true, type: 'png' })
  protocol.screenshots.push(png)
}

test.describe('Portal Feldbuch CRUD Praxis', () => {
  test.describe.configure({ timeout: 300_000 })

  test.afterAll(() => {
    fs.mkdirSync(path.dirname(PROTOCOL_PATH), { recursive: true })
    fs.writeFileSync(PROTOCOL_PATH, JSON.stringify(protocol, null, 2), 'utf-8')
  })

  test('Praxisfälle: anlegen, bearbeiten, löschen, Sammel, Info, Auswertungen', async ({ page }) => {
    page.on('dialog', async (d) => { await d.accept() })

    await page.goto('/portal/feldbuch', { waitUntil: 'domcontentloaded' })
    try {
      await waitForDashboardShell(page)
    } catch {
      // Portal-Layout kann ohne ERP-Shell laufen
    }
    await expect(page.getByRole('heading', { name: /Ackerschlagkartei/i })).toBeVisible({ timeout: 60_000 })
    log('Feldbuch geladen', true)
    await shot(page, 'portal__feldbuch')

    try {
      await expect(page.getByRole('heading', { name: /Arbeitskontext/i })).toBeVisible({ timeout: 10_000 })
      log('Arbeitskontext sichtbar', true)
    } catch (e) {
      log('Arbeitskontext sichtbar', false, (e as Error).message)
    }

    await page.getByRole('tab', { name: /Schläge/i }).click()
    const stamp = Date.now()
    const schlagName = `Praxis-Schlag ${stamp}`

    const createSchlagBtn = page.getByTestId('schlag-create').or(page.getByRole('button', { name: /^Schlag anlegen$/i }))
    await createSchlagBtn.first().click({ timeout: 30_000 })
    await expect(page.getByRole('heading', { name: /Schlag anlegen/i })).toBeVisible({ timeout: 10_000 })
    await page.getByTestId('schlag-name').or(page.getByLabel(/^Name/i)).fill(schlagName)
    await page.getByTestId('schlag-flaeche').or(page.getByLabel(/Fläche/i)).fill('12.5')
    await page.getByTestId('schlag-kultur').or(page.getByLabel(/^Kultur/i)).fill('Winterweizen')
    await page.getByTestId('schlag-gemeinde').or(page.getByLabel(/Gemeinde/i)).fill('Musterdorf')
    await page.getByRole('button', { name: /^Schlag anlegen$/i }).last().click()
    await expect(page.getByText(schlagName)).toBeVisible({ timeout: 20_000 })
    log('Schlag angelegt', true)
    await shot(page, 'portal__feldbuch__schlag-angelegt')

    const schlagRow = page.locator('tr', { hasText: schlagName }).first()
    const kulturEdit = `Kultur-${stamp}`
    const schlagEdit = schlagRow.getByRole('button', { name: /Bearbeiten/i })
    if (await schlagEdit.count()) {
      await schlagEdit.click()
      await page.getByTestId('schlag-kultur').or(page.getByLabel(/^Kultur/i)).fill(kulturEdit)
      await page.getByRole('button', { name: /Änderungen speichern/i }).click()
      await expect(schlagRow.getByText(kulturEdit)).toBeVisible({ timeout: 20_000 })
      log('Schlag bearbeitet', true)
    } else {
      log('Schlag bearbeitet', false, 'Kein Bearbeiten-Button — Dev-Server ohne CRUD-UI?')
    }
    await shot(page, 'portal__feldbuch__schlag-bearbeitet')

    const infoBtn = schlagRow.getByRole('button', { name: new RegExp(`Info\\s+${schlagName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i') })
      .or(schlagRow.getByRole('button', { name: /^Info/i }))
    if (await infoBtn.count()) {
      await infoBtn.first().click()
      await expect(page.getByRole('heading', { name: /Schlaginformation/i })).toBeVisible({ timeout: 10_000 })
      log('Schlaginfo Dialog', true)
      await shot(page, 'portal__feldbuch__schlaginfo')
      await page.getByRole('button', { name: /Schließen/i }).click()
    } else {
      log('Schlaginfo Dialog', false, 'Kein Info-Button')
    }

    await page.getByRole('tab', { name: /Maßnahmen/i }).click()
    const createMassn = page.getByTestId('massnahme-create').or(page.getByRole('button', { name: /Maßnahme erfassen/i }))
    await createMassn.first().click({ timeout: 15_000 })
    await expect(page.getByRole('heading', { name: /Maßnahme erfassen/i })).toBeVisible({ timeout: 10_000 })
    // Düngung statt PSM — vermeidet Pflicht-Sachkunde im Happy Path
    const typSelect = page.getByTestId('massnahme-typ')
    if (await typSelect.count()) {
      await typSelect.selectOption('duengung')
    } else {
      await page.locator('select').filter({ has: page.locator('option', { hasText: 'Düngung' }) }).first().selectOption({ label: 'Düngung' })
    }
    const mittelName = `KAS Praxis ${stamp}`
    const mittelEdit = `${mittelName} Edit`
    await page.getByTestId('massnahme-datum').or(page.getByLabel(/Datum/i)).fill('2026-03-15')
    await page.getByTestId('massnahme-mittel').or(page.getByLabel(/Mittel/i)).fill(mittelName)
    await page.getByTestId('massnahme-menge').or(page.getByLabel(/^Menge/i)).fill('350')
    await page.getByTestId('massnahme-flaeche').or(page.getByLabel(/Fläche/i)).fill('12.5')
    await page.getByTestId('massnahme-anwender').or(page.getByLabel(/Anwender/i)).fill('Max Mustermann')
    await page.getByRole('button', { name: /^Maßnahme erfassen$/i }).last().click()
    await expect(page.getByText(mittelName, { exact: true })).toBeVisible({ timeout: 20_000 })
    log('Maßnahme angelegt', true)
    await shot(page, 'portal__feldbuch__massnahme-angelegt')

    const mRow = page.locator('tr', { hasText: mittelName }).first()
    const editBtn = mRow.getByRole('button', { name: /Bearbeiten/i })
    if (await editBtn.count() && await editBtn.isEnabled()) {
      await editBtn.click()
      await page.getByTestId('massnahme-mittel').or(page.getByLabel(/Mittel/i)).fill(mittelEdit)
      await page.getByRole('button', { name: /Änderungen speichern/i }).click()
      await expect(page.getByText(mittelEdit, { exact: true })).toBeVisible({ timeout: 20_000 })
      log('Maßnahme bearbeitet', true)
    } else {
      log('Maßnahme bearbeitet', false, 'Edit nicht verfügbar')
    }
    await shot(page, 'portal__feldbuch__massnahme-bearbeitet')

    const sammel = page.getByRole('button', { name: /Sammeldüngung/i })
    if (await sammel.count()) {
      await sammel.click()
      await expect(page.getByRole('heading', { name: /Sammeldüngung/i })).toBeVisible()
      log('Sammeldüngung Dialog', true)
      await shot(page, 'portal__feldbuch__sammelduengung')
      await page.getByRole('button', { name: /Abbrechen/i }).click()
    } else {
      log('Sammeldüngung Dialog', false, 'Button fehlt auf laufendem Build')
    }

    await page.getByRole('button', { name: /^Export$/i }).click()
    await expect(page.getByText(/Export|Ackerschlagkartei/i).first()).toBeVisible({ timeout: 10_000 })
    log('Export Dialog', true)
    await shot(page, 'portal__feldbuch__export')
    await page.getByRole('button', { name: /Schließen|Abbrechen/i }).first().click()

    await page.getByRole('tab', { name: /Maßnahmen/i }).click()
    const delM = page.locator('tr', { hasText: mittelEdit }).or(page.locator('tr', { hasText: mittelName })).first()
      .getByRole('button', { name: /Löschen/i })
    if (await delM.count() && await delM.isEnabled()) {
      await delM.click()
      await expect(page.getByText(mittelEdit).or(page.getByText(mittelName, { exact: true }))).toHaveCount(0, { timeout: 15_000 })
      log('Maßnahme gelöscht', true)
    } else {
      log('Maßnahme gelöscht', false, 'Delete nicht verfügbar')
    }

    await page.getByRole('tab', { name: /Schläge/i }).click()
    const delS = page.locator('tr', { hasText: schlagName }).first()
      .getByRole('button', { name: /Löschen/i })
    if (await delS.count()) {
      await delS.click()
      await expect(page.getByText(schlagName)).toHaveCount(0, { timeout: 20_000 })
      log('Schlag gelöscht', true)
    } else {
      log('Schlag gelöscht', false, 'Delete-Button fehlt')
    }
    await shot(page, 'portal__feldbuch__nach-loeschen')

    await page.goto('/portal/feldbuch-auswertungen', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: /DüV-Auswertungen|Auswertungen/i })).toBeVisible({ timeout: 60_000 })
    log('Auswertungen geladen', true)
    await shot(page, 'portal__feldbuch-auswertungen')

    for (const label of [/Düngebedarf/i, /Düngebilanz/i, /Stoffstrombilanz/i, /Pflanzenschutz/i, /Ernte/i]) {
      try {
        await page.getByRole('button', { name: label }).first().click({ timeout: 8_000 })
        await page.waitForTimeout(300)
        log(`Auswertung ${label.source}`, true)
      } catch (e) {
        log(`Auswertung ${label.source}`, false, (e as Error).message)
      }
    }

    const critical = protocol.steps.filter((s) =>
      !s.ok && /Feldbuch geladen|Schlag angelegt|Maßnahme angelegt|Auswertungen geladen/.test(s.step),
    )
    const failed = protocol.steps.filter((s) => !s.ok)
    expect(critical, `Kritische Fehlschritte: ${JSON.stringify(critical)}`).toHaveLength(0)
    if (failed.length) {
      // eslint-disable-next-line no-console
      console.warn('[Praxis] Nicht-kritische Fehlschritte:', failed)
    }
  })

  test('Praxisfälle: CSV-Import, Jahreswechsel, PSM-Sachkunde', async ({ page }) => {
    page.on('dialog', async (d) => { await d.accept() })
    const stamp = Date.now()
    const csvPath = path.resolve(__dirname, 'fixtures/feldbuch-praxis-import.csv')
    const schlagJw = `JW-Schlag ${stamp}`
    const psmMittel = `Atlantis Praxis ${stamp}`

    await page.goto('/portal/feldbuch', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: /Ackerschlagkartei/i })).toBeVisible({ timeout: 60_000 })

    // ── CSV-Import ──────────────────────────────────────────────────────────
    await page.getByRole('button', { name: /^Import$/i }).click()
    await expect(page.getByRole('heading', { name: /CSV importieren/i })).toBeVisible({ timeout: 10_000 })
    await shot(page, 'portal__feldbuch__import')
    await page.getByTestId('feldbuch-import-file').setInputFiles(csvPath)
    await expect(page.getByText(/Import abgeschlossen/i)).toBeVisible({ timeout: 20_000 })
    log('CSV-Import erfolgreich', true)
    await shot(page, 'portal__feldbuch__import-ergebnis')
    await page.getByRole('button', { name: /Schließen/i }).click()
    await page.getByRole('tab', { name: /Schläge/i }).click()
    await expect(page.getByText(/Import-Praxis-Nord/i)).toBeVisible({ timeout: 20_000 })
    log('Import-Schlag in Liste', true)

    // ── Jahreswechsel ───────────────────────────────────────────────────────
    await page.getByTestId('schlag-create').or(page.getByRole('button', { name: /^Schlag anlegen$/i })).first().click()
    await page.getByTestId('schlag-name').fill(schlagJw)
    await page.getByTestId('schlag-flaeche').fill('4.0')
    await page.getByTestId('schlag-kultur').fill('Raps')
    await page.getByRole('button', { name: /^Schlag anlegen$/i }).last().click()
    await expect(page.getByText(schlagJw)).toBeVisible({ timeout: 20_000 })
    log('Jahreswechsel-Quellschlag angelegt', true)

    const wjSelect = page.locator('select').filter({ has: page.locator('option', { hasText: /WJ / }) }).first()
    const wjBefore = await wjSelect.inputValue()
    await page.getByRole('button', { name: /Jahreswechsel/i }).click()
    await expect(wjSelect).toHaveValue(String(Number(wjBefore) + 1), { timeout: 15_000 })
    await expect(page.getByText(schlagJw)).toBeVisible({ timeout: 15_000 })
    log('Jahreswechsel ausgeführt', true, `WJ ${wjBefore} → ${Number(wjBefore) + 1}`)
    await shot(page, 'portal__feldbuch__jahreswechsel')

    // ── PSM ohne Sachkunde → Prüfen-Badge ───────────────────────────────────
    await page.getByRole('tab', { name: /Maßnahmen/i }).click()
    await page.getByTestId('massnahme-create').or(page.getByRole('button', { name: /Maßnahme erfassen/i })).first().click()
    await expect(page.getByRole('heading', { name: /Maßnahme erfassen/i })).toBeVisible()
    await page.getByTestId('massnahme-typ').selectOption('psm')
    await page.getByTestId('massnahme-datum').fill('2026-05-10')
    await page.getByTestId('massnahme-mittel').fill(psmMittel)
    await page.getByTestId('massnahme-menge').fill('1.5')
    await page.getByTestId('massnahme-flaeche').fill('4.0')
    await page.getByTestId('massnahme-anwender').fill('Max Mustermann')
    // bewusst ohne Begründung/Sachkunde
    await shot(page, 'portal__feldbuch__psm-ohne-sachkunde')
    await page.getByRole('button', { name: /^Maßnahme erfassen$/i }).last().click()
    const psmRow = page.locator('tr', { hasText: psmMittel }).first()
    await expect(psmRow).toBeVisible({ timeout: 20_000 })
    await expect(psmRow.getByText(/Prüfen/i)).toBeVisible({ timeout: 10_000 })
    log('PSM ohne Sachkunde → Prüfen', true)
    await shot(page, 'portal__feldbuch__psm-pruefen-badge')

    // ── PSM mit Sachkunde vervollständigen ──────────────────────────────────
    await psmRow.getByRole('button', { name: /Bearbeiten/i }).click()
    await page.getByTestId('massnahme-begruendung').fill('Schadschwelle Ungras überschritten')
    await page.getByTestId('massnahme-sachkunde-nr').fill('SK-NI-PRAXIS-001')
    await page.getByTestId('massnahme-sachkunde-bis').fill('2027-12-31')
    await page.getByRole('button', { name: /Änderungen speichern/i }).click()
    await expect(page.locator('tr', { hasText: psmMittel }).first().getByText(/Prüfen/i)).toHaveCount(0, { timeout: 15_000 })
    log('PSM mit Sachkunde compliant', true)
    await shot(page, 'portal__feldbuch__psm-mit-sachkunde')

    const criticalExtra = protocol.steps.filter((s) =>
      !s.ok && /CSV-Import erfolgreich|Jahreswechsel ausgeführt|PSM ohne Sachkunde|PSM mit Sachkunde/.test(s.step),
    )
    expect(criticalExtra, `Kritische Extra-Fehlschritte: ${JSON.stringify(criticalExtra)}`).toHaveLength(0)
  })
})
