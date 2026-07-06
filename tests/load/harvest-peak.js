/**
 * k6 Lasttest — Erntepeak-Szenario (Gap 037)
 *
 * Ziel: 500 gleichzeitige Nutzer, Antwortzeit P95 < 800ms
 * Kernprozesse: Annahme, Waage, Qualitätsprüfung, Einlagerung
 *
 * Ausführen:
 *   k6 run tests/load/harvest-peak.js
 *   k6 run --env BASE_URL=https://staging.valeo-erp.de tests/load/harvest-peak.js
 */

import http from 'k6/http'
import { check, group, sleep } from 'k6'
import { Trend, Rate, Counter } from 'k6/metrics'

// ─── Konfiguration ────────────────────────────────────────────────────────────

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000'
const API_TOKEN = __ENV.API_DEV_TOKEN || 'dev-token'
const TENANT_ID = __ENV.TENANT_ID || 'tenant-001'

const HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_TOKEN}`,
  'X-Tenant-ID': TENANT_ID,
}

// ─── Custom Metrics ───────────────────────────────────────────────────────────

const annahmeDuration    = new Trend('annahme_duration_ms')
const qualitaetDuration  = new Trend('qualitaet_duration_ms')
const einlagerungDuration = new Trend('einlagerung_duration_ms')
const warteschlangeDuration = new Trend('warteschlange_duration_ms')
const errorRate          = new Rate('api_errors')
const annahmeCount       = new Counter('annahme_vorgaenge')

// ─── Last-Stufen (VU = Virtual Users) ────────────────────────────────────────

export const options = {
  scenarios: {
    // Stufe 1: Normalbetrieb (50 VU, 5 min)
    normalbetrieb: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },
        { duration: '3m', target: 50 },
        { duration: '1m', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
    // Stufe 2: Erntepeak (500 VU, 10 min) — Kernziel Gap 037
    erntepeak: {
      executor: 'ramping-vus',
      startVUs: 0,
      startTime: '5m30s',
      stages: [
        { duration: '2m', target: 200 },
        { duration: '2m', target: 500 },
        { duration: '5m', target: 500 },
        { duration: '1m', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
    // Stufe 3: Spike (800 VU, 2 min) — Robustheitsnachweis
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      startTime: '16m',
      stages: [
        { duration: '30s', target: 800 },
        { duration: '1m', target: 800 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    // Globale SLA-Grenzen
    http_req_duration:           ['p(95)<800', 'p(99)<2000'],
    http_req_failed:             ['rate<0.02'],     // < 2% Fehler
    // Fachliche Kernprozesse
    annahme_duration_ms:         ['p(95)<600'],
    qualitaet_duration_ms:       ['p(95)<700'],
    einlagerung_duration_ms:     ['p(95)<600'],
    warteschlange_duration_ms:   ['p(95)<400'],
    api_errors:                  ['rate<0.02'],
  },
}

// ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

function randomKennzeichen() {
  const buchstaben = 'ABCDEFGHKLMNPRSTUVWXYZ'
  const prefix = buchstaben[Math.floor(Math.random() * buchstaben.length)]
  const num = Math.floor(Math.random() * 9000 + 1000)
  return `BI-${prefix}${num}`
}

function randomArtikel() {
  const artikel = ['Weizen', 'Gerste', 'Raps', 'Mais', 'Roggen', 'Hafer']
  return artikel[Math.floor(Math.random() * artikel.length)]
}

function randomFeuchtigkeit() {
  return (Math.random() * 6 + 11).toFixed(1) // 11.0 - 17.0%
}

// ─── Szenarien ────────────────────────────────────────────────────────────────

/** Szenario: Nutzer liest Warteschlange → registriert LKW → prüft Qualität → lagert ein */
export default function erntePeakFlow() {
  const kennzeichen = randomKennzeichen()
  const artikel = randomArtikel()
  const lieferscheinNr = `LS-${Date.now()}-${Math.floor(Math.random() * 9999)}`

  // 1. Warteschlange lesen
  group('Warteschlange', () => {
    const start = Date.now()
    const res = http.get(`${BASE_URL}/api/v1/annahme/warteschlange`, { headers: HEADERS })
    warteschlangeDuration.add(Date.now() - start)
    const ok = check(res, {
      'Warteschlange 200': (r) => r.status === 200,
      'Warteschlange < 400ms': (r) => r.timings.duration < 400,
    })
    if (!ok) errorRate.add(1)
    else errorRate.add(0)
  })

  sleep(0.5)

  // 2. LKW registrieren (Annahme starten)
  let eintragId = null
  group('LKW-Registrierung', () => {
    const start = Date.now()
    const res = http.post(
      `${BASE_URL}/api/v1/annahme/warteschlange`,
      JSON.stringify({
        kennzeichen,
        lieferant: `Landwirt-${Math.floor(Math.random() * 500)}`,
        lieferschein_nr: lieferscheinNr,
        artikel,
        prioritaet: 'normal',
      }),
      { headers: HEADERS },
    )
    annahmeDuration.add(Date.now() - start)
    annahmeCount.add(1)
    const ok = check(res, {
      'LKW-Registrierung 201': (r) => r.status === 201 || r.status === 200,
      'LKW-Registrierung < 600ms': (r) => r.timings.duration < 600,
    })
    if (!ok) errorRate.add(1)
    else {
      errorRate.add(0)
      try {
        eintragId = JSON.parse(res.body).id
      } catch (_) {
        // ignorieren
      }
    }
  })

  sleep(1)

  // 3. Qualitätsprüfung speichern
  group('Qualitaetspruefung', () => {
    const start = Date.now()
    const feuchtigkeit = parseFloat(randomFeuchtigkeit())
    const res = http.post(
      `${BASE_URL}/api/v1/agrar/quality-protocols`,
      JSON.stringify({
        harvest_acceptance_id: eintragId ?? null,
        moisture_pct: feuchtigkeit,
        protein_pct: parseFloat((Math.random() * 4 + 10).toFixed(1)),
        impurities_pct: parseFloat((Math.random() * 2).toFixed(1)),
        source_type: 'manual',
        other_values: {
          fremdgeruch: 'nein',
          schaedlinge: 'nein',
          farbe: 'normal',
          ergebnis: feuchtigkeit > 16 ? 'gesperrt' : feuchtigkeit > 14 ? 'bedingt' : 'freigegeben',
          lieferschein_nr: lieferscheinNr,
          artikel,
        },
      }),
      { headers: HEADERS },
    )
    qualitaetDuration.add(Date.now() - start)
    const ok = check(res, {
      'Qualitaetspruefung 201/200': (r) => r.status === 201 || r.status === 200,
      'Qualitaetspruefung < 700ms': (r) => r.timings.duration < 700,
    })
    if (!ok) errorRate.add(1)
    else errorRate.add(0)
  })

  sleep(1)

  // 4. Einlagerung buchen
  group('Einlagerung', () => {
    const start = Date.now()
    const lagerorte = ['silo-1', 'silo-2', 'halle-a', 'halle-b']
    const res = http.post(
      `${BASE_URL}/api/v1/lager/einlagerung`,
      JSON.stringify({
        chargen_id: `CH-${lieferscheinNr}`,
        artikel,
        menge: parseFloat((Math.random() * 25 + 5).toFixed(3)),
        lagerort: lagerorte[Math.floor(Math.random() * lagerorte.length)],
        lagerplatz: null,
      }),
      { headers: HEADERS },
    )
    einlagerungDuration.add(Date.now() - start)
    const ok = check(res, {
      'Einlagerung 201/200': (r) => r.status === 201 || r.status === 200,
      'Einlagerung < 600ms': (r) => r.timings.duration < 600,
    })
    if (!ok) errorRate.add(1)
    else errorRate.add(0)
  })

  sleep(Math.random() * 2 + 1) // 1-3s Denkpause
}
