/**
 * Omnibox-Command-Sicherheit (UIX-070).
 *
 * Uebersetzt eine per NL erkannte Aktion in eine IntentPlan-Variante — streng
 * nach der Sicherheitsmatrix aus ActionRuntime (`classifyOmniboxAction`). Kein
 * Auto-Submit: Drafts laufen durch das Confirmation-Ritual der Maske, Prefill
 * armiert nichts. high/critical → nur Navigation; forbiddenForAgents → gar nicht.
 */
import {
  classifyOmniboxAction,
  OMNIBOX_COMMAND_MIN_CONFIDENCE,
  type OmniboxActionDisposition,
} from '@/components/mask-builder/runtime/ActionRuntime'
import type { ActionDangerLevel } from '@/components/mask-builder/schema'
import type { CommandDraftIntent, FormPrefillIntent, NavigateIntent } from './types'

export { classifyOmniboxAction, OMNIBOX_COMMAND_MIN_CONFIDENCE }
export type { OmniboxActionDisposition }

/** Feld-Definition der Ziel-Aktion (aus SD action.fields[] oder Formular-Tab). */
export interface OmniboxActionField {
  key: string
  type?: string
  required?: boolean
}

export interface OmniboxActionInput {
  screenId: string
  routePath: string
  action: {
    key: string
    label: string
    dangerLevel?: ActionDangerLevel
    requiresConfirmation?: boolean
    forbiddenForAgents?: boolean
    fields?: OmniboxActionField[]
  }
}

/** Aus der NL-Eingabe extrahierte, typisierte Entitaeten fuer das Slot-Filling. */
export interface ExtractedEntities {
  /** ISO-Datum (yyyy-mm-dd) */
  date?: string
  /** Dezimalzahl */
  number?: number
  /** Freitext-Rest (Betreff, Notiz …) */
  text?: string
  /** Eindeutig aufgeloeste Lookups je Feldschluessel */
  lookups?: Record<string, string>
}

/**
 * Type-aware Slot-Filling: mappt erkannte Entitaeten auf die Feld-Definitionen
 * der Aktion. Nur Schema-Felder werden befuellt; Pflichtfelder ohne Wert landen
 * in missingFields (das Ritual fragt nach).
 */
export function fillPayloadDraft(
  fields: OmniboxActionField[],
  entities: ExtractedEntities,
): { payloadDraft: Record<string, unknown>; missingFields: string[] } {
  const payloadDraft: Record<string, unknown> = {}
  const lookups = entities.lookups ?? {}

  for (const field of fields) {
    if (field.key in lookups) {
      payloadDraft[field.key] = lookups[field.key]
      continue
    }
    const type = field.type ?? 'text'
    if ((type === 'date' || type === 'datetime') && entities.date !== undefined) {
      payloadDraft[field.key] = entities.date
    } else if ((type === 'number' || type === 'currency' || type === 'percentage') && entities.number !== undefined) {
      payloadDraft[field.key] = entities.number
    } else if ((type === 'text' || type === 'textarea' || type === 'email') && entities.text) {
      payloadDraft[field.key] = entities.text
    }
  }

  const missingFields = fields
    .filter((f) => f.required && payloadDraft[f.key] === undefined)
    .map((f) => f.key)

  return { payloadDraft, missingFields }
}

/**
 * Baut die IntentPlan-Variante fuer eine erkannte Aktion. Rueckgabe null =
 * Aktion im NL-Pfad nicht verfuegbar (forbiddenForAgents). navigateOnly liefert
 * eine reine NavigateIntent auf die Maske.
 */
export function buildCommandIntent(
  input: OmniboxActionInput,
  entities: ExtractedEntities,
  confidence: number,
  navigateCommand: NavigateIntent['command'],
): CommandDraftIntent | FormPrefillIntent | NavigateIntent | null {
  const disposition = classifyOmniboxAction(
    {
      dangerLevel: input.action.dangerLevel ?? 'safe',
      requiresConfirmation: input.action.requiresConfirmation ?? false,
      forbiddenForAgents: input.action.forbiddenForAgents ?? false,
    },
    confidence,
  )

  if (disposition === 'unavailable') return null

  if (disposition === 'navigateOnly') {
    return {
      kind: 'navigate',
      command: navigateCommand,
      routePath: input.routePath,
      filters: [],
      confidence,
      label: `${input.action.label} öffnen`,
    }
  }

  const fields = input.action.fields ?? []
  const { payloadDraft, missingFields } = fillPayloadDraft(fields, entities)

  if (disposition === 'formPrefill') {
    return {
      kind: 'formPrefill',
      screenId: input.screenId,
      actionKey: input.action.key,
      routePath: input.routePath,
      payloadDraft,
      label: input.action.label,
      confidence,
    }
  }

  // disposition === 'ritual'
  return {
    kind: 'commandDraft',
    screenId: input.screenId,
    actionKey: input.action.key,
    routePath: input.routePath,
    payloadDraft,
    missingFields,
    label: input.action.label,
    confidence,
  }
}
