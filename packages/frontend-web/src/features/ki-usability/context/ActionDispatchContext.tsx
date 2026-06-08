/**
 * Central dispatcher for actions: same entry point for Toolbar, Command Palette, Shortcut, and Voice.
 * Pages register handlers for action IDs; dispatch(actionId, params) runs the handler or falls back to navigation.
 */

import {
  createContext,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { globalShortcutManager, type GlobalShortcutAction } from '@/lib/shortcuts/global-shortcuts'

type ActionHandler = (params: Record<string, unknown>) => void | Promise<void>

type ActionDispatchContextValue = {
  registerHandler: (actionId: string, handler: ActionHandler) => () => void
  dispatch: (actionId: string, params?: Record<string, unknown>) => Promise<boolean>
}

export const ActionDispatchContext = createContext<ActionDispatchContextValue | null>(null)

const NAV_ACTIONS: Record<string, string> = {
  'nav-dashboard': '/',
  'nav-customers': '/verkauf/kunden-liste',
  'nav-orders': '/sales/auftraege-liste',
  'nav-invoices': '/sales/rechnungen-liste',
  'nav-inventory': '/lager/bestandsuebersicht',
  'nav-fibu': '/fibu-suite',
  'action-new-order': '/sales/order-editor',
  'action-new-invoice': '/finance/invoices/new',
  'action-new-customer': '/verkauf/kunde/neu',
  // Slice-010: Lager / Einkauf / HR
  'nav-lager': '/lager/bestandsuebersicht',
  'lager-wareneingang': '/lager/einlagerung',
  'lager-inventur': '/lager/inventur',
  'lager-umlagerung': '/lager/lagerbewegungen',
  'lager-artikel-suche': '/lager/bestandsuebersicht',
  'nav-einkauf': '/einkauf/bestellungen',
  'einkauf-bestellung-neu': '/einkauf/bestellungen',
  'einkauf-lieferantenrechnung': '/einkauf/rechnung-eingang-erfassung',
  'einkauf-angebot': '/einkauf/anfrage-erfassung',
  'einkauf-lieferant-suche': '/einkauf/lieferanten',
  'nav-hr': '/personal/mitarbeiter-liste',
  'hr-abwesenheit': '/personal/zeiterfassung',
  'hr-mitarbeiter-neu': '/personal/onboarding',
  'hr-lohnlauf': '/personal/hrm-operations-gates',
  'hr-mitarbeiter-suche': '/personal/mitarbeiter-liste',
  // Slice-011 Wave A: Verkauf
  'nav-verkauf': '/sales/orders-modern',
  'nav-angebote': '/sales/angebote-liste',
  'nav-lieferscheine': '/sales/lieferungen-liste',
  'verkauf-angebot-neu': '/sales/angebot/neu',
  'verkauf-lieferschein-neu': '/sales/delivery-editor-new',
  'verkauf-kunde-suche': '/verkauf/kunden-liste',
  'verkauf-artikel-suche': '/artikel/liste',
  // Slice-011 Wave A: CRM
  'nav-crm': '/crm/crm-dashboard',
  'nav-crm-leads': '/crm/leads',
  'nav-crm-aktivitaeten': '/crm/aktivitaeten',
  'nav-crm-betriebsprofile': '/crm/betriebsprofile-liste',
  'nav-crm-kontakte': '/crm/kontakte-liste',
  'crm-lead-neu': '/crm/leads',
  'crm-aktivitaet-neu': '/crm/aktivitaeten',
  'crm-kontakt-suche': '/crm/kontakte-liste',
  // Slice-012 Wave B: Finanzen
  'nav-fibu-hauptbuch': '/fibu/hauptbuch',
  'nav-op-debitoren': '/finance/op-debitoren',
  'nav-op-kreditoren': '/finance/op-kreditoren',
  'nav-zahlungslaeufe': '/fibu/zahlungslaeufe',
  'finance-booking': '/finance/bookings/new',
  'nav-buchungsjournal': '/fibu/buchungsjournal',
  'nav-ustva': '/export/ustva',
  'nav-bilanz': '/fibu/bilanz',
  // Slice-012 Wave B: Compliance
  'nav-compliance-dashboard': '/admin/compliance',
  'nav-verarbeitungsverzeichnis': '/compliance/verarbeitungsverzeichnis',
  'nav-datenpannen': '/compliance/datenpannen',
  'compliance-dsgvo-anfragen': '/crm/gdpr-requests',
  'nav-sanktionspruefung': '/compliance/sanktionspruefung',
  // Slice-012 Wave C: Agrar
  'nav-agrar': '/agrar/ernte-annahme-erfassung',
  'nav-ernte-annahme': '/agrar/annahme',
  'agrar-ernte-erfassen': '/agrar/ernte-annahme-erfassung',
  'nav-agrar-vertraege': '/agrar/vertraege',
  'nav-schlaege': '/agrar/schlaege',
  'nav-silos': '/lager/silos',
  'nav-rohware-annahme': '/agrar/annahme/rohware',
  'nav-feldbuch': '/agrar/schlaege',
  // Slice-012 Wave C: Logistik
  'nav-logistik': '/logistik/tourenplanung',
  'nav-tourenplanung': '/logistik/tourenplanung',
  'nav-frachtbriefe': '/logistik/frachtbriefe',
  'nav-versandprofile': '/logistik/versandprofile',
  'logistik-tour-planen': '/logistik/tourenplanung',
}

const GLOBAL_SHORTCUT_ACTION_IDS = new Set<string>([
  'open-customer-selection',
  'open-article-selection',
  'confirm-position',
  'save-document',
  'print-document',
  'delete-document',
  'close-document',
  'copy-previous-positions',
  'create-invoice',
  'open-attachments',
  'copy-previous-full',
  'show-information',
  'cancel',
])

export function ActionDispatchProvider({ children }: { children: ReactNode }): JSX.Element {
  const navigate = useNavigate()
  const handlersRef = useMemo(() => new Map<string, ActionHandler>(), [])

  const registerHandler = useCallback((actionId: string, handler: ActionHandler) => {
    handlersRef.set(actionId, handler)
    return () => {
      handlersRef.delete(actionId)
    }
  }, [handlersRef])

  const dispatch = useCallback(
    async (actionId: string, params?: Record<string, unknown>): Promise<boolean> => {
      const handler = handlersRef.get(actionId)
      if (handler) {
        try {
          await handler(params ?? {})
          return true
        } catch {
          return false
        }
      }
      const path = NAV_ACTIONS[actionId]
      if (path) {
        navigate(path)
        return true
      }
      const dynamicPath = typeof params?.path === 'string' ? params.path : null
      if (dynamicPath) {
        navigate(dynamicPath)
        return true
      }
      const eventName = typeof params?.eventName === 'string' ? params.eventName : null
      if (eventName) {
        const detail = params?.eventDetail
        window.dispatchEvent(new CustomEvent(eventName, { detail }))
        return true
      }
      if (GLOBAL_SHORTCUT_ACTION_IDS.has(actionId)) {
        await globalShortcutManager.execute(actionId as GlobalShortcutAction)
        return true
      }
      return false
    },
    [navigate, handlersRef]
  )

  const value = useMemo<ActionDispatchContextValue>(
    () => ({ registerHandler, dispatch }),
    [registerHandler, dispatch]
  )

  return (
    <ActionDispatchContext.Provider value={value}>
      {children}
    </ActionDispatchContext.Provider>
  )
}

export type { ActionDispatchContextValue }
