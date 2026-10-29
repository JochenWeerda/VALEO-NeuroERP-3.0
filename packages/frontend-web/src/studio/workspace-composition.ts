/**
 * WorkspaceComposition — Studio-Metadatenvertrag (Adaptive Workspace Phase 2).
 *
 * Arbeitsräume und Spezialkomponenten (Document-Inbox, Dispo-Tafel) werden
 * deklarativ eingebunden. Die Meridian-Pipeline bleibt unverändert:
 * ScreenDefinition → RenderPlan → useUniversalMaskRuntime → UniversalMaskRenderer.
 *
 * Dieser Vertrag ersetzt weder ScreenDefinition noch Launchpad-Katalog;
 * er komponiert freigegebene Module/Views und referenziert Spezial-Hosts
 * sowie typisierte Fachaktionen nur per ID.
 */

export const WORKSPACE_COMPOSITION_SCHEMA_VERSION = 1 as const

/** SemVer der Composition selbst (Studio-Versionierung, nicht npm). */
export const STUDIO_VERSION_PATTERN = /^[1-9][0-9]*\.[0-9]+\.[0-9]+$/

/** Stabiler ID-Schluessel: kebab-case, Punkte fuer Screen-IDs erlaubt. */
export const WORKSPACE_ID_PATTERN = /^[a-z][a-z0-9_./-]*$/

export type SpecializedComponentKind = 'inbox' | 'disposition_board'

export const SPECIALIZED_COMPONENT_KINDS: readonly SpecializedComponentKind[] = [
  'inbox',
  'disposition_board',
] as const

export type FachaktionScope = 'workspace' | 'view' | 'specialized'

export interface WorkspaceModuleRef {
  id: string
  label: string
  /** Optionale Domain-Kennung (crm, logistics, …) — informativ, kein Recht. */
  domain?: string
  order?: number
}

export interface WorkspaceViewRef {
  id: string
  moduleId: string
  label: string
  /**
   * ScreenDefinition.id — Einstieg in die Meridian-Pipeline.
   * Cockpit-/Overview-Hosts nutzen floorplan=cockpit (CockpitOverviewParent).
   */
  screenId: string
  /** Optionale Route; Runtime darf weiterhin ueber Omnibox-Bruecke aufloesen. */
  routePath?: string
  order?: number
}

/**
 * Spezialkomponente als Metadaten-Slot — Implementierung bleibt bei
 * Geschwister-Agenten (Inbox / Disposition). Hier nur kind + Binding-IDs.
 */
export interface WorkspaceSpecializedComponentRef {
  id: string
  kind: SpecializedComponentKind
  label: string
  order?: number
  /** View, in die der Slot eingehaengt wird. */
  hostViewId: string
  /**
   * Fachliche Binding-ID (z. B. Inbox-Queue oder Dispo-Board-Profil).
   * Besitz und Runtime liegen ausserhalb dieses Vertrags.
   */
  bindingId: string
  /** Optionaler ScreenDefinition-Wrapper um den Slot. */
  screenId?: string
  /** Nur skalare, versionierbare Props — keine Funktionen/Closures. */
  props?: Record<string, string | number | boolean>
}

/**
 * Verweis auf eine typisierte Fachaktion (Capability / ScreenDefinition-Action).
 * Keine freien API-/DB-Calls — Mapping erfolgt in Phase-1-Registry / Command Center.
 */
export interface WorkspaceFachaktionRef {
  id: string
  actionKey: string
  label: string
  scope: FachaktionScope
  viewId?: string
  specializedComponentId?: string
  permission?: string
}

/**
 * Pin-/Personalisierungsschluessel — Overlay bleibt lokal (Launchpad-Vertrag),
 * Composition deklariert nur die stabilen Key-Namen.
 */
export interface WorkspacePersonalizationKeys {
  /** localStorage-/Overlay-Namespace, z. B. valeo.workspace.composition.overlay */
  pinStorageKey: string
  /** Feldname fuer angepinnte View-IDs im Overlay. */
  pinnedViewsKey: string
  /** Feldname fuer fixierte Start-View. */
  fixedStartViewKey: string
}

export interface WorkspaceComposition {
  schemaVersion: typeof WORKSPACE_COMPOSITION_SCHEMA_VERSION
  id: string
  /** Studio-versionierbare SemVer der Composition. */
  studioVersion: string
  title: string
  description?: string
  modules: WorkspaceModuleRef[]
  views: WorkspaceViewRef[]
  specializedComponents: WorkspaceSpecializedComponentRef[]
  fachaktionRefs: WorkspaceFachaktionRef[]
  personalization: WorkspacePersonalizationKeys
  defaultViewId?: string
}

export type WorkspaceCompositionIssue =
  | { path: string; code: string; message: string }

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

