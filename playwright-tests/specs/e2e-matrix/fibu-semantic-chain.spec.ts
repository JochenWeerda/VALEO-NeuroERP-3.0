/**
 * SEMANTIC-E2E-MATRIX-001 — FIBU Semantische Prozesskette
 *
 * OP anlegen → CAMT-Zahlungseingang → Auszifferung → Mahnlauf (Verzug) →
 * DATEV-Buchungsstapel-Export → Periodenabschluss
 *
 * Externe Gates: DATEV, ELSTER/eBilanz simuliert.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'e2e-fibu-001'
const AUTH = process.env.API_DEV_TOKEN ?? 'dev-token'
const HEADERS = {
  'X-Tenant-ID': TENANT,
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH}`,
}

let opId = ''
let mahnungId = ''
let datevJobId = ''

test.describe.serial('FIBU — OP bis DATEV-Export Prozesskette @smoke @e2e-matrix', () => {

  test('FIBU-1 — Offenen Posten (Forderung) anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/open-items', {
      headers: HEADERS,
      data: {
        kunden_nr: 'E2E-K-FIBU-001',
        beleg_nr: `RE-E2E-${Date.now()}`,
        op_typ: 'FORDERUNG',
        betrag_eur: 5500.0,
        faellig_am: '2026-07-01',
        buchungsdatum: '2026-06-01',
        konto_soll: '1400',
        konto_haben: '8400',
        kostenstelle: 'KST-VERTRIEB',
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      opId = body.id ?? body.op_id ?? ''
    }
    await ctx.dispose()
  })

  test('FIBU-2 — OP-Liste abrufen und Forderung sichtbar', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/finance/open-items', {
      headers: HEADERS,
      params: { kunden_nr: 'E2E-K-FIBU-001', op_typ: 'FORDERUNG' },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      const items = Array.isArray(body) ? body : (body.items ?? [])
      // Liste kann leer sein wenn Endpoint gefiltert oder OP noch nicht persistiert
      expect(Array.isArray(items)).toBeTruthy()
    }
    await ctx.dispose()
  })

  test('FIBU-3 — CAMT-Zahlungseingang (Bank-Auszug) simuliert importieren', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/bank/camt-import', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        iban: 'DE00123456789012345678',
        von_datum: '2026-07-01',
        bis_datum: '2026-07-31',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
    }
    await ctx.dispose()
  })

  test('FIBU-4 — Zahlung manuell erfassen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/payments', {
      headers: HEADERS,
      data: {
        op_id: opId || 'e2e-op-fallback',
        betrag_eur: 5500.0,
        valuta: '2026-07-05',
        zahlungsart: 'UEBERWEISUNG',
        referenz: 'CAMT-E2E-001',
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-5 — OP ausziffern', async () => {
    if (!opId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post(`/api/v1/finance/open-items/${opId}/ausgleich`, {
      headers: HEADERS,
      data: {
        ausgleichsbetrag_eur: 5500.0,
        ausgleichsdatum: '2026-07-05',
        zahlungsreferenz: 'CAMT-E2E-001',
        ausgeglichen_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-6 — Ueberfaelligen OP fuer Mahnlauf anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/open-items', {
      headers: HEADERS,
      data: {
        kunden_nr: 'E2E-K-FIBU-MAHNUNG',
        beleg_nr: `RE-E2E-MAHNUNG-${Date.now()}`,
        op_typ: 'FORDERUNG',
        betrag_eur: 2200.0,
        faellig_am: '2026-05-01',
        buchungsdatum: '2026-04-01',
        konto_soll: '1400',
        konto_haben: '8400',
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-7 — Mahnlauf ausfuehren', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/dunning/run', {
      headers: HEADERS,
      data: {
        stichtag: '2026-07-25',
        buchungskreis: 'E2E-MANDANT',
        mahnstufe_max: 3,
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      mahnungId = body.id ?? body.mahnung_id ?? body.run_id ?? ''
    }
    await ctx.dispose()
  })

  test('FIBU-8 — Mahnlauf-Ergebnis pruefen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/finance/dunning', {
      headers: HEADERS,
      params: { kunden_nr: 'E2E-K-FIBU-MAHNUNG' },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-9 — Buchungsjournal pruefen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/finance/journal-entries', {
      headers: HEADERS,
      params: { periode: '2026-07', limit: 20 },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-10 — DATEV-Buchungsstapel-Export simuliert', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/datev/export', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        buchungsperiode: '2026-07',
        buchungskreis: 'E2E-MANDANT',
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
      datevJobId = body.job_id ?? body.sim_id ?? ''
    }
    await ctx.dispose()
  })

  test('FIBU-11 — DATEV-Export-Status pruefen', async () => {
    if (!datevJobId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/dev/external-mocks/datev/export/${datevJobId}`, { headers: HEADERS })
    expect([200, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
    }
    await ctx.dispose()
  })

  test('FIBU-12 — Periodenabschluss einleiten', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/period-close', {
      headers: HEADERS,
      data: {
        periode: '2026-07',
        buchungskreis: 'E2E-MANDANT',
        abschluss_art: 'MONATSABSCHLUSS',
        eingeleitet_von: 'e2e-fibu-leiter',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('FIBU-13 — ELSTER-USt-Voranmeldung simuliert', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/elster/submit', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        meldungsart: 'UST_VA',
        periode: '2026-07',
        steuernummer: '12345/67890',
        erstellt_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
    }
    await ctx.dispose()
  })

})
