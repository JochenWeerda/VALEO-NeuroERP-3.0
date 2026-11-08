/**
 * Reine Authoring-Mutationen fuer WorkspaceComposition.
 * Persistenz bleibt bei workspace-composition-session (localStorage/Fixture).
 * Kein Server-Write, keine zweite Frontend-Welt.
 */

import {
  normalizeWorkspaceComposition,
  type SpecializedComponentKind,
  type WorkspaceComposition,
  type WorkspaceModuleRef,
  type WorkspaceViewRef,
} from './workspace-composition'

function cloneComposition(composition: WorkspaceComposition): WorkspaceComposition {
  return structuredClone(composition)
}

/** Freigegebene ScreenDefinition — Authoring-Schritt nach Studio-Freigabe. */
export type ReleasedScreenRef = {
  screenId: string
  label: string
  routePath?: string
  /** Bestehendes oder neues Modul; Default studio-released. */
  moduleId?: string
  moduleLabel?: string
  domain?: string
  /** Wenn true: defaultViewId auf die View setzen. */
  asDefault?: boolean
}

export type WorkspaceCompositionMetaPatch = {
  title?: string
  description?: string | null
  defaultViewId?: string | null
}

function slugFromScreenId(screenId: string): string {
  const raw = screenId.trim().toLowerCase().replace(/[^a-z0-9./-]+/g, '-')
  const cleaned = raw.replace(/^-+|-+$/g, '').replace(/\/+/g, '-')
  return cleaned.length > 0 ? `view-${cleaned}` : 'view-released'
}

function ensureModule(
  modules: WorkspaceModuleRef[],
  moduleId: string,
  label: string,
  domain?: string,
): WorkspaceModuleRef[] {
  if (modules.some((mod) => mod.id === moduleId)) {
    return modules
  }
  const maxOrder = modules.reduce(
    (acc, mod) => Math.max(acc, mod.order ?? 0),
    0,
  )
  return [
    ...modules,
    {
      id: moduleId,
      label,
      domain,
      order: maxOrder + 10,
    },
  ]
}

/**
 * Titel/Beschreibung/Default-View patchen — nur skalare Metadaten.
 */
export function patchWorkspaceCompositionMeta(
  composition: WorkspaceComposition,
  patch: WorkspaceCompositionMetaPatch,
): WorkspaceComposition {
  const next = cloneComposition(composition)
  if (patch.title !== undefined) {
    next.title = patch.title
  }
  if (patch.description !== undefined) {
    if (patch.description === null || patch.description.trim() === '') {
      delete next.description
    } else {
      next.description = patch.description
    }
  }
  if (patch.defaultViewId !== undefined) {
    if (patch.defaultViewId === null || patch.defaultViewId.trim() === '') {
      delete next.defaultViewId
    } else {
      next.defaultViewId = patch.defaultViewId
    }
  }
  return normalizeWorkspaceComposition(next)
}

/**
 * Host-View fuer alle Slots einer Art setzen (Inbox / Dispo).
 * Unbekannte hostViewId bleibt stehen — Validator meldet spaeter.
 */
export function setSpecializedHostView(
  composition: WorkspaceComposition,
  kind: SpecializedComponentKind,
  hostViewId: string,
): WorkspaceComposition {
  const next = cloneComposition(composition)
  next.specializedComponents = next.specializedComponents.map((slot) =>
    slot.kind === kind ? { ...slot, hostViewId } : slot,
  )
  return normalizeWorkspaceComposition(next)
}

/**
 * Freigegebene ScreenDefinition als View in die Composition aufnehmen
 * (Authoring-Schritt nach Freigabe — kein Parallel-Frontend).
 */
export function upsertReleasedScreenView(
  composition: WorkspaceComposition,
  released: ReleasedScreenRef,
): WorkspaceComposition {
  const screenId = released.screenId.trim()
  const label = released.label.trim()
  if (!screenId || !label) {
    return normalizeWorkspaceComposition(cloneComposition(composition))
  }

  const moduleId = (released.moduleId?.trim() || 'studio-released')
  const moduleLabel = released.moduleLabel?.trim() || 'Studio-Freigabe'
  const next = cloneComposition(composition)
  next.modules = ensureModule(next.modules, moduleId, moduleLabel, released.domain)

  const existingIndex = next.views.findIndex((view) => view.screenId === screenId)
  if (existingIndex >= 0) {
    const current = next.views[existingIndex]
    if (current === undefined) throw new Error("Existing workspace view disappeared")
    next.views[existingIndex] = {
      ...current,
      label,
      moduleId,
      routePath: released.routePath ?? current.routePath,
    }
    if (released.asDefault) {
      next.defaultViewId = current.id
    }
    return normalizeWorkspaceComposition(next)
  }

  const maxOrder = next.views.reduce((acc, view) => Math.max(acc, view.order ?? 0), 0)
  let viewId = slugFromScreenId(screenId)
  const used = new Set(next.views.map((view) => view.id))
  if (used.has(viewId)) {
    let suffix = 2
    while (used.has(`${viewId}-${suffix}`)) suffix += 1
    viewId = `${viewId}-${suffix}`
  }

  const view: WorkspaceViewRef = {
    id: viewId,
    moduleId,
    label,
    screenId,
    routePath: released.routePath,
    order: maxOrder + 10,
  }
  next.views.push(view)
  if (released.asDefault) {
    next.defaultViewId = viewId
  }
  return normalizeWorkspaceComposition(next)
}
