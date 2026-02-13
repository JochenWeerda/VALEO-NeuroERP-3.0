import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API_PREFIX = `${BASE_URL}/api/v1`;
const API_TOKEN = __ENV.API_TOKEN || "dev-token";
const TENANT_ID = __ENV.TENANT_ID || "00000000-0000-0000-0000-000000000001";

const failedChecks = new Counter("agrar_failed_checks");
const billingPreviewDuration = new Trend("agrar_billing_preview_duration", true);

const commonHeaders = {
  Authorization: `Bearer ${API_TOKEN}`,
  "X-Tenant-ID": TENANT_ID,
  "Content-Type": "application/json",
};

export const options = {
  discardResponseBodies: true,
  scenarios: {
    weighing_ticket_list: {
      executor: "constant-vus",
      vus: 10,
      duration: "2m",
      exec: "listWeighingTickets",
      tags: { flow: "weighing-list" },
    },
    settlement_preview: {
      executor: "constant-vus",
      vus: 6,
      duration: "2m",
      exec: "previewSettlement",
      tags: { flow: "settlement-preview" },
    },
    create_weighing_ticket: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "30s", target: 3 },
        { duration: "60s", target: 6 },
        { duration: "30s", target: 0 },
      ],
      exec: "createWeighingTicket",
      tags: { flow: "weighing-create" },
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.02"],
    http_req_duration: ["p(95)<900", "p(99)<1500"],
    agrar_failed_checks: ["count<10"],
    agrar_billing_preview_duration: ["p(95)<1000"],
  },
};

export function setup() {
  const res = http.get(`${API_PREFIX}/health`, { headers: commonHeaders });
  check(res, { "health endpoint reachable": (r) => r.status === 200 || r.status === 404 });
  return { startedAt: new Date().toISOString() };
}

export function listWeighingTickets() {
  const res = http.get(`${API_PREFIX}/weighing-tickets?limit=50`, { headers: commonHeaders });
  const ok = check(res, {
    "list weighing status ok": (r) => r.status === 200,
  });
  if (!ok) failedChecks.add(1);
  sleep(0.2);
}

export function previewSettlement() {
  const payload = JSON.stringify({
    net_weight_kg: 25000,
    moisture_pct: 16.5,
    impurities_pct: 1.8,
    target_moisture_pct: 14,
    base_impurities_pct: 2,
    allow_bonus: false,
  });

  const res = http.post(`${API_PREFIX}/agrar/settlements/billing-weight/preview`, payload, { headers: commonHeaders });
  billingPreviewDuration.add(res.timings.duration);
  const ok = check(res, {
    "billing preview status ok": (r) => r.status === 200,
  });
  if (!ok) failedChecks.add(1);
  sleep(0.3);
}

export function createWeighingTicket() {
  const idPart = `${__VU}-${__ITER}-${Date.now()}`;
  const payload = JSON.stringify({
    ticket_number: `PERF-${idPart}`,
    scale_id: "W-001",
    vehicle_plate: `PERF-${__VU}`,
    gross_weight: 30000,
    tare_weight: 9000,
    moisture_pct: 15.2,
    impurities_pct: 1.4,
    direction: "in",
    reference_doc: "k6-loadtest",
  });

  const res = http.post(`${API_PREFIX}/weighing-tickets`, payload, { headers: commonHeaders });
  const ok = check(res, {
    "create weighing status ok": (r) => r.status === 201,
  });
  if (!ok) failedChecks.add(1);
  sleep(0.5);
}

export function teardown(data) {
  console.log(`AGRAR-PERF-01 finished. startedAt=${data.startedAt}`);
}

export function handleSummary(data) {
  const startedAt = new Date().toISOString();
  return {
    stdout: `\nAGRAR-PERF-01 SUMMARY (${startedAt})\n${JSON.stringify(
      {
        vus_max: data.metrics.vus_max?.values?.max ?? null,
        iterations: data.metrics.iterations?.values?.count ?? null,
        http_req_failed_rate: data.metrics.http_req_failed?.values?.rate ?? null,
        p95_ms: data.metrics.http_req_duration?.values?.["p(95)"] ?? null,
        p99_ms: data.metrics.http_req_duration?.values?.["p(99)"] ?? null,
      },
      null,
      2,
    )}\n`,
    "reports/performance/agrar-perf-summary.json": JSON.stringify(data, null, 2),
  };
}
