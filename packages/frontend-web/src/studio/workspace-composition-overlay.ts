/**
 * Persönliche Composition-Anpassung jenseits Studio-Authoring.
 * Overlay lokal (wie Launchpad): Pin von Views + fixierte Start-View.
 * Katalog/Composition bleibt Source of Truth; Overlay ändert nur Laufzeit-Reihenfolge.
 */

import {
  normalizeWorkspaceComposition,
  type WorkspaceComposition,
  type WorkspacePersonalizationKeys,
  type WorkspaceSpecializedComponentRef,
  type WorkspaceViewRef,
} from './workspace-composition'

export const COMPOSITION_OVERLAY_SYNC_EVENT = 'valeo:composition-overlay-changed'

export type CompositionPersonalizationOverlay = {
  version: 1
  pinnedViewIds: string[]
  fixedStartViewId: string | null
}

export const EMPTY_COMPOSITION_OVERLAY: CompositionPersonalizationOverlay = {
  version: 1,
  pinnedViewIds: [],
  fixedStartViewId: null,
}

function scopePart(value?: string | null): string {
  return typeof value === 'string' ? value.trim() : ''
}

/**
 * Ohne sub der Namespace aus der Composition. Mit sub `.<sub>`.
 * Mit Mandant und sub `.<tenant>.<sub>`.
 */
export function compositionOverlayStorageKey(
  pinStorageKey: string,
  sub?: string | null,
  tenantId?: string | null,
): string {
  const base = pinStorageKey.trim() || 'valeo.workspace.composition.overlay'
  const id = scopePart(sub)
  if (!id) return base
  const tenant = scopePart(tenantId)
  if (!tenant) return `${base}.${id}`
  return `${base}.${tenant}.${id}`
}

function compositionOverlayReadKeys(
  pinStorageKey: string,
  sub?: string | null,
  tenantId?: string | null,
): string[] {
  const active = compositionOverlayStorageKey(pinStorageKey, sub, tenantId)
  const keys = [active]
  const userKey = compositionOverlayStorageKey(pinStorageKey, sub)
  if (userKey !== active) keys.push(userKey)
  const globalKey = compositionOverlayStorageKey(pinStorageKey)
  if (globalKey !== keys[keys.length - 1]) keys.push(globalKey)
  return keys
}

/** Liest den aktivsten Key; Fallback auf allgemeinere Keys. Schreiben nur aktiv. */
export function readCompositionOverlayRaw(
  storage: Pick<Storage, 'getItem'>,
  pinStorageKey: string,
  sub?: string | null,
  tenantId?: string | null,
): string | null {
  const keys = compositionOverlayReadKeys(pinStorageKey, sub, tenantId)
  let emptyActive: string | null = null
  for (let index = 0; index < keys.length; index += 1) {
    const value = storage.getItem(keys[index] ?? '')
    if (value != null && value.trim() !== '') return value
    if (index === 0) emptyActive = value
  }
  return emptyActive
}

export function writeCompositionOverlayRaw(
  storage: Pick<Storage, 'setItem'>,
  raw: string,
  pinStorageKey: string,
  sub?: string | null,
  tenantId?: string | null,
): void {
  storage.setItem(compositionOverlayStorageKey(pinStorageKey, sub, tenantId), raw)
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  const out: string[] = []
  for (const entry of value) {
    if (typeof entry === 'string' && entry.trim() !== '' && !out.includes(entry)) {
      out.push(entry)
    }
  }
  return out
}

/**
 * Liest Overlay-Felder unter den in der Composition deklarierten Key-Namen
 * (pinnedViewsKey / fixedStartViewKey) sowie den kanonischen Alias-Namen.
 */
export function parseCompositionOverlay(
  raw: unknown,
  keys: WorkspacePersonalizationKeys,
): CompositionPersonalizationOverlay {
  if (!raw || typeof raw !== 'object') {
    return { ...EMPTY_COMPOSITION_OVERLAY }
  }
  const value = raw as Record<string, unknown>
  const fromDeclared = stringList(value[keys.pinnedViewsKey])
  const pinnedViewIds = fromDeclared.length > 0 ? fromDeclared : stringList(value.pinnedViewIds)
  const fixedRaw = value[keys.fixedStartViewKey] ?? value.fixedStartViewId
  const fixedStartViewId =
    typeof fixedRaw === 'string' && fixedRaw.trim() !== '' ? fixedRaw.trim() : null
  return {
    version: 1,
    pinnedViewIds,
    fixedStartViewId,
  }
}

