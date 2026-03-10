/**
 * ESG/CO2-Bericht (Gap 046: Nachhaltigkeit/CO2 Reporting für Agrarkonzerne)
 * Aggregierte Nährstoff- und CO2-Daten aus Lieferscheinen – Berichte in <1 Tag erzeugbar
 */

import { useState } from 'react'
import {
  useEsgReport,
  downloadEsgReportCsv,
  downloadEsgReportPdf,
  useSustainabilityProviders,
} from '@/lib/api/sustainability'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { NativeSelect } from '@/components/ui/native-select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { Download, Leaf, BarChart3, Droplets, Zap, Loader2 } from 'lucide-react'
import { toast } from '@/hooks/use-toast'

export default function EsgReportPage(): JSX.Element {
  const currentYear = new Date().getFullYear()
  const [year, setYear] = useState<number>(currentYear)
  const [exporting, setExporting] = useState<'csv' | 'pdf' | null>(null)

  const { data, isLoading, isError, error, refetch } = useEsgReport(year)
  const { data: providers } = useSustainabilityProviders()

  const handleDownload = async (format: 'csv' | 'pdf'): Promise<void> => {
    setExporting(format)
    try {
      if (format === 'csv') {
        await downloadEsgReportCsv(year)
      } else {
        await downloadEsgReportPdf(year)
      }
      toast({ title: 'Export erfolgreich', description: `ESG-Bericht ${year} wurde heruntergeladen.` })
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Export fehlgeschlagen',
        description: err instanceof Error ? err.message : 'Unbekannter Fehler',
      })
    } finally {
      setExporting(null)
    }
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => void refetch()} />
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold flex items-center gap-2">
            <Leaf className="h-6 w-6" />
            ESG/CO2-Bericht
          </h1>
          <p className="mt-1 text-muted-foreground">
            Aggregierte Nährstoff- und CO2-Daten aus Lieferscheinen (Gap 046). Berichte in &lt;1 Tag erzeugbar.
          </p>
        </div>
        <NativeSelect
          value={String(year)}
          onValueChange={(v) => setYear(parseInt(v, 10))}
          options={[currentYear, currentYear - 1, currentYear - 2].map((y) => ({
            value: String(y),
            label: String(y),
          }))}
          className="w-[140px]"
        />
      </div>

      {providers && (
        <div className="flex flex-wrap gap-2">
          <Badge variant={providers.providers.climatiq.configured ? 'default' : 'secondary'}>
            Climatiq {providers.providers.climatiq.configured ? 'aktiv' : 'nicht konfiguriert'}
          </Badge>
          <Badge variant="outline">Daten aus Lieferscheinen</Badge>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground py-8">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Lade ESG-Daten...</span>
        </div>
      ) : data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Droplets className="h-4 w-4" />
                  N gesamt
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{Number(data.totalNutrientNKg).toLocaleString('de-DE', { minimumFractionDigits: 3 })} kg</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  P2O5 gesamt
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{Number(data.totalNutrientP2o5Kg).toLocaleString('de-DE', { minimumFractionDigits: 3 })} kg</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Leaf className="h-4 w-4" />
                  CO2e gesamt
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{Number(data.totalCo2eKg).toLocaleString('de-DE', { minimumFractionDigits: 3 })} kg</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Lieferscheine
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{data.deliveryCount}</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Monatliche Aufschlüsselung {year}</CardTitle>
                <CardDescription>N, P2O5 und CO2e je Monat</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void handleDownload('csv')}
                  disabled={exporting !== null}
                >
                  {exporting === 'csv' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                  CSV
                </Button>
                <Button
                  size="sm"
                  onClick={() => void handleDownload('pdf')}
                  disabled={exporting !== null}
                >
                  {exporting === 'pdf' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                  PDF
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {Object.keys(data.byMonth).length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">Keine Lieferscheindaten für {year} vorhanden.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Monat</TableHead>
                      <TableHead className="text-right">Lieferscheine</TableHead>
                      <TableHead className="text-right">N (kg)</TableHead>
                      <TableHead className="text-right">P2O5 (kg)</TableHead>
                      <TableHead className="text-right">CO2e (kg)</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Object.entries(data.byMonth).map(([month, row]) => (
                      <TableRow key={month}>
                        <TableCell className="font-medium">{month}</TableCell>
                        <TableCell className="text-right">{row.deliveries}</TableCell>
                        <TableCell className="text-right">{Number(row.n_kg).toLocaleString('de-DE', { minimumFractionDigits: 3 })}</TableCell>
                        <TableCell className="text-right">{Number(row.p2o5_kg).toLocaleString('de-DE', { minimumFractionDigits: 3 })}</TableCell>
                        <TableCell className="text-right">{Number(row.co2e_kg).toLocaleString('de-DE', { minimumFractionDigits: 3 })}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  )
}
