/**
 * DOM-CON-004 Playwright Smoke — Kontrakt-Lifecycle API-Vertrag.
 */
import { test, expect } from "@playwright/test";

const API = process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000/api/v1";
const H = { "X-Tenant-ID": "smoke-tenant", Authorization: "Bearer dev-token", "Content-Type": "application/json" };

test("@smoke Kontrakt-Lifecycle ENTWURF→FREIGEGEBEN→AKTIV", async ({ request }) => {
  const kid = `K-SMOKE-${Date.now()}`;
  const r1 = await request.post(`${API}/kontrakte/lifecycle`, { headers: H, data: {
    kontrakt_id: kid, kontrakt_nr: `KNR-${kid}`, artikel_id: "weizen",
    menge_t: 100.0, preis_eur_t: 220.0, lieferant_id: "lft-1", periode: "2026-07",
  }});
  expect(r1.ok()).toBeTruthy();
  const body = await r1.json();
  expect(body.status).toBe("ENTWURF");

  const r2 = await request.post(`${API}/kontrakte/lifecycle/${kid}/transition`,
    { headers: H, data: { new_status: "FREIGEGEBEN", operator: "smoke" } });
  expect(r2.ok()).toBeTruthy();

  const r3 = await request.post(`${API}/kontrakte/lifecycle/${kid}/transition`,
    { headers: H, data: { new_status: "AKTIV", operator: "smoke" } });
  expect(r3.ok()).toBeTruthy();
  expect((await r3.json()).status).toBe("AKTIV");
});

test("@smoke Fixing-Summary für leeren Kontrakt", async ({ request }) => {
  const kid = `K-FIX-${Date.now()}`;
  await request.post(`${API}/kontrakte/lifecycle`, { headers: H, data: {
    kontrakt_id: kid, kontrakt_nr: `KNR-${kid}`, artikel_id: "gerste",
    menge_t: 200.0, preis_eur_t: 180.0, lieferant_id: "lft-2", periode: "2026-08",
  }});
  const r = await request.get(`${API}/kontrakte/fixing/${kid}/summary`, { headers: H });
  expect(r.ok()).toBeTruthy();
  const s = await r.json();
  expect(s.gefixte_menge_t).toBe(0);
  expect(s.vollstaendig_gefixt).toBe(false);
});
