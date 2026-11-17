/** Navigation only: account access remains enforced by PortalKunde on every server call. */
import type { User } from './auth'
import { INNENDIENST_ROLLEN } from './portal-konto'

export function canInspectCustomerPortal(user: User | null): boolean {
  return Boolean(user?.roles.some(role => (INNENDIENST_ROLLEN as readonly string[]).includes(role)))
}

export async function loginLanding(user: User | null, loadAccounts: () => Promise<unknown>): Promise<'/' | '/portal'> {
  if (!user?.sub) throw new Error('Keine gültige Anmeldung für die Startauswahl')
  if (canInspectCustomerPortal(user)) return '/'
  const accounts = await loadAccounts()
  if (!Array.isArray(accounts) || accounts.some(account => !account || typeof account.customer_id !== 'string' || !account.customer_id.trim())) {
    throw new Error('Kundenzuordnung konnte nicht geprüft werden')
  }
  return accounts.length > 0 ? '/portal' : '/'
}
