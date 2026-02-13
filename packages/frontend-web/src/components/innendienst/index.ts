/**
 * Innendienst Components
 *
 * Komponenten für Power-User im Innendienst (CRM/Sales):
 * - Keyboard-First Navigation
 * - Command Palette (Ctrl+K)
 * - Quick Search
 * - Tastenkürzel-System
 */

export {
  CommandPalette,
  useCommandPalette,
  type CommandItem,
} from './CommandPalette'

export { QuickSearch, type SearchResult } from './QuickSearch'

export {
  KeyboardShortcutsHelp,
  useKeyboardShortcutsHelp,
} from './KeyboardShortcutsHelp'
