/**
 * Sprach-Navigation (UIX-072, V2) — der harte Voice-Gate.
 *
 * Sprache darf ausschliesslich NAVIGIEREN (oder nichts treffen) — niemals eine
 * Aktion armieren. Command-Drafts (UIX-070) und gefaehrliche Aktionen sind per
 * Vertrag ("Danger nie per Stimme") aus dem Sprach-Pfad ausgeschlossen: diese
 * Funktion ruft bewusst NUR den Navigations-Compiler und gibt ausschliesslich
 * NavigateIntent | NoneIntent zurueck. V3/Command-Sprache waere UIX-080 mit
 * eigenem Ritual.
 */
import type { PaletteCommand } from '@/components/navigation/command-palette-model'
import { compileIntent, normalize } from '@/lib/omnibox/intent-compiler'
import type { CompileOptions, NavigateIntent, NoneIntent } from '@/lib/omnibox/types'

/** Praefix-Grammatik (V2): fuehrende Verben werden vor dem Matching entfernt. */
const NAV_PREFIXES = new Set(['oeffne', 'zeige', 'filtere', 'suche', 'zeig', 'finde'])

/** Entfernt ein fuehrendes Navigations-Verb (öffne/zeige/filtere/suche …). */
export function stripNavPrefix(text: string): string {
  const tokens = normalize(text).split(' ').filter(Boolean)
  if (tokens.length > 1 && NAV_PREFIXES.has(tokens[0])) {
    return tokens.slice(1).join(' ')
  }
  return tokens.join(' ')
}

/**
 * Kompiliert finalen Sprach-Text zu einem Navigations-Plan. Rueckgabe ist per
 * Typ auf navigate|none begrenzt — Sprache kann keine Command-Drafts erzeugen.
 */
export function compileVoiceNavigation(
  finalText: string,
  commands: PaletteCommand[],
  options: CompileOptions = {},
): NavigateIntent | NoneIntent {
  const query = stripNavPrefix(finalText)
  if (query.length === 0) return { kind: 'none', suggestions: [] }
  const plan = compileIntent(query, commands, options)
  // Sicherheitsnetz: der Navigations-Compiler liefert ohnehin nur navigate|none,
  // aber falls sich das je aendert, degradieren wir hier hart auf none.
  if (plan.kind === 'navigate' || plan.kind === 'none') return plan
  return { kind: 'none', suggestions: [] }
}
