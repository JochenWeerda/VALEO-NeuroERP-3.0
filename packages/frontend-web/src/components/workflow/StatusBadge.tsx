import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import type { WorkflowState } from '@/hooks/useWorkflow'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

interface StatusBadgeProps {
  status: WorkflowState
  'data-testid'?: string
}

const STATUS_VARIANTS: Record<WorkflowState, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  draft: 'outline',
  pending: 'secondary',
  approved: 'default',
  posted: 'default',
  rejected: 'destructive',
}

export function StatusBadge({ status, 'data-testid': testId }: StatusBadgeProps): JSX.Element {
  const { t } = useTranslation()
  const label = getStatusLabel(t, status, status)
  return (
    <Badge variant={STATUS_VARIANTS[status]} data-testid={testId}>
      {label}
    </Badge>
  )
}