export function serializeCompositionOverlay(
  overlay: CompositionPersonalizationOverlay,
  keys: WorkspacePersonalizationKeys,
): string {
  return JSON.stringify({
    version: 1,
    [keys.pinnedViewsKey]: overlay.pinnedViewIds,
    [keys.fixedStartViewKey]: overlay.fixedStartViewId,
  })
}

export function pinCompositionView(
  overlay: CompositionPersonalizationOverlay,
  viewId: string,
): CompositionPersonalizationOverlay {
  if (!viewId || overlay.pinnedViewIds.includes(viewId)) {
    return overlay
  }
  return { ...overlay, pinnedViewIds: [...overlay.pinnedViewIds, viewId] }
}

export function unpinCompositionView(
  overlay: CompositionPersonalizationOverlay,
  viewId: string,
): CompositionPersonalizationOverlay {
  if (!overlay.pinnedViewIds.includes(viewId)) {
    return overlay
  }
  return {
    ...overlay,
    pinnedViewIds: overlay.pinnedViewIds.filter((id) => id !== viewId),
    fixedStartViewId: overlay.fixedStartViewId === viewId ? null : overlay.fixedStartViewId,
  }
}

export function setFixedStartView(
  overlay: CompositionPersonalizationOverlay,
  viewId: string | null,
): CompositionPersonalizationOverlay {
  if (viewId == null || viewId.trim() === '') {
    if (overlay.fixedStartViewId == null) return overlay
    return { ...overlay, fixedStartViewId: null }
  }
  const id = viewId.trim()
  if (overlay.fixedStartViewId === id) {
    return overlay
  }
  const pinned = overlay.pinnedViewIds.includes(id)
    ? overlay.pinnedViewIds
    : [...overlay.pinnedViewIds, id]
  return { ...overlay, pinnedViewIds: pinned, fixedStartViewId: id }
}

function reorderViews(
  views: WorkspaceViewRef[],
  overlay: CompositionPersonalizationOverlay,
): WorkspaceViewRef[] {
  const byId = new Map(views.map((view) => [view.id, view]))
  const knownPinned = overlay.pinnedViewIds.filter((id) => byId.has(id))
  const fixed =
    overlay.fixedStartViewId && byId.has(overlay.fixedStartViewId)
      ? overlay.fixedStartViewId
      : null

  const head: string[] = []
  if (fixed) head.push(fixed)
  for (const id of knownPinned) {
    if (!head.includes(id)) head.push(id)
  }

  const used = new Set(head)
  const rest = views.map((view) => view.id).filter((id) => !used.has(id))
  const orderedIds = [...head, ...rest]

  return orderedIds.map((id, index) => {
    const view = byId.get(id)
    if (view === undefined) throw new Error(`Workspace view missing: ${id}`)
    return { ...view, order: (index + 1) * 10 }
  })
}

function reorderSpecialists(
  slots: WorkspaceSpecializedComponentRef[],
  views: WorkspaceViewRef[],
): WorkspaceSpecializedComponentRef[] {
  const viewRank = new Map(views.map((view, index) => [view.id, index]))
  return slots
    .slice()
    .sort((a, b) => {
      const ar = viewRank.get(a.hostViewId) ?? Number.MAX_SAFE_INTEGER
      const br = viewRank.get(b.hostViewId) ?? Number.MAX_SAFE_INTEGER
      if (ar !== br) return ar - br
      const ao = a.order ?? Number.MAX_SAFE_INTEGER
      const bo = b.order ?? Number.MAX_SAFE_INTEGER
      if (ao !== bo) return ao - bo
      return a.id.localeCompare(b.id)
    })
    .map((slot, index) => ({ ...slot, order: (index + 1) * 10 }))
}

/**
 * Wendet persönliches Overlay auf eine Composition an (Laufzeit).
 * Unbekannte View-IDs werden ignoriert. Studio-Session bleibt unverändert.
 * Fachaktions-Priorisierung (Reason-Codes/Pin) bleibt unberührt.
 */
export function applyCompositionPersonalization(
  composition: WorkspaceComposition,
  overlay: CompositionPersonalizationOverlay,
): WorkspaceComposition {
  const normalized = normalizeWorkspaceComposition(composition)
  if (overlay.pinnedViewIds.length === 0 && overlay.fixedStartViewId == null) {
    return normalized
  }

  const views = reorderViews(normalized.views, overlay)
  const specializedComponents = reorderSpecialists(normalized.specializedComponents, views)
  const fixed =
    overlay.fixedStartViewId && views.some((view) => view.id === overlay.fixedStartViewId)
      ? overlay.fixedStartViewId
      : normalized.defaultViewId

  return {
    ...normalized,
    views,
    specializedComponents,
    defaultViewId: fixed,
  }
}
