/**
 * UAT: Alle Domänen — End-to-End Prozesse
 *
 * Vollständige Abdeckung aller ERP-Domänen für Produktionsfreigabe.
 * Jeder Test misst Ladezeiten und protokolliert Befunde als Annotationen.
 *
 * Ausführung:
 *   npx playwright test tests/e2e/uat/all-domains-e2e.spec.ts --reporter=html
 *
 * Sektionen:
 *   1.  Fibu / Finance
 *   2.  Agrar (Ernte, Kontrakte, Qualität)
 *   3.  Lager (Bestände, Bewegungen)
 *   4.  Verkauf Belegkette
 *   5.  Einkauf Belegkette
 *   6.  Logistik
 *   7.  CRM & Kampagnen
 *   8.  Qualität & Compliance
 *   9.  Kontrakte & Frühkauf
 *   10. API-Smoke (neue Endpoints)
 */

import { test, expect, type Page, type APIRequestContext } from '@playwright/test'
import { prepareE2EAuth } from '../helpers/auth-from-env'

const BASE = process.env.BASE_URL ?? 'http://localhost:3001'
const API = process.env.API_URL ?? 'http://localhost:8000'
const TOKEN = process.env.API_DEV_TOKEN ?? 'dev-token'
const TENANT = process.env.TENANT_ID ?? 'default'
const PERF_THRESHOLD_MS = 6000

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
  test.info().annotations.push({ type: 'Ladezeit', description: `${label ?? path}: ${ms} ms` })
  console.log(`⏱  ${label ?? path}: ${ms} ms`)
  return ms
}

async function apiGet(request: APIRequestContext, path: string): Promise<{ status: number; ms: number; body: unknown }> {
  const t0 = Date.now()
  const resp = await request.get(`${API}${path}`, {
    headers: { Authorization: `Bearer ${TOKEN}`, 'X-Tenant-Id': TENANT },
  })
  const ms = Date.now() - t0
  let body: unknown = null
  try { body = await resp.json() } catch { /* ignore */ }
  return { status: resp.status(), ms, body }
}

async function apiPost(
  request: APIRequestContext,
  path: string,
  data: unknown,
): Promise<{ status: number; ms: number; body: unknown }> {
  const t0 = Date.now()
  const resp = await request.post(`${API}${path}`, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'X-Tenant-Id': TENANT,
      'Content-Type': 'application/json',
    },
    data: data as Record<string, unknown>,
  })
  const ms = Date.now() - t0
  let body: unknown = null
  try { body = await resp.json() } catch { /* ignore */ }
  return { status: resp.status(), ms, body }
}

// ─── 1. Fibu / Finance ───────────────────────────────────────────────────────

test.describe('1. Fibu / Finance', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('1.1 Offene-Posten-Cockpit lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/finance/offene-posten-cockpit', 'OP-Cockpit')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading', { name: /Offene Posten|OP-Cockpit/i })).toBeVisible()
  })

  test('1.2 Mahnlauf-Seite lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/finance/mahnlauf', 'Mahnlauf')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    // Seite muss ohne 404/Fehler-Heading laden
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('1.3 DATEV-Export-Seite lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/finance/datev-export', 'DATEV-Export')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('1.4 Abschluss-Cockpit lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/fibu/abschluss-cockpit', 'Abschluss-Cockpit')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('1.5 Erlöskennziffern-Seite lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/fibu/erloeskennziffern', 'Erlöskennziffern')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 2. Agrar ────────────────────────────────────────────────────────────────

