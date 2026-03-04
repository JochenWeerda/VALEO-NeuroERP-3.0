/**
 * Central dispatcher for actions: same entry point for Toolbar, Command Palette, Shortcut, and Voice.
 * Pages register handlers for action IDs; dispatch(actionId, params) runs the handler or falls back to navigation.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import { globalShortcutManager } from '@/lib/shortcuts/global-shortcuts'
import type { GlobalShortcutAction } from '@/lib/shortcuts/global-shortcuts'

type ActionHandler = (params: Record<string, unknown>) => void | Promise<void>

type ActionDispatchContextValue = {
  registerHandler: (actionId: string, handler: ActionHandler) => () => void
  dispatch: (actionId: string, params?: Record<string, unknown>) => Promise<boolean>
}

const ActionDispatchContext = createContext<ActionDispatchContextValue | null>(null)

const NAV_ACTIONS: Record<string, string> = {
  'nav-dashboard': '/',
  'nav-customers': '/crm/kunden-stamm',
  'nav-orders': '/sales/auftraege-liste',
  'nav-invoices': '/sales/rechnungen-liste',
  'nav-inventory': '/lager/bestandsuebersicht',
  'nav-fibu': '/fibu-suite',
  'action-new-order': '/sales/order-editor',
  'action-new-invoice': '/finance/invoices/new',
  'action-new-customer': '/verkauf/kunde-neu',
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

export function useActionDispatch(): ActionDispatchContextValue {
  const ctx = useContext(ActionDispatchContext)
  if (!ctx) {
    throw new Error('useActionDispatch must be used within ActionDispatchProvider')
  }
  return ctx
}

export function useActionDispatchOptional(): ActionDispatchContextValue | null {
  return useContext(ActionDispatchContext)
}
