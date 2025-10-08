export interface AuthSession {
  accessToken: string | null
  refreshToken?: string | null
  expiresAt?: number | null
}

type AuthListener = (session: AuthSession) => void

let currentSession: AuthSession = {
  accessToken: null,
  refreshToken: null,
  expiresAt: null,
}

const listeners = new Set<AuthListener>()

const notifyListeners = (): void => {
  const snapshot: AuthSession = { ...currentSession }
  for (const listener of listeners) {
    listener(snapshot)
  }
}

export function getAccessToken(): string | null {
  return currentSession.accessToken ?? null
}

export function setAuthSession(update: Partial<AuthSession>): void {
  currentSession = {
    ...currentSession,
    ...update,
  }
  notifyListeners()
}

export function clearAuthSession(): void {
  currentSession = {
    accessToken: null,
    refreshToken: null,
    expiresAt: null,
  }
  notifyListeners()
}

export function onAuthSessionChange(listener: AuthListener): () => void {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export function handleUnauthorized(): void {
  clearAuthSession()
  const context = typeof globalThis !== 'undefined' ? (globalThis as Record<string, unknown>) : null
  const locationValue = context && 'location' in context ? context.location : null
  if (locationValue != null && typeof locationValue === 'object' && 'href' in locationValue) {
    (locationValue as { href: string }).href = '/login'
  }
}
