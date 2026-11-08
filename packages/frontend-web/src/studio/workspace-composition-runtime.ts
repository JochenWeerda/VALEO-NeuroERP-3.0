/**
 * WorkspaceComposition Runtime — mountet Spezial-Slots aus einer Composition.
 *
 * ADDITIV zum Parser/Validator: keine Schema-Aenderung, keine Meridian-Pipeline.
 * inbox → bestehendes InboxWidget; disposition_board → registrierte Tafel
 * derselben Dispositionsseite (kein Navigationslink, kein zweites Board).
 */

import {
  normalizeWorkspaceComposition,
  type SpecializedComponentKind,
  type WorkspaceComposition,
  type WorkspaceSpecializedComponentRef,
} from './workspace-composition'

/** Bestehende Dispo-Tafel — keine zweite Implementierung. */
export const DISPOSITION_BOARD_ROUTE = '/disposition/touren-disposition' as const

/** Vorgesehener Preview-Pfad (Registrierung ohne Godfile-Routenbaum). */
export const WORKSPACE_COMPOSITION_PREVIEW_ROUTE =
  '/studio/workspace-composition-preview' as const

export type WorkspaceSlotMountBase = {
  id: string
  kind: SpecializedComponentKind
  label: string
  bindingId: string
  hostViewId: string
  screenId?: string
  props: Record<string, string | number | boolean>
}

export type InboxSlotMount = WorkspaceSlotMountBase & {
  kind: 'inbox'
  /** Widget-Props, die aus skalaren Composition-Props abgeleitet werden. */
  widget: {
    compact: boolean
    confidenceMin: number
  }
}

export type DispositionBoardSlotMount = WorkspaceSlotMountBase & {
  kind: 'disposition_board'
  /**
   * Route der bestehenden Dispositionsseite. Der Host mountet darueber die
   * registrierte Tafel (SpecializedComponentHost), keinen Link.
   */
  href: typeof DISPOSITION_BOARD_ROUTE
}

export type WorkspaceSlotMount = InboxSlotMount | DispositionBoardSlotMount

export type WorkspaceCompositionMountPlan = {
  compositionId: string
  title: string
  studioVersion: string
  defaultViewId?: string
  slots: WorkspaceSlotMount[]
}

function scalarProps(
  props: WorkspaceSpecializedComponentRef['props'],
): Record<string, string | number | boolean> {
  return { ...(props ?? {}) }
}

function inboxWidgetFromProps(
  props: Record<string, string | number | boolean>,
): InboxSlotMount['widget'] {
  const compact = props.compact === true || props.density === 'compact'
  const confidenceRaw = props.confidenceMin
  const confidenceMin =
    typeof confidenceRaw === 'number' && Number.isFinite(confidenceRaw)
      ? confidenceRaw
      : 0
  return { compact, confidenceMin }
}

/**
 * Leitet aus einer gueltigen Composition den Mount-Plan ab.
 * Reihenfolge: normalizeWorkspaceComposition (order → id).
 */
export function resolveWorkspaceCompositionMounts(
  composition: WorkspaceComposition,
): WorkspaceCompositionMountPlan {
  const normalized = normalizeWorkspaceComposition(composition)
  const slots: WorkspaceSlotMount[] = []

  for (const slot of normalized.specializedComponents) {
    const props = scalarProps(slot.props)
    const base = {
      id: slot.id,
      label: slot.label,
      bindingId: slot.bindingId,
      hostViewId: slot.hostViewId,
      screenId: slot.screenId,
      props,
    }

    if (slot.kind === 'inbox') {
      slots.push({
        ...base,
        kind: 'inbox',
        widget: inboxWidgetFromProps(props),
      })
      continue
    }

    if (slot.kind === 'disposition_board') {
      slots.push({
        ...base,
        kind: 'disposition_board',
        href: DISPOSITION_BOARD_ROUTE,
      })
    }
  }

  return {
    compositionId: normalized.id,
    title: normalized.title,
    studioVersion: normalized.studioVersion,
    defaultViewId: normalized.defaultViewId,
    slots,
  }
}

export function listMountedKinds(
  plan: WorkspaceCompositionMountPlan,
): SpecializedComponentKind[] {
  return plan.slots.map((slot) => slot.kind)
}
