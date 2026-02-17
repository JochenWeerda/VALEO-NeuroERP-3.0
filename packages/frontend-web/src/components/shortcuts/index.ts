/**
 * Shortcuts Module
 * Exportiert alle Shortcut-Komponenten und Utilities
 */

export { ShortcutHelpPanel, ShortcutHintButton, type ShortcutDefinition, type ShortcutDisplayMode } from './ShortcutHelpPanel'
export { GlobalShortcutProvider } from './GlobalShortcutProvider'
export { useGlobalShortcuts, globalShortcutManager, GLOBAL_SHORTCUTS, type GlobalShortcutAction } from '@/lib/shortcuts/global-shortcuts'

