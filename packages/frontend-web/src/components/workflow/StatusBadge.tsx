import { Badge } from '@/components/ui/badge'
import type { WorkflowState } from '@/hooks/useWorkflow'

interface StatusBadgeProps {
  status: WorkflowState
  'data-testid'?: string
}

export function StatusBadge({ status, 'data-testid': testId }: StatusBadgeProps) {
  const variants: Record<WorkflowState, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    draft: 'outline',
    pending: 'secondary',
    approved: 'default',
    posted: 'default',
    rejected: 'destructive',
  }

  return (
    <Badge variant={variants[status]} data-testid={testId}>
      {status.toUpperCase()}
    </Badge>
  )
}