function pushUnique(
  issues: WorkspaceCompositionIssue[],
  path: string,
  code: string,
  message: string,
): void {
  issues.push({ path, code, message })
}

/**
 * Validiert eine WorkspaceComposition deterministisch.
 * Liefert eine stabile, nach path sortierte Issueliste (leer = gueltig).
 */
export function validateWorkspaceComposition(
  composition: WorkspaceComposition,
): WorkspaceCompositionIssue[] {
  const issues: WorkspaceCompositionIssue[] = []

  if (composition.schemaVersion !== WORKSPACE_COMPOSITION_SCHEMA_VERSION) {
    pushUnique(
      issues,
      'schemaVersion',
      'schema_version',
      `schemaVersion must be ${String(WORKSPACE_COMPOSITION_SCHEMA_VERSION)}`,
    )
  }
  if (!isNonEmptyString(composition.id) || !WORKSPACE_ID_PATTERN.test(composition.id)) {
    pushUnique(issues, 'id', 'id_invalid', 'id must match kebab-case workspace id pattern')
  }
  if (!isNonEmptyString(composition.studioVersion) || !STUDIO_VERSION_PATTERN.test(composition.studioVersion)) {
    pushUnique(issues, 'studioVersion', 'studio_version', 'studioVersion must be SemVer (e.g. 1.0.0)')
  }
  if (!isNonEmptyString(composition.title)) {
    pushUnique(issues, 'title', 'title_required', 'title is required')
  }

  const personalization = composition.personalization
  if (!personalization || typeof personalization !== 'object') {
    pushUnique(issues, 'personalization', 'personalization_required', 'personalization is required')
  } else {
    for (const key of ['pinStorageKey', 'pinnedViewsKey', 'fixedStartViewKey'] as const) {
      if (!isNonEmptyString(personalization[key])) {
        pushUnique(issues, `personalization.${key}`, 'personalization_key', `${key} is required`)
      }
    }
    if (
      isNonEmptyString(personalization.pinStorageKey)
      && !personalization.pinStorageKey.startsWith('valeo.')
    ) {
      pushUnique(
        issues,
        'personalization.pinStorageKey',
        'personalization_prefix',
        'pinStorageKey must start with valeo.',
      )
    }
  }

  const moduleIds = new Set<string>()
  for (const [index, mod] of (composition.modules ?? []).entries()) {
    const base = `modules[${index}]`
    if (!isNonEmptyString(mod.id) || !WORKSPACE_ID_PATTERN.test(mod.id)) {
      pushUnique(issues, `${base}.id`, 'module_id', 'module id is invalid')
      continue
    }
    if (moduleIds.has(mod.id)) {
      pushUnique(issues, `${base}.id`, 'module_duplicate', `duplicate module id: ${mod.id}`)
    }
    moduleIds.add(mod.id)
    if (!isNonEmptyString(mod.label)) {
      pushUnique(issues, `${base}.label`, 'module_label', `module ${mod.id} requires label`)
    }
  }

  const viewIds = new Set<string>()
  for (const [index, view] of (composition.views ?? []).entries()) {
    const base = `views[${index}]`
    if (!isNonEmptyString(view.id) || !WORKSPACE_ID_PATTERN.test(view.id)) {
      pushUnique(issues, `${base}.id`, 'view_id', 'view id is invalid')
      continue
    }
    if (viewIds.has(view.id)) {
      pushUnique(issues, `${base}.id`, 'view_duplicate', `duplicate view id: ${view.id}`)
    }
    viewIds.add(view.id)
    if (!isNonEmptyString(view.label)) {
      pushUnique(issues, `${base}.label`, 'view_label', `view ${view.id} requires label`)
    }
    if (!isNonEmptyString(view.screenId)) {
      pushUnique(issues, `${base}.screenId`, 'view_screen', `view ${view.id} requires screenId`)
    }
    if (!isNonEmptyString(view.moduleId) || !moduleIds.has(view.moduleId)) {
      pushUnique(
        issues,
        `${base}.moduleId`,
        'view_module',
        `view ${view.id} references unknown moduleId: ${view.moduleId ?? ''}`,
      )
    }
  }

  const specializedIds = new Set<string>()
  for (const [index, slot] of (composition.specializedComponents ?? []).entries()) {
    const base = `specializedComponents[${index}]`
    if (!isNonEmptyString(slot.id) || !WORKSPACE_ID_PATTERN.test(slot.id)) {
      pushUnique(issues, `${base}.id`, 'specialized_id', 'specializedComponent id is invalid')
      continue
    }
    if (specializedIds.has(slot.id)) {
      pushUnique(issues, `${base}.id`, 'specialized_duplicate', `duplicate specializedComponent id: ${slot.id}`)
    }
    specializedIds.add(slot.id)
    if (!isNonEmptyString(slot.label)) {
      pushUnique(issues, `${base}.label`, 'specialized_label', `specializedComponent ${slot.id} requires label`)
    }
    if (!SPECIALIZED_COMPONENT_KINDS.includes(slot.kind)) {
      pushUnique(
        issues,
        `${base}.kind`,
        'specialized_kind',
        `specializedComponent ${slot.id} has invalid kind: ${String(slot.kind)}`,
      )
    }
    if (!isNonEmptyString(slot.bindingId)) {
      pushUnique(issues, `${base}.bindingId`, 'specialized_binding', `specializedComponent ${slot.id} requires bindingId`)
    }
    if (!isNonEmptyString(slot.hostViewId) || !viewIds.has(slot.hostViewId)) {
      pushUnique(
        issues,
        `${base}.hostViewId`,
        'specialized_host',
        `specializedComponent ${slot.id} references unknown hostViewId: ${slot.hostViewId ?? ''}`,
      )
    }
    if (slot.props) {
      for (const [propKey, propValue] of Object.entries(slot.props)) {
        const t = typeof propValue
        if (t !== 'string' && t !== 'number' && t !== 'boolean') {
          pushUnique(
            issues,
            `${base}.props.${propKey}`,
            'specialized_props',
            `props.${propKey} must be string | number | boolean`,
          )
        }
      }
    }
  }

  const fachaktionIds = new Set<string>()
  for (const [index, action] of (composition.fachaktionRefs ?? []).entries()) {
    const base = `fachaktionRefs[${index}]`
    if (!isNonEmptyString(action.id) || !WORKSPACE_ID_PATTERN.test(action.id)) {
      pushUnique(issues, `${base}.id`, 'fachaktion_id', 'fachaktionRef id is invalid')
      continue
    }
    if (fachaktionIds.has(action.id)) {
      pushUnique(issues, `${base}.id`, 'fachaktion_duplicate', `duplicate fachaktionRef id: ${action.id}`)
    }
    fachaktionIds.add(action.id)
    if (!isNonEmptyString(action.actionKey)) {
      pushUnique(issues, `${base}.actionKey`, 'fachaktion_key', `fachaktionRef ${action.id} requires actionKey`)
    }
    if (!isNonEmptyString(action.label)) {
      pushUnique(issues, `${base}.label`, 'fachaktion_label', `fachaktionRef ${action.id} requires label`)
    }
    if (!['workspace', 'view', 'specialized'].includes(action.scope)) {
      pushUnique(
        issues,
        `${base}.scope`,
        'fachaktion_scope',
        `fachaktionRef ${action.id} has invalid scope: ${String(action.scope)}`,
      )
    }
    if (action.scope === 'view') {
      if (!isNonEmptyString(action.viewId) || !viewIds.has(action.viewId)) {
        pushUnique(
          issues,
          `${base}.viewId`,
          'fachaktion_view',
          `fachaktionRef ${action.id} (scope=view) requires known viewId`,
        )
      }
    }
    if (action.scope === 'specialized') {
      if (
        !isNonEmptyString(action.specializedComponentId)
        || !specializedIds.has(action.specializedComponentId)
      ) {
        pushUnique(
          issues,
          `${base}.specializedComponentId`,
          'fachaktion_specialized',
          `fachaktionRef ${action.id} (scope=specialized) requires known specializedComponentId`,
        )
      }
    }
  }

  if (composition.defaultViewId !== undefined) {
    if (!viewIds.has(composition.defaultViewId)) {
      pushUnique(
        issues,
        'defaultViewId',
        'default_view',
        `defaultViewId references unknown view: ${composition.defaultViewId}`,
      )
    }
  }

  return issues.slice().sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code))
}

/**
 * Normalisiert Reihenfolgen deterministisch (Module → Views → Slots → Fachaktionen).
 * Unveraenderte Semantik; geeignet fuer Hash/Studio-Diff.
 */
export function normalizeWorkspaceComposition(
  composition: WorkspaceComposition,
): WorkspaceComposition {
  const byOrderThenId = <T extends { id: string; order?: number }>(items: T[]): T[] =>
    items
      .slice()
      .sort((a, b) => {
        const ao = a.order ?? Number.MAX_SAFE_INTEGER
        const bo = b.order ?? Number.MAX_SAFE_INTEGER
        if (ao !== bo) return ao - bo
        return a.id.localeCompare(b.id)
      })

  return {
    ...composition,
    modules: byOrderThenId(composition.modules ?? []),
    views: byOrderThenId(composition.views ?? []),
    specializedComponents: byOrderThenId(composition.specializedComponents ?? []),
    fachaktionRefs: (composition.fachaktionRefs ?? [])
      .slice()
      .sort((a, b) => a.id.localeCompare(b.id)),
  }
}

export function isWorkspaceCompositionValid(composition: WorkspaceComposition): boolean {
  return validateWorkspaceComposition(composition).length === 0
}
