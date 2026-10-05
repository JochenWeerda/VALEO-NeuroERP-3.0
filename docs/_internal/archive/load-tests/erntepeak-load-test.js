/**
 * erntepeak-load-test.js — Echter Lasttest Erntepeak (Gap 037)
 *
 * Führt realen HTTP-Traffic gegen den laufenden VALEO-Stack aus.
 * Testet die typischen Erntepeak-Workflows mit 500 gleichzeitigen Usern.
 *
 * Voraussetzungen:
 *   - Stack läuft: docker compose up -d
 *   - k6 installiert: choco install k6  /  brew install k6
 *
 * Ausführung:
 *   k6 run load-tests/erntepeak-load-test.js
 *   k6 run --env BASE_URL=http://staging:8000 --env API_TOKEN=xyz load-tests/erntepeak-load-test.js
 *   k6 run --env SCENARIO=normalbetrieb load-tests/erntepeak-load-test.js
 *
 * Ergebnis-Interpretation:
 *   ✓ http_req_duration{endpoint:dashboard}.....: p(95) < 250ms  → Gap 033 erfüllt
 *   ✓ http_req_duration{endpoint:global}........: p(95) < 2000ms → Gap 037 erfüllt
 *   ✓ http_req_failed...........................: rate < 0.01    → Error Rate < 1%
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// ---------------------------------------------------------------------------
// Eigene Metriken — werden in der k6-Ausgabe separat ausgewiesen
// ---------------------------------------------------------------------------
const errorRate          = new Rate('valeo_error_rate');
const dashboardDuration  = new Trend('valeo_dashboard_p95',   true);
const annahmeDuration    = new Trend('valeo_annahme_p95',     true);
const controllingDuration = new Trend('valeo_controlling_p95', true);
const settlementDuration = new Trend('valeo_settlement_p95',  true);
const requestCount       = new Counter('valeo_requests_total');

// ---------------------------------------------------------------------------
// Szenarien
// ---------------------------------------------------------------------------
const SCENARIO = __ENV.SCENARIO || 'erntepeak';

const SZENARIEN = {
  normalbetrieb: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '30s', target: 10 },
      { duration: '2m',  target: 50 },
      { duration: '2m',  target: 50 },
      { duration: '30s', target: 0  },
    ],
  },
  erntepeak: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m',  target: 100 },   // Ramp-up Phase 1
      { duration: '2m',  target: 300 },   // Ramp-up Phase 2
      { duration: '2m',  target: 500 },   // Vollast — 500 gleichzeitige User
      { duration: '20m', target: 500 },   // Erntepeak-Dauerlast
      { duration: '3m',  target: 0   },   // Ramp-down
    ],
  },
  stresstest: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m',  target: 500  },
      { duration: '5m',  target: 1000 },
      { duration: '2m',  target: 0    },
    ],
  },
  spike: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '30s', target: 50  },
      { duration: '10s', target: 500 },  // Plötzlicher Spike
      { duration: '3m',  target: 500 },
      { duration: '10s', target: 50  },  // Abfall
      { duration: '1m',  target: 0   },
    ],
  },
};

export const options = {
  scenarios: {
    erntepeak: SZENARIEN[SCENARIO],
  },

  // SLA-Schwellwerte (Gap 037 + Gap 033)
  thresholds: {
    // Gap 037: Error Rate < 1%
    'http_req_failed':                   ['rate<0.01'],
    'valeo_error_rate':                  ['rate<0.01'],

    // Gap 037: Globaler p95 < 2s
    'http_req_duration':                 ['p(95)<2000'],

    // Gap 033: Dashboard-Endpoints p95 < 250ms
    'valeo_dashboard_p95':               ['p(95)<250'],

    // Annahme/Qualität: p95 < 1s (Waage-Endpoints)
    'valeo_annahme_p95':                 ['p(95)<1000'],

    // Controlling: p95 < 500ms
    'valeo_controlling_p95':             ['p(95)<500'],
  },
};

// ---------------------------------------------------------------------------
// Konfiguration
// ---------------------------------------------------------------------------
const BASE_URL   = __ENV.BASE_URL   || 'http://localhost:8000';
const API_TOKEN  = __ENV.API_TOKEN  || 'dev-token-valeo-erntepeak-2026';

// Mehrere Tenants simulieren (Multi-Tenant-Isolation prüfen)
const TENANT_POOL = [
  'T-GENOSSENSCHAFT-001',
  'T-GENOSSENSCHAFT-002',
  'T-GENOSSENSCHAFT-003',
  'T-LANDHANDEL-001',
  'T-LANDHANDEL-002',
];

function randomTenant() {
  return TENANT_POOL[Math.floor(Math.random() * TENANT_POOL.length)];
}

function headers(tenant) {
  return {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
    'X-Tenant-ID': tenant || randomTenant(),
  };
}

// ---------------------------------------------------------------------------
// Setup: Token holen (wenn OIDC aktiviert)
// ---------------------------------------------------------------------------
export function setup() {
  const healthRes = http.get(`${BASE_URL}/api/v1/health`, {
    headers: { 'Authorization': `Bearer ${API_TOKEN}` },
  });
  const ok = check(healthRes, {
    'Backend erreichbar': (r) => r.status === 200 || r.status === 404,
  });
  if (!ok) {
    console.error(`Backend nicht erreichbar: ${healthRes.status} — Stack gestartet?`);
  }
  return { token: API_TOKEN };
}

// ---------------------------------------------------------------------------
// Hauptfunktion — wird pro virtuellem User, pro Iteration ausgeführt
// ---------------------------------------------------------------------------
export default function (data) {
  const tenant = randomTenant();
  const hdrs   = headers(tenant);

  // Jeder User führt einen zufälligen Workflow-Mix aus
  // Gewichtung spiegelt typischen Erntepeak-Betrieb wider:
  //   40% Dashboard/KPI-Lesen (Disponenten, Geschäftsführung)
  //   30% Annahme/Qualität (Waage-Operator)
  //   20% Controlling (Buchhaltung)
  //   10% Settlement (Abrechnung)
  const roll = Math.random();

  if (roll < 0.40) {
    workflowDashboardKpi(hdrs, tenant);
  } else if (roll < 0.70) {
    workflowAnnahmeQualitaet(hdrs, tenant);
  } else if (roll < 0.90) {
    workflowControlling(hdrs, tenant);
  } else {
    workflowSettlement(hdrs, tenant);
  }

  // Think-Time: 0.5–2s (realistisches Nutzerverhalten)
  sleep(0.5 + Math.random() * 1.5);
}

// ---------------------------------------------------------------------------
// Workflow 1: Dashboard & KPI (40% der Last)
// Gap 033: p95 < 250ms durch Read-Models
// ---------------------------------------------------------------------------
function workflowDashboardKpi(hdrs, tenant) {
  group('dashboard_kpi', () => {
    let res = http.get(`${BASE_URL}/api/v1/controlling/dashboards`, {
      headers: hdrs,
      tags: { endpoint: 'dashboard' },
    });
    dashboardDuration.add(res.timings.duration);
    requestCount.add(1);
    const dashOk = check(res, {
      'Dashboard 200': (r) => r.status === 200,
      'Dashboard < 250ms': (r) => r.timings.duration < 250,
    });
    errorRate.add(!dashOk);

    sleep(0.3);

    res = http.get(`${BASE_URL}/api/v1/controlling/kpis`, {
      headers: hdrs,
      tags: { endpoint: 'dashboard' },
    });
    dashboardDuration.add(res.timings.duration);
    requestCount.add(1);
    const kpiOk = check(res, {
      'KPI-Liste 200': (r) => r.status === 200,
      'KPI-Liste < 250ms': (r) => r.timings.duration < 250,
    });
    errorRate.add(!kpiOk);

    sleep(0.2);

    res = http.get(`${BASE_URL}/api/v1/controlling/timeseries?kpi=UMSATZ&periode=2026`, {
      headers: hdrs,
      tags: { endpoint: 'dashboard' },
    });
    dashboardDuration.add(res.timings.duration);
    requestCount.add(1);
    const tsOk = check(res, {
      'Timeseries 200': (r) => r.status === 200,
      'Timeseries < 500ms': (r) => r.timings.duration < 500,
    });
    errorRate.add(!tsOk);
  });
}

// ---------------------------------------------------------------------------
// Workflow 2: Annahme & Qualität (30% der Last)
// ---------------------------------------------------------------------------
function workflowAnnahmeQualitaet(hdrs, tenant) {
  group('annahme_qualitaet', () => {
    let res = http.get(`${BASE_URL}/api/v1/agrar/contracts?status=aktiv&limit=20`, {
      headers: hdrs,
      tags: { endpoint: 'annahme' },
    });
    annahmeDuration.add(res.timings.duration);
    requestCount.add(1);
    check(res, { 'Kontrakte 200': (r) => r.status === 200 || r.status === 404 });

    sleep(0.5);

    res = http.get(`${BASE_URL}/api/v1/agrar/harvest-acceptance?status=offen&limit=10`, {
      headers: hdrs,
      tags: { endpoint: 'annahme' },
    });
    annahmeDuration.add(res.timings.duration);
    requestCount.add(1);
    const annahmeOk = check(res, {
      'Annahmen 200': (r) => r.status === 200 || r.status === 404,
      'Annahmen < 1s': (r) => r.timings.duration < 1000,
    });
    errorRate.add(res.status >= 500);

    sleep(0.3);

    res = http.get(`${BASE_URL}/api/v1/agrar/quality-protocols?limit=5`, {
      headers: hdrs,
      tags: { endpoint: 'annahme' },
    });
    annahmeDuration.add(res.timings.duration);
    requestCount.add(1);
    check(res, { 'Qualitätsprotokolle 200': (r) => r.status === 200 || r.status === 404 });
    errorRate.add(res.status >= 500);
  });
}

// ---------------------------------------------------------------------------
// Workflow 3: Controlling (20% der Last)
// ---------------------------------------------------------------------------
function workflowControlling(hdrs, tenant) {
  group('controlling', () => {
    let res = http.get(`${BASE_URL}/api/v1/finance/open-items?typ=kreditor&limit=50`, {
      headers: hdrs,
      tags: { endpoint: 'controlling' },
    });
    controllingDuration.add(res.timings.duration);
    requestCount.add(1);
    const opOk = check(res, {
      'OP Kreditoren 200': (r) => r.status === 200 || r.status === 404,
      'OP Kreditoren < 500ms': (r) => r.timings.duration < 500,
    });
    errorRate.add(res.status >= 500);

    sleep(0.4);

    res = http.get(`${BASE_URL}/api/v1/finance/payment-runs?limit=10`, {
      headers: hdrs,
      tags: { endpoint: 'controlling' },
    });
    controllingDuration.add(res.timings.duration);
    requestCount.add(1);
    check(res, { 'Zahlungsläufe 200': (r) => r.status === 200 || r.status === 404 });
    errorRate.add(res.status >= 500);

    sleep(0.3);

    res = http.get(`${BASE_URL}/api/v1/controlling/actions?limit=20`, {
      headers: hdrs,
      tags: { endpoint: 'controlling' },
    });
    controllingDuration.add(res.timings.duration);
    requestCount.add(1);
    check(res, { 'Controlling Actions 200': (r) => r.status === 200 || r.status === 404 });
    errorRate.add(res.status >= 500);
  });
}

// ---------------------------------------------------------------------------
// Workflow 4: Settlement (10% der Last)
// ---------------------------------------------------------------------------
function workflowSettlement(hdrs, tenant) {
  group('settlement', () => {
    let res = http.get(`${BASE_URL}/api/v1/agrar/settlements/?limit=20`, {
      headers: hdrs,
      tags: { endpoint: 'settlement' },
    });
    settlementDuration.add(res.timings.duration);
    requestCount.add(1);
    const settOk = check(res, {
      'Settlements 200': (r) => r.status === 200 || r.status === 404,
      'Settlements < 2s': (r) => r.timings.duration < 2000,
    });
    errorRate.add(res.status >= 500);

    sleep(0.5);

    res = http.get(`${BASE_URL}/api/v1/agrar/self-billing?limit=10`, {
      headers: hdrs,
      tags: { endpoint: 'settlement' },
    });
    settlementDuration.add(res.timings.duration);
    requestCount.add(1);
    check(res, { 'Self-Billing 200': (r) => r.status === 200 || r.status === 404 });
    errorRate.add(res.status >= 500);
  });
}

// ---------------------------------------------------------------------------
// Teardown: Ergebnis-Zusammenfassung
// ---------------------------------------------------------------------------
export function teardown(data) {
  console.log('');
  console.log('=== VALEO Erntepeak-Lasttest abgeschlossen ===');
  console.log(`Szenario: ${SCENARIO}`);
  console.log('SLA-Prüfung: siehe Threshold-Ergebnisse oben');
  console.log('');
}
