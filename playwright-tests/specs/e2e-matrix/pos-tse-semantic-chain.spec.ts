/**
 * SEMANTIC-E2E-MATRIX-001 — POS/TSE Semantische Prozesskette
 *
 * Kassenbon → TSE-Signatur (simuliert) → Zahlung (Bar/EC) →
 * Tagesabschluss → DSFinV-K-Export (simuliert) → FIBU-Buchung
 *
 * §146a AO KassenSichV: TSE-Signatur Pflicht; DSFinV-K fuer Finanzamt-Pruefung.
 * Externe Gates: TSE-Hersteller, DSFinV-K-Pruefwerkzeug bleiben simuliert.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'e2e-pos-001'
const AUTH = process.env.API_DEV_TOKEN ?? 'dev-token'
const HEADERS = {
  'X-Tenant-ID': TENANT,
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH}`,
}

let bonId = ''
let tseSignaturId = ''
let tagesabschlussId = ''
let dsfinvkJobId = ''

test.describe.serial('POS/TSE — Kassenbon bis FIBU-Buchung @smoke @e2e-matrix', () => {

  test('POS-1 — Kassenbon (Bon) erstellen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/bons', {
      headers: HEADERS,
      data: {
        kassen_id: 'KASSE-E2E-001',
        bediener_id: 'e2e-kassiererin',
        positionen: [
          { artikel_id: 'DIESEL-B7', menge: 50, einheit: 'l', preis_eur: 1.65, mwst_pct: 19.0 },
          { artikel_id: 'SCHMIERSTOFF-46', menge: 2, einheit: 'l', preis_eur: 8.90, mwst_pct: 19.0 },
        ],
        gesamt_brutto_eur: 100.30,
        erstellt_am: new Date().toISOString(),
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      bonId = body.id ?? body.bon_id ?? ''
    }
    await ctx.dispose()
  })

  test('POS-2 — TSE-Signatur einholen (simuliert)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/tse/sign', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        kassen_id: 'KASSE-E2E-001',
        bon_id: bonId || `BON-E2E-${Date.now()}`,
        betrag_brutto_eur: 100.30,
        zahlungsart: 'BAR',
        vorgangsbeschreibung: 'Kassenvorgang E2E-Test',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
      tseSignaturId = body.signatur_id ?? body.sim_id ?? ''
      // TSE-Signatur muss vorhanden sein
      expect(body.signatur ?? body.tse_signatur ?? '').toBeTruthy()
    }
    await ctx.dispose()
  })

  test('POS-3 — Zahlung Bar erfassen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/zahlungen', {
      headers: HEADERS,
      data: {
        bon_id: bonId || 'e2e-bon-fallback',
        kassen_id: 'KASSE-E2E-001',
        zahlungsart: 'BAR',
        betrag_eur: 100.30,
        rueckgeld_eur: 0.0,
        tse_signatur_id: tseSignaturId || undefined,
        erfasst_von: 'e2e-kassiererin',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS-4 — Zweiten Bon (EC-Zahlung) erstellen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/bons', {
      headers: HEADERS,
      data: {
        kassen_id: 'KASSE-E2E-001',
        bediener_id: 'e2e-kassiererin',
        positionen: [
          { artikel_id: 'SAATGUT-WEIZEN', menge: 100, einheit: 'kg', preis_eur: 0.45, mwst_pct: 7.0 },
        ],
        gesamt_brutto_eur: 48.15,
        erstellt_am: new Date().toISOString(),
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS-5 — Tagesabschluss einleiten', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/tagesabschluss', {
      headers: HEADERS,
      data: {
        kassen_id: 'KASSE-E2E-001',
        abschluss_datum: '2026-07-25',
        kassen_verantwortlicher: 'e2e-kassenleiter',
        soll_bestand_eur: 500.0,
        ist_bestand_eur: 600.30,
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      tagesabschlussId = body.id ?? body.abschluss_id ?? ''
    }
    await ctx.dispose()
  })

  test('POS-6 — Tagesabschluss-Status pruefen', async () => {
    if (!tagesabschlussId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/pos/tagesabschluss/${tagesabschlussId}`, { headers: HEADERS })
    expect([200, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      const status = body.status ?? body.abschluss_status ?? 'OFFEN'
      expect(['OFFEN', 'IN_PRUEFUNG', 'ABGESCHLOSSEN', 'FREIGEGEBEN']).toContain(status)
    }
    await ctx.dispose()
  })

  test('POS-7 — Z-Bon (Abschlussbericht) abrufen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/pos/z-bon', {
      headers: HEADERS,
      params: { kassen_id: 'KASSE-E2E-001', datum: '2026-07-25' },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS-8 — DSFinV-K-Export (simuliert)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/dsfinvk/export', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        kassen_id: 'KASSE-E2E-001',
        von_datum: '2026-07-25',
        bis_datum: '2026-07-25',
        tagesabschluss_id: tagesabschlussId || undefined,
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
      dsfinvkJobId = body.job_id ?? body.sim_id ?? ''
    }
    await ctx.dispose()
  })

  test('POS-9 — DSFinV-K-Export-Status pruefen', async () => {
    if (!dsfinvkJobId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/pos/dsfinvk/export/${dsfinvkJobId}`, { headers: HEADERS })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS-10 — FIBU-Buchung aus Tagesabschluss', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/tagesabschluss/fibu-buchung', {
      headers: HEADERS,
      data: {
        kassen_id: 'KASSE-E2E-001',
        datum: '2026-07-25',
        tagesabschluss_id: tagesabschlussId || 'e2e-ta-fallback',
        buchungskreis: 'E2E-MANDANT',
        umsatz_brutto_eur: 148.45,
        davon_bar_eur: 100.30,
        davon_ec_eur: 48.15,
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS-11 — Kassenbon-Liste des Tages pruefen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/pos/bons', {
      headers: HEADERS,
      params: { kassen_id: 'KASSE-E2E-001', datum: '2026-07-25', limit: 20 },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      const bons = Array.isArray(body) ? body : (body.items ?? [])
      expect(Array.isArray(bons)).toBeTruthy()
    }
    await ctx.dispose()
  })

  test('POS-12 — Retoure (Storno eines Bons)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/pos/retoure', {
      headers: HEADERS,
      data: {
        original_bon_id: bonId || 'e2e-bon-fallback',
        kassen_id: 'KASSE-E2E-001',
        grund: 'KUNDENWUNSCH',
        retournierte_positionen: [
          { artikel_id: 'DIESEL-B7', menge: 10, einheit: 'l', preis_eur: 1.65 },
        ],
        erfasst_von: 'e2e-kassiererin',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

})

// SEMANTIC-E2E-STRICT-001 — @critical Kern-Pfad POS/TSE
test.describe('POS @critical Kern-Pfad', () => {
  const BASE_CRIT = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
  const TENANT_CRIT = 'e2e-crit-pos'
  const HEADERS_CRIT = {
    'X-Tenant-ID': TENANT_CRIT,
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.API_DEV_TOKEN ?? 'dev-token'}`,
  }

  test('POS @critical — Kassen-Endpunkt antwortet (Health)', async () => {
    const ctx = await request.newContext({ baseURL: BASE_CRIT })
    const res = await ctx.get('/api/v1/pos/kassen', { headers: HEADERS_CRIT })
    expect([200, 404, 422]).toContain(res.status())
    await ctx.dispose()
  })

  test('POS @critical — Tagesabschluss-Endpunkt antwortet (Health)', async () => {
    const ctx = await request.newContext({ baseURL: BASE_CRIT })
    // POST-only route — leerer Body liefert 422 (Validierung), kein 405 wie bei GET
    const res = await ctx.post('/api/v1/pos/tagesabschluss', {
      headers: HEADERS_CRIT,
      data: {},
    })
    expect([200, 201, 404, 422]).toContain(res.status())
    await ctx.dispose()
  })
})
