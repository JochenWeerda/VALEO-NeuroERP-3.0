import type { ToolbarAction } from '@/components/navigation/PageToolbar'
import type { Action } from './api/actions'

type ActionDispatchLike = {
  dispatch: (actionId: string, params?: Record<string, unknown>) => Promise<boolean>
} | null

interface BuildToolbarActionsResult {
  primary: ToolbarAction[]
  overflow: ToolbarAction[]
}

function mapVariant(category: string): ToolbarAction['variant'] {
  if (category === 'danger') {
    return 'destructive'
  }
  return 'outline'
}

function sortActions(actions: Action[]): Action[] {
  return [...actions].sort((left, right) => {
    const leftScore = left.relevance_score ?? 0
    const rightScore = right.relevance_score ?? 0
    if (leftScore !== rightScore) {
      return rightScore - leftScore
    }
    const leftPriority = left.priority ?? 100
    const rightPriority = right.priority ?? 100
    if (leftPriority !== rightPriority) {
      return leftPriority - rightPriority
    }
    return left.label.localeCompare(right.label, 'de')
  })
}

function toToolbarAction(action: Action, dispatch: ActionDispatchLike): ToolbarAction {
  return {
    id: action.id,
    label: action.label,
    shortcut: action.shortcut,
    onClick: () => {
      if (dispatch) {
        void dispatch.dispatch(action.id, action.default_params)
      }
    },
    variant: mapVariant(action.category),
    mcp: { intent: action.id, requiredData: action.required_data },
  }
}

export function buildToolbarActionsFromRegistry(
  actions: Action[] | undefined,
  dispatch: ActionDispatchLike,
): BuildToolbarActionsResult {
  const resolvedActions = sortActions(actions ?? [])
  const primaryCandidates = resolvedActions.filter((action) => action.surfaces?.includes('toolbar-primary'))
  const overflowCandidates = resolvedActions.filter((action) => action.surfaces?.includes('toolbar-overflow'))

  const primary = primaryCandidates.slice(0, 2).map((action) => toToolbarAction(action, dispatch))

  const usedIds = new Set(primary.map((action) => action.id))
  const overflow = overflowCandidates
    .filter((action) => !usedIds.has(action.id))
    .map((action) => toToolbarAction(action, dispatch))

  if (primary.length > 0 || overflow.length > 0) {
    return { primary, overflow }
  }

  const fallback = resolvedActions.map((action) => toToolbarAction(action, dispatch))
  return {
    primary: fallback.slice(0, 2),
    overflow: fallback.slice(2),
  }
}
