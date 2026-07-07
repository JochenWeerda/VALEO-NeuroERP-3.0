/**
 * NL-Command-Erkennung (UIX-070).
 *
 * Erkennt in einer Omnibox-Eingabe ein Aktions-Verb fuer die getroffene Maske
 * und erzeugt — streng nach der Sicherheitsmatrix — eine commandDraft/formPrefill/
 * navigate-Variante. Rein & testbar; die Confirmation/Ausfuehrung uebernimmt der
 * bestehende Maskenpfad (kein Auto-Submit).
 */
import type { OmniboxAction } from '@/lib/api/mask-registry'
import { normalize, extractDateFilters } from './intent-compiler'
import { buildCommandIntent, type ExtractedEntities, type OmniboxActionField } from './command-safety'
import type { CommandDraftIntent, FormPrefillIntent, NavigateIntent } from './types'

const VERB_STOPWORDS = new Set([
  'der', 'die', 'das', 'den', 'dem', 'ein', 'eine', 'mit', 'und', 'oder', 'fuer',
  'von', 'im', 'in', 'am', 'an', 'auf', 'zeig', 'zeige', 'mir', 'alle', 'oeffne',
  'bitte', 'neue', 'neuer', 'neu', 'zu',
])

function tokenize(text: string): string[] {
  return normalize(text).split(' ').filter((t) => t.length > 0)
}

/** Findet die Aktion, deren Verben die meisten Query-Tokens treffen. */
function matchAction(tokens: string[], actions: OmniboxAction[]): { action: OmniboxAction; matched: Set<string> } | null {
  let best: { action: OmniboxAction; matched: Set<string> } | null = null
  for (const action of actions) {
    const verbs = new Set(action.verbs.map((v) => normalize(v)))
    const matched = new Set(tokens.filter((t) => verbs.has(t) || Array.from(verbs).some((v) => v.length >= 4 && (v.startsWith(t) || t.startsWith(v)) && t.length >= 4)))
    if (matched.size === 0) continue
    if (!best || matched.size > best.matched.size) best = { action, matched }
  }
  return best
}

export interface CommandDetectionInput {
  screenId: string
  route: string
  actions: OmniboxAction[]
  /** Navigations-Command des getroffenen Screens (fuer navigateOnly/Fallback). */
  navigateCommand: NavigateIntent['command']
  /** Tokens, die bereits den Screen selbst getroffen haben (nicht als Freitext werten). */
  screenTokens?: Set<string>
}

/**
 * Erzeugt eine Command-Variante, wenn die Eingabe ein Aktions-Verb fuer den Screen
 * enthaelt — sonst null (dann bleibt es beim reinen Navigations-Plan).
 */
export function detectCommandIntent(
  query: string,
  input: CommandDetectionInput,
  options: { today?: string; confidence?: number } = {},
): CommandDraftIntent | FormPrefillIntent | NavigateIntent | null {
  if (!input.actions || input.actions.length === 0) return null
  const tokens = tokenize(query)
  if (tokens.length === 0) return null

  const match = matchAction(tokens, input.actions)
  if (!match) return null

  const todayIso = options.today ?? new Date().toISOString().slice(0, 10)
  const { filters, consumed } = extractDateFilters(tokens, todayIso)
  const dateFilter = filters.find((f) => f.key === 'date' || f.key === 'from')
  const numberToken = tokens.find((t) => /^\d+([.,]\d+)?$/.test(t))

  const screenTokens = input.screenTokens ?? new Set<string>()
  const restTokens = tokens.filter(
    (t) =>
      !match.matched.has(t) &&
      !consumed.has(t) &&
      !screenTokens.has(t) &&
      !VERB_STOPWORDS.has(t) &&
      t !== numberToken,
  )

  const entities: ExtractedEntities = {
    date: dateFilter?.value,
    number: numberToken ? Number(numberToken.replace(',', '.')) : undefined,
    text: restTokens.length > 0 ? restTokens.join(' ') : undefined,
  }

  // Konfidenz: Verb-Treffer stark, Freitext-Kontext leicht erhoehend.
  const confidence = options.confidence ?? Math.min(1, 0.7 + 0.1 * match.matched.size + (entities.text ? 0.1 : 0))

  const fields: OmniboxActionField[] = match.action.fields
  return buildCommandIntent(
    {
      screenId: input.screenId,
      routePath: input.route,
      action: {
        key: match.action.key,
        label: match.action.label,
        dangerLevel: match.action.dangerLevel,
        requiresConfirmation: match.action.requiresConfirmation,
        forbiddenForAgents: match.action.forbiddenForAgents,
        fields,
      },
    },
    entities,
    confidence,
    input.navigateCommand,
  )
}
