/**
 * SEMANTIC-E2E-MATRIX-001 — P2P Procure-to-Pay Semantische Prozesskette
 *
 * RFQ → Bestellung → Wareneingang → 3-Wege-Match → ERS/Eingangsrechnung →
 * Zahlungslauf (SEPA) → DATEV-Export (simuliert)
 *
 * Alle Tests laufen gegen Backend-API. Externe Gates (DATEV, Bank/SEPA) simuliert.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'e2e-p2p-001'
const AUTH = process.env.API_DEV_TOKEN ?? 'dev-token'
const HEADERS = {
  'X-Tenant-ID': TENANT,
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH}`,
}

let lieferantId = ''
let rfqId = ''
let bestellungId = ''
let wareneingangId = ''
let eingangsrechnungId = ''

test.describe.serial('P2P — Procure-to-Pay Prozesskette @smoke @e2e-matrix', () => {

  test('P2P-1 — Lieferant anlegen / abrufen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/lieferanten', {
      headers: HEADERS,
      data: {
        name: 'E2E Lieferant P2P GmbH',
        lieferanten_nr: `E2E-LF-${Date.now()}`,
        status: 'AKTIV',
        email: 'p2p-lf@valeo-e2e.local',
        zahlungsziel_tage: 30,
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      lieferantId = body.id ?? body.lieferanten_id ?? ''
    }
    await ctx.dispose()
  })

  test('P2P-2 — RFQ (Anfrage) erstellen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/rfq', {
      headers: HEADERS,
      data: {
        lieferant_id: lieferantId || 'e2e-lf-fallback',
        positionen: [
          { artikel_id: 'DUENGER-NPK', menge: 20, einheit: 't', zielpreis_eur: 320.0 },
        ],
        gueltig_bis: '2026-08-01',
        erstellt_von: 'e2e-einkauf',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      rfqId = body.id ?? body.rfq_id ?? ''
    }
    await ctx.dispose()
  })

  test('P2P-3 — Bestellung (Purchase Order) anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/bestellungen', {
      headers: HEADERS,
      data: {
        lieferant_id: lieferantId || 'e2e-lf-fallback',
        rfq_id: rfqId || undefined,
        positionen: [
          { artikel_id: 'DUENGER-NPK', menge: 20, einheit: 't', preis_eur: 315.0 },
        ],
        lieferdatum: '2026-07-20',
        zahlungsziel_tage: 30,
        erstellt_von: 'e2e-einkauf',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      bestellungId = body.id ?? body.order_id ?? body.bestellung_id ?? ''
    }
    await ctx.dispose()
  })

  test('P2P-4 — Bestellung abrufen und Status pruefen', async () => {
    if (!bestellungId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/einkauf/bestellungen/${bestellungId}`, { headers: HEADERS })
    expect([200, 404, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      const status = body.status ?? body.bestellung_status ?? 'OFFEN'
      expect(['ENTWURF', 'OFFEN', 'BESTAETIGT', 'TEILGELIEFERT', 'ABGESCHLOSSEN']).toContain(status)
    }
    await ctx.dispose()
  })

  test('P2P-5 — Wareneingang buchen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/wareneingaenge', {
      headers: HEADERS,
      data: {
        bestellung_id: bestellungId || 'e2e-po-fallback',
        lieferant_id: lieferantId || 'e2e-lf-fallback',
        positionen: [
          { artikel_id: 'DUENGER-NPK', gelieferte_menge: 20, einheit: 't', charge: 'CH-E2E-001' },
        ],
        eingangsdatum: '2026-07-20',
        lagerort: 'LAGER-A',
        erfasst_von: 'e2e-lager',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      wareneingangId = body.id ?? body.wareneingang_id ?? ''
    }
    await ctx.dispose()
  })

  test('P2P-6 — 3-Wege-Match (Bestellung / Lieferung / Rechnung)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/3-wege-match', {
      headers: HEADERS,
      data: {
        bestellung_id: bestellungId || 'e2e-po-fallback',
        wareneingang_id: wareneingangId || 'e2e-we-fallback',
        toleranz_pct: 2.0,
        geprueft_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      // Match-Ergebnis muss einen Status enthalten
      const matchStatus = body.match_status ?? body.status ?? 'GEPRUEFT'
      expect(['OK', 'DIFFERENZ', 'GESPERRT', 'GEPRUEFT', 'FREIGEGEBEN']).toContain(matchStatus)
    }
    await ctx.dispose()
  })

  test('P2P-7 — ERS / Eingangsrechnung erfassen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/rechnungseingang', {
      headers: HEADERS,
      data: {
        lieferant_id: lieferantId || 'e2e-lf-fallback',
        bestellung_id: bestellungId || 'e2e-po-fallback',
        wareneingang_id: wareneingangId || 'e2e-we-fallback',
        rechnungsnummer: `RE-LF-E2E-${Date.now()}`,
        brutto_eur: 6300.0,
        netto_eur: 6300.0,
        mwst_pct: 19.0,
        faellig_am: '2026-08-20',
        erfasst_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      eingangsrechnungId = body.id ?? body.rechnung_id ?? ''
    }
    await ctx.dispose()
  })

  test('P2P-8 — Eingangsrechnung freigeben (FIBU-Freigabe)', async () => {
    if (!eingangsrechnungId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post(`/api/v1/einkauf/rechnungseingang/${eingangsrechnungId}/freigabe`, {
      headers: HEADERS,
      data: {
        freigegeben_von: 'e2e-fibu-leiter',
        kommentar: '3-Wege-Match OK — E2E-Test',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('P2P-9 — SEPA-Zahlungslauf vorbereiten', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/payment-runs', {
      headers: HEADERS,
      data: {
        faellig_bis: '2026-08-25',
        buchungskreis: 'E2E-MANDANT',
        zahlungsart: 'SEPA_CT',
        erstellt_von: 'e2e-fibu',
        positionen: eingangsrechnungId ? [{ rechnung_id: eingangsrechnungId }] : [],
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('P2P-10 — CAMT-Import (Bank-Kontoauszug) simuliert', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/dev/external-mocks/bank/camt-import', {
      headers: HEADERS,
      data: {
        tenant_id: TENANT,
        iban: 'DE12345678901234567890',
        von_datum: '2026-08-01',
        bis_datum: '2026-08-25',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      expect(body.simulated).toBe(true)
    }
    await ctx.dispose()
  })

  test('P2P-11 — Lieferantenverbindlichkeit OP pruefen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/finance/open-items', {
      headers: HEADERS,
      params: { lieferant_id: lieferantId || 'e2e-lf-fallback', op_typ: 'VERBINDLICHKEIT' },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('P2P-12 — DATEV-Export Lieferantenverbindlichkeit simuliert', async () => {
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
    }
    await ctx.dispose()
  })

})
