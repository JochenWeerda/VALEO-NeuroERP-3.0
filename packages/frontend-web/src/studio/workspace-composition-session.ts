/**
 * Compose-Persistenz fuer WorkspaceComposition — lokal, kein Server-Write.
 * Nutzt Parser/Validator; ungültige Entwürfe werden nicht still gemountet.
 * Fixiert in localStorage (überlebt Tab-Close); API-Namen bleiben session-*.
 */

import { WORKSPACE_COMPOSITION_FIXTURE } from './workspace-composition.fixture'
import { parseWorkspaceComposition } from './workspace-composition-parser'
import {
  normalizeWorkspaceComposition,
  type SpecializedComponentKind,
  type WorkspaceComposition,
  type WorkspaceCompositionIssue,
  type WorkspaceFachaktionRef,
  type WorkspaceSpecializedComponentRef,
  type WorkspaceViewRef,
} from './workspace-composition'

/** localStorage-Schluessel ohne Nutzer-ID. Mit sub hängt workspaceCompositionStorageKey die ID an. */
export const WORKSPACE_COMPOSITION_STORAGE_KEY = 'valeo.workspace.composition' as const

function scopePart(value?: string | null): string {
  return typeof value === 'string' ? value.trim() : ''
}

/**
 * Ohne sub der globale Key. Mit sub `valeo.workspace.composition.<sub>`.
 * Mit Mandant und sub `valeo.workspace.composition.<tenant>.<sub>`.
 */
export function workspaceCompositionStorageKey(sub?: string | null, tenantId?: string | null): string {
  const id = scopePart(sub)
  if (!id) return WORKSPACE_COMPOSITION_STORAGE_KEY
  const tenant = scopePart(tenantId)
  if (!tenant) return `${WORKSPACE_COMPOSITION_STORAGE_KEY}.${id}`
  return `${WORKSPACE_COMPOSITION_STORAGE_KEY}.${tenant}.${id}`
}

/** Aktivster Key zuerst, danach je der nächst allgemeinere. */
function workspaceCompositionReadKeys(sub?: string | null, tenantId?: string | null): string[] {
  const active = workspaceCompositionStorageKey(sub, tenantId)
  const keys = [active]
  const userKey = workspaceCompositionStorageKey(sub)
  if (userKey !== active) keys.push(userKey)
  if (WORKSPACE_COMPOSITION_STORAGE_KEY !== keys[keys.length - 1]) {
    keys.push(WORKSPACE_COMPOSITION_STORAGE_KEY)
  }
  return keys
}

export type WorkspaceCompositionResolveResult =
  | { ok: true; composition: WorkspaceComposition; issues: [] }
  | { ok: false; composition: null; issues: WorkspaceCompositionIssue[] }

export type WorkspaceCompositionSessionRead =
  | { status: 'empty' }
  | { status: 'ok'; composition: WorkspaceComposition }
  | { status: 'invalid'; issues: WorkspaceCompositionIssue[]; raw: unknown }

function cloneComposition(composition: WorkspaceComposition): WorkspaceComposition {
  return structuredClone(composition)
}

/** Parser + Validator — einzige Freigabe vor Host-Mount. */
export function resolveComposableWorkspace(raw: unknown): WorkspaceCompositionResolveResult {
  const parsed = parseWorkspaceComposition(raw)
  if (!parsed.ok) {
    return { ok: false, composition: null, issues: parsed.issues }
  }
  return { ok: true, composition: parsed.composition, issues: [] }
}

function readCompositionText(
  storage: Pick<Storage, 'getItem'>,
  sub?: string | null,
  tenantId?: string | null,
): string | null {
  const keys = workspaceCompositionReadKeys(sub, tenantId)
  let emptyActive: string | null = null
  for (let index = 0; index < keys.length; index += 1) {
    const value = storage.getItem(keys[index] ?? '')
    if (value != null && value.trim() !== '') return value
    if (index === 0) emptyActive = value
  }
  return emptyActive
}

