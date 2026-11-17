/**
 * Aktives Kundenkonto im Portal (PORTAL-CONTEXT-001).
 *
 * Welche Kundenkonten eine Anmeldung sieht, entscheidet der Server (`/api/v1/portal/kundenkonten`); das Frontend
 * waehlt nur aus dieser Menge und schickt die Wahl im Kopf `X-Kundenkonto` mit (`lib/api-client.ts`). Interne
 * Betreuung (Innendienst ohne Zuordnung) waehlt einen Kunden des Mandanten; auch das prueft der Server.
 *
 * Die Wahl liegt nur im Arbeitsspeicher — kein localStorage ohne Einwilligung (Portalvorgaben vom 14.10.2026). Nach
 * einem Neuladen gilt bei genau einem Konto dieses, bei mehreren wird neu gewaehlt.
 */
import { create } from 'zustand'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'

export const KUNDENKONTO_KOPF = 'X-Kundenkonto'

/**
 * Belegleserollen des Hauses (app/auth/finance_roles.BELEG_READ_ROLES): wer eine davon hat und keinem Betrieb
 * zugeordnet ist, betreut Kunden intern. Nur Anzeige — der Server entscheidet.
 */
export const INNENDIENST_ROLLEN = [
  'FINANCE_LESEN', 'FINANCE_BEARBEITEN', 'FINANCE_ADMIN',
  'SALES_LESEN', 'SALES_BEARBEITEN', 'SALES_ADMIN',
  'CRM_LESEN', 'CRM_BEARBEITEN', 'CRM_ADMIN',
  'EINKAUF_LESEN', 'EINKAUF_BEARBEITEN', 'EINKAUF_ADMIN',
  'admin', 'manager',
] as const

export interface PortalKundenkonto {
  customer_id: string
  customer_number: string | null
  name: string | null
  rolle: string
  /** Portalrechte der Rolle; bei interner Betreuung leer (der Server prueft je Weg). */
  rechte: string[]
}

interface PortalKontoState {
  aktiv: PortalKundenkonto | null
  sitzung: string | null
  sitzungswechsel: number
  pruefansicht: boolean
  waehle: (konto: PortalKundenkonto | null) => void
}

/** Dieselben Berechtigungsgrenzen wie DataBootstrap, niemals das Zugriffstoken selbst. */
export function portalSitzung(): string | null {
  const user = auth.getUser()
  const tenant = tenantFromToken(auth.getAccessToken())
  const claims = user as unknown as { iss?: unknown; sid?: unknown; session_state?: unknown } | null
  const issuer = typeof claims?.iss === 'string' ? claims.iss : null
  const sessionId = typeof claims?.sid === 'string' ? claims.sid : typeof claims?.session_state === 'string' ? claims.session_state : null
  return user?.sub && tenant ? JSON.stringify([user.sub, tenant,
    [...new Set(user.roles)].sort((a, b) => a.localeCompare(b)),
    [...new Set(user.scopes)].sort((a, b) => a.localeCompare(b)), issuer, sessionId]) : null
}

export const usePortalKonto = create<PortalKontoState>((set) => ({
  aktiv: null,
  sitzung: null,
  sitzungswechsel: 0,
  pruefansicht: false,
  waehle: (konto) => {
    const sitzung = portalSitzung()
    set((state) => ({ aktiv: sitzung ? konto : null, sitzung,
      pruefansicht: Boolean(sitzung && state.sitzung === sitzung && state.pruefansicht) }))
  },
}))

// Logout und Identitaetswechsel loeschen die Auswahl auch dann, wenn spaeter dieselbe Identitaet zurueckkehrt.
if (typeof window !== 'undefined') {
  window.addEventListener('valeo-auth-changed', () => {
    const state = usePortalKonto.getState()
    if (state.sitzung !== portalSitzung()) {
      usePortalKonto.setState({ aktiv: null, sitzung: portalSitzung(), sitzungswechsel: state.sitzungswechsel + 1,
        pruefansicht: false })
    }
  })
}

/** Interne Ansicht ist nur eine Oberflaechenauswahl und verleiht keine Berechtigungen. */
export function beginPortalInspection(): boolean {
  const sitzung = portalSitzung()
  if (!sitzung) return false
  usePortalKonto.setState((state) => ({ aktiv: null, sitzung, pruefansicht: true,
    sitzungswechsel: state.sitzungswechsel + 1 }))
  return true
}

export function endPortalInspection(): void {
  usePortalKonto.setState((state) => ({ aktiv: null, pruefansicht: false,
    sitzungswechsel: state.sitzungswechsel + 1 }))
}

/** Auch vor Verarbeitung eines Anmeldeereignisses niemals eine fremde Sitzung anzeigen. */
export function isPortalInspection(): boolean {
  const state = usePortalKonto.getState()
  const sitzung = portalSitzung()
  return Boolean(sitzung && state.sitzung === sitzung && state.pruefansicht)
}

/** Fuer den API-Client: die ID des gewaehlten Kontos, sonst null. */
export function aktivesKundenkonto(): string | null {
  const state = usePortalKonto.getState()
  const sitzung = portalSitzung()
  return sitzung && state.sitzung === sitzung ? state.aktiv?.customer_id ?? null : null
}

/** Darf das aktive Konto die Portalfunktion nutzen? Interne Betreuung (`rolle === 'intern'`) sieht alles. */
export function kontoDarf(konto: PortalKundenkonto | null, recht: string | undefined): boolean {
  if (!recht) return true
  if (!konto) return false
  return konto.rolle === 'intern' || konto.rechte.includes(recht)
}
