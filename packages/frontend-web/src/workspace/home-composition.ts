/**
 * Home-Slots aus der Studio-Preview-Session.
 * Parser und Session-Helper bleiben in src/studio — hier nur konsumieren.
 * Home mountet denselben WorkspaceCompositionHost (variant=embedded), nicht nur Kind-Filter.
 */

import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  normalizeWorkspaceComposition,
  type SpecializedComponentKind,
  type WorkspaceComposition,
} from '@/studio/workspace-composition'
import {
  applyCompositionPersonalization,
  type CompositionPersonalizationOverlay,
} from '@/studio/workspace-composition-overlay'
import {
  isSpecializedKindEnabled,
  readWorkspaceCompositionSession,
} from '@/studio/workspace-composition-session'
import type { WorkspaceSignal } from './types'

/**
 * Fallback-Kinds wenn keine gueltige Session vorliegt — Reihenfolge wie Fixture-Views
 * (Dispo vor Inbox), damit Home und Studio denselben Host-Pfad teilen.
 */
export const DEFAULT_HOME_SPECIALIST_KINDS: readonly SpecializedComponentKind[] = [
  'disposition_board',
  'inbox',
] as const

const HOME_SLOT_KINDS = new Set<SpecializedComponentKind>(DEFAULT_HOME_SPECIALIST_KINDS)

export type HomeCompositionResolution = {
  /** Gueltige Composition fuer WorkspaceCompositionHost (auch Fallback = Fixture). */
  composition: WorkspaceComposition
  /** Spezial-Kinds in Host-View-Reihenfolge; leer = Host nicht mounten. */
  kinds: SpecializedComponentKind[]
  source: 'session' | 'fallback'
}

export function kindsFromValidComposition(
  compositionInput: WorkspaceComposition,
): SpecializedComponentKind[] {
  const composition = normalizeWorkspaceComposition(compositionInput)
  const kinds: SpecializedComponentKind[] = []

  for (const view of composition.views) {
    for (const slot of composition.specializedComponents) {
      if (slot.hostViewId !== view.id) continue
      if (!HOME_SLOT_KINDS.has(slot.kind)) continue
      if (!isSpecializedKindEnabled(composition, slot.kind)) continue
      if (kinds.includes(slot.kind)) continue
      kinds.push(slot.kind)
    }
  }

  return kinds
}

/**
 * Persönliches View-Pin/Start-Fix auf Home anwenden — ohne Studio-Session zu schreiben.
 * Reihenfolge der Specialist-Kinds folgt den gepinnten/fixierten Views.
 */
export function personalizeHomeComposition(
  resolution: HomeCompositionResolution,
  overlay: CompositionPersonalizationOverlay,
): HomeCompositionResolution {
  const composition = applyCompositionPersonalization(resolution.composition, overlay)
  return {
    composition,
    kinds: kindsFromValidComposition(composition),
    source: resolution.source,
  }
}

function fallbackHomeComposition(): HomeCompositionResolution {
  return {
    composition: WORKSPACE_COMPOSITION_FIXTURE,
    kinds: kindsFromValidComposition(WORKSPACE_COMPOSITION_FIXTURE),
    source: 'fallback',
  }
}

/**
 * Liest die Composition fuer Home → denselben Host wie Studio-Preview.
 * Ohne sub: `valeo.workspace.composition`. Mit sub: `.<sub>`.
 * Mit Mandant und sub: `.<tenant>.<sub>`.
 * Leer oder ungueltig: Fixture-Fallback (volle Inbox+Dispo).
 * Gueltig mit leeren Slots: kinds=[] → kein Host-Mount.
 */
export function resolveHomeComposition(
  storage?: Pick<Storage, 'getItem'>,
  sub?: string | null,
  tenantId?: string | null,
): HomeCompositionResolution {
  try {
    const source =
      storage ?? (typeof sessionStorage === 'undefined' ? undefined : sessionStorage)
    if (!source) {
      return fallbackHomeComposition()
    }

    const session = readWorkspaceCompositionSession(source, sub, tenantId)
    if (session.status === 'empty' || session.status === 'invalid') {
      return fallbackHomeComposition()
    }

    return {
      composition: session.composition,
      kinds: kindsFromValidComposition(session.composition),
      source: 'session',
    }
  } catch {
    // sessionStorage kann werfen; Home darf nicht abstuerzen.
    return fallbackHomeComposition()
  }
}

/**
 * Kind-Filter fuer Signale — abgeleitet aus resolveHomeComposition.
 * Leer oder ungueltig: Fixture-Default (nicht eine leere Liste).
 */
export function resolveHomeSpecialistKinds(
  storage?: Pick<Storage, 'getItem'>,
  sub?: string | null,
  tenantId?: string | null,
): SpecializedComponentKind[] {
  return resolveHomeComposition(storage, sub, tenantId).kinds
}

/**
 * Quellen, die zu einem Home-Specialist gehoeren.
 * Andere Live-Signale (Freigaben, Kalender, SSE, Agrar-Kette) haben hier kein Kind.
 */
const HOME_SIGNAL_SPECIALIST_KIND: Readonly<Record<string, SpecializedComponentKind>> = {
  'inbox-queue': 'inbox',
  'queue:inbox': 'inbox',
  'disposition:open-abrufe': 'disposition_board',
}

export function homeSignalSpecialistKind(
  signal: Pick<WorkspaceSignal, 'source'>,
): SpecializedComponentKind | null {
  return HOME_SIGNAL_SPECIALIST_KIND[signal.source] ?? null
}

/**
 * Laesst Signale weg, deren Specialist-Kind die aufgeloeste Composition nicht enthaelt.
 * `mountedKinds` kommt aus resolveHomeSpecialistKinds: leer oder ungueltig ist dort
 * schon der bisherige Default, nicht eine leere Liste — ausser Session ohne Slots.
 */
export function signalsForHomeSpecialists<T extends Pick<WorkspaceSignal, 'source'>>(
  signals: readonly T[],
  mountedKinds: readonly SpecializedComponentKind[],
): T[] {
  const mounted = new Set(mountedKinds)
  return signals.filter((signal) => {
    const kind = homeSignalSpecialistKind(signal)
    return kind === null || mounted.has(kind)
  })
}