function readCompositionFromStorage(
  storage: Pick<Storage, 'getItem'>,
  sub?: string | null,
  tenantId?: string | null,
): WorkspaceCompositionSessionRead {
  const rawText = readCompositionText(storage, sub, tenantId)
  if (rawText == null || rawText.trim() === '') {
    return { status: 'empty' }
  }
  let raw: unknown
  try {
    raw = JSON.parse(rawText) as unknown
  } catch {
    return {
      status: 'invalid',
      issues: [{ path: '', code: 'session_json', message: 'gespeicherte Composition enthält kein gültiges JSON' }],
      raw: rawText,
    }
  }
  const resolved = resolveComposableWorkspace(raw)
  if (!resolved.ok) {
    return { status: 'invalid', issues: resolved.issues, raw }
  }
  return { status: 'ok', composition: resolved.composition }
}

/**
 * Liest die fixierte Composition. Default: localStorage.
 * Wenn Aufrufer (z. B. Home) noch sessionStorage uebergibt und der Key dort leer ist,
 * wird localStorage nachgezogen — ohne Home-Edit, ohne Funktionsumbenennung.
 */
export function readWorkspaceCompositionSession(
  storage: Pick<Storage, 'getItem'> = localStorage,
  sub?: string | null,
  tenantId?: string | null,
): WorkspaceCompositionSessionRead {
  const primary = readCompositionFromStorage(storage, sub, tenantId)
  if (primary.status !== 'empty') {
    return primary
  }
  if (
    typeof localStorage !== 'undefined'
    && typeof sessionStorage !== 'undefined'
    && storage === sessionStorage
  ) {
    return readCompositionFromStorage(localStorage, sub, tenantId)
  }
  return primary
}

/**
 * Speichert nur gültige Compositions. Ungültige Rohdaten werden abgelehnt
 * (kein stilles Überschreiben des letzten gültigen Stands).
 */
export function saveWorkspaceCompositionSession(
  composition: WorkspaceComposition,
  storage: Pick<Storage, 'setItem'> = localStorage,
  sub?: string | null,
  tenantId?: string | null,
): WorkspaceCompositionResolveResult {
  const resolved = resolveComposableWorkspace(composition)
  if (!resolved.ok) {
    return resolved
  }
  storage.setItem(workspaceCompositionStorageKey(sub, tenantId), JSON.stringify(resolved.composition))
  return resolved
}

/** Startzustand: gespeicherte Composition wenn gültig, sonst Fixture. */
export function initialWorkspaceCompositionDraft(
  storage: Pick<Storage, 'getItem'> = localStorage,
  fallback: WorkspaceComposition = WORKSPACE_COMPOSITION_FIXTURE,
  sub?: string | null,
  tenantId?: string | null,
): {
  draft: WorkspaceComposition
  mounted: WorkspaceComposition | null
  issues: WorkspaceCompositionIssue[]
  source: 'session' | 'fallback' | 'session-invalid'
} {
  const read = readWorkspaceCompositionSession(storage, sub, tenantId)
  if (read.status === 'ok') {
    return {
      draft: cloneComposition(read.composition),
      mounted: read.composition,
      issues: [],
      source: 'session',
    }
  }
  if (read.status === 'invalid') {
    return {
      draft: cloneComposition(fallback),
      mounted: null,
      issues: read.issues,
      source: 'session-invalid',
    }
  }
  const resolved = resolveComposableWorkspace(fallback)
  return {
    draft: cloneComposition(fallback),
    mounted: resolved.ok ? resolved.composition : null,
    issues: resolved.ok ? [] : resolved.issues,
    source: 'fallback',
  }
}

function catalogSlotsByKind(
  catalog: WorkspaceComposition,
  kind: SpecializedComponentKind,
): WorkspaceSpecializedComponentRef[] {
  return catalog.specializedComponents.filter((slot) => slot.kind === kind)
}

