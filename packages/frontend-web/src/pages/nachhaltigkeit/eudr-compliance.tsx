import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { AlertTriangle, CheckCircle, Globe, MapPin } from 'lucide-react'

type EUDRStatus = {
  status: string
  last_check: string
  batches_total: number
  batches_compliant: number
  batches_flagged: number
  due_diligence_statements: number
  origin_countries: string[]
  deforestation_risk: string
  next_report_due: string
}

export default function EUDRCompliancePage(): JSX.Element {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['compliance', 'eudr'],
    queryFn: async () => (await apiClient.get<EUDRStatus>('/api/v1/compliance/eudr')).data,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const eudr = data ?? {
    status: '-',
    batches_total: 0,
    batches_compliant: 0,
    batches_flagged: 0,
    due_diligence_statements: 0,
    origin_countries: [],
    deforestation_risk: '-',
    next_report_due: '-',
    last_check: '-',
  }

  const complianceRate = eudr.batches_total > 0
    ? ((eudr.batches_compliant / eudr.batches_total) * 100).toFixed(1)
    : '0.0'

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">EUDR-Compliance</h1>
        <p className="text-muted-foreground">Entwaldungsfreie Lieferketten</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Chargen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{eudr.batches_total}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Konform</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold text-status-success">{eudr.batches_compliant}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Markiert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{eudr.batches_flagged}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compliance-Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-status-success" />
              <span className="text-2xl font-bold text-status-success">{complianceRate}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {eudr.batches_flagged > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{eudr.batches_flagged} Charge(n) sind NICHT EUDR-konform!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Herkunftsländer
            </CardTitle>
          </CardHeader>
          <CardContent>
            {eudr.origin_countries.length === 0 ? (
              <p className="text-sm text-muted-foreground">Keine Herkunftsländer erfasst.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {eudr.origin_countries.map((land) => (
                  <Badge key={land} variant="outline">{land}</Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Status</span>
              <Badge variant={eudr.status === 'KONFORM' ? 'outline' : 'destructive'}>{eudr.status}</Badge>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Entwaldungsrisiko</span>
              <span className="font-semibold">{eudr.deforestation_risk}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Due-Diligence-Erklärungen</span>
              <span className="font-semibold">{eudr.due_diligence_statements}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Nächste Meldung</span>
              <span className="font-semibold">{eudr.next_report_due}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Letzte Prüfung</span>
              <span className="font-semibold">{eudr.last_check ? new Date(eudr.last_check).toLocaleString('de-DE') : '-'}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
