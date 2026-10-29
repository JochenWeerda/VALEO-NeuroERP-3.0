/**
 * Parser fuer WorkspaceComposition aus Plain-Objects (YAML/JSON nach Deserialisierung).
 * Kein CLI-Generator, kein ScreenDefinition-Rewrite — nur Vertragsauflösung.
 */

import {
  SPECIALIZED_COMPONENT_KINDS,
  type FachaktionScope,
  type SpecializedComponentKind,
  type WorkspaceComposition,
  type WorkspaceCompositionIssue,
  type WorkspaceFachaktionRef,
  type WorkspaceModuleRef,
  type WorkspacePersonalizationKeys,
  type WorkspaceSpecializedComponentRef,
  type WorkspaceViewRef,
  WORKSPACE_COMPOSITION_SCHEMA_VERSION,
  validateWorkspaceComposition,
} from './workspace-composition'

export type ParseWorkspaceCompositionResult =
  | { ok: true; composition: WorkspaceComposition; issues: [] }
  | { ok: false; composition: null; issues: WorkspaceCompositionIssue[] }

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function asString(value: unknown): string | undefined {
  return typeof value === 'string' ? value : undefined
}

function asOptionalNumber(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function asScalarProp(value: unknown): string | number | boolean | undefined {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return value
  }
  return undefined
}

function parseModules(raw: unknown, issues: WorkspaceCompositionIssue[]): WorkspaceModuleRef[] {
  if (raw === undefined) return []
  if (!Array.isArray(raw)) {
    issues.push({ path: 'modules', code: 'modules_type', message: 'modules must be an array' })
    return []
  }
  const modules: WorkspaceModuleRef[] = []
  for (const [index, item] of raw.entries()) {
    if (!isRecord(item)) {
      issues.push({ path: `modules[${index}]`, code: 'module_type', message: 'module must be an object' })
      continue
    }
    modules.push({
      id: asString(item.id) ?? '',
      label: asString(item.label) ?? '',
      domain: asString(item.domain),
      order: asOptionalNumber(item.order),
    })
  }
  return modules
}

function parseViews(raw: unknown, issues: WorkspaceCompositionIssue[]): WorkspaceViewRef[] {
  if (raw === undefined) return []
  if (!Array.isArray(raw)) {
    issues.push({ path: 'views', code: 'views_type', message: 'views must be an array' })
    return []
  }
  const views: WorkspaceViewRef[] = []
  for (const [index, item] of raw.entries()) {
    if (!isRecord(item)) {
      issues.push({ path: `views[${index}]`, code: 'view_type', message: 'view must be an object' })
      continue
    }
    views.push({
      id: asString(item.id) ?? '',
      moduleId: asString(item.moduleId) ?? '',
      label: asString(item.label) ?? '',
      screenId: asString(item.screenId) ?? '',
      routePath: asString(item.routePath),
      order: asOptionalNumber(item.order),
    })
  }
  return views
}

function parseSpecialized(
  raw: unknown,
  issues: WorkspaceCompositionIssue[],
): WorkspaceSpecializedComponentRef[] {
  if (raw === undefined) return []
  if (!Array.isArray(raw)) {
    issues.push({
      path: 'specializedComponents',
      code: 'specialized_type',
      message: 'specializedComponents must be an array',
    })
    return []
  }
  const slots: WorkspaceSpecializedComponentRef[] = []
  for (const [index, item] of raw.entries()) {
    if (!isRecord(item)) {
      issues.push({
        path: `specializedComponents[${index}]`,
        code: 'specialized_type',
        message: 'specializedComponent must be an object',
      })
      continue
    }
    const kindRaw = asString(item.kind) ?? ''
    const kind = SPECIALIZED_COMPONENT_KINDS.includes(kindRaw as SpecializedComponentKind)
      ? (kindRaw as SpecializedComponentKind)
      : (kindRaw as SpecializedComponentKind)

    let props: Record<string, string | number | boolean> | undefined
    if (item.props !== undefined) {
      if (!isRecord(item.props)) {
        issues.push({
          path: `specializedComponents[${index}].props`,
          code: 'specialized_props_type',
          message: 'props must be an object',
        })
      } else {
        props = {}
        for (const [key, value] of Object.entries(item.props)) {
          const scalar = asScalarProp(value)
          if (scalar === undefined) {
            issues.push({
              path: `specializedComponents[${index}].props.${key}`,
              code: 'specialized_props',
              message: `props.${key} must be string | number | boolean`,
            })
          } else {
            props[key] = scalar
          }
        }
      }
    }

    slots.push({
      id: asString(item.id) ?? '',
      kind,
      label: asString(item.label) ?? '',
      hostViewId: asString(item.hostViewId) ?? '',
      bindingId: asString(item.bindingId) ?? '',
      screenId: asString(item.screenId),
      props,
    })
  }
  return slots
}

