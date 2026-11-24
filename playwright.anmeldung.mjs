import { mkdirSync, writeFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const rootDir = path.resolve(fileURLToPath(new URL("./", import.meta.url)));

/**
 * Browser-Sitzung der Verwaltungs-Testkennung fuer `use.storageState` (Projekt `full`): die Tokens liegen so in
 * `localStorage`, wie die SPA sie nach dem PKCE-Rueckruf ablegt (`packages/frontend-web/src/lib/auth.ts`). Die Datei
 * enthaelt ein gueltiges Token; sie liegt deshalb unter `playwright/.auth/` (gitignored, nicht im Artefakt-Upload).
 */
export const SITZUNG_ADMIN = path.join(rootDir, "playwright", ".auth", "sitzung-admin.json");

/**
 * Einmalige Anmeldung je Playwright-Lauf: holt die Tokens der Verwaltungs-Testkennung vom Test-Keycloak, legt das
 * Zugriffstoken in `VALEO_E2E_ACCESS_TOKEN` ab (Worker erben die Umgebung des Hauptprozesses; Specs lesen es ueber
 * `apiToken()` in playwright-tests/helpers/anmeldung.ts) und schreibt die Browser-Sitzung nach `SITZUNG_ADMIN`.
 * Ohne Kennung bleibt die Sitzung leer — Browser-Specs landen dann sichtbar auf der Anmeldeseite, API-Specs
 * scheitern mit 401, statt still ohne Identitaet weiterzulaufen.
 */
export default async function anmeldung() {
  const benutzer = process.env.VALEO_USER_ADMIN;
  const kennwort = process.env.VALEO_PASS_ADMIN;
  let tokens = null;
  if (benutzer && kennwort) {
    const url =
      process.env.VALEO_OIDC_TOKEN_URL ??
      "http://localhost:8080/realms/valeo-neuro-erp/protocol/openid-connect/token";
    const antwort = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "password",
        client_id: process.env.VALEO_OIDC_CLIENT_ID ?? "valeo-neuro-erp-frontend",
        username: benutzer,
        password: kennwort,
        scope: "openid",
      }),
    });
    if (!antwort.ok) {
      throw new Error(`[global-setup] E2E-Anmeldung abgelehnt (${antwort.status}) — laeuft der Test-Keycloak?`);
    }
    tokens = await antwort.json();
    if (!process.env.VALEO_E2E_ACCESS_TOKEN) process.env.VALEO_E2E_ACCESS_TOKEN = tokens.access_token;
  } else {
    console.warn("[global-setup] VALEO_USER_ADMIN/VALEO_PASS_ADMIN fehlen — Browser-Sitzung bleibt leer.");
  }

  const frontendUrl = process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? "http://127.0.0.1:4173";
  const localStorage = tokens
    ? [
        { name: "access_token", value: tokens.access_token },
        ...(tokens.refresh_token ? [{ name: "refresh_token", value: tokens.refresh_token }] : []),
      ]
    : [];
  mkdirSync(path.dirname(SITZUNG_ADMIN), { recursive: true });
  writeFileSync(
    SITZUNG_ADMIN,
    JSON.stringify({ cookies: [], origins: [{ origin: new URL(frontendUrl).origin, localStorage }] }),
  );
}