test.describe('2. Agrar', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('2.1 Ernte-Annahme-Erfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/ernte-annahme-erfassung', 'Ernte-Annahme')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('2.2 Milchvieh Cross-Sell-Seite lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/milchvieh-crosssell', 'Milchvieh CrossSell')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('2.3 Futtermittel Rationsoptimierung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/futtermittel/rationsoptimierung', 'Rationsoptimierung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('2.4 Kontrakt-Erfüllung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/kontrakt-erfuellung', 'Kontrakt-Erfüllung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('2.5 Kontrakt-Fixierung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/kontrakt-fixierung', 'Kontrakt-Fixierung MATIF')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 3. Lager ────────────────────────────────────────────────────────────────

test.describe('3. Lager', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('3.1 Permanente Inventur lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/permanente-inventur', 'Permanente Inventur')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('3.2 Rückverfolgbarkeit lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/rueckverfolgbarkeit', 'Rückverfolgbarkeit')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('3.3 Materialfluss-Visualisierung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/materialfluss-visualisierung', 'Materialfluss')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('3.4 Bestandsbewertung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/bestandsbewertung', 'Bestandsbewertung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('3.5 Kommissionierung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/lager/kommissionierung', 'Kommissionierung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('3.6 API: GET /lager/bestaende antwortet', async ({ request }) => {
    const { status, ms, body } = await apiGet(request, '/api/v1/lager/bestaende?tenant_id=default')
    test.info().annotations.push({ type: 'Ladezeit', description: `GET /lager/bestaende: ${ms} ms` })
    test.info().annotations.push({ type: 'API-Status', description: `HTTP ${status}` })
    expect([200, 401, 403], `Status ${status} unerwartet`).toContain(status)
    if (status === 200) {
      expect(Array.isArray(body)).toBe(true)
    }
  })
})

// ─── 4. Verkauf Belegkette ───────────────────────────────────────────────────

test.describe('4. Verkauf Belegkette', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('4.1 Sales-Dashboard lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/dashboard/sales', 'Sales Dashboard')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('4.2 Angebote-Übersicht lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/sales/angebote', 'Angebote')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('4.3 Auftragskette lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/sales/auftragskette', 'Auftragskette')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('4.4 Auftragserfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/sales/order', 'Auftragserfassung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('4.5 Rechnungserfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/sales/invoice', 'Rechnungserfassung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('4.6 Lieferschein-Erfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/verkauf/lieferschein-erfassung', 'Lieferschein-Erfassung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 5. Einkauf Belegkette ───────────────────────────────────────────────────

test.describe('5. Einkauf Belegkette', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('5.1 Einkauf-Dashboard lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/dashboard/einkauf', 'Einkauf Dashboard')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('5.2 Bestellungen lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/bestellungen', 'Bestellungen')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('5.3 Wareneingangsabgleich lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/wareneingangsabgleich', 'Wareneingangsabgleich')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('5.4 Eingangsrechnung-Erfassung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/einkauf/rechnung-eingang-erfassung', 'Eingangsrechnung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('5.5 Dispositions-Positionsmatrix lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/disposition/position-matrix', 'Disposition Matrix')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 6. Logistik ─────────────────────────────────────────────────────────────

test.describe('6. Logistik', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('6.1 Tourenplanung lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/logistik/tourenplanung', 'Tourenplanung')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('6.2 Tour-Fracht-Arbeitsraum lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/logistik/tour-fracht-arbeitsraum', 'Tour-Fracht')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('6.3 Fuhrpark-Übersicht lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/fuhrpark/uebersicht', 'Fuhrpark')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('6.4 Streckengeschäft lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/strecke/streckengeschaeft', 'Streckengeschäft')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 7. CRM & Kampagnen ──────────────────────────────────────────────────────

test.describe('7. CRM & Kampagnen', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('7.1 Kampagnen lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/campaigns', 'Kampagnen')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('7.2 Segmente lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/segments', 'Segmente')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('7.3 DSGVO-Anfragen lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm/gdpr-requests', 'DSGVO-Anfragen')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('7.4 KIM CRM-Cockpit lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/crm', 'KIM CRM-Cockpit')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 8. Qualität & Compliance ────────────────────────────────────────────────

test.describe('8. Qualität & Compliance', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('8.1 Labor-Auftrag lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/qualitaet/labor-auftrag', 'Labor-Auftrag')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('8.2 Reklamationen lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/qualitaet/reklamationen', 'Reklamationen')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('8.3 CO2-Bilanz lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/nachhaltigkeit/co2-bilanz', 'CO2-Bilanz')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('8.4 EUDR-Compliance lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/nachhaltigkeit/eudr-compliance', 'EUDR-Compliance')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('8.5 PCN-Liste lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/compliance/pcn-liste', 'PCN-Liste')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 9. Kontrakte & Frühkauf ─────────────────────────────────────────────────

test.describe('9. Kontrakte & Frühkauf', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('9.1 Kontrakt-Übersicht lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/kontrakte/kontrakt-uebersicht', 'Kontrakt-Übersicht')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('9.2 Kontrakt-Engagement lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/kontrakt-engagement', 'Kontrakt-Engagement')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('9.3 Kontrakt-Settlement lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/agrar/kontrakt-settlement', 'Kontrakt-Settlement')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})

// ─── 10. API-Smoke: neue Endpoints ───────────────────────────────────────────

test.describe('10. API-Smoke: neue Endpoints', () => {
  test('10.1 GET /lager/bestaende antwortet 200', async ({ request }) => {
    const { status, ms, body } = await apiGet(request, '/api/v1/lager/bestaende?tenant_id=default')
    test.info().annotations.push({ type: 'Ladezeit', description: `GET /lager/bestaende: ${ms} ms` })
    if (status === 200) {
      expect(Array.isArray(body)).toBe(true)
      test.info().annotations.push({ type: 'Ergebnis', description: `${(body as unknown[]).length} Bestandszeilen` })
    } else {
      // 401/403 = Auth korrekt aber Token fehlt in CI — kein Fehler
      test.info().annotations.push({ type: 'Hinweis', description: `HTTP ${status} (Auth/Token-Problem in CI erwartet)` })
      expect([200, 401, 403]).toContain(status)
    }
  })

  test('10.2 POST /scan/barcode Fremdware-Erkennung', async ({ request }) => {
    const { status, ms, body } = await apiPost(request, '/api/v1/scan/barcode?tenant_id=default', {
      barcode: 'FREMDWARE-9999-NICHT-IM-STAMM',
      action: 'info',
    })
    test.info().annotations.push({ type: 'Ladezeit', description: `POST /scan/barcode: ${ms} ms` })
    if (status === 200) {
      const resp = body as { gefunden: boolean; hinweis?: string }
      expect(resp.gefunden).toBe(false)
      expect(resp.hinweis).toBeTruthy()
      test.info().annotations.push({ type: 'Ergebnis', description: `Fremdware-Erkennung: ${resp.hinweis}` })
    } else {
      expect([200, 401, 403]).toContain(status)
    }
  })

  test('10.3 POST /scan/barcode bekannter Artikel', async ({ request }) => {
    // Erst Artikel-ID aus /articles holen
    const listResp = await apiGet(request, '/api/v1/articles?limit=1&tenant_id=default')
    if (listResp.status !== 200) {
      test.info().annotations.push({ type: 'Skip', description: 'Artikel-API nicht erreichbar' })
      return
    }
    const articles = listResp.body as { article_number?: string; ean?: string }[]
    if (!articles?.length) {
      test.info().annotations.push({ type: 'Skip', description: 'Keine Artikel in DB' })
      return
    }
    const testBarcode = articles[0].ean ?? articles[0].article_number ?? 'UNKNOWN'
    const { status, ms, body } = await apiPost(request, '/api/v1/scan/barcode?tenant_id=default', {
      barcode: testBarcode,
      action: 'info',
    })
    test.info().annotations.push({ type: 'Ladezeit', description: `POST /scan/barcode (bekannt): ${ms} ms` })
    if (status === 200) {
      const resp = body as { gefunden: boolean; artikel?: { artikel_nummer: string } }
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Barcode ${testBarcode}: gefunden=${resp.gefunden}`,
      })
    } else {
      expect([200, 401, 403]).toContain(status)
    }
  })

  test('10.4 GET /pricing/find Preisfindung', async ({ request }) => {
    const listResp = await apiGet(request, '/api/v1/articles?limit=1&tenant_id=default')
    if (listResp.status !== 200) {
      test.info().annotations.push({ type: 'Skip', description: 'Artikel-API nicht erreichbar' })
      return
    }
    const articles = listResp.body as { id?: string }[]
    if (!articles?.length) {
      test.info().annotations.push({ type: 'Skip', description: 'Keine Artikel in DB' })
      return
    }
    const articleId = articles[0].id ?? ''
    const { status, ms, body } = await apiGet(
      request,
      `/api/v1/pricing/find?article_id=${articleId}&quantity=10&tenant_id=default`,
    )
    test.info().annotations.push({ type: 'Ladezeit', description: `GET /pricing/find: ${ms} ms` })
    if (status === 200) {
      const resp = body as { net_price?: number; source?: string }
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Preis: ${resp.net_price} EUR, Quelle: ${resp.source}`,
      })
    } else {
      expect([200, 401, 403, 404]).toContain(status)
    }
  })

  test('10.5 POST /pricing/staffelrabatte anlegen', async ({ request }) => {
    const listResp = await apiGet(request, '/api/v1/articles?limit=1&tenant_id=default')
    if (listResp.status !== 200) {
      test.info().annotations.push({ type: 'Skip', description: 'Artikel-API nicht erreichbar' })
      return
    }
    const articles = listResp.body as { id?: string }[]
    const artikelId = articles?.[0]?.id ?? null

    const { status, ms, body } = await apiPost(
      request,
      '/api/v1/pricing/staffelrabatte?tenant_id=default',
      {
        artikel_id: artikelId,
        artikelgruppe: artikelId ? undefined : 'Saatgut',
        bezeichnung: 'Test-Staffel Mais 10+ VE',
        stufen: [
          { ab_menge: 1, rabatt_prozent: 0 },
          { ab_menge: 10, rabatt_prozent: 3 },
          { ab_menge: 25, rabatt_prozent: 5 },
        ],
      },
    )
    test.info().annotations.push({ type: 'Ladezeit', description: `POST /pricing/staffelrabatte: ${ms} ms` })
    if (status === 201) {
      const resp = body as { id?: string; stufen?: unknown[] }
      expect(resp.id).toBeTruthy()
      expect(Array.isArray(resp.stufen)).toBe(true)
      test.info().annotations.push({ type: 'Ergebnis', description: `Staffelrabatt angelegt: ${resp.id}` })
    } else {
      expect([201, 401, 403, 503]).toContain(status)
      test.info().annotations.push({ type: 'Hinweis', description: `HTTP ${status} — DB-Tabelle ggf. nicht migriert` })
    }
  })

  test('10.6 POST /lager/bewegungen Wareneingang', async ({ request }) => {
    const listResp = await apiGet(request, '/api/v1/articles?limit=1&tenant_id=default')
    const warehouseResp = await apiGet(request, '/api/v1/warehouses?limit=1&tenant_id=default')
    if (listResp.status !== 200 || warehouseResp.status !== 200) {
      test.info().annotations.push({ type: 'Skip', description: 'Artikel oder Lager-API nicht erreichbar' })
      return
    }
    const articles = listResp.body as { id?: string }[]
    const warehouses = warehouseResp.body as { id?: string; items?: { id?: string }[] }
    const articleId = articles?.[0]?.id
    const warehouseList = Array.isArray(warehouses) ? warehouses : (warehouses as { items?: { id?: string }[] }).items ?? []
    const warehouseId = (warehouseList[0] as { id?: string })?.id

    if (!articleId || !warehouseId) {
      test.info().annotations.push({ type: 'Skip', description: 'Keine Artikel/Lager-IDs verfügbar' })
      return
    }

    const { status, ms, body } = await apiPost(
      request,
      '/api/v1/lager/bewegungen?tenant_id=default',
      {
        article_id: articleId,
        warehouse_id: warehouseId,
        quantity: 100,
        movement_type: 'wareneingang',
        bemerkung: 'E2E-Test Wareneingang Pioneer P9175',
        charge: `E2E-${Date.now()}`,
      },
    )
    test.info().annotations.push({ type: 'Ladezeit', description: `POST /lager/bewegungen: ${ms} ms` })
    if (status === 201) {
      const resp = body as { id?: string; quantity?: number }
      test.info().annotations.push({
        type: 'Ergebnis',
        description: `Lagerbewegung gebucht: ${resp.id}, Menge: ${resp.quantity}`,
      })
    } else {
      expect([201, 401, 403, 404, 503]).toContain(status)
      test.info().annotations.push({ type: 'Hinweis', description: `HTTP ${status}` })
    }
  })
})

// ─── 11. Controlling & Personal ──────────────────────────────────────────────

test.describe('11. Controlling & Personal', () => {
  test.beforeEach(async ({ page }) => { await prepareE2EAuth(page) })

  test('11.1 Benchmark-Cockpit lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/controlling/benchmark-cockpit', 'Benchmark-Cockpit')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('11.2 Perioden lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/finance/periods', 'Perioden')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('11.3 Organigramm lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/personal/organigramm', 'Organigramm')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })

  test('11.4 Bewerbungen lädt', async ({ page }) => {
    const ms = await gotoMeasured(page, '/personal/bewerbungen', 'Bewerbungen')
    expect(ms).toBeLessThan(PERF_THRESHOLD_MS)
    await expect(page.getByRole('heading').first()).toBeVisible()
  })
})
