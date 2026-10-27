import { aliasesForCatalogId } from './fachaktion-resolve'
import type { CommandCenterEntry, TypedFachaktion, UserContext } from './types'
import { hasRequiredScope } from './user-context'

const LAYER_CATEGORY: Record<TypedFachaktion['layer'], string> = {
  personal: 'Persoenlich',
  situational: 'Situativ',
  proactive: 'Handlungsbedarf',
  dialog: 'Fachaktionen',
}

function withQuery(route: string, query: Record<string, string> | undefined): string {
  if (!query || Object.keys(query).length === 0) {
    return route
  }
  const params = new URLSearchParams(query)
  const sep = route.includes('?') ? '&' : '?'
  return `${route}${sep}${params.toString()}`
}

/**
 * Mappt eine typisierte Fachaktion auf einen Command-Center-Eintrag.
 * prepare-command haengt omniboxAction an — kein Auto-Submit.
 */
export function mapFachaktionToCommand(action: TypedFachaktion): CommandCenterEntry {
  const params: Record<string, unknown> = {
    path: withQuery(action.target.route, action.target.worklistQuery),
    fachaktionId: action.id,
    kind: action.kind,
  }
  if (action.target.screenId) {
    params.screenId = action.target.screenId
  }
  if (action.catalogId) {
    params.catalogId = action.catalogId
  }
  if (action.kind === 'prepare-command' && action.target.actionKey) {
    params.path = withQuery(action.target.route, {
      ...action.target.worklistQuery,
      omniboxAction: action.target.actionKey,
    })
    params.actionKey = action.target.actionKey
  }

  return {
    id: `fachaktion:${action.id}`,
    label: action.label,
    keywords: [
      ...action.keywords,
      action.id,
      action.kind,
      ...(action.catalogId ? [action.catalogId] : []),
      ...aliasesForCatalogId(action.catalogId),
    ],
    category: LAYER_CATEGORY[action.layer],
    actionId: `fachaktion:${action.id}`,
    actionParams: params,
    hint: action.kind === 'prepare-command' ? 'vorbereiten' : action.target.screenId,
    mcp: {
      intent: action.mcpIntent,
      businessDomain: action.businessDomain,
      requiredScopes: action.requiredScopes.length > 0 ? action.requiredScopes : undefined,
    },
  }
}

export function authorizeFachaktionen(
  actions: TypedFachaktion[],
  scopes: string[] | undefined,
): TypedFachaktion[] {
  if (scopes === undefined) {
    return actions
  }
  return actions.filter((action) => hasRequiredScope(action.requiredScopes, scopes))
}

export function mapAuthorizedFachaktionen(
  actions: TypedFachaktion[],
  context: Pick<UserContext, 'scopes'> | { scopes?: string[] },
): CommandCenterEntry[] {
  return authorizeFachaktionen(actions, context.scopes).map(mapFachaktionToCommand)
}
