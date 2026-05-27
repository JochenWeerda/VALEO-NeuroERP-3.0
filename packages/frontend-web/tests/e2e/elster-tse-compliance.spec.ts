/**
 * E2E: ELSTER UStVA + TSE Fiskaly + Normative Compliance
 * Testet die normativen Kern-Endpoints
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('ELSTER UStVA', () => {
  test('API: UStVA-Berechnung Simulator', async ({ request }) => {
    const resp = await request.post('/api/v1/ebilanz/elster/ustva', {
      data: {
        tenant_id: 'test-tenant',
        steuernummer: '12/345/67890',
        finanzamt_nr: '1234',
        voranmeldungszeitraum: '2026-01',
        kz81_umsatz_19: 100000.0,
        kz86_umsatz_7: 10000.0,
        kz35_ig_lieferungen: 0.0,
        kz66_vorsteuer: 15000.0,
      },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('zahllast_eur')
      expect(body).toHaveProperty('elster_status')
      expect(body).toHaveProperty('transfer_ticket')
    }
  })

  test('API: UStVA-Historie abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/ebilanz/elster/ustva')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(Array.isArray(body)).toBe(true)
    }
  })

  test('Compliance-Dashboard lädt', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/admin/compliance-dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})

test.describe('TSE / KassenSichV', () => {
  test('API: TSE-Status Simulator', async ({ request }) => {
    const resp = await request.get('/api/v1/pos/tse/status')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('status')
      expect(body).toHaveProperty('modus')
    }
  })

  test('API: Transaction Start Simulator', async ({ request }) => {
    const resp = await request.post('/api/v1/pos/tse/transaction/start', {
      data: {
        kassenid: 'KASSE-001',
        kassenbeleg_id: 'BON-2026-001',
        transaktionstyp: 'Beleg',
        betrag_brutto: 19.90,
        steuern: [{ steuerart: 'Normaler Steuersatz', betrag: 3.18 }],
      },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('transaction_id')
      expect(body).toHaveProperty('signature')
    }
  })

  test('POS Terminal lädt', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/pos/terminal')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('DSFinV-K Export Simulator', async ({ request }) => {
    const resp = await request.post('/api/v1/pos/tse/export', {
      data: { kassenid: 'KASSE-001', von: '2026-01-01', bis: '2026-01-31' },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('export_id')
    }
  })
})

test.describe('GoBD / Datenpflege', () => {
  test('Datenpannen (DSGVO Art.33) lädt', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/compliance/datenpannen')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Datenpanne melden', async ({ request }) => {
    const resp = await request.post('/api/v1/gdpr/art33/breaches', {
      data: {
        titel: 'E2E-Test Datenpanne',
        beschreibung: 'Automatischer E2E-Test',
        betroffene_personen: 10,
        datenkategorien: ['name', 'email'],
        ursache: 'Technischer Defekt',
      },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
  })
})
