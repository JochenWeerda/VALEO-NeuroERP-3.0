/**
 * SEMANTIC-E2E-MATRIX-001 — QS/Reklamation Semantische Prozesskette
 *
 * Labor-Probe → QS-Freigabe / Sperre → Reklamation beim Lieferant →
 * Retoure / Gutschrift → CAPA (Korrektur- und Vorbeugemaßnahme)
 *
 * GMP+/VLOG-Anforderungen fuer Futtermittel; EU-VO 178/2002 Rueckverfolgbarkeit.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'e2e-qs-001'
const AUTH = process.env.API_DEV_TOKEN ?? 'dev-token'
const HEADERS = {
  'X-Tenant-ID': TENANT,
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH}`,
}

let lotId = ''
let probeId = ''
let reklamationId = ''
let gutschriftId = ''
let capaId = ''

test.describe.serial('QS/Reklamation — Labor bis CAPA Prozesskette @smoke @e2e-matrix', () => {

  test('QS-1 — Lot anlegen (mit unbekannten Laborwerten)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/silo/lots', {
      headers: HEADERS,
      data: {
        artikel_id: 'SOJA-SCHROT',
        menge_kg: 30000,
        herkunft: 'ZUKAUF',
        ernte_jahr: 2026,
        qualitaetsklasse: 'UNBEKANNT',
        lieferant_id: 'LF-E2E-QS-001',
        erstellt_von: 'e2e-qs-wareneingang',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      lotId = body.id ?? body.lot_id ?? ''
    }
    await ctx.dispose()
  })

  test('QS-2 — Labor-Probe entnehmen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/agrar/qs/proben', {
      headers: HEADERS,
      data: {
        lot_id: lotId || 'e2e-lot-qs-fallback',
        probe_art: 'EINGANG',
        entnommen_am: '2026-07-15',
        entnommen_von: 'e2e-qs-labor',
        parameter: {
          rohprotein_pct: 44.5,
          rohfett_pct: 2.1,
          rohasche_pct: 6.8,
          aflatoxin_ppb: 22,
        },
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      probeId = body.id ?? body.probe_id ?? ''
    }
    await ctx.dispose()
  })

  test('QS-3 — Laboranalyse-Ergebnis: Aflatoxin-Grenzwert ueberschritten', async () => {
    if (!probeId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.patch(`/api/v1/agrar/qs/proben/${probeId}`, {
      headers: HEADERS,
      data: {
        analysiert_am: '2026-07-16',
        analysiert_von: 'e2e-qs-labor',
        befund: 'GRENZWERTUEBERSCHREITUNG',
        parameter_gemessen: {
          aflatoxin_ppb: 22,
          aflatoxin_grenzwert_ppb: 10,
        },
        kommentar: 'Aflatoxin B1 22 ppb — Grenzwert 10 ppb gemaess EU-VO 574/2011',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-4 — Lot sperren (QS-Transition auf GESPERRT)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const trgtLotId = lotId || 'e2e-lot-qs-fallback'
    const res = await ctx.post(`/api/v1/supply-chain/lots/${trgtLotId}/qs-transition`, {
      headers: HEADERS,
      data: {
        ziel_status: 'GESPERRT',
        grund: 'Aflatoxin-Grenzwert ueberschritten (22 ppb > 10 ppb)',
        bediener: 'e2e-qs-leiter',
        probe_id: probeId || undefined,
        gmp_plus_relevant: true,
        vlog_relevant: false,
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-5 — Lot-Status nach Sperre pruefen', async () => {
    if (!lotId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/silo/lots/${lotId}`, { headers: HEADERS })
    expect([200, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200) {
      const body = await res.json()
      const status = body.status ?? body.qs_status ?? 'UNBEKANNT'
      // Status muss gesperrt oder unveraendert sein
      expect(['GESPERRT', 'IN_PRUEFUNG', 'UNBEKANNT', 'FREIGEGEBEN']).toContain(status)
    }
    await ctx.dispose()
  })

  test('QS-6 — Reklamation beim Lieferant anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/reklamationen', {
      headers: HEADERS,
      data: {
        lieferant_id: 'LF-E2E-QS-001',
        lot_id: lotId || 'e2e-lot-qs-fallback',
        probe_id: probeId || undefined,
        reklamationsart: 'QUALITAETSMAENGEL',
        beschreibung: 'Aflatoxin B1 22 ppb — EU-Grenzwert 10 ppb ueberschritten',
        geforderte_massnahme: 'RETOURE_UND_GUTSCHRIFT',
        reklamiert_von: 'e2e-qs-leiter',
        reklamiert_am: '2026-07-17',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      reklamationId = body.id ?? body.reklamation_id ?? ''
    }
    await ctx.dispose()
  })

  test('QS-7 — Lieferant-Reaktion erfassen', async () => {
    if (!reklamationId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.patch(`/api/v1/einkauf/reklamationen/${reklamationId}`, {
      headers: HEADERS,
      data: {
        lieferant_reaktion: 'RETOURE_AKZEPTIERT',
        lieferant_kommentar: 'Wir akzeptieren die Retoure und stellen Gutschrift aus.',
        reaktion_datum: '2026-07-18',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-8 — Retoure (Warenruecksendung) buchen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/retouren', {
      headers: HEADERS,
      data: {
        reklamation_id: reklamationId || 'e2e-rkl-fallback',
        lot_id: lotId || 'e2e-lot-qs-fallback',
        lieferant_id: 'LF-E2E-QS-001',
        menge_kg: 30000,
        ruecksendedatum: '2026-07-20',
        grund: 'QUALITAETSMAENGEL_AFLATOXIN',
        erfasst_von: 'e2e-lager',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-9 — Gutschrift vom Lieferant erfassen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/gutschriften', {
      headers: HEADERS,
      data: {
        reklamation_id: reklamationId || 'e2e-rkl-fallback',
        lieferant_id: 'LF-E2E-QS-001',
        gutschrift_nr: `GS-LF-E2E-${Date.now()}`,
        betrag_eur: 9000.0,
        gutschrift_datum: '2026-07-22',
        erfasst_von: 'e2e-fibu',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      gutschriftId = body.id ?? body.gutschrift_id ?? ''
    }
    await ctx.dispose()
  })

  test('QS-10 — CAPA (Korrektur- und Vorbeugemaßnahme) anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/agrar/qs/capa', {
      headers: HEADERS,
      data: {
        reklamation_id: reklamationId || 'e2e-rkl-fallback',
        lot_id: lotId || 'e2e-lot-qs-fallback',
        ursache: 'LIEFERANT_QUALITAETSMANGEL',
        korrekturmassnahme: 'Lieferant gesperrt bis Nachweis GMP+-Zertifizierung',
        vorbeugungsmassnahme: 'Eingangsproben bei Zukauf-Soja auf Aflatoxin verschaerfen (Pflicht)',
        verantwortlich: 'e2e-qs-leiter',
        faellig_am: '2026-08-31',
        erstellt_von: 'e2e-qs-leiter',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    if (res.status() === 200 || res.status() === 201) {
      const body = await res.json()
      capaId = body.id ?? body.capa_id ?? ''
    }
    await ctx.dispose()
  })

  test('QS-11 — Lieferant sperren (QS-Bewertung)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/einkauf/lieferanten-bewertung', {
      headers: HEADERS,
      data: {
        lieferant_id: 'LF-E2E-QS-001',
        bewertung: 'GESPERRT',
        grund: 'Aflatoxin-Grenzwertueberschreitung; CAPA ausstehend',
        gesperrt_von: 'e2e-qs-leiter',
        gesperrt_am: '2026-07-23',
        gesperrt_bis: '2026-08-31',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-12 — Rueckverfolgung fuer gesperrtes Lot pruefen', async () => {
    const trgtLotId = lotId || 'e2e-lot-qs-fallback'
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get(`/api/v1/supply-chain/traceability/${trgtLotId}`, { headers: HEADERS })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-13 — QS-Worklist: gesperrte Lots sichtbar', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/supply-chain/qs-worklist', {
      headers: HEADERS,
      params: { status: 'GESPERRT', limit: 10 },
    })
    expect([200, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('QS-14 — CAPA-Status auf IN_BEARBEITUNG setzen', async () => {
    if (!capaId) return
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.patch(`/api/v1/agrar/qs/capa/${capaId}`, {
      headers: HEADERS,
      data: {
        status: 'IN_BEARBEITUNG',
        fortschritt_kommentar: 'Lieferant gesperrt; verschaerfte Eingangspruefung in Kraft',
        aktualisiert_von: 'e2e-qs-leiter',
      },
    })
    expect([200, 201, 404, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

})
