import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search } from 'lucide-react'

type LksgAssessment = {
  id: string
  supplier_name: string
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  last_assessed: string
  status: string
}

const LEVEL_VARIANT: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  LOW: 'default',
  MEDIUM: 'secondary',
  HIGH: 'outline',
  CRITICAL: 'destructive',
}

export default function LksgPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: assessments = [], isError, error, refetch } = useQuery<LksgAssessment[]>({
    queryKey: ['lksg-assessments'],
    queryFn: async () => (await apiClient.get<LksgAssessment[]>('/api/v1/compliance/lksg/supplier-risk-assessments')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = assessments.filter((a) =>
    a.supplier_name.toLowerCase().includes(search.toLowerCase()),
  )

  const highRisk = assessments.filter((a) => a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL').length

  const columns = [
    { key: 'supplier_name' as const, label: 'Lieferant' },
    {
      key: 'risk_score' as const,
      label: 'Risiko-Score',
      render: (a: LksgAssessment) => (
        <div className="flex items-center gap-2">
          <div className="h-2 w-24 rounded-full bg-muted">
            <div
              className={`h-2 rounded-full ${a.risk_score >= 75 ? 'bg-red-500' : a.risk_score >= 50 ? 'bg-orange-500' : a.risk_score >= 25 ? 'bg-yellow-500' : 'bg-green-500'}`}
              style={{ width: `${a.risk_score}%` }}
            />
          </div>
          <span className="text-sm font-mono">{a.risk_score}</span>
        </div>
      ),
    },
    {
      key: 'risk_level' as const,
      label: 'Risiko-Level',
      render: (a: LksgAssessment) => <Badge variant={LEVEL_VARIANT[a.risk_level] ?? 'outline'}>{a.risk_level}</Badge>,
    },
    { key: 'last_assessed' as const, label: 'Letzte Bewertung', render: (a: LksgAssessment) => a.last_assessed ? new Date(a.last_assessed).toLocaleDateString('de-DE') : '–' },
    { key: 'status' as const, label: 'Status' },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">LKSG Lieferanten-Risikobewertung</h1>
            <p className="text-muted-foreground">Lieferkettensorgfaltspflichtengesetz – Risikobewertungen</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neue Bewertung</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Lieferanten bewertet</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{assessments.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">HIGH / CRITICAL</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-red-600">{highRisk}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">LOW / MEDIUM</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{assessments.length - highRisk}</span></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Bewertungen</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Lieferant suchen..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
