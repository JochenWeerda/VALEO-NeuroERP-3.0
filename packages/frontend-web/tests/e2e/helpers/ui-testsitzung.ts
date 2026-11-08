import type { Page } from '@playwright/test'

/**
 * Ausdrueckliches UI-Test-Double fuer Laeufe ohne Anmeldedienst und ohne Backend (z. B. axe in CI).
 *
 * Seit 12.10.2026 gibt es keinen UI-Bypass mehr: geschuetzte Seiten leiten ohne Anmeldung auf `/login` um. Das
 * Frontend prueft nur, ob ein dekodierbares, nicht abgelaufenes Zugriffstoken vorliegt; die Signatur prueft allein das
 * Backend. Dieses Token ist unsigniert — jeder echte API-Aufruf damit wird abgelehnt. Es beweist deshalb nur, dass die
 * Oberflaeche rendert (Barrierefreiheit, Layout), nichts ueber Anmeldung oder Rechte.
 */
export async function setzeUiTestsitzung(page: Page, rollen: string[] = ['admin']): Promise<void> {
  const teil = (wert: object) => Buffer.from(JSON.stringify(wert)).toString('base64url')
  const token = [
    teil({ alg: 'none', typ: 'JWT' }),
    teil({
      sub: 'ui-testsitzung',
      name: 'UI-Testsitzung',
      exp: Math.floor(Date.now() / 1000) + 3600,
      roles: rollen,
      scope: 'admin:all',
      tenant_id: '00000000-0000-0000-0000-000000000001',
    }),
    'unsigniert',
  ].join('.')
  await page.addInitScript((wert) => {
    try {
      localStorage.setItem('access_token', wert)
    } catch {
      /* Speicher gesperrt: dann bleibt die Seite auf /login, der Test zeigt das */
    }
  }, token)
}
