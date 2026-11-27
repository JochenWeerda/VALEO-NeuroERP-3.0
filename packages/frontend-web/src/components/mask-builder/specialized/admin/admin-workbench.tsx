import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'
import WebhooksSurface from './webhooks-surface'
import ControlCenterSurface from './control-center-surface'

const AgentOpsSurface = lazy(() => import('./agent-ops-surface'))
const SuperglueSurface = lazy(() => import('./superglue-surface'))
const GapPipelineSurface = lazy(() => import('./gap-pipeline-surface'))
const AgentenIntegrationSurface = lazy(() => import('./agenten-integration-surface'))
const PostfaecherRueckrufSurface = lazy(() => import('./postfaecher-rueckruf-surface'))
const ScreenStudioSurface = lazy(() => import('./screen-studio-surface'))
const SetupSurface = lazy(() => import('./setup-surface'))
const SetupDmsSurface = lazy(() => import('./setup-dms-surface'))
const VoiceChannelSurface = lazy(() => import('./voice-channel-surface'))
const VordruckEditorSurface = lazy(() => import('./vordruck-editor-surface'))
const WorkspaceCompositionPreviewSurface = lazy(() => import('./workspace-composition-preview-surface'))

const WEBHOOK_FIELDS = ['id', 'nr', 'url', 'bereich', 'is_active', 'erstellt_am', 'letzte_auslosung_am', 'fehler_count', 'signiert', 'secret', 'versucht_am', 'erfolgreich', 'status_code', 'dauer_ms', 'fehler']
const CONTROL_FIELDS = ['tenant_id', 'incident_id', 'source', 'severity', 'status', 'title', 'owner', 'recommended_action', 'scheduled_for', 'plan_id', 'kind', 'calendar_window', 'open_quarantine_count', 'journal_error_count']
const AGENT_OPS_FIELDS = ['persisted', 'history_count', 'state_path']
const SUPERGLUE_FIELDS = ['tenant_id', 'storage_path']
const GAP_FIELDS = ['year', 'pipeline_complete', 'gap_payments_count']
const AGENTEN_FIELDS = ['tenant_id', 'section']
const POST_FIELDS = ['code', 'state']
const STUDIO_FIELDS = ['screen_id', 'status']
const SETUP_FIELDS = ['step', 'status']
const DMS_FIELDS = ['status', 'connected']
const VOICE_FIELDS = ['enabled', 'last_utterance']
const VORDRUCK_FIELDS = ['id', 'name', 'kategorie']
const WORKSPACE_PREVIEW_FIELDS = ['draft_id', 'status']

function LazySurface({ children }: { children: React.ReactNode }): JSX.Element {
  return <Suspense fallback={<p role="status">Admin-Oberfläche wird geladen…</p>}>{children}</Suspense>
}

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
    return <DomainContractBoundary plan={plan} fields={AGENT_OPS_FIELDS}><LazySurface><AgentOpsSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/control-center/superglue') {
    return <DomainContractBoundary plan={plan} fields={SUPERGLUE_FIELDS}><LazySurface><SuperglueSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/GapPipelineConsole') {
    return <DomainContractBoundary plan={plan} fields={GAP_FIELDS}><LazySurface><GapPipelineSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/agenten-integration') {
    return <DomainContractBoundary plan={plan} fields={AGENTEN_FIELDS}><LazySurface><AgentenIntegrationSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/postfaecher-anmeldung-rueckruf') {
    return <DomainContractBoundary plan={plan} fields={POST_FIELDS}><LazySurface><PostfaecherRueckrufSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/screen-studio') {
    return <DomainContractBoundary plan={plan} fields={STUDIO_FIELDS}><LazySurface><ScreenStudioSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/setup') {
    return <DomainContractBoundary plan={plan} fields={SETUP_FIELDS}><LazySurface><SetupSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/setup/dms-integration') {
    return <DomainContractBoundary plan={plan} fields={DMS_FIELDS}><LazySurface><SetupDmsSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/voice-channel') {
    return <DomainContractBoundary plan={plan} fields={VOICE_FIELDS}><LazySurface><VoiceChannelSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'admin/vordruck-editor') {
    return <DomainContractBoundary plan={plan} fields={VORDRUCK_FIELDS}><LazySurface><VordruckEditorSurface /></LazySurface></DomainContractBoundary>
  }
  if (contract.id === 'studio/workspace-composition-preview') {
    return <DomainContractBoundary plan={plan} fields={WORKSPACE_PREVIEW_FIELDS}><LazySurface><WorkspaceCompositionPreviewSurface /></LazySurface></DomainContractBoundary>
  }
  return <p role="alert">Unbekannter Adminvertrag.</p>
}
