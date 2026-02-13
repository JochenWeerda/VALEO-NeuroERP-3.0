import { useMemo, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import {
  downloadComplianceCsv,
  fetchLotTrace,
  useGefahrstoffExport,
  useNaehrstoffExport,
  type HazardExportRow,
  type LotTraceResponse,
} from '@/lib/api/compliance-exports'
import { Download, FileSearch } from 'lucide-react'

const currentYear = new Date().getFullYear()

function formatNumber(value: number | undefined): string {
  return new Intl.NumberFormat('de-DE', { maximumFractionDigits: 3 }).format(value ?? 0)
}

export default function ComplianceExportPruefprotokollPage(): JSX.Element {
  const { toast } = useToast()
  const [year, setYear] = useState<number>(currentYear)
  const [lotId, setLotId] = useState<string>('')

  const hazardQuery = useGefahrstoffExport(year)
  const nutrientQuery = useNaehrstoffExport(year)

  const traceMutation = useMutation({
    mutationFn: async () => fetchLotTrace(lotId),
    onError: (e: unknown) => {
      const message = e instanceof Error ? e.message : 'Chargen-Trace konnte nicht geladen werden'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    },
  })

  const hazardRows = hazardQuery.data?.rows ?? []
  const monthlyRows = useMemo(
    () =>
      Object.entries(nutrientQuery.data?.byMonth ?? {}).map(([month, values]) => ({
        month,
        ...values,
      })),
    [nutrientQuery.data?.byMonth],
  )

  const hasGlobalError = hazardQuery.isError || nutrientQuery.isError
  if (hasGlobalError) {
    return (
      <ErrorState
        error={(hazardQuery.error ?? nutrientQuery.error) as Error}
        onRetry={() => {
          void hazardQuery.refetch()
          void nutrientQuery.refetch()
        }}
      />
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Export und Pruefprotokoll</h1>
          <p className="text-muted-foreground">Gefahrstoffdoku, N/P2O5-Export und Chargen-Trace ohne Mock-Daten</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter und Export</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div>
            <Label htmlFor="year">Jahr</Label>
            <Input
              id="year"
              type="number"
              min={2000}
              max={2100}
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
            />
          </div>
          <div className="flex items-end gap-2">
            <Button
              variant="outline"
              className="gap-2"
              onClick={() => {
                void downloadComplianceCsv('gefahrstoffdoku', year)
              }}
            >
              <Download className="h-4 w-4" />
              Gefahrstoff CSV
            </Button>
            <Button
              variant="outline"
              className="gap-2"
              onClick={() => {
                void downloadComplianceCsv('naehrstoffstrom', year)
              }}
            >
              <Download className="h-4 w-4" />
              N/P2O5 CSV
            </Button>
          </div>
          <div className="rounded-md bg-muted p-3 text-sm">
            Exportzeitpunkt Gefahrstoff:{' '}
            <span className="font-medium">
              {hazardQuery.data?.generated_at ? new Date(hazardQuery.data.generated_at).toLocaleString('de-DE') : '-'}
            </span>
            <br />
            Exportzeitpunkt Naehrstoff:{' '}
            <span className="font-medium">
              {nutrientQuery.data?.generated_at ? new Date(nutrientQuery.data.generated_at).toLocaleString('de-DE') : '-'}
            </span>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">PSM-Zeilen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{hazardQuery.data?.total ?? 0}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferscheine Jahr</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{nutrientQuery.data?.deliveryCount ?? 0}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Summe N (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{formatNumber(nutrientQuery.data?.totalNutrientNKg)}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Summe P2O5 (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{formatNumber(nutrientQuery.data?.totalNutrientP2o5Kg)}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Gefahrstoffdokumentation</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable<HazardExportRow>
            data={hazardRows}
            columns={[
              { key: 'deliveryNumber', label: 'Lieferschein' },
              { key: 'deliveryDate', label: 'Datum' },
              { key: 'article', label: 'Artikel' },
              { key: 'bvlZulassungsnummer', label: 'BVL-Zulassung' },
              {
                key: 'compliant',
                label: 'Compliance',
                render: (row) => <Badge variant={row.compliant ? 'outline' : 'destructive'}>{row.compliant ? 'ja' : 'nein'}</Badge>,
              },
            ]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Naehrstoffstrom pro Monat</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            data={monthlyRows}
            columns={[
              { key: 'month', label: 'Monat' },
              { key: 'deliveries', label: 'Lieferscheine' },
              { key: 'n_kg', label: 'N (kg)', render: (row) => formatNumber(row.n_kg) },
              { key: 'p2o5_kg', label: 'P2O5 (kg)', render: (row) => formatNumber(row.p2o5_kg) },
            ]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Chargen-Trace Drilldown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="lot_id oder chargen_id"
              value={lotId}
              onChange={(e) => setLotId(e.target.value)}
            />
            <Button
              className="gap-2"
              onClick={() => {
                void traceMutation.mutateAsync()
              }}
              disabled={traceMutation.isPending || !lotId.trim()}
            >
              <FileSearch className="h-4 w-4" />
              Trace laden
            </Button>
          </div>

          {traceMutation.data && <TraceResult result={traceMutation.data} />}
        </CardContent>
      </Card>
    </div>
  )
}

function TraceResult({ result }: { result: LotTraceResponse }): JSX.Element {
  if (result.error) {
    return <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">{result.error}</div>
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md bg-muted p-3 text-sm">
        Charge: <span className="font-medium">{result.lot?.lotId ?? result.lot?.id ?? '-'}</span> | Artikel:{' '}
        <span className="font-medium">{result.lot?.article ?? '-'}</span> | Menge:{' '}
        <span className="font-medium">{formatNumber(result.lot?.quantity)} t</span> | Lieferungen:{' '}
        <span className="font-medium">{result.deliveryCount ?? 0}</span>
      </div>

      <DataTable
        data={result.linkedDeliveries ?? []}
        columns={[
          { key: 'deliveryNumber', label: 'Lieferschein' },
          { key: 'deliveryDate', label: 'Datum' },
          { key: 'article', label: 'Artikel' },
          { key: 'quantity', label: 'Menge', render: (row) => formatNumber(row.quantity) },
          { key: 'customerId', label: 'Kunde' },
        ]}
      />
    </div>
  )
}
