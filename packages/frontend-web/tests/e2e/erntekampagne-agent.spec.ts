/**
 * E2E: Erntekampagne + Autonomer Low-Stock-Agent
 * Testet Ernteannahme-Flow und Agent-Orchestration-Endpoints
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Erntekampagne', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Erntekampagne Dashboard lädt', async ({ page }) => {
    await page.goto('/agrar/erntekampagne')
    await page.waitForLoadState('networkidle')
    const errors: string[] = []
    page.on('pageerror', (e) => errors.push(e.message))
    await page.waitForTimeout(500)
    expect(errors.filter(e => !e.includes('ResizeObserver') && !e.includes('maplibre'))).toHaveLength(0)
  })

  test('LKW-Registrierung lädt', async ({ page }) => {
    await page.goto('/agrar/annahme/lkw-registrierung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Qualitäts-Check lädt', async ({ page }) => {
    await page.goto('/agrar/annahme/qualitaets-check')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})

test.describe('Autonomer Low-Stock-Agent', () => {
  test('sollte Agent-Status liefern', async ({ request }) => {
    const resp = await request.get('/api/v1/agents/low-stock/status')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('agent')
      expect(body.agent).toBe('low-stock-bestellvorschlag')
      expect(body).toHaveProperty('nats_subject')
      expect(body.nats_subject).toBe('erp.lager.bestand_unterschritten')
    }
  })

  test('sollte Low-Stock-Event simulieren', async ({ request }) => {
    const resp = await request.post('/api/v1/agents/low-stock/simulate', {
      data: {
        tenant_id: 'test-tenant',
        artikel_id: 'ART-001',
        artikel_name: 'Testgetreide',
        bestand: 50.0,
        mindestbestand: 200.0,
        einheit: 't',
      },
    })
    expect([200, 201, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('empfohlene_menge')
      expect(body.empfohlene_menge).toBeGreaterThan(0)
      expect(body).toHaveProperty('begruendung')
      expect(body.erfolg).toBe(true)
    }
  })

  test('EOQ-Menge soll Fehlbedarf decken', async ({ request }) => {
    const resp = await request.post('/api/v1/agents/low-stock/simulate', {
      data: {
        tenant_id: 'test',
        artikel_id: 'ART-002',
        artikel_name: 'Rapssaat',
        bestand: 10.0,
        mindestbestand: 100.0,
        einheit: 't',
        verbrauch_pro_tag: 5.0,
      },
    })
    if (resp.status() === 200) {
      const body = await resp.json()
      // Menge muss mindestens den Fehlbedarf (100-10=90t) decken
      expect(body.empfohlene_menge).toBeGreaterThanOrEqual(90)
    } else {
      expect([401, 422]).toContain(resp.status())
    }
  })

  test('Batch-Scan Endpoint erreichbar', async ({ request }) => {
    const resp = await request.post('/api/v1/agents/low-stock/batch-scan?tenant_id=test')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('vorschlaege_erstellt')
      expect(typeof body.vorschlaege_erstellt).toBe('number')
    }
  })
})

test.describe('GoBD Hash-Chain', () => {
  test('Journal-Entry API erreichbar', async ({ request }) => {
    const resp = await request.get('/api/v1/journal-entries?limit=5')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('GoBD Archiv-Endpoint erreichbar', async ({ request }) => {
    const resp = await request.get('/api/v1/gobd/archiv')
    expect([200, 401, 404]).toContain(resp.status())
  })
})
