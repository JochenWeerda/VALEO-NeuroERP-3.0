/**
 * Globale Keyboard-Shortcuts für alle Eingabemasken
 * Konsistente Shortcuts über alle Masken hinweg
 */
import { useEffect } from 'react'

export type GlobalShortcutAction =
  | 'open-customer-selection'
  | 'open-article-selection'
  | 'confirm-position'
  | 'save-document'
  | 'print-document'
  | 'delete-document'
  | 'close-document'
  | 'copy-previous-full' // F11: Kopiert ALLE Daten (Kunde + Positionen)
  | 'copy-previous-positions' // Strg+F8: Kopiert nur Positionen (ohne Kunde)
  | 'create-invoice'
  | 'open-attachments'
  | 'show-information'
  | 'cancel'

export type ShortcutHandler = (action: GlobalShortcutAction) => void | Promise<void>

type ShortcutConfig = {
  key: string
  label: string
  description: string
  category: string
  action: GlobalShortcutAction
}

/**
 * Standard-Shortcut-Definitionen für alle Eingabemasken
 */
export const GLOBAL_SHORTCUTS: ShortcutConfig[] = [
  {
    key: 'Strg+F1',
    label: 'Kundenauswahl',
    description: 'Kundenauswahl-Dialog öffnen',
    category: 'Navigation',
    action: 'open-customer-selection',
  },
  {
    key: 'Strg+F2',
    label: 'Artikelauswahl',
    description: 'Artikelauswahl-Dialog öffnen',
    category: 'Navigation',
    action: 'open-article-selection',
  },
  {
    key: 'Strg+F3',
    label: 'Position OK',
    description: 'Aktuelle Position übernehmen',
    category: 'Aktionen',
    action: 'confirm-position',
  },
  {
    key: 'Strg+F4',
    label: 'Speichern',
    description: 'Beleg speichern',
    category: 'Aktionen',
    action: 'save-document',
  },
  {
    key: 'Strg+F5',
    label: 'Drucken',
    description: 'Beleg drucken',
    category: 'Aktionen',
    action: 'print-document',
  },
  {
    key: 'Strg+F6',
    label: 'Löschen',
    description: 'Beleg löschen',
    category: 'Aktionen',
    action: 'delete-document',
  },
  {
    key: 'Strg+F7',
    label: 'Schließen',
    description: 'Beleg schließen',
    category: 'Navigation',
    action: 'close-document',
  },
  {
    key: 'Strg+F8',
    label: 'Wie vorheriger (nur Positionen)',
    description: 'Nur Positionen vom vorherigen Beleg übernehmen (aktuell ausgewählter Kunde bleibt erhalten)',
    category: 'Aktionen',
    action: 'copy-previous-positions',
  },
  {
    key: 'Strg+F9',
    label: 'Sofort-Rechnung',
    description: 'Sofort-Rechnung aus Beleg erstellen',
    category: 'Aktionen',
    action: 'create-invoice',
  },
  {
    key: 'Strg+F10',
    label: 'Unterlagen',
    description: 'Unterlagen-Dialog öffnen',
    category: 'Navigation',
    action: 'open-attachments',
  },
  {
    key: 'F11',
    label: 'Wie vorheriger Beleg',
    description: 'ALLE Daten vom vorherigen Beleg übernehmen (Kunde + Positionen)',
    category: 'Aktionen',
    action: 'copy-previous-full',
  },
  {
    key: 'Strg+F12',
    label: 'Information',
    description: 'Informationen anzeigen',
    category: 'Navigation',
    action: 'show-information',
  },
  {
    key: 'Esc',
    label: 'Abbrechen',
    description: 'Aktuelle Aktion abbrechen',
    category: 'Navigation',
    action: 'cancel',
  },
]

/**
 * Global Shortcut Manager
 * Verwaltet Shortcuts und Handler für alle Masken
 */
class GlobalShortcutManager {
  private handlers: Map<GlobalShortcutAction, ShortcutHandler> = new Map()
  private isEnabled = true

  /**
   * Registriere einen Handler für eine Aktion
   */
  registerHandler(action: GlobalShortcutAction, handler: ShortcutHandler): void {
    this.handlers.set(action, handler)
  }

  /**
   * Entferne Handler für eine Aktion
   */
  unregisterHandler(action: GlobalShortcutAction): void {
    this.handlers.delete(action)
  }

  /**
   * Führe eine Aktion aus
   */
  async execute(action: GlobalShortcutAction): Promise<void> {
    if (!this.isEnabled) return

    const handler = this.handlers.get(action)
    if (handler) {
      await handler(action)
    }
  }

  /**
   * Aktiviere/Deaktiviere Shortcuts
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled
  }

  /**
   * Prüfe ob Shortcuts aktiviert sind
   */
  getEnabled(): boolean {
    return this.isEnabled
  }
}

// Singleton-Instanz
export const globalShortcutManager = new GlobalShortcutManager()

/**
 * Hook für globale Shortcuts
 */
export function useGlobalShortcuts(
  handlers: Partial<Record<GlobalShortcutAction, ShortcutHandler>>
): void {
  useEffect(() => {
    // Registriere Handler
    Object.entries(handlers).forEach(([action, handler]) => {
      if (handler) {
        globalShortcutManager.registerHandler(action as GlobalShortcutAction, handler)
      }
    })

    // Cleanup: Entferne Handler
    return () => {
      Object.keys(handlers).forEach((action) => {
        globalShortcutManager.unregisterHandler(action as GlobalShortcutAction)
      })
    }
  }, [handlers])
}

/**
 * Keyboard-Event Handler
 */
export function handleGlobalShortcutKeyDown(e: KeyboardEvent): void {
  // F11 (ohne Strg) - "Wie vorheriger Beleg"
  if (e.key === 'F11' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
    e.preventDefault()
    e.stopPropagation()
    void globalShortcutManager.execute('copy-previous-full')
    return
  }

  // Strg+F1-F12
  if (e.ctrlKey && e.key.startsWith('F')) {
    const fKey = parseInt(e.key.substring(1))
    if (fKey >= 1 && fKey <= 12) {
      e.preventDefault()
      e.stopPropagation()

      const shortcuts: GlobalShortcutAction[] = [
        'open-customer-selection', // Strg+F1
        'open-article-selection', // Strg+F2
        'confirm-position', // Strg+F3
        'save-document', // Strg+F4
        'print-document', // Strg+F5
        'delete-document', // Strg+F6
        'close-document', // Strg+F7
        'copy-previous-positions', // Strg+F8: Nur Positionen
        'create-invoice', // Strg+F9
        'open-attachments', // Strg+F10
        'copy-previous-full', // Strg+F11: Alle Daten (Alternative zu F11)
        'show-information', // Strg+F12
      ]

      const action = shortcuts[fKey - 1]
      if (action) {
        void globalShortcutManager.execute(action)
      }
    }
  }

  // Esc
  if (e.key === 'Escape' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
    void globalShortcutManager.execute('cancel')
  }
}

