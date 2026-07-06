/**
 * k6 Health-Check — Schnelltest vor Erntepeak (Gap 037)
 *
 * Läuft in < 60s, prüft alle kritischen Endpunkte auf Verfügbarkeit.
 * Für pre-deploy-Checks und CI/CD-Gates.
 *
 * Ausführen:
 *   k6 run tests/load/health-check.js
 */

import http from 'k6/http'
import { check, group } from 'k6'

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000'
const API_TOKEN = __ENV.API_DEV_TOKEN || 'dev-token'
const TENANT_ID = __ENV.TENANT_ID || 'tenant-001'

const HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_TOKEN}`,
  'X-Tenant-ID': TENANT_ID,
}

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    http_req_failed: ['rate==0'],
    http_req_duration: ['p(95)<1000'],
  },
}

const ENDPOINTS = [
  { name: 'Health',          url: '/health' },
  { name: 'Warteschlange',   url: '/api/v1/annahme/warteschlange' },
  { name: 'Lager-Bestand',   url: '/api/v1/lager/bestand' },
  { name: 'Finance OP',      url: '/api/v1/finance/open-items?typ=kreditoren' },
  { name: 'Workflows',       url: '/api/v1/agents/neuroassist/runs' },
  { name: 'Process Mining',  url: '/api/v1/process-mining/finance/bottlenecks' },
  { name: 'Capabilities',    url: '/api/v1/agents/neuroassist/capabilities' },
]

export default function healthCheck() {
  group('Endpunkt-Verfügbarkeit', () => {
    for (const ep of ENDPOINTS) {
      const res = http.get(`${BASE_URL}${ep.url}`, { headers: HEADERS })
      check(res, {
        [`${ep.name}: HTTP 2xx`]: (r) => r.status >= 200 && r.status < 300,
        [`${ep.name}: < 1000ms`]: (r) => r.timings.duration < 1000,
      })
    }
  })
}