function parseFachaktionen(
  raw: unknown,
  issues: WorkspaceCompositionIssue[],
): WorkspaceFachaktionRef[] {
  if (raw === undefined) return []
  if (!Array.isArray(raw)) {
    issues.push({
      path: 'fachaktionRefs',
      code: 'fachaktion_type',
      message: 'fachaktionRefs must be an array',
    })
    return []
  }
  const actions: WorkspaceFachaktionRef[] = []
  for (const [index, item] of raw.entries()) {
    if (!isRecord(item)) {
      issues.push({
        path: `fachaktionRefs[${index}]`,
        code: 'fachaktion_type',
        message: 'fachaktionRef must be an object',
      })
      continue
    }
    actions.push({
      id: asString(item.id) ?? '',
      actionKey: asString(item.actionKey) ?? '',
      label: asString(item.label) ?? '',
      scope: (asString(item.scope) ?? '') as FachaktionScope,
      viewId: asString(item.viewId),
      specializedComponentId: asString(item.specializedComponentId),
      permission: asString(item.permission),
    })
  }
  return actions
}

function parsePersonalization(
  raw: unknown,
  issues: WorkspaceCompositionIssue[],
): WorkspacePersonalizationKeys {
  if (!isRecord(raw)) {
    issues.push({
      path: 'personalization',
      code: 'personalization_type',
      message: 'personalization must be an object',
    })
    return { pinStorageKey: '', pinnedViewsKey: '', fixedStartViewKey: '' }
  }
  return {
    pinStorageKey: asString(raw.pinStorageKey) ?? '',
    pinnedViewsKey: asString(raw.pinnedViewsKey) ?? '',
    fixedStartViewKey: asString(raw.fixedStartViewKey) ?? '',
  }
}

/**
 * Parst und validiert eine WorkspaceComposition aus einem Plain-Object.
 * YAML-Dateien werden ausserhalb (Studio/CI) deserialisiert und hier uebergeben.
 */
export function parseWorkspaceComposition(raw: unknown): ParseWorkspaceCompositionResult {
  const issues: WorkspaceCompositionIssue[] = []

  if (!isRecord(raw)) {
    return {
      ok: false,
      composition: null,
      issues: [{ path: '', code: 'root_type', message: 'WorkspaceComposition must be an object' }],
    }
  }

  const schemaVersion = raw.schemaVersion
  if (schemaVersion !== WORKSPACE_COMPOSITION_SCHEMA_VERSION && schemaVersion !== undefined) {
    issues.push({
      path: 'schemaVersion',
      code: 'schema_version',
      message: `schemaVersion must be ${WORKSPACE_COMPOSITION_SCHEMA_VERSION}`,
    })
  }

  const composition: WorkspaceComposition = {
    schemaVersion: WORKSPACE_COMPOSITION_SCHEMA_VERSION,
    id: asString(raw.id) ?? '',
    studioVersion: asString(raw.studioVersion) ?? '',
    title: asString(raw.title) ?? '',
    description: asString(raw.description),
    modules: parseModules(raw.modules, issues),
    views: parseViews(raw.views, issues),
    specializedComponents: parseSpecialized(raw.specializedComponents, issues),
    fachaktionRefs: parseFachaktionen(raw.fachaktionRefs, issues),
    personalization: parsePersonalization(raw.personalization, issues),
    defaultViewId: asString(raw.defaultViewId),
  }

  const validationIssues = validateWorkspaceComposition(composition)
  const allIssues = [...issues, ...validationIssues]
    .slice()
    .sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code))

  // Dedupliziere gleiche path+code
  const seen = new Set<string>()
  const unique = allIssues.filter((issue) => {
    const key = `${issue.path}|${issue.code}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })

  if (unique.length > 0) {
    return { ok: false, composition: null, issues: unique }
  }
  return { ok: true, composition, issues: [] }
}
