import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { BarChart3, Leaf, TrendingDown } from 'lucide-react'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'

type EsgReport = {
  totalCo2eKg: number
  byMonth: Record<string, { deliveries: number; n_kg: number; p2o5_kg: number; co2e_kg: number }>
  [key: string]: unknown
}

export default function CO2BilanzPage(): JSX.Element {
  const currentYear = new Date().getFullYear()
  const [searchParams] = useSearchParams()
  const [year] = useState(currentYear)
  const workflowContext = readWorkflowEntryContext(searchParams)

  useEffect(() => {
    if (!workflowContext?.process || !workflowContext.instanceId) return
    void saveFlowSpineResumeCheckpoint(workflowContext.process, workflowContext.instanceId, {
      resume_node_id: 'aggregation',
      resume_route: `/nachhaltigkeit/co2-bilanz?${searchParams.toString()}`,
      resume_payload: {
        screen: 'co2-balance',
        year,
        workflowCase: workflowContext.caseNumber || undefined,
      },
      business_status: 'reporting_in_bearbeitung',
      action_label: 'CO2-Bilanz geoeffnet',
    })
  }, [searchParams, workflowContext, year])

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['sustainability', 'esg-report', 'co2', year],
    queryFn: async () => (await apiClient.get<EsgReport>(`/api/v1/sustainability/esg-report?year=${year}`)).data,
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

  // totalCo2eKg is in kg — convert to tonnes
  const gesamtTonnen = data ? Math.round((data.totalCo2eKg ?? 0) / 1000) : 0
  const byMonth = data?.byMonth ?? {}

  // Build per-month breakdown for the bar chart
  const monthEntries = Object.entries(byMonth)
    .map(([month, values]) => ({
      monat: month,
      co2Kg: values.co2e_kg ?? 0,
    }))
    .sort((a, b) => a.monat.localeCompare(b.monat))

  const maxMonthCo2 = Math.max(...monthEntries.map((m) => m.co2Kg), 1)

  return (
    <div className="space-y-6 p-6">
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Compliance-to-Report"
          description="CO2-, EUDR- und ESG-Daten werden jetzt in den Reporting-Cockpits konsolidiert. Der Flow-Fall bleibt als Referenz erhalten."
        />
      ) : null}
      <div>
        <h1 className="text-3xl font-bold">CO₂-Bilanz</h1>
        <p className="text-muted-foreground">Klimabilanz {year}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">CO₂-Emissionen (t)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Leaf className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{gesamtTonnen.toLocaleString('de-DE')} t CO₂e</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Monate mit Daten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{monthEntries.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt CO₂e (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {(data?.totalCo2eKg ?? 0).toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            CO₂e-Emissionen nach Monat ({year})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {monthEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Keine Monatsdaten für {year} verfügbar.
            </p>
          ) : (
            <div className="space-y-3">
              {monthEntries.map((m) => {
                const anteil = maxMonthCo2 > 0 ? (m.co2Kg / maxMonthCo2) * 100 : 0
                return (
                  <div key={m.monat} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{m.monat}</div>
                      <div className="text-right">
                        <div className="text-xl font-bold">
                          {m.co2Kg.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg CO₂e
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-green-600" style={{ width: `${anteil}%` }} />
                      </div>
                      <Badge variant="outline">{anteil.toFixed(0)}%</Badge>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
