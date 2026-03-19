/**
 * useKeyboardShortcuts — Keyboard-Shortcut-System für Kernmasken (Gap 023, Wave 77)
 *
 * KPI: >=90% der Kernflows ohne Maus bedienbar
 * Unterstützt: Ctrl/Cmd+Key, Escape, F-Keys, reine Buchstaben-Keys (mit focus-guard)
 *
 * Verwendung:
 *   useKeyboardShortcuts([
 *     { key: 's', ctrl: true, label: 'Speichern', action: handleSave },
 *     { key: 'Escape', label: 'Abbrechen', action: handleCancel },
 *     { key: 'n', ctrl: true, label: 'Neu', action: handleNew },
 *   ])
 */

import { useEffect, useCallback, useRef } from 'react'

export interface KeyboardShortcut {
  /** Taste (z.B. 's', 'Escape', 'F2', 'Delete') */
  key: string
  /** Ctrl (Windows) oder Cmd (Mac) */
  ctrl?: boolean
  /** Alt / Option-Taste */
  alt?: boolean
  /** Shift-Taste */
  shift?: boolean
  /** Beschriftung für ShortcutBar (z.B. 'Speichern') */
  label: string
  /** Callback wenn ausgelöst */
  action: () => void
  /** false = Shortcut ignoriert wenn Eingabefeld fokussiert ist (default: false für Buchstaben) */
  allowInInputs?: boolean
  /** Deaktiviert den Shortcut (z.B. während Mutation läuft) */
  disabled?: boolean
}

/** Manche Keys sollen auch in Inputs auslösbar sein */
const INPUT_SAFE_KEYS = new Set(['Escape', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'])

function isInputElement(el: Element | null): boolean {
  if (!el) return false
  const tag = el.tagName.toLowerCase()
  return tag === 'input' || tag === 'textarea' || tag === 'select' || (el as HTMLElement).isContentEditable
}

/**
 * Registriert Keyboard-Shortcuts für die Dauer des Lebenszyklus der Komponente.
 * Shortcuts werden automatisch entregistriert beim Unmount.
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]): void {
  // Shortcut-Liste per Ref speichern (kein Re-Mount bei Änderungen)
  const shortcutsRef = useRef(shortcuts)
  shortcutsRef.current = shortcuts

  const handler = useCallback((e: KeyboardEvent) => {
    const active = document.activeElement
    const inInput = isInputElement(active)

    for (const sc of shortcutsRef.current) {
      if (sc.disabled) continue

      // Key-Match
      if (e.key !== sc.key && e.key.toLowerCase() !== sc.key.toLowerCase()) continue

      // Modifier-Match
      const ctrlMatch = (sc.ctrl ?? false) === (e.ctrlKey || e.metaKey)
      const altMatch = (sc.alt ?? false) === e.altKey
      const shiftMatch = (sc.shift ?? false) === e.shiftKey
      if (!ctrlMatch || !altMatch || !shiftMatch) continue

      // Input-Guard: Buchstaben-Shortcuts nicht in Eingabefeldern feuern
      // (außer explizit erlaubt oder Key ist input-safe)
      const isSafeKey = INPUT_SAFE_KEYS.has(sc.key) || (sc.ctrl ?? false) || (sc.alt ?? false)
      if (inInput && !sc.allowInInputs && !isSafeKey) continue

      e.preventDefault()
      e.stopPropagation()
      sc.action()
      break
    }
  }, [])

  useEffect(() => {
    window.addEventListener('keydown', handler, { capture: true })
    return () => window.removeEventListener('keydown', handler, { capture: true })
  }, [handler])
}

/**
 * Formatiert einen Shortcut für die Anzeige.
 * z.B. { key: 's', ctrl: true } → 'Ctrl+S' oder '⌘S' auf Mac
 */
export function formatShortcutLabel(sc: Pick<KeyboardShortcut, 'key' | 'ctrl' | 'alt' | 'shift'>): string {
  const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform)
  const parts: string[] = []

  if (sc.ctrl) parts.push(isMac ? '⌘' : 'Ctrl')
  if (sc.alt) parts.push(isMac ? '⌥' : 'Alt')
  if (sc.shift) parts.push(isMac ? '⇧' : 'Shift')

  const key = sc.key === ' ' ? 'Space' : sc.key.length === 1 ? sc.key.toUpperCase() : sc.key
  parts.push(key)

  return isMac ? parts.join('') : parts.join('+')
}

/**
 * Standard-Shortcuts für alle Kernmasken (ObjectPage, ListReport, Wizard)
 */
export interface CoreMaskShortcuts {
  onSave?: () => void
  onCancel?: () => void
  onNew?: () => void
  onDelete?: () => void
  onSearch?: () => void
  onRefresh?: () => void
  isSaveDisabled?: boolean
  isDeleteDisabled?: boolean
}

export function buildCoreMaskShortcuts(opts: CoreMaskShortcuts): KeyboardShortcut[] {
  const shortcuts: KeyboardShortcut[] = []

  if (opts.onSave) {
    shortcuts.push({
      key: 's',
      ctrl: true,
      label: 'Speichern',
      action: opts.onSave,
      disabled: opts.isSaveDisabled,
      allowInInputs: true,
    })
  }
  if (opts.onCancel) {
    shortcuts.push({
      key: 'Escape',
      label: 'Abbrechen',
      action: opts.onCancel,
      allowInInputs: false,
    })
  }
  if (opts.onNew) {
    shortcuts.push({
      key: 'n',
      ctrl: true,
      label: 'Neu',
      action: opts.onNew,
    })
  }
  if (opts.onDelete) {
    shortcuts.push({
      key: 'Delete',
      ctrl: true,
      label: 'Löschen',
      action: opts.onDelete,
      disabled: opts.isDeleteDisabled,
    })
  }
  if (opts.onSearch) {
    shortcuts.push({
      key: 'f',
      ctrl: true,
      label: 'Suchen',
      action: opts.onSearch,
      allowInInputs: false,
    })
  }
  if (opts.onRefresh) {
    shortcuts.push({
      key: 'F5',
      label: 'Aktualisieren',
      action: opts.onRefresh,
      allowInInputs: true,
    })
  }

  return shortcuts
}
