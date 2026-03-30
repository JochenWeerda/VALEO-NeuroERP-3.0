/**
 * Labor-Auftrag Detail — REK-001-P6
 * GET /api/v1/qualitaet/labor-auftraege/{id}
 */

import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ArrowLeft, Beaker } from 'lucide-react'
import type { LaborAuftrag } from '@/lib/api/betrieb'

export default function LaborDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: auftrag, isLoading, isError } = useQuery({
    queryKey: ['qualitaet', 'labor', id],
    queryFn: async () =>
      (await apiClient.get<LaborAuftrag>(`/api/v1/qualitaet/labor-auftraege/${id}`)).data,
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48" />
      </div>
    )
  }

  if (isError || !auftrag) {
    return (
      <div className="p-6">
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-red-600">Labor-Auftrag konnte nicht geladen werden.</p>
            <Button variant="outline" className="mt-4" onClick={() => navigate('/qualitaet/labor')}>
              Zurueck zur Liste
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/qualitaet/labor')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Labor-Auftrag {auftrag.id}</h1>
            <p className="text-muted-foreground">
              Charge {auftrag.chargenId} · {auftrag.labor}
            </p>
          </div>
        </div>
        <Badge
          variant={
            auftrag.status === 'abgeschlossen'
              ? 'outline'
              : auftrag.status === 'in-bearbeitung'
                ? 'secondary'
                : 'default'
          }
        >
          {auftrag.status === 'offen'
            ? 'Offen'
            : auftrag.status === 'in-bearbeitung'
              ? 'In Bearbeitung'
              : 'Abgeschlossen'}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Beaker className="h-5 w-5" />
              Auftragsdaten
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Auftrags-ID</span>
              <span className="font-mono font-medium">{auftrag.id}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Chargen-ID</span>
              <span className="font-mono">{auftrag.chargenId}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Labor</span>
              <span>{auftrag.labor}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Analysen</span>
              <span>{auftrag.analysen}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Auftragsdatum</span>
              <span>
                {auftrag.auftragsdatum
                  ? new Date(auftrag.auftragsdatum).toLocaleDateString('de-DE')
                  : '–'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
