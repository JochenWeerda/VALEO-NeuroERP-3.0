import { Button } from '@/components/ui/button'
import { useWorkflow } from '@/hooks/useWorkflow'
import { StatusBadge } from '@/components/workflow/StatusBadge'
import { Loader2 } from 'lucide-react'

interface ApprovalPanelProps {
  domain: 'sales' | 'purchase'
  doc: {
    number: string
    lines?: Array<{
      article?: string
      qty?: number
      price?: number
      cost?: number
    }>
    total?: number
    [key: string]: any
  }
}

export default function ApprovalPanel({ domain, doc }: ApprovalPanelProps) {
  const { state, transition, loading } = useWorkflow(domain, doc.number)

  // Berechne erlaubte Aktionen basierend auf State
  const can = {
    submit: state === 'draft',
    approve: state === 'pending',
    reject: state === 'pending',
    post: state === 'approved',
  }

  const handleSubmit = async () => {
    const result = await transition('submit', doc)
    if (!result.ok) {
      console.error('Submit failed:', result.error)
    }
  }

  const handleApprove = async () => {
    const result = await transition('approve', doc)
    if (!result.ok) {
      console.error('Approve failed:', result.error)
    }
  }

  const handleReject = async () => {
    // In Production: Dialog für Ablehnungsgrund
    const reason = prompt('Ablehnungsgrund:')
    if (!reason) return

    const result = await transition('reject', { ...doc, reason })
    if (!result.ok) {
      console.error('Reject failed:', result.error)
    }
  }

  const handlePost = async () => {
    // Confirmation-Dialog für finale Buchung
    if (!confirm('Beleg wirklich buchen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      return
    }

    const result = await transition('post', doc)
    if (!result.ok) {
      console.error('Post failed:', result.error)
    }
  }

  return (
    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg border">
      <StatusBadge status={state} data-testid="approval-status-badge" />

      <div className="flex-1" />

      <div className="flex items-center gap-2">
        {loading && (
          <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
        )}

        {can.submit && (
          <Button
            disabled={loading}
            onClick={handleSubmit}
            variant="outline"
            data-testid="btn-submit"
          >
            Einreichen
          </Button>
        )}

        {can.approve && (
          <Button
            disabled={loading}
            onClick={handleApprove}
            variant="default"
            data-testid="btn-approve"
          >
            Freigeben
          </Button>
        )}

        {can.reject && (
          <Button
            disabled={loading}
            onClick={handleReject}
            variant="destructive"
            data-testid="btn-reject"
          >
            Ablehnen
          </Button>
        )}

        {can.post && (
          <Button
            disabled={loading}
            onClick={handlePost}
            variant="default"
            className="bg-green-600 hover:bg-green-700"
            data-testid="btn-post"
          >
            Buchen
          </Button>
        )}
      </div>
    </div>
  )
}
