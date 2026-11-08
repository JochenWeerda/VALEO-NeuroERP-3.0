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
  waehle: (konto: PortalKundenkonto | null) => void
}

export const usePortalKonto = create<PortalKontoState>((set) => ({
  aktiv: null,
  waehle: (konto) => set({ aktiv: konto }),
}))

/** Fuer den API-Client: die ID des gewaehlten Kontos, sonst null. */
export function aktivesKundenkonto(): string | null {
  return usePortalKonto.getState().aktiv?.customer_id ?? null
}

/** Darf das aktive Konto die Portalfunktion nutzen? Interne Betreuung (`rolle === 'intern'`) sieht alles. */
export function kontoDarf(konto: PortalKundenkonto | null, recht: string | undefined): boolean {
  if (!recht) return true
  if (!konto) return false
  return konto.rolle === 'intern' || konto.rechte.includes(recht)
}
