/**
 * E2E-Auth (M-05): Token aus Umgebung oder OIDC Password Grant (Realm muss direct grant erlauben).
 *
 * Variablen:
 * - E2E_AUTH_TOKEN — direkter Token in localStorage (Key: E2E_AUTH_STORAGE_KEY oder access_token)
 * - E2E_OIDC_TOKEN_URL, E2E_OIDC_CLIENT_ID, E2E_OIDC_USERNAME, E2E_OIDC_PASSWORD
 * - optional: E2E_OIDC_CLIENT_SECRET, E2E_OIDC_SCOPE
 */
import type { Page } from '@playwright/test'

const DEFAULT_TOKEN_KEY = process.env.E2E_AUTH_STORAGE_KEY ?? 'access_token'

export async function applyE2EAuthFromEnv(page: Page): Promise<void> {
  const token = process.env.E2E_AUTH_TOKEN
  if (!token) return

  const key = DEFAULT_TOKEN_KEY
  await page.addInitScript(
    ({ storageKey, tok }) => {
      try {
        localStorage.setItem(storageKey, tok)
      } catch {
        /* ignore */
      }
    },
    { storageKey: key, tok: token }
  )
}

/**
 * Holt access_token vom Token-Endpoint und legt ihn wie das Frontend unter access_token ab.
 */
export async function applyE2EAuthFromOidCPasswordGrant(page: Page): Promise<void> {
  if (process.env.E2E_AUTH_TOKEN) return

  const tokenUrl = process.env.E2E_OIDC_TOKEN_URL?.trim()
  const clientId = process.env.E2E_OIDC_CLIENT_ID?.trim()
  const username = process.env.E2E_OIDC_USERNAME?.trim()
  const password = process.env.E2E_OIDC_PASSWORD?.trim()
  if (!tokenUrl || !clientId || !username || !password) return

  const body = new URLSearchParams({
    grant_type: 'password',
    client_id: clientId,
    username,
    password,
    scope: process.env.E2E_OIDC_SCOPE ?? 'openid profile email',
  })
  const clientSecret = process.env.E2E_OIDC_CLIENT_SECRET?.trim()
  if (clientSecret) body.set('client_secret', clientSecret)

  const r = await fetch(tokenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })
  const raw = await r.text()
  if (!r.ok) {
    console.warn(`E2E password grant failed: HTTP ${r.status} ${raw.slice(0, 400)}`)
    return
  }
  let data: { access_token?: string; refresh_token?: string }
  try {
    data = JSON.parse(raw) as { access_token?: string; refresh_token?: string }
  } catch {
    console.warn('E2E password grant: invalid JSON')
    return
  }
  const tok = data.access_token
  if (!tok) return
  const refresh = data.refresh_token
  const key = DEFAULT_TOKEN_KEY
  await page.addInitScript(
    ({ storageKey, accessTok, refreshTok }) => {
      try {
        localStorage.setItem(storageKey, accessTok)
        if (refreshTok) localStorage.setItem('refresh_token', refreshTok)
      } catch {
        /* ignore */
      }
    },
    { storageKey: key, accessTok: tok, refreshTok: refresh ?? '' }
  )
}

/** Reihenfolge: fester Token > Password-Grant > kein Effekt */
export async function prepareE2EAuth(page: Page): Promise<void> {
  await applyE2EAuthFromEnv(page)
  await applyE2EAuthFromOidCPasswordGrant(page)
}
