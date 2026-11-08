/**
 * Echte Anmeldung fuer E2E-Laeufe: Tokens vom konfigurierten Anbieter (Keycloak), keine Dev-Tokens.
 *
 * Seit 12.10.2026 nimmt das Backend nur signierte Tokens mit Mandant und Sitzung. In CI startet der Workflow einen
 * Wegwerf-Keycloak und legt die Kennungen ueber `scripts/ci/e2e_identitaeten.py` an; nur dort ist der Password Grant
 * am Frontend-Client offen. Lokal gegen den Entwicklungs-Keycloak bleibt er zu — dann schlaegt die Anmeldung mit einer
 * klaren Meldung fehl, statt still ohne Identitaet weiterzulaufen.
 */

export interface Tokens {
  access: string
  refresh?: string
}

const TOKEN_URL =
  process.env.VALEO_OIDC_TOKEN_URL ??
  'http://localhost:8080/realms/valeo-neuro-erp/protocol/openid-connect/token'
const CLIENT_ID = process.env.VALEO_OIDC_CLIENT_ID ?? 'valeo-neuro-erp-frontend'

export async function holeTokens(benutzer: string, kennwort: string): Promise<Tokens> {
  if (!benutzer || !kennwort) {
    throw new Error('E2E-Anmeldung: Kennung oder Kennwort fehlt (VALEO_USER_* / VALEO_PASS_*).')
  }
  const antwort = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'password',
      client_id: CLIENT_ID,
      username: benutzer,
      password: kennwort,
      scope: 'openid',
    }),
  })
  if (!antwort.ok) {
    throw new Error(`E2E-Anmeldung fuer ${benutzer} abgelehnt (${antwort.status}) — laeuft der Test-Keycloak?`)
  }
  const daten = (await antwort.json()) as { access_token?: string; refresh_token?: string }
  if (!daten.access_token) throw new Error('E2E-Anmeldung: Anbieter lieferte kein Zugriffstoken.')
  return { access: daten.access_token, refresh: daten.refresh_token }
}

/**
 * Zugriffstoken fuer direkte API-Aufrufe in Specs; das Playwright-global-setup holt es einmal je Lauf.
 *
 * Wirft bewusst nicht: Playwright laedt die Spec-Dateien zum Sammeln schon vor dem global-setup, dort ist die Variable
 * noch leer. In den Workern ist sie gesetzt; fehlt sie dort, antwortet das Backend 401 — sichtbar im Test.
 */
export function apiToken(): string {
  return process.env.VALEO_E2E_ACCESS_TOKEN ?? ''
}

/**
 * Der Mandant der Testkennungen. Das Backend nimmt den Mandanten aus dem Token und lehnt einen abweichenden
 * `X-Tenant-ID` mit 403 ab — eigene Phantasiemandanten je Spec (frueher `test-tenant-…`) gibt es deshalb nicht mehr.
 */
export const E2E_MANDANT = process.env.VALEO_E2E_TENANT ?? '00000000-0000-0000-0000-000000000001'
