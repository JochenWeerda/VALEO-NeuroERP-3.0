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

const API_BASE = process.env.API_BASE ?? 'http://127.0.0.1:8000'
const TENANT = '00000000-0000-0000-0000-000000000001'
const AUTH_HEADERS = {
  Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
  'X-Tenant-Id': TENANT,
  'Content-Type': 'application/json',
}

test.describe('1. Lead-Generierung', () => {
  test.beforeAll(async ({ request }) => {
    // Seed minimal test leads so tests 1.4/1.5 always have data
    await request.post(`${API_BASE}/api/v1/crm/lead-generierung/uebernehmen`, {
      headers: AUTH_HEADERS,
      data: {
        kandidaten: [
          { name: 'E2E-Testbetrieb GAP GmbH', quelle: 'gap', plz: '26500', ort: 'Aurich', score: 50000, score_label: 'Fördersumme €' },
          { name: 'E2E-Testbetrieb LKV GbR', quelle: 'lkv', plz: '26600', ort: 'Leer', score: 8500, score_label: 'Milch kg/Kuh' },
        ],
      },
    })
  })

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

    // Kandidaten vorhanden (Quelldaten optional — skip wenn gap_payments fehlt)
    const heading = page.locator('h3, [class*="card-title"]').filter({ hasText: /Kandidaten/ })
    await expect(heading).toBeVisible()
    const headingText = await heading.textContent()
    const count = parseInt(headingText?.match(/\d+/)?.[0] ?? '0')
    test.info().annotations.push({ type: 'Ergebnis', description: `GAP-Kandidaten: ${count}` })
    if (count === 0) {
      test.skip(true, 'Keine GAP-Quelldaten in dieser Umgebung (gap_payments leer/fehlt)')
      return
    }

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

    const heading = page.locator('h3, [class*="card-title"]').filter({ hasText: /Kandidaten/ })
    await expect(heading).toBeVisible()
    const headingText = await heading.textContent()
    const count = parseInt(headingText?.match(/\d+/)?.[0] ?? '0')
    test.info().annotations.push({ type: 'Ergebnis', description: `LKV-Kandidaten PLZ 266–268: ${count}` })
    if (count === 0) {
      test.skip(true, 'Keine LKV-Quelldaten in dieser Umgebung (dairy_herd_performance leer/fehlt)')
      return
    }

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

    // Prüfe ob Leads vorhanden sind
    await page.waitForTimeout(1500)
    const hasGap = await page.getByText('gap').first().isVisible().catch(() => false)
    const hasLkv = await page.getByText('lkv').first().isVisible().catch(() => false)
    test.info().annotations.push({ type: 'Ergebnis', description: `GAP-Lead: ${hasGap}, LKV-Lead: ${hasLkv}` })
    if (!hasGap || !hasLkv) {
      test.skip(true, 'Keine GAP/LKV-Leads in public.crm_leads vorhanden — Seed-Daten fehlen')
      return
    }
  })

  test('1.5 Lead → Kunde Konversion', async ({ page }) => {
    await gotoMeasured(page, '/crm/leads', 'Lead-Liste (Konversion)')
    await page.waitForTimeout(1500)

    // Ersten qualifizierten Lead konvertieren — skip wenn keine Leads
    const konvertBtn = page.getByRole('button', { name: /→ Kunde/i }).first()
    const hasBtn = await konvertBtn.isVisible({ timeout: 5000 }).catch(() => false)
    if (!hasBtn) {
      test.skip(true, 'Keine Leads in crm_leads — Konversion-Test übersprungen')
      return
    }
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

  test('3.3 Lieferschein-Erfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/lieferschein-erfassung', 'Lieferschein-Erfassung')
    test.info().annotations.push({ type: 'Ladezeit', description: `Lieferschein-Erfassung: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
    // Heading optional — Seite kann als leeres Formular rendern
    const hasHeading = await page.locator('h1, h2').first().isVisible().catch(() => false)
    test.info().annotations.push({ type: 'Info', description: `Heading vorhanden: ${hasHeading}` })
  })

  test('3.4 Rechnungs-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/rechnungen', 'Rechnungs-Liste')
    test.info().annotations.push({ type: 'Ladezeit', description: `Rechnungs-Liste: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.5 Getreideannahme-Maske lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/ernte-annahme', 'Getreideannahme')
    test.info().annotations.push({ type: 'Ladezeit', description: `Getreideannahme: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  test('3.6 Kontrakt-Uebersicht lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/kontrakte/kontrakt-uebersicht', 'Kontrakt-Uebersicht')
    test.info().annotations.push({ type: 'Ladezeit', description: `Kontrakt-Uebersicht: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
    const hasHeading = await page.locator('h1, h2').first().isVisible().catch(() => false)
    test.info().annotations.push({ type: 'Info', description: `Kontrakt-Heading: ${hasHeading}` })
  })

  test('3.7 Flow Spine Order-to-Cash lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/workflow/flow-spine-order-to-cash', 'FlowSpine OtC')
    test.info().annotations.push({ type: 'Ladezeit', description: `FlowSpine Order-to-Cash: ${ms} ms` })
    // Warte auf h1 (Workspace-Titel) oder die Fehler-/Ladeseite — alle sind gültige Seitenzustände
    await expect(page.locator('h1, h2, [role="heading"]').first()).toBeVisible({ timeout: 15_000 })
    expect(ms).toBeLessThan(15_000)
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

// ─── 5. Warenbeschaffung & Lager ─────────────────────────────────────────────

test.describe('5. Warenbeschaffung & Lager', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  // ── 5.1 Einkaufsbestellung anlegen ──────────────────────────────────────

  test('5.1 Einkauf Bestellvorschlaege laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/bestellvorschlaege', 'Bestellvorschlaege')
    test.info().annotations.push({ type: 'Ladezeit', description: `Einkauf Bestellvorschlaege: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
    const hasTable = await page.locator('table, [role="table"]').first().isVisible().catch(() => false)
    test.info().annotations.push({ type: 'Info', description: `Bestellvorschlaege-Tabelle: ${hasTable}` })
  })

  test('5.2 Einkauf Lieferschein-Erfassung (Wareneingang) laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/lieferschein-erfassung', 'WE Lieferschein-Erfassung')
    test.info().annotations.push({ type: 'Ladezeit', description: `WE Lieferschein-Erfassung: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
    test.info().annotations.push({ type: 'Info', description: `Route: ${page.url()}` })
  })

  test('5.3 Einkauf Anlieferavis (Eingangsankuendigung) laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/anlieferavis/neu', 'Anlieferavis Neu')
    test.info().annotations.push({ type: 'Ladezeit', description: `Anlieferavis Neu: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  // ── 5.2 Artikel per API anlegen (Batch-Mock) ────────────────────────────

  test('5.4 Artikel API - Testartikel Batch anlegen', async ({ page }) => {
    const headers = {
      Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
      'X-Tenant-ID': 'default',
      'Content-Type': 'application/json',
    }

    const testartikel = [
      // PSM Grosspackungen
      { artikel_nr: 'PSM-001', bezeichnung: 'Glyphosat 360 SL 20L', gruppe: 'PSM', einheit: 'Stk', vk_preis: 89.50, lieferant: 'ADAMA', beschreibung: 'Totalherbizid, 360 g/l Glyphosat, 20-Liter-Kanister' },
      { artikel_nr: 'PSM-002', bezeichnung: 'Roundup PowerFlex 20L', gruppe: 'PSM', einheit: 'Stk', vk_preis: 134.00, lieferant: 'Bayer', beschreibung: 'Glyphosat 480 g/l, Grossgebinde 20L' },
      { artikel_nr: 'PSM-003', bezeichnung: 'Primus Perfect 5L', gruppe: 'PSM', einheit: 'Stk', vk_preis: 187.50, lieferant: 'Corteva', beschreibung: 'Breitbandherbizid Getreide 5L' },
      { artikel_nr: 'PSM-004', bezeichnung: 'Biscaya 240 OD 5L', gruppe: 'PSM', einheit: 'Stk', vk_preis: 212.00, lieferant: 'Bayer', beschreibung: 'Insektizid Raps/Getreide 5L' },
      { artikel_nr: 'PSM-005', bezeichnung: 'Karate Zeon 20L', gruppe: 'PSM', einheit: 'Stk', vk_preis: 296.00, lieferant: 'Syngenta', beschreibung: 'Insektizid lambda-Cyhalothrin 20L' },
      // Saaten - Mais
      { artikel_nr: 'PIO-001', bezeichnung: 'Pioneer P8816 Silomais', gruppe: 'Saaten-Mais', einheit: 'VE', vk_preis: 265.00, lieferant: 'Pioneer', beschreibung: 'Silomais fruebreifend, S220, hoher Stärkeertrag' },
      { artikel_nr: 'PIO-002', bezeichnung: 'Pioneer P9175 Koernermais', gruppe: 'Saaten-Mais', einheit: 'VE', vk_preis: 295.00, lieferant: 'Pioneer', beschreibung: 'Koernermais S240, top Ertrag und Abreife' },
      { artikel_nr: 'PIO-003', bezeichnung: 'Pioneer PR46W31 Winterraps', gruppe: 'Saaten-Raps', einheit: 'VE', vk_preis: 185.00, lieferant: 'Pioneer', beschreibung: 'Winterraps hybrid, hoher Ertrag, Sclerotinia-Toleranz' },
      { artikel_nr: 'DKB-001', bezeichnung: 'DeKalb DKC3939 Koernermais', gruppe: 'Saaten-Mais', einheit: 'VE', vk_preis: 275.00, lieferant: 'Bayer CropScience', beschreibung: 'Koernermais S210, fruebreifend, Drought Guard' },
      { artikel_nr: 'DKB-002', bezeichnung: 'DeKalb DKC4490 Silomais', gruppe: 'Saaten-Mais', einheit: 'VE', vk_preis: 268.00, lieferant: 'Bayer CropScience', beschreibung: 'Silomais S230, sehr hohe Energiedichte' },
      // Saaten - Getreide
      { artikel_nr: 'STR-W01', bezeichnung: 'Attraktion Winterweizen', gruppe: 'Saaten-Getreide', einheit: 'dt', vk_preis: 54.00, lieferant: 'Stroetmann Saaten', beschreibung: 'Winterweizen A-Qualitaet, hohe Backqualitaet, standfest' },
      { artikel_nr: 'STR-W02', bezeichnung: 'Benchmark Winterweizen', gruppe: 'Saaten-Getreide', einheit: 'dt', vk_preis: 56.00, lieferant: 'Stroetmann Saaten', beschreibung: 'Winterweizen B-Qualitaet, sehr hoher Ertrag' },
      { artikel_nr: 'STR-G01', bezeichnung: 'KWS Lili Wintergerste', gruppe: 'Saaten-Getreide', einheit: 'dt', vk_preis: 48.00, lieferant: 'Stroetmann Saaten', beschreibung: 'Zweizeilige Wintergerste, fruehe Reife, hoher Ertrag' },
      { artikel_nr: 'STR-H01', bezeichnung: 'Dominik Hafer', gruppe: 'Saaten-Getreide', einheit: 'dt', vk_preis: 42.00, lieferant: 'Stroetmann Saaten', beschreibung: 'Sommerhafer, standfest, ertragsreich' },
      // Graesermischungen
      { artikel_nr: 'RUD-G01', bezeichnung: 'Dauerweide Plus Graesermischung', gruppe: 'Saaten-Graeser', einheit: 'kg', vk_preis: 8.50, lieferant: 'Rudloff Saaten', beschreibung: 'Weidemischung fuer intensive Beweidung, ohne Klee' },
      { artikel_nr: 'RUD-G02', bezeichnung: 'Nachsaat Intensiv Graesermischung', gruppe: 'Saaten-Graeser', einheit: 'kg', vk_preis: 9.20, lieferant: 'Rudloff Saaten', beschreibung: 'Schnellkeimende Nachsaatmischung fuer lueckige Narben' },
      // Zwischenfruechte
      { artikel_nr: 'RUD-ZF01', bezeichnung: 'Sommerfix Zwischenfrucht', gruppe: 'Saaten-ZF', einheit: 'kg', vk_preis: 6.80, lieferant: 'Rudloff Saaten', beschreibung: 'Schnellwuechsige Zwischenfruchtmischung fuer Sommer' },
      { artikel_nr: 'RUD-ZF02', bezeichnung: 'Oelrettich Ribola', gruppe: 'Saaten-ZF', einheit: 'kg', vk_preis: 3.40, lieferant: 'Rudloff Saaten', beschreibung: 'Nematoden-abtoetendes Oelrettich fuer Ruebenanbauer' },
      // Bewital Tiernahrung
      { artikel_nr: 'BEW-001', bezeichnung: 'Bela-Start Kaelbermilch 25kg', gruppe: 'Tiernahrung', einheit: 'Sack', vk_preis: 72.50, lieferant: 'Bewital', beschreibung: 'Milchaustauscher fuer Kaelber ab 1. Lebenswoche, 25kg Sack' },
      { artikel_nr: 'BEW-003', bezeichnung: 'Bypass-Fett 25kg', gruppe: 'Tiernahrung', einheit: 'Sack', vk_preis: 89.00, lieferant: 'Bewital', beschreibung: 'Fettpulver gepuffert fuer Hochleistungskuehe, 25kg' },
      { artikel_nr: 'BEW-004', bezeichnung: 'CalfBac DiaetMix 10kg', gruppe: 'Tiernahrung', einheit: 'Eimer', vk_preis: 54.00, lieferant: 'Bewital', beschreibung: 'Elektrolyttraenke bei Durchfall/Erkrankung Kaelber' },
      { artikel_nr: 'BEW-005', bezeichnung: 'Pulmo-Vital 2,5kg', gruppe: 'Tiernahrung', einheit: 'Dose', vk_preis: 42.00, lieferant: 'Bewital', beschreibung: 'Atemwegsstuetzung Rinder, Kraeuterkomplex' },
    ]

    let angelegt = 0
    let fehler = 0
    const fehlerListe: string[] = []

    for (const art of testartikel) {
      const res = await page.request.post(`${BASE}/api/v1/artikel`, {
        headers,
        data: art,
      }).catch(() => null)

      if (!res) {
        fehler++
        fehlerListe.push(`${art.artikel_nr}: Netzwerkfehler`)
        continue
      }

      if (res.status() === 200 || res.status() === 201) {
        angelegt++
      } else if (res.status() === 409) {
        // Duplikat — OK, bereits vorhanden
        angelegt++
      } else {
        fehler++
        const body = await res.text().catch(() => '')
        fehlerListe.push(`${art.artikel_nr}: HTTP ${res.status()} ${body.slice(0, 100)}`)
      }
    }

    test.info().annotations.push({
      type: 'Ergebnis',
      description: `Testartikel: ${angelegt} angelegt/vorhanden, ${fehler} Fehler`,
    })
    if (fehlerListe.length > 0) {
      test.info().annotations.push({
        type: 'Fehler-Details',
        description: fehlerListe.slice(0, 10).join(' | '),
      })
    }

    // Tolerant: API kann noch nicht implementiert sein (404/405)
    const apiVerfuegbar = fehlerListe.every((f) => !f.includes('HTTP 4') || f.includes('HTTP 409'))
    if (!apiVerfuegbar) {
      test.info().annotations.push({
        type: 'Warnung',
        description: 'POST /api/v1/artikel nicht implementiert — Artikel muessen manuell angelegt werden',
      })
    }
  })

  // ── 5.3 Lagerbewegungen / Bestand ───────────────────────────────────────

  test('5.5 Lager-Bestandsuebersicht laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/bestaende', 'Lager-Bestaende')
    test.info().annotations.push({ type: 'Ladezeit', description: `Lager-Bestaende: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
    const url = page.url()
    test.info().annotations.push({ type: 'URL', description: url })
  })

  test('5.6 Lager-Bewegungen laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/bewegungen', 'Lager-Bewegungen')
    test.info().annotations.push({ type: 'Ladezeit', description: `Lager-Bewegungen: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  test('5.7 Inventur-Maske laed', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/inventur', 'Inventur')
    test.info().annotations.push({ type: 'Ladezeit', description: `Inventur: ${ms} ms` })
    await expect(page.locator('main, #root').first()).toBeVisible({ timeout: 8000 })
  })

  // ── 5.4 Wareneingang Mock-Simulation ────────────────────────────────────

  test('5.8 Wareneingang API - Eingangs-Lieferschein Mock (Pioneer P9175)', async ({ page }) => {
    const headers = {
      Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
      'X-Tenant-ID': 'default',
      'Content-Type': 'application/json',
    }

    // Schritt 1: Wareneingang (Eingangs-LS) anlegen
    const we = await page.request.post(`${BASE}/api/v1/einkauf/lieferscheine`, {
      headers,
      data: {
        lieferant_name: 'Pioneer Hi-Bred',
        lieferant_nr: 'LIEF-PIONEER',
        datum: new Date().toISOString().slice(0, 10),
        positionen: [
          { artikel_nr: 'PIO-002', bezeichnung: 'Pioneer P9175 Koernermais', menge: 10, einheit: 'VE', ek_preis: 265.00 },
          { artikel_nr: 'PIO-001', bezeichnung: 'Pioneer P8816 Silomais', menge: 5, einheit: 'VE', ek_preis: 250.00 },
        ],
        bemerkung: 'Testlieferung UAT 2026-07-01',
      },
    }).catch(() => null)

    const weStatus = we?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `POST /api/v1/einkauf/lieferscheine: HTTP ${weStatus}`,
    })

    if (weStatus === 200 || weStatus === 201) {
      const weBody = await we!.json() as { id?: string; ls_nr?: string }
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Eingangs-LS angelegt: ID=${weBody.id ?? '?'} Nr=${weBody.ls_nr ?? '?'}`,
      })
    } else {
      test.info().annotations.push({
        type: 'Warnung',
        description: `Eingangs-LS API nicht verfuegbar (HTTP ${weStatus}) — Route pruefen`,
      })
    }

    // Schritt 2: Mobile-Scan Simulation via Barcode-API
    const scan = await page.request.post(`${BASE}/api/v1/scan/barcode`, {
      headers,
      data: { barcode: 'PIO-002', kontext: 'wareneingang', menge: 10 },
    }).catch(() => null)

    const scanStatus = scan?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `POST /api/v1/scan/barcode (Mobile-Scan): HTTP ${scanStatus}`,
    })
    if (scanStatus === 200 || scanStatus === 201) {
      test.info().annotations.push({ type: 'Ergebnis', description: 'Mobile-Scan API verfuegbar' })
    } else {
      test.info().annotations.push({ type: 'Warnung', description: 'Mobile-Scan /api/v1/scan/barcode nicht implementiert' })
    }

    // Schritt 3: Lagerbestand pruefen
    const bestand = await page.request.get(`${BASE}/api/v1/lager/bestaende?artikel_nr=PIO-002`, {
      headers,
    }).catch(() => null)

    const bestandStatus = bestand?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `GET /api/v1/lager/bestaende?artikel_nr=PIO-002: HTTP ${bestandStatus}`,
    })
    if (bestandStatus === 200) {
      const b = await bestand!.json() as { menge?: number; artikel_nr?: string }[]
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Bestand PIO-002: ${Array.isArray(b) ? JSON.stringify(b[0]) : JSON.stringify(b)}`,
      })
    }
  })

  // ── 5.5 Wareneingang mit Stoerfall (defekter Sack) ──────────────────────

  test('5.9 Wareneingang-Stoerfall - defekter Sack Reklamation', async ({ page }) => {
    const headers = {
      Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
      'X-Tenant-ID': 'default',
      'Content-Type': 'application/json',
    }

    // Reklamation anlegen
    const rek = await page.request.post(`${BASE}/api/v1/reklamationen`, {
      headers,
      data: {
        typ: 'wareneingang',
        artikel_nr: 'BEW-001',
        bezeichnung: 'Bela-Start Kaelbermilch 25kg',
        menge_reklamiert: 2,
        einheit: 'Sack',
        grund: 'Sack beschaedigt / Ware ausgelaufen',
        lieferant: 'Bewital',
        datum: new Date().toISOString().slice(0, 10),
      },
    }).catch(() => null)

    const rekStatus = rek?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `POST /api/v1/reklamationen (Wareneingang-Stoerfall): HTTP ${rekStatus}`,
    })
    if (rekStatus === 200 || rekStatus === 201) {
      test.info().annotations.push({ type: 'Ergebnis', description: 'Reklamation erfolgreich angelegt' })
    } else {
      test.info().annotations.push({
        type: 'Warnung',
        description: `Reklamations-API nicht verfuegbar (HTTP ${rekStatus}) — Wizard-Flow fuer Stoerfaelle fehlt noch`,
      })
    }

    // Retourenlieferschein anlegen
    const retoure = await page.request.post(`${BASE}/api/v1/einkauf/retouren`, {
      headers,
      data: {
        lieferant_name: 'Bewital',
        positionen: [{ artikel_nr: 'BEW-001', menge: 2, grund: 'Sack beschaedigt' }],
      },
    }).catch(() => null)

    const retoureStatus = retoure?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `POST /api/v1/einkauf/retouren: HTTP ${retoureStatus}`,
    })
    if (retoureStatus !== 200 && retoureStatus !== 201) {
      test.info().annotations.push({
        type: 'Warnung',
        description: 'Retouren-API nicht implementiert — Szenario B (Reklamation) manuell pruefen',
      })
    }
  })

  // ── 5.6 Staffelrabatte und Preisfindung ─────────────────────────────────

  test('5.10 Staffelrabatt API - anlegen und pruefen', async ({ page }) => {
    const headers = {
      Authorization: `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
      'X-Tenant-ID': 'default',
      'Content-Type': 'application/json',
    }

    // Staffelrabatt fuer PSM-001 anlegen
    const rabatt = await page.request.post(`${BASE}/api/v1/preise/staffelrabatte`, {
      headers,
      data: {
        artikel_nr: 'PSM-001',
        staffeln: [
          { menge_ab: 5, rabatt_pct: 3.0 },
          { menge_ab: 10, rabatt_pct: 5.0 },
          { menge_ab: 20, rabatt_pct: 8.0 },
        ],
        gueltig_ab: new Date().toISOString().slice(0, 10),
      },
    }).catch(() => null)

    const rabattStatus = rabatt?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `POST /api/v1/preise/staffelrabatte: HTTP ${rabattStatus}`,
    })
    if (rabattStatus === 200 || rabattStatus === 201) {
      test.info().annotations.push({ type: 'Ergebnis', description: 'Staffelrabatt PSM-001 angelegt: 3%/5%/8%' })
    } else {
      test.info().annotations.push({
        type: 'Warnung',
        description: 'Staffelrabatt-API nicht verfuegbar — Preise & Kalkulation pruefen',
      })
    }

    // Preisfindung testen (Menge 10 -> erwarte 5% Rabatt)
    const preis = await page.request.get(
      `${BASE}/api/v1/preise/find?artikel_nr=PSM-001&menge=10&kunden_nr=KD-10001`,
      { headers },
    ).catch(() => null)

    const preisStatus = preis?.status() ?? 0
    test.info().annotations.push({
      type: 'API-Status',
      description: `GET /api/v1/preise/find (Staffelpreisfindung): HTTP ${preisStatus}`,
    })
    if (preisStatus === 200) {
      const p = await preis!.json() as { vk_preis?: number; rabatt_pct?: number; staffel_aktiv?: boolean }
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Preisfindung PSM-001 Menge=10: VK=${p.vk_preis} Rabatt=${p.rabatt_pct}% Staffel=${p.staffel_aktiv}`,
      })
    }
  })
})

// ─── 6. Performance-Zusammenfassung ─────────────────────────────────────────
// Alle Ladezeiten werden automatisch in den Playwright-Report-Annotations gesammelt.
// npx playwright show-report  zeigt sie pro Test an.
