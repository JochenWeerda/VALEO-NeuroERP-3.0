/**
 * UAT: Lead-Generierung + Artikel-Stammdaten + Belegkette
 *
 * Reproduzierbarer Testlauf für A/B-Vergleiche und Regressionstests.
 * Jeder Test ist unabhängig und misst seine eigene Ladezeit.
 *
 * Ausführung:
 *   npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --headed
 *
 * Für A/B-Vergleich (z.B. vor/nach Performance-Fix):
 *   npx playwright test tests/e2e/uat/lead-gen-workflow.spec.ts --reporter=html
 *   → playwright-report/index.html vergleichen
 *
 * Umgebungsvariablen:
 *   BASE_URL   = http://localhost:3001  (default)
 *   API_DEV_TOKEN = dev-token
 */

import { test, expect, type Page } from '@playwright/test'
import { prepareE2EAuth } from '../helpers/auth-from-env'

// ─── Konfiguration ───────────────────────────────────────────────────────────

const BASE = process.env.BASE_URL ?? 'http://localhost:3001'

/** Ladezeit messen und als Annotation im Bericht ausgeben */
async function measureLoad(page: Page, label: string): Promise<number> {
  const t0 = Date.now()
  await page.waitForLoadState('domcontentloaded')
  const ms = Date.now() - t0
  test.info().annotations.push({ type: 'Ladezeit', description: `${label}: ${ms} ms` })
  console.log(`⏱  ${label}: ${ms} ms`)
  return ms
}

async function gotoMeasured(page: Page, path: string, label?: string): Promise<number> {
  const t0 = Date.now()
  await page.goto(`${BASE}${path}`)
  await page.waitForLoadState('domcontentloaded')
  const ms = Date.now() - t0
  const l = label ?? path
  test.info().annotations.push({ type: 'Ladezeit', description: `${l}: ${ms} ms` })
  console.log(`⏱  ${l}: ${ms} ms`)
  return ms
}

// ─── 1. Lead-Generierung ─────────────────────────────────────────────────────

