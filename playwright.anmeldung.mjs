/**
 * Einmalige API-Anmeldung je Playwright-Lauf: holt ein Zugriffstoken der Verwaltungs-Testkennung vom Test-Keycloak
 * und legt es in `VALEO_E2E_ACCESS_TOKEN` ab; Worker erben die Umgebung des Hauptprozesses. Specs lesen es ueber
 * `apiToken()` (playwright-tests/helpers/anmeldung.ts). Ohne Kennung bleibt die Variable leer — Specs, die die API
 * brauchen, scheitern dann mit einer klaren Meldung statt mit einem stillen 401.
 */
export default async function anmeldung() {
  const benutzer = process.env.VALEO_USER_ADMIN;
  const kennwort = process.env.VALEO_PASS_ADMIN;
  if (!benutzer || !kennwort || process.env.VALEO_E2E_ACCESS_TOKEN) return;
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
  process.env.VALEO_E2E_ACCESS_TOKEN = (await antwort.json()).access_token;
}
