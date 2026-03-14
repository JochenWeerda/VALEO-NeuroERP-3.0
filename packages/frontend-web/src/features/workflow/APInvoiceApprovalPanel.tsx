import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import {
  useActOnAPApproval,
  useAPApprovalStatus,
  useRequestAPApproval,
} from '@/lib/api/ap-approval-workflow'

type APInvoiceApprovalPanelProps = {
  invoiceId: string
  canRequestApproval: boolean
  canPost: boolean
  onPosted: () => Promise<void> | void
  onStatusChanged: () => Promise<void> | void
}

const CURRENT_USER = 'current_user'

export default function APInvoiceApprovalPanel({
  invoiceId,
  canRequestApproval,
  canPost,
  onPosted,
  onStatusChanged,
}: APInvoiceApprovalPanelProps): JSX.Element {
  const [comment, setComment] = useState('')
  const statusQuery = useAPApprovalStatus(invoiceId)
  const requestApproval = useRequestAPApproval()
  const actOnApproval = useActOnAPApproval()

  const approval = statusQuery.data
  const decisionView = buildDecisionView(approval?.explainability)
  const isBusy = statusQuery.isLoading || requestApproval.isPending || actOnApproval.isPending

  const handleRequestApproval = async (): Promise<void> => {
    await requestApproval.mutateAsync({
      invoice_id: invoiceId,
      requested_by: CURRENT_USER,
      comment: comment.trim() || undefined,
    })
    setComment('')
    await onStatusChanged()
  }

  const handleApprovalAction = async (action: 'approve' | 'reject'): Promise<void> => {
    await actOnApproval.mutateAsync({
      invoice_id: invoiceId,
      approved_by: CURRENT_USER,
      action,
      comment: comment.trim() || undefined,
    })
    setComment('')
    await onStatusChanged()
  }

  return (
    <Card className="space-y-4 p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold">Freigabe und Explainability</h3>
          <p className="text-sm text-muted-foreground">AP-Freigabestatus fuer {invoiceId}</p>
        </div>
        {isBusy ? <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" /> : null}
      </div>

      {decisionView !== null ? (
        <ProcessStatusPanel view={decisionView} />
      ) : (
        <p className="text-sm text-muted-foreground">
          Noch keine strukturierte Freigabeentscheidung verfuegbar.
        </p>
      )}

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-md border p-3">
          <div className="text-xs uppercase text-muted-foreground">Status</div>
          <div className="mt-1 font-medium">{approval?.status ?? 'wird geladen'}</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs uppercase text-muted-foreground">Freigaben</div>
          <div className="mt-1 font-medium">
            {approval ? `${approval.current_approvals}/${approval.required_approvals}` : '-'}
          </div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs uppercase text-muted-foreground">Regel</div>
          <div className="mt-1 font-medium">
            {typeof approval?.applicable_rule?.name === 'string'
              ? approval.applicable_rule.name
              : 'Standard'}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Input
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Kommentar oder Ablehnungsgrund"
        />
        <div className="flex flex-wrap gap-2">
          {canRequestApproval && approval?.status === 'not_requested' ? (
            <Button disabled={isBusy} onClick={() => void handleRequestApproval()} variant="outline">
              Freigabe anfordern
            </Button>
          ) : null}
          {approval?.status === 'pending' || approval?.status === 'partially_approved' ? (
            <>
              <Button disabled={isBusy} onClick={() => void handleApprovalAction('approve')}>
                Freigeben
              </Button>
              <Button
                disabled={isBusy || comment.trim().length === 0}
                onClick={() => void handleApprovalAction('reject')}
                variant="destructive"
              >
                Ablehnen
              </Button>
            </>
          ) : null}
          {approval?.can_post && canPost ? (
            <Button
              disabled={isBusy}
              onClick={() => void onPosted()}
              className="bg-green-600 hover:bg-green-700"
            >
              Buchen
            </Button>
          ) : null}
        </div>
      </div>
    </Card>
  )
}