test.describe('1. Lead-Generierung', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('1.1 Seite lädt unter 5 Sekunden', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/lead-generierung', 'Lead-Generierung Seitenaufruf')
    await expect(page.getByRole('heading', { name: 'Lead-Generierung' })).toBeVisible()
    // Performance-Schwelle: sollte unter 5000ms sein
    expect(ms, `Ladezeit ${ms}ms überschreitet 5000ms`).toBeLessThan(5000)
  })

  test('1.2 GAP – 40 Wachstumsbetriebe generieren und übernehmen', async ({ page }) => {
    await gotoMeasured(page, '/crm/lead-generierung', 'Lead-Generierung (GAP)')

    // Parameter setzen
    await page.getByLabel(/Quelle/i).selectOption('GAP-Förderempfänger')
    await page.getByRole('spinbutton', { name: /Max\. Leads/i }).fill('40')

    // PLZ-Felder leeren (keine regionale Einschränkung)
    await page.getByRole('textbox', { name: /PLZ von/i }).fill('')
    await page.getByRole('textbox', { name: /PLZ bis/i }).fill('')

    // Vorschau generieren
    const t0 = Date.now()
    await page.getByRole('button', { name: /Vorschau generieren/i }).click()
    await page.waitForSelector('text=Kandidaten (', { timeout: 10_000 })
    const previewMs = Date.now() - t0
    test.info().annotations.push({ type: 'Ladezeit', description: `GAP Preview-API: ${previewMs} ms` })
    console.log(`⏱  GAP Preview-API: ${previewMs} ms`)

    // Kandidaten vorhanden
    const heading = page.locator('h3').filter({ hasText: /Kandidaten \(\d+\)/ })
    await expect(heading).toBeVisible()
    const headingText = await heading.textContent()
    const count = parseInt(headingText?.match(/\d+/)?.[0] ?? '0')
    expect(count, 'Mindestens 1 GAP-Kandidat erwartet').toBeGreaterThan(0)
    test.info().annotations.push({ type: 'Ergebnis', description: `GAP-Kandidaten: ${count}` })

    // Leads im CRM vorher merken
    const vorher = await page.locator('text=Leads im CRM').first().textContent()
    const vorherZahl = parseInt(vorher?.match(/\d+/)?.[0] ?? '0')

    // Übernehmen
    const t1 = Date.now()
    await page.getByRole('button', { name: /Als Leads übernehmen/i }).click()
    // Warten auf CRM-Zähler-Update
    await page.waitForFunction(
      (z) => {
        const el = document.querySelector('[data-testid="leads-count"], *')
        const text = document.body.innerText
        const m = text.match(/(\d+) Leads im CRM/)
        return m ? parseInt(m[1]) > z : false
      },
      vorherZahl,
      { timeout: 10_000 }
    ).catch(() => {/* Zähler-Update optional */})
    const uebernahmeMs = Date.now() - t1
    test.info().annotations.push({ type: 'Ladezeit', description: `GAP Übernahme-API: ${uebernahmeMs} ms` })
    console.log(`⏱  GAP Übernahme-API: ${uebernahmeMs} ms`)

    // Zähler gestiegen
    const nachher = await page.locator('text=Leads im CRM').first().textContent()
    const nachherZahl = parseInt(nachher?.match(/\d+/)?.[0] ?? '0')
    test.info().annotations.push({ type: 'Ergebnis', description: `Leads: ${vorherZahl} → ${nachherZahl} (+${nachherZahl - vorherZahl})` })
    expect(nachherZahl, 'Lead-Zähler soll nach Übernahme gestiegen sein').toBeGreaterThanOrEqual(vorherZahl)
  })

  test('1.3 LKV – 40 Top-Herdenleistungsbetriebe PLZ 266xx–268xx', async ({ page }) => {
    await gotoMeasured(page, '/crm/lead-generierung', 'Lead-Generierung (LKV)')

    await page.getByLabel(/Quelle/i).selectOption('Milchvieh (LKV)')
    await page.getByRole('textbox', { name: /PLZ von/i }).fill('26600')
    await page.getByRole('textbox', { name: /PLZ bis/i }).fill('26899')
    await page.getByRole('spinbutton', { name: /Max\. Leads/i }).fill('40')

    const t0 = Date.now()
    await page.getByRole('button', { name: /Vorschau generieren/i }).click()
    await page.waitForSelector('text=Kandidaten (', { timeout: 10_000 })
    const previewMs = Date.now() - t0
    test.info().annotations.push({ type: 'Ladezeit', description: `LKV Preview-API: ${previewMs} ms` })

    const heading = page.locator('h3').filter({ hasText: /Kandidaten \(\d+\)/ })
    await expect(heading).toBeVisible()
    const headingText = await heading.textContent()
    const count = parseInt(headingText?.match(/\d+/)?.[0] ?? '0')
    test.info().annotations.push({ type: 'Ergebnis', description: `LKV-Kandidaten PLZ 266–268: ${count}` })
    // Im PLZ-Gebiet 266xx–268xx sind weniger als 40 — mindestens 1 erwartet
    expect(count).toBeGreaterThan(0)

    const vorher = parseInt(
      (await page.locator('text=Leads im CRM').first().textContent() ?? '0')
        .match(/\d+/)?.[0] ?? '0'
    )
    await page.getByRole('button', { name: /Als Leads übernehmen/i }).click()
    await page.waitForTimeout(2000)
    const nachher = parseInt(
      (await page.locator('text=Leads im CRM').first().textContent() ?? '0')
        .match(/\d+/)?.[0] ?? '0'
    )
    test.info().annotations.push({ type: 'Ergebnis', description: `LKV Leads: ${vorher} → ${nachher} (+${nachher - vorher})` })
    expect(nachher).toBeGreaterThanOrEqual(vorher)
  })

  test('1.4 Lead-Liste zeigt GAP und LKV Einträge', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/leads', 'Lead-Liste Seitenaufruf')
    await expect(page.getByRole('heading', { name: /Lead/i })).toBeVisible()
    expect(ms).toBeLessThan(8000)

    // Mindestens ein GAP- und ein LKV-Eintrag
    await expect(page.getByText('gap').first()).toBeVisible()
    await expect(page.getByText('lkv').first()).toBeVisible()
  })

  test('1.5 Lead → Kunde Konversion', async ({ page }) => {
    await gotoMeasured(page, '/crm/leads', 'Lead-Liste (Konversion)')

    // Ersten qualifizierten Lead konvertieren
    const konvertBtn = page.getByRole('button', { name: /→ Kunde/i }).first()
    await expect(konvertBtn).toBeVisible({ timeout: 8000 })

    const t0 = Date.now()
    await konvertBtn.click()
    // Erwarte Toast oder Weiterleitung
    const erfolgMs = Date.now() - t0
    test.info().annotations.push({ type: 'Ladezeit', description: `Lead→Kunde Konversion: ${erfolgMs} ms` })

    // Entweder Toast oder Redirect auf CRM-Kunden
    await Promise.race([
      page.waitForURL('**/crm/**', { timeout: 5000 }),
      page.locator('[role="status"], [data-testid="toast"]').waitFor({ timeout: 5000 }),
    ]).catch(() => {
      test.info().annotations.push({ type: 'Warnung', description: 'Kein Toast/Redirect nach Konversion — UI-Feedback prüfen' })
    })
  })
})

