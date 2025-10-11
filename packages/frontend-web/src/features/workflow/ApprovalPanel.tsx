import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/workflow/StatusBadge'
import { useWorkflow } from '@/hooks/useWorkflow'

interface ApprovalPanelProps {
  domain: 'sales' | 'purchase'
  doc: ApprovalDocument
}

type ApprovalLine = {
  article?: string
  qty?: number
  price?: number
  cost?: number
}

type ApprovalDocument = {
  number: string
  lines?: ApprovalLine[]
  total?: number
} & Record<string, unknown>

export default function ApprovalPanel({ domain, doc }: ApprovalPanelProps): JSX.Element {
  const { state, transition, loading } = useWorkflow(domain, doc.number)

  const allowedActions = {
    submit: state === 'draft',
    approve: state === 'pending',
    reject: state === 'pending',
    post: state === 'approved',
  }

  const handleSubmit = async (): Promise<void> => {
    const result = await transition('submit', doc)
    if (!result.ok) {
      console.error('Submit failed:', result.error)
    }
  }

  const handleApprove = async (): Promise<void> => {
    const result = await transition('approve', doc)
    if (!result.ok) {
      console.error('Approve failed:', result.error)
    }
  }

  const handleReject = async (): Promise<void> => {
    // In production: ask for a rejection reason via a dialog
    const reason = prompt('Ablehnungsgrund:')
    if (reason == null || reason.trim().length === 0) {
      return
    }

    const result = await transition('reject', { ...doc, reason })
    if (!result.ok) {
      console.error('Reject failed:', result.error)
    }
  }

  const handlePost = async (): Promise<void> => {
    // Confirmation dialog for final posting
    const confirmed = confirm('Beleg wirklich buchen? Diese Aktion kann nicht rueckgaengig gemacht werden.')
    if (!confirmed) {
      return
    }

    const result = await transition('post', doc)
    if (!result.ok) {
      console.error('Post failed:', result.error)
    }
  }

  return (
    <div className="flex items-center gap-3 rounded-lg border bg-gray-50 p-4">
      <StatusBadge status={state} data-testid="approval-status-badge" />

      <div className="flex-1" />

      <div className="flex items-center gap-2">
        {loading ? <Loader2 className="h-4 w-4 animate-spin text-gray-500" /> : null}

        {allowedActions.submit ? (
          <Button disabled={loading} onClick={handleSubmit} variant="outline" data-testid="btn-submit">
            Einreichen
          </Button>
        ) : null}

        {allowedActions.approve ? (
          <Button disabled={loading} onClick={handleApprove} variant="default" data-testid="btn-approve">
            Freigeben
          </Button>
        ) : null}

        {allowedActions.reject ? (
          <Button disabled={loading} onClick={handleReject} variant="destructive" data-testid="btn-reject">
            Ablehnen
          </Button>
        ) : null}

        {allowedActions.post ? (
          <Button
            disabled={loading}
            onClick={handlePost}
            variant="default"
            className="bg-green-600 hover:bg-green-700"
            data-testid="btn-post"
          >
            Buchen
          </Button>
        ) : null}
      </div>
    </div>
  )
}
