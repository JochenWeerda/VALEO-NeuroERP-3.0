/**
 * Registriert Shortcut-Handler sowohl für Tastatur (globalShortcutManager) als auch
 * für Sprachsteuerung (ActionDispatchContext). Eine Maske ruft diesen Hook statt
 * useGlobalShortcuts auf, dann funktionieren Strg+Fx und Sprachbefehle mit denselben Aktionen.
 */

import { useEffect } from 'react'
import {
  useGlobalShortcuts,
  type GlobalShortcutAction,
  type ShortcutHandler,
} from '@/lib/shortcuts/global-shortcuts'
import { useActionDispatchOptional } from '../context/ActionDispatchHooks'

export function useGlobalShortcutsWithVoice(
  handlers: Partial<Record<GlobalShortcutAction, ShortcutHandler>>
): void {
  useGlobalShortcuts(handlers)

  const dispatchContext = useActionDispatchOptional()

  useEffect(() => {
    if (!dispatchContext) return
    const unregs = Object.entries(handlers)
      .filter(([, h]) => typeof h === 'function')
      .map(([actionId, handler]) =>
        dispatchContext.registerHandler(
          actionId,
          (_params) => void (handler as ShortcutHandler)(actionId as GlobalShortcutAction)
        )
      )
    return () => {
      unregs.forEach((u) => u())
    }
  }, [dispatchContext, handlers])
}