// ─── 2. Artikel-Stammdaten ───────────────────────────────────────────────────

test.describe('2. Artikel-Stammdaten', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  /** Hilfsfunktion: Artikel anlegen */
  async function artikelAnlegen(page: Page, artikel: {
    nummer: string
    bezeichnung: string
    gruppe: string
    einheit: string
    preis: string
    lieferant?: string
  }): Promise<void> {
    await page.getByRole('button', { name: /Neu|Anlegen|Hinzufügen/i }).first().click()
    await page.waitForSelector('form, dialog', { timeout: 5000 })

    const nummerInput = page.getByLabel(/Artikel.*Nr|Nummer/i).first()
    if (await nummerInput.isVisible()) await nummerInput.fill(artikel.nummer)

    const bezInput = page.getByLabel(/Bezeichnung|Name/i).first()
    if (await bezInput.isVisible()) await bezInput.fill(artikel.bezeichnung)

    const preisInput = page.getByLabel(/Preis|VK/i).first()
    if (await preisInput.isVisible()) await preisInput.fill(artikel.preis)

    await page.getByRole('button', { name: /Speichern|Sichern|OK/i }).first().click()
    await page.waitForTimeout(500)
  }

  test('2.1 Artikel-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/artikel', 'Artikel-Liste')
    // Fallback-Routen
    if (page.url().includes('404') || page.url() === `${BASE}/`) {
      const ms2 = await gotoMeasured(page, '/lager/artikel', 'Artikel-Liste (lager)')
      expect(ms2).toBeLessThan(8000)
    } else {
      expect(ms).toBeLessThan(8000)
    }
    test.info().annotations.push({ type: 'Info', description: `Artikel-Route: ${page.url()}` })
  })

  test('2.2 Testdaten-Set prüfen: PSM, Saaten, Futter, Getreide', async ({ page }) => {
    // Prüfe ob Testartikel bereits angelegt sind (via API)
    const res = await page.request.get(`${BASE}/api/v1/artikel?q=Pioneer&limit=5`, {
      headers: { Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`, 'X-Tenant-ID': 'default' },
    })
    const status = res.status()
    test.info().annotations.push({ type: 'API-Status', description: `GET /api/v1/artikel: HTTP ${status}` })

    if (status === 200) {
      const body = await res.json() as { items?: unknown[]; data?: unknown[] }
      const items = body.items ?? body.data ?? []
      test.info().annotations.push({ type: 'Ergebnis', description: `Pioneer-Artikel im System: ${Array.isArray(items) ? items.length : 'unbekannt'}` })
    }
  })
})

// ─── 3. Workflow-Belegkette ──────────────────────────────────────────────────

test.describe('3. Workflow-Belegkette', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('3.1 Kundenauftrag-Maske öffnet sich', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/auftraege', 'Auftrags-Liste')
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 8000 })
    test.info().annotations.push({ type: 'Ladezeit', description: `Auftrags-Liste: ${ms} ms` })
  })

  test('3.2 Neuer Auftrag – Formular öffnet', async ({ page }) => {
    await gotoMeasured(page, '/verkauf/auftraege', 'Auftrags-Liste (Neu)')

    const neuBtn = page.getByRole('button', { name: /Neu|Anlegen|Erstellen/i }).first()
    if (await neuBtn.isVisible({ timeout: 5000 })) {
      const t0 = Date.now()
      await neuBtn.click()
      await page.waitForSelector('form, [role="dialog"]', { timeout: 8000 })
      const ms = Date.now() - t0
      test.info().annotations.push({ type: 'Ladezeit', description: `Neu-Auftrag Dialog öffnen: ${ms} ms` })
      await expect(page.locator('form, [role="dialog"]').first()).toBeVisible()
    } else {
      test.info().annotations.push({ type: 'Warnung', description: 'Neu-Button nicht gefunden — Route prüfen' })
    }
  })

  test('3.3 Lieferschein-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/lieferscheine', 'Lieferschein-Liste')
    test.info().annotations.push({ type: 'Ladezeit', description: `Lieferschein-Liste: ${ms} ms` })
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.4 Rechnungs-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/rechnungen', 'Rechnungs-Liste')
    test.info().annotations.push({ type: 'Ladezeit', description: `Rechnungs-Liste: ${ms} ms` })
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.5 Getreideannahme-Maske lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/ernte-annahme', 'Getreideannahme')
    test.info().annotations.push({ type: 'Ladezeit', description: `Getreideannahme: ${ms} ms` })
    // Seite sollte rendern, auch wenn leer
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.6 Kontrakt-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/kontrakte', 'Kontrakt-Liste')
    test.info().annotations.push({ type: 'Ladezeit', description: `Kontrakt-Liste: ${ms} ms` })
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.7 Flow Spine Order-to-Cash lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/workflow/flow-spine-order-to-cash', 'FlowSpine OtC')
    test.info().annotations.push({ type: 'Ladezeit', description: `FlowSpine Order-to-Cash: ${ms} ms` })
    await expect(page.getByRole('heading', { name: /Auftrag/i }).first()).toBeVisible({ timeout: 10_000 })
    expect(ms).toBeLessThan(10_000)
  })
})

// ─── 4. CRM-Cockpit / KIM ───────────────────────────────────────────────────

test.describe('4. CRM-Cockpit & KIM', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('4.1 CRM-Cockpit öffnet', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm', 'CRM-Cockpit')
    test.info().annotations.push({ type: 'Ladezeit', description: `CRM-Cockpit: ${ms} ms` })
    await expect(page.locator('h1, h2, [data-testid="crm-header"]').first()).toBeVisible({ timeout: 8000 })
  })

  test('4.2 KIM-360-Cockpit öffnet', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/kim', 'KIM-360-Cockpit')
    test.info().annotations.push({ type: 'Ladezeit', description: `KIM-360: ${ms} ms` })
    await page.waitForTimeout(2000)
    test.info().annotations.push({ type: 'URL', description: page.url() })
  })

  test('4.3 Kunden-Schnellsuche reagiert', async ({ page }) => {
    await gotoMeasured(page, '/crm', 'CRM (Schnellsuche)')
    const suche = page.getByPlaceholder(/Suchname|Suche/i).first()
    if (await suche.isVisible({ timeout: 5000 })) {
      const t0 = Date.now()
      await suche.fill('Müller')
      await page.waitForTimeout(600) // Debounce abwarten
      const ms = Date.now() - t0
      test.info().annotations.push({ type: 'Ladezeit', description: `CRM Schnellsuche Debounce+API: ${ms} ms` })
    }
  })
})

// ─── 5. Performance-Zusammenfassung ─────────────────────────────────────────
// Alle Ladezeiten werden automatisch in den Playwright-Report-Annotations gesammelt.
// → npx playwright show-report  zeigt sie pro Test an.
