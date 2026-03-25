/**
 * AI-Aktionen zur Freigabe (Gap 015).
 * Human-in-the-loop für AI/Agent-Vorschläge.
 * Zeigt Rechnungen im Status ZUR_FREIGABE aus der AP-Invoice-Queue.
 */

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bot, CheckCircle2, Clock } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'

type APInvoice = {
  id: string
  number?: string
  customerId?: string
  amount?: number
  currency?: string
  status?: string
  semantic_status?: string
  approval_status?: string
  created_at?: string
  [key: string]: unknown
}

export default function AiApprovalsPage(): JSX.Element {
  const { data: pendingItems = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['admin', 'ai-approvals', 'ap-invoices-pending'],
    queryFn: async () => {
      const res = await apiClient.get<APInvoice[]>('/api/v1/ap/invoices?status=ZUR_FREIGABE&limit=50')
      return Array.isArray(res?.data) ? res.data : []
    },
    staleTime: 60_000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-9 w-72" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <Bot className="h-6 w-6" />
          AI-Aktionen zur Freigabe
        </h1>
        <p className="mt-1 text-muted-foreground">
          Human-in-the-loop: Eingangsrechnungen zur manuellen Freigabe (Status: ZUR_FREIGABE).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Ausstehende Freigaben ({pendingItems.length})
          </CardTitle>
          <CardDescription>
            AP-Eingangsrechnungen im Freigabe-Workflow, die eine manuelle Bestätigung erfordern.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-dashed py-12">
              <CheckCircle2 className="h-12 w-12 text-green-500" />
              <p className="text-center text-muted-foreground">
                Keine ausstehenden Freigabe-Aktionen. Alle AP-Rechnungen sind aktuell verarbeitet.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {pendingItems.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <div className="font-medium">{item.number ?? item.id}</div>
                    <div className="text-xs text-muted-foreground">
                      Lieferant: {item.customerId ?? '-'}
                      {item.amount != null && (
                        <span className="ml-2">
                          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: item.currency ?? 'EUR' }).format(item.amount)}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">
                      {item.semantic_status ?? item.approval_status ?? item.status ?? 'ZUR_FREIGABE'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Freigabe-Endpunkte
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• AP-Rechnungen: <code>/api/v1/ap/invoices?status=ZUR_FREIGABE</code></li>
            <li>• Freigabe-Regeln: <code>/api/v1/ap/approval-workflow/rules</code></li>
            <li>• Freigabe-Aktion: <code>POST /api/v1/ap/approval-workflow/approve</code></li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
