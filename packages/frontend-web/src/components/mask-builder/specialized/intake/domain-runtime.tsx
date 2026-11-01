import { createContext, useContext, useEffect, useRef, useCallback, Fragment } from 'react'
import type { ReactNode, MutableRefObject } from 'react'
import type { RenderPlan } from '../../render-plan/types'
import { UniversalNativeCockpitPage } from '../../UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useDomainIdentity } from './domain-data'
import { useScreenPermissions } from '../../runtime/screen-permissions'

type Handler = (_payload: Record<string, unknown>) => void | Promise<void>
type Handlers = Record<string, Handler>
const DispatchContext = createContext<MutableRefObject<Handlers> | null>(null)

/** Domain controls and the shared action bar execute the same guarded handlers. */
export function IntakeWeighingPage({ screenId }: { screenId: string }): JSX.Element {
  const handlers = useRef<Handlers>({})
  const schema = useScreenDefinition(screenId)
  const permissions = useScreenPermissions(schema.data)
  const dispatch = useCallback((key: string, payload: Record<string, unknown>) => handlers.current[key]?.(payload), [])
  return <DispatchContext.Provider value={handlers}>
    <UniversalNativeCockpitPage screenId={screenId} permissions={permissions} onAction={dispatch} />
  </DispatchContext.Provider>
}

export function canDomainAction(plan: RenderPlan, key: string): boolean {
  const action = plan.actions.find(item => item.key === key)
  // Dynamic row conditions need an explicit domain evaluation; never assume true.
  return Boolean(action && !action.disabled && !action.enabledWhen)
}

export function useDomainDispatch(plan: RenderPlan, handlers: Handlers): void {
  const registry = useContext(DispatchContext)
  const latest = useRef(handlers)
  latest.current = handlers
  useEffect(() => {
    if (!registry) return
    const bound = Object.fromEntries(Object.keys(handlers).map(key => [key, (payload: Record<string, unknown>) => {
      if (canDomainAction(plan, key)) return latest.current[key]?.(payload)
    }]))
    registry.current = bound
    return () => { if (registry.current === bound) registry.current = {} }
  }, [registry, plan])
}

/** Do not mount a data-reading specialist when an overlay removed its contract. */
export function DomainContractBoundary({ plan, fields, children }: {
  plan: RenderPlan; fields: string[]; children: ReactNode
}): JSX.Element {
  const identity = useDomainIdentity()
  if (!identity.tenantId || !identity.actor) return <p role="alert">Ein eindeutiger angemeldeter Mandant ist für diese Ansicht erforderlich.</p>
  const missing = fields.filter(key => !plan.fieldsByKey[key]?.visible)
  if (missing.length) return <p role="alert">Diese Ansicht kann mit ausgeblendeten Pflichtbereichen nicht geöffnet werden. Bitte die Ansichtsänderung zurücksetzen.</p>
  return <Fragment key={`${identity.tenantId}/${identity.actor}`}>{children}</Fragment>
}

export function fieldsEditable(plan: RenderPlan, keys: string[]): boolean {
  return keys.every(key => plan.fieldsByKey[key]?.visible && !plan.fieldsByKey[key]?.readOnly)
}