function catalogFachaktionenForSlots(
  catalog: WorkspaceComposition,
  slotIds: Set<string>,
): WorkspaceFachaktionRef[] {
  return catalog.fachaktionRefs.filter(
    (action) =>
      action.scope === 'specialized'
      && action.specializedComponentId
      && slotIds.has(action.specializedComponentId),
  )
}

export function isSpecializedKindEnabled(
  composition: WorkspaceComposition,
  kind: SpecializedComponentKind,
): boolean {
  return composition.specializedComponents.some((slot) => slot.kind === kind)
}

/**
 * Slot-Art an- oder abwählen. Katalog (Default: Fixture) liefert fehlende Slots
 * und zugehörige specialized-Fachaktionen zurück.
 */
export function setSpecializedKindEnabled(
  composition: WorkspaceComposition,
  kind: SpecializedComponentKind,
  enabled: boolean,
  catalog: WorkspaceComposition = WORKSPACE_COMPOSITION_FIXTURE,
): WorkspaceComposition {
  const next = cloneComposition(composition)

  if (!enabled) {
    const removedIds = new Set(
      next.specializedComponents.filter((slot) => slot.kind === kind).map((slot) => slot.id),
    )
    next.specializedComponents = next.specializedComponents.filter((slot) => slot.kind !== kind)
    next.fachaktionRefs = next.fachaktionRefs.filter(
      (action) =>
        !(
          action.scope === 'specialized'
          && action.specializedComponentId
          && removedIds.has(action.specializedComponentId)
        ),
    )
    return normalizeWorkspaceComposition(next)
  }

  const existingKinds = new Set(next.specializedComponents.map((slot) => slot.kind))
  if (existingKinds.has(kind)) {
    return normalizeWorkspaceComposition(next)
  }

  const toAdd = catalogSlotsByKind(catalog, kind)
  const existingIds = new Set(next.specializedComponents.map((slot) => slot.id))
  for (const slot of toAdd) {
    if (!existingIds.has(slot.id)) {
      next.specializedComponents.push({
        ...slot,
        props: slot.props ? { ...slot.props } : undefined,
      })
    }
  }
  const addedIds = new Set(toAdd.map((slot) => slot.id))
  const existingActionIds = new Set(next.fachaktionRefs.map((action) => action.id))
  for (const action of catalogFachaktionenForSlots(catalog, addedIds)) {
    if (!existingActionIds.has(action.id)) {
      next.fachaktionRefs.push({ ...action })
    }
  }
  return normalizeWorkspaceComposition(next)
}

/**
 * View um eine Position nach oben/unten verschieben und order neu vergeben.
 */
export function moveWorkspaceView(
  composition: WorkspaceComposition,
  viewId: string,
  direction: 'up' | 'down',
): WorkspaceComposition {
  const next = cloneComposition(composition)
  const views = normalizeWorkspaceComposition(next).views.slice()
  const index = views.findIndex((view) => view.id === viewId)
  if (index < 0) return normalizeWorkspaceComposition(next)

  const swapWith = direction === 'up' ? index - 1 : index + 1
  if (swapWith < 0 || swapWith >= views.length) {
    return normalizeWorkspaceComposition(next)
  }

  const reordered: WorkspaceViewRef[] = views.slice()
  const tmp = reordered[index]
  reordered[index] = reordered[swapWith]
  reordered[swapWith] = tmp
  next.views = reordered.map((view, orderIndex) => ({
    ...view,
    order: (orderIndex + 1) * 10,
  }))
  return normalizeWorkspaceComposition(next)
}

export function clearWorkspaceCompositionSession(
  storage: Pick<Storage, 'removeItem'> = localStorage,
  sub?: string | null,
  tenantId?: string | null,
): void {
  storage.removeItem(workspaceCompositionStorageKey(sub, tenantId))
}
