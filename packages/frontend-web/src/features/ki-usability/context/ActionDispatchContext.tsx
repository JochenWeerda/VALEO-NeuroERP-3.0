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
import { useNavigate } from '@/app/routing/typed-router'
import {
  callAgrarContractOpen,
  callWeighingTicketOpen,
  pickSafeAgrarContractRoutePath,
  pickSafeWeighingRoutePath,
} from '@/lib/mcp-agrar-open'
import { callCellStatusOpen, pickSafeCellRoutePath } from '@/lib/mcp-cell-open'
import { callCustomerOpen, pickSafeCustomerRoutePath } from '@/lib/mcp-customer-open'
import { callDocumentSearchOpen, pickSafeDmsDocumentRoutePath } from '@/lib/mcp-dms-open'
import { callLotTraceOpen, pickSafeLotRoutePath } from '@/lib/mcp-lot-open'
import { callOrderStatusOpen, pickSafeOrderRoutePath } from '@/lib/mcp-order-open'
import { callPoStatusOpen, pickSafePoRoutePath } from '@/lib/mcp-po-open'
import { callStockBestandOpen, pickSafeStockRoutePath } from '@/lib/mcp-stock-open'
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
  'nav-invoices': '/verkauf/rechnungen',
  'nav-inventory': '/lager/bestandsuebersicht',
  'nav-lot': '/charge/rueckverfolgung',
  'nav-silo-cell': '/lager/silo-uebersicht',
  'nav-nachweisraum': '/docflow/nachweisraum',
  'nav-wiegeschein': '/waage/wiegeschein-detail',
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
  'nav-kreditoren': '/fibu/kreditoren',
  'nav-zahlungsvorschlaege': '/fibu/zahlungsvorschlaege',
  'nav-op-verwaltung': '/fibu/op-verwaltung',
  'nav-anlieferavis': '/einkauf/anlieferavis-liste',
  'nav-auftragsbestaetigungen': '/einkauf/auftragsbestaetigungen',
  'nav-einkaufsanfragen': '/einkauf/anfragen',
  'nav-fibu-offene-posten': '/fibu/offene-posten',
  'finance-booking': '/finance/bookings/new',
  'nav-buchungsjournal': '/fibu/buchungsjournal',
  'nav-buchungsimport': '/finance/buchungsimport',
  'nav-schnittstelle-fibu': '/fibu/schnittstelle-fibu',
  'nav-ustva': '/export/ustva',
  'nav-bilanz': '/fibu/bilanz',
  'nav-bwa': '/fibu/bwa',
  'nav-guv': '/fibu/guv',
  'nav-lastschriften-debitoren': '/finance/lastschriften-debitoren',
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
      if (actionId === 'nav-customers') {
        const direct = pickSafeCustomerRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const kundenNr = typeof params?.kunden_nr === 'string' ? params.kunden_nr.trim() : ''
        if (kundenNr) {
          try {
            const opened = await callCustomerOpen(kundenNr)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-customers'])
        return true
      }
      if (actionId === 'nav-orders') {
        const direct = pickSafeOrderRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const auftragNr = typeof params?.auftrag_nr === 'string' ? params.auftrag_nr.trim() : ''
        if (auftragNr) {
          try {
            const opened = await callOrderStatusOpen(auftragNr)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-orders'])
        return true
      }
      if (actionId === 'nav-lot') {
        const direct = pickSafeLotRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const lotId = typeof params?.lot_id === 'string' ? params.lot_id.trim() : ''
        if (lotId) {
          try {
            const opened = await callLotTraceOpen(lotId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-lot'])
        return true
      }
      if (actionId === 'nav-silo-cell') {
        const direct = pickSafeCellRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const cellCode = typeof params?.cell_code === 'string' ? params.cell_code.trim() : ''
        if (cellCode) {
          try {
            const opened = await callCellStatusOpen(cellCode)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-silo-cell'])
        return true
      }
      if (actionId === 'nav-einkauf') {
        const direct = pickSafePoRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const bestellungId =
          typeof params?.bestellung_id === 'string' ? params.bestellung_id.trim() : ''
        if (bestellungId) {
          try {
            const opened = await callPoStatusOpen(bestellungId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-einkauf'])
        return true
      }
      if (actionId === 'nav-nachweisraum') {
        const direct = pickSafeDmsDocumentRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const dokumentId =
          typeof params?.dokument_id === 'string' ? params.dokument_id.trim() : ''
        if (dokumentId) {
          try {
            const opened = await callDocumentSearchOpen(dokumentId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-nachweisraum'])
        return true
      }
      if (actionId === 'nav-agrar-vertraege') {
        const direct = pickSafeAgrarContractRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const kontraktId =
          typeof params?.kontrakt_id === 'string' ? params.kontrakt_id.trim() : ''
        if (kontraktId) {
          try {
            const opened = await callAgrarContractOpen(kontraktId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-agrar-vertraege'])
        return true
      }
      if (actionId === 'nav-wiegeschein') {
        const direct = pickSafeWeighingRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const ticketId = typeof params?.ticket_id === 'string' ? params.ticket_id.trim() : ''
        if (ticketId) {
          try {
            const opened = await callWeighingTicketOpen(ticketId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-wiegeschein'])
        return true
      }
      if (actionId === 'nav-lager') {
        const direct = pickSafeStockRoutePath(params?.route_path)
        if (direct) {
          navigate(direct)
          return true
        }
        const artikelId =
          typeof params?.artikel_id === 'string' ? params.artikel_id.trim() : ''
        if (artikelId) {
          try {
            const opened = await callStockBestandOpen(artikelId)
            navigate(opened.route_path)
            return true
          } catch {
            return false
          }
        }
        navigate(NAV_ACTIONS['nav-lager'])
        return true
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
