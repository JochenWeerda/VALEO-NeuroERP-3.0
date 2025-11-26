/**
 * Global Setup für Playwright Tests
 * Wartet auf App-Ready vor Test-Start
 */

import { request } from "@playwright/test";

const baseURL = process.env.NEUROERP_URL || "http://localhost:3000";

export default async function globalSetup() {
  const ctx = await request.newContext();
  const deadline = Date.now() + 60_000;

  console.log(`[Global Setup] Warte auf App-Ready: ${baseURL}`);

  while (Date.now() < deadline) {
    try {
      const res = await ctx.get(`${baseURL}/health`);
      if (res.ok()) {
        console.log("[Global Setup] App ist bereit!");
        return;
      }
    } catch (e) {
      // Ignore errors, retry
    }
    await new Promise(r => setTimeout(r, 1000));
  }

  throw new Error(`App nicht erreichbar bei ${baseURL} nach 60 Sekunden`);
}
