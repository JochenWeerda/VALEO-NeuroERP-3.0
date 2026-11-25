import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'
import WebhooksSurface from './webhooks-surface'
import ControlCenterSurface from './control-center-surface'

const AgentOpsSurface = lazy(() => import('./agent-ops-surface'))
const SuperglueSurface = lazy(() => import('./superglue-surface'))

const WEBHOOK_FIELDS = ['id', 'nr', 'url', 'bereich', 'is_active', 'erstellt_am', 'letzte_auslosung_am', 'fehler_count', 'signiert', 'secret', 'versucht_am', 'erfolgreich', 'status_code', 'dauer_ms', 'fehler']
const CONTROL_FIELDS = ['tenant_id', 'incident_id', 'source', 'severity', 'status', 'title', 'owner', 'recommended_action', 'scheduled_for', 'plan_id', 'kind', 'calendar_window', 'open_quarantine_count', 'journal_error_count']
const AGENT_OPS_FIELDS = ['persisted', 'history_count', 'state_path']
const SUPERGLUE_FIELDS = ['tenant_id', 'storage_path']

export function AdminWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (!plan || plan.specialized?.id !== contract.id || plan.specialized.type !== 'admin_workbench'
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))) {
    return <p role="alert">Adminvertrag ist nicht verfügbar.</p>
  }
  if (contract.id === 'admin/webhooks-liste') {
    return <DomainContractBoundary plan={plan} fields={WEBHOOK_FIELDS}><WebhooksSurface plan={plan} /></DomainContractBoundary>
  }
  if (contract.id === 'admin/control-center') {
    return <DomainContractBoundary plan={plan} fields={CONTROL_FIELDS}><ControlCenterSurface plan={plan} /></DomainContractBoundary>
  }
  if (contract.id === 'admin/control-center/agent-ops') {
    return (
      <DomainContractBoundary plan={plan} fields={AGENT_OPS_FIELDS}>
        <Suspense fallback={<p role="status">Agent Ops wird geladen…</p>}>
          <AgentOpsSurface />
        </Suspense>
      </DomainContractBoundary>
    )
  }
  if (contract.id === 'admin/control-center/superglue') {
    return (
      <DomainContractBoundary plan={plan} fields={SUPERGLUE_FIELDS}>
        <Suspense fallback={<p role="status">Superglue wird geladen…</p>}>
          <SuperglueSurface />
        </Suspense>
      </DomainContractBoundary>
    )
  }
  return <p role="alert">Unbekannter Adminvertrag.</p>
}
