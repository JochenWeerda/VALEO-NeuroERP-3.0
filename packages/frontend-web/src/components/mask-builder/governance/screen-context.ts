import type { ScreenCondition } from '../schema'
import { evaluateCondition } from './condition-engine'

export interface PermissionSet {
  granted: string[]
}

export interface ScreenState {
  values: Record<string, unknown>
  policies: Record<string, unknown>
}

export type ActionHandler = (_payload: Record<string, unknown>) => void | Promise<void>

/** Anwendungseigene Befehle. Der Renderer kennt nur den Namen. */
export type ActionRegistry = Record<string, ActionHandler>

export interface NavigationContext {
  currentPath?: string
  push: (_route: string) => void
}

export interface ScreenContext {
  data: Record<string, unknown>
  permissions: PermissionSet
  state: ScreenState
  actions: ActionRegistry
  navigation: NavigationContext
}

export function createScreenContext(context: ScreenContext): ScreenContext {
  return context
}

/** Wurzel für die Condition Engine: Daten, Formularkwerte und gesetzte Policies. */
export function conditionRoot(context: ScreenContext | undefined): Record<string, unknown> | undefined {
  if (!context) return undefined
  return {
    ...context.data,
    ...context.state.values,
    ...context.state.policies,
  }
}

export function actionIsEnabled(
  action: { disabled?: boolean; enabledWhen?: ScreenCondition },
  root: Record<string, unknown> | undefined,
): boolean {
  if (action.disabled) return false
  if (!action.enabledWhen || !root) return true
  return evaluateCondition(action.enabledWhen, root)
}

export async function dispatchScreenAction(
  context: ScreenContext | undefined,
  action: { key: string; command?: string },
  payload: Record<string, unknown>,
  fallback?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>,
): Promise<void> {
  const command = action.command ?? action.key
  const handler = context?.actions[command]
  if (handler) {
    await handler(payload)
    return
  }
  await fallback?.(action.key, payload)
}
