import { useSSE } from '@/lib/sse'
import { useToast } from '@/hooks/use-toast'
import { type WorkflowAction } from './useWorkflow'

type WorkflowEventTopic = 'workflow' | 'audit'
type WorkflowReplayType = 'live' | 'replay'

interface BaseEventPayload {
  topic: WorkflowEventTopic
}

interface WorkflowEventPayload extends BaseEventPayload {
  topic: 'workflow'
  domain: string
  number: string
  action: WorkflowAction
  type?: WorkflowReplayType
}

type AuditEventType = 'export' | 'audit_access'

interface AuditEventPayload extends BaseEventPayload {
  topic: 'audit'
  type: AuditEventType
  user?: string
  domain?: string
  count?: number
}

type KnownEventPayload = WorkflowEventPayload | AuditEventPayload

const ACTION_LABELS: Record<WorkflowAction, string> = {
  submit: 'eingereicht',
  approve: 'freigegeben',
  reject: 'abgelehnt',
  post: 'gebucht',
}

const AUDIT_ACCESS_THRESHOLD = 10

const isKnownEventPayload = (payload: unknown): payload is KnownEventPayload => {
  if (payload == null || typeof payload !== 'object') {
    return false
  }

  const candidate = payload as Partial<KnownEventPayload>
  return candidate.topic === 'workflow' || candidate.topic === 'audit'
}

const isWorkflowEventPayload = (payload: KnownEventPayload): payload is WorkflowEventPayload => {
  return (
    payload.topic === 'workflow' &&
    typeof payload.domain === 'string' &&
    typeof payload.number === 'string' &&
    typeof payload.action === 'string'
  )
}

const isAuditEventPayload = (payload: KnownEventPayload): payload is AuditEventPayload => {
  return payload.topic === 'audit' && typeof payload.type === 'string'
}

const formatActionLabel = (action: WorkflowAction): string => {
  return ACTION_LABELS[action] ?? action
}

export function useWorkflowEvents(): void {
  const { toast } = useToast()

  const handleWorkflowEvent = (event: WorkflowEventPayload): void => {
    if (event.type === 'replay') {
      return
    }

    const message = `${event.domain.toUpperCase()} ${event.number}: ${formatActionLabel(event.action)}`
    const title = event.action === 'reject' ? 'Workflow abgelehnt' : 'Workflow aktualisiert'

    toast({
      title: `${title}: ${message}`,
      variant: event.action === 'reject' ? 'destructive' : 'default',
    })
  }

  const handleAuditEvent = (event: AuditEventPayload): void => {
    switch (event.type) {
      case 'export':
        toast({
          title: 'Audit Export abgeschlossen',
          description: `${event.count ?? 0} ${event.domain ?? 'Unbekannt'}-Eintraege von ${event.user ?? 'Unbekannt'}`,
        })
        break
      case 'audit_access':
        if ((event.count ?? 0) > AUDIT_ACCESS_THRESHOLD) {
          toast({
            title: 'Audit Zugriffshaeufigkeit',
            description: `${event.domain ?? 'Unbekannt'} ${event.count}x`,
          })
        }
        break
      default:
        console.info('Unbekannter Audit-Event', event)
    }
  }

  useSSE('workflow', (rawEvent) => {
    if (!isKnownEventPayload(rawEvent)) {
      return
    }

    if (isWorkflowEventPayload(rawEvent)) {
      handleWorkflowEvent(rawEvent)
    } else if (isAuditEventPayload(rawEvent)) {
      handleAuditEvent(rawEvent)
    }
  })
}

interface WorkflowReplayResponse {
  ok: boolean
  events?: WorkflowEventPayload[]
}

export function useWorkflowReplay(): { replayEvents: (since?: number) => Promise<WorkflowEventPayload[]> } {
  const replayEvents = async (since = 0): Promise<WorkflowEventPayload[]> => {
    try {
      const response = await fetch(`/api/workflow/replay/workflow?since=${since}`)
      const data = (await response.json()) as WorkflowReplayResponse

      if (data.ok) {
        return data.events ?? []
      }

      console.warn('Workflow replay failed:', data)
      return []
    } catch (error) {
      console.error('Error replaying workflow events:', error)
      return []
    }
  }

  return { replayEvents }
}
