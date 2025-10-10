import { useSSE } from '@/lib/sse'
import { useToast } from '@/hooks/use-toast'

/**
 * Workflow Events Hook
 * Listens to workflow SSE events and shows appropriate toasts
 * Handles audit events, replay, and status notifications
 */
export function useWorkflowEvents(): void {
  const { toast } = useToast()

  // SSE listener for workflow events
  useSSE('workflow', (eventData: any) => {
    try {
      // Handle workflow state transition events
      if (eventData.topic === 'workflow') {
        handleWorkflowEvent(eventData)
      }
      // Handle audit events (exports, access logs, etc.)
      else if (eventData.topic === 'audit') {
        handleAuditEvent(eventData)
      }
    } catch (error) {
      console.error('Error processing workflow event:', error)
    }
  })

  // Handle workflow state transition events
  const handleWorkflowEvent = (event: any): void => {
    const { domain, number, action, type } = event

    if (type === 'replay') {
      // Skip toasts for replay events to avoid spam
      return
    }

    // German action labels
    const actionLabels: Record<string, string> = {
      submit: 'eingereicht',
      approve: 'freigegeben',
      reject: 'abgelehnt',
      post: 'gebucht'
    }

    const actionLabel = actionLabels[action] || action
    const message = `${domain?.toUpperCase()} ${number}: ${actionLabel}`

    // Different toast styles based on action
    if (action === 'reject') {
      toast({
        title: '❌ ' + message,
        variant: 'destructive',
      })
    } else {
      toast({
        title: '✅ ' + message,
      })
    }
  }

  // Handle audit events (exports, access logs, etc.)
  const handleAuditEvent = (event: any): void => {
    const { type, user, domain, count } = event

    switch (type) {
      case 'export':
        toast({
          title: `📊 Export: ${count} ${domain}-Datensätze von ${user}`,
        })
        break
      case 'audit_access':
        // Only show for unusual access patterns
        if (count && count > 10) {
          toast({
            title: `🔍 Häufiger Audit-Zugriff: ${domain} ${count}x`,
            variant: 'default',
          })
        }
        break
      default:
        console.log('Audit event:', event)
    }
  }
}

/**
 * Workflow Replay Hook
 * Can fetch and replay workflow events since a timestamp
 */
export function useWorkflowReplay() {
  const replayEvents = async (since: number = 0): Promise<any[]> => {
    try {
      const response = await fetch(`/api/workflow/replay/workflow?since=${since}`)
      const data = await response.json()

      if (data.ok) {
        return data.events || []
      }

      console.warn('Replay failed:', data)
      return []
    } catch (error) {
      console.error('Error replaying workflow events:', error)
      return []
    }
  }

  return { replayEvents }
}