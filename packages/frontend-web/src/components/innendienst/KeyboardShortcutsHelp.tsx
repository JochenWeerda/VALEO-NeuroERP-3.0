/**
 * Keyboard Shortcuts Help
 *
 * Overlay mit allen verfügbaren Tastenkombinationen
 * Öffnet mit Shift+?
 */

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Command, Keyboard } from 'lucide-react'

interface ShortcutGroup {
  title: string
  shortcuts: {
    keys: string[]
    description: string
  }[]
}

const shortcutGroups: ShortcutGroup[] = [
  {
    title: 'Global',
    shortcuts: [
      { keys: ['Ctrl', 'K'], description: 'Command Palette öffnen' },
      { keys: ['Ctrl', '/'], description: 'Schnellsuche fokussieren' },
      { keys: ['Shift', '?'], description: 'Tastenkürzel anzeigen' },
      { keys: ['Esc'], description: 'Dialog schließen / Abbrechen' },
    ],
  },
  {
    title: 'Navigation',
    shortcuts: [
      { keys: ['G', 'H'], description: 'Zum Dashboard' },
      { keys: ['G', 'K'], description: 'Zu Kunden' },
      { keys: ['G', 'A'], description: 'Zu Aufträgen' },
      { keys: ['G', 'R'], description: 'Zu Rechnungen' },
      { keys: ['G', 'L'], description: 'Zum Lager' },
    ],
  },
  {
    title: 'Aktionen',
    shortcuts: [
      { keys: ['N', 'K'], description: 'Neuer Kunde' },
      { keys: ['N', 'A'], description: 'Neuer Auftrag' },
      { keys: ['N', 'O'], description: 'Neues Angebot' },
      { keys: ['N', 'R'], description: 'Neue Rechnung' },
    ],
  },
  {
    title: 'Bearbeitung',
    shortcuts: [
      { keys: ['Ctrl', 'S'], description: 'Speichern' },
      { keys: ['Ctrl', 'Enter'], description: 'Speichern und Schließen' },
      { keys: ['Ctrl', 'Z'], description: 'Rückgängig' },
      { keys: ['Ctrl', 'Shift', 'Z'], description: 'Wiederholen' },
    ],
  },
  {
    title: 'Tabellen',
    shortcuts: [
      { keys: ['↑', '↓'], description: 'Zeile wechseln' },
      { keys: ['Tab'], description: 'Nächste Zelle' },
      { keys: ['Shift', 'Tab'], description: 'Vorherige Zelle' },
      { keys: ['Enter'], description: 'Zeile bearbeiten / bestätigen' },
      { keys: ['Delete'], description: 'Zeile löschen' },
      { keys: ['Ctrl', '+'], description: 'Neue Zeile' },
    ],
  },
]

interface KeyboardShortcutsHelpProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function KeyboardShortcutsHelp({
  open,
  onOpenChange,
}: KeyboardShortcutsHelpProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5" />
            Tastenkürzel
          </DialogTitle>
        </DialogHeader>

        <div className="grid gap-6 py-4">
          {shortcutGroups.map((group) => (
            <div key={group.title}>
              <h3 className="text-sm font-semibold text-muted-foreground mb-3">
                {group.title}
              </h3>
              <div className="space-y-2">
                {group.shortcuts.map((shortcut, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-muted/50"
                  >
                    <span className="text-sm">{shortcut.description}</span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, keyIdx) => (
                        <span key={keyIdx} className="flex items-center">
                          {keyIdx > 0 && (
                            <span className="text-muted-foreground mx-1">+</span>
                          )}
                          <kbd className="inline-flex h-6 min-w-[24px] items-center justify-center rounded border bg-muted px-1.5 text-xs font-medium">
                            {key === 'Ctrl' ? (
                              <span className="flex items-center gap-0.5">
                                <Command className="h-3 w-3" />
                              </span>
                            ) : (
                              key
                            )}
                          </kbd>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t text-sm text-muted-foreground text-center">
          Drücken Sie <kbd className="inline-flex h-5 items-center rounded border bg-muted px-1 mx-1 text-xs">Esc</kbd> zum Schließen
        </div>
      </DialogContent>
    </Dialog>
  )
}

/**
 * Hook für Shift+? Shortcut
 */
export function useKeyboardShortcutsHelp() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === '?') {
        e.preventDefault()
        setOpen(o => !o)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { open, setOpen }
}
