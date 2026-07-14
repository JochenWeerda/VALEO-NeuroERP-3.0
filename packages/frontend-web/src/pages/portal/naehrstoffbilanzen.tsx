/**
 * Kundenportal - Nährstoffbilanzen
 * 
 * Jahresübersichten der Nährstoffbilanzen zum Download als PDF
 */

import { useState } from 'react'
import {
  downloadSalesDeliverySustainabilityCsv,
  downloadSalesDeliverySustainabilityPdf,
  usePortalNaehrstoffbilanzen,
} from '@/lib/api/portal'
import { useSustainabilityProviders, useSustainabilityPsm } from '@/lib/api/sustainability'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { EmptyStateWithAction, NextActionPanel } from '@/components/workflow'
import { NativeSelect } from '@/components/ui/native-select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Download,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  Leaf,
  Droplets,
  Calendar,
  Info,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react'

interface NaehrstoffBilanz {
  jahr: number
  stickstoff: { zugang: number; abgang: number; saldo: number }
  phosphor: { zugang: number; abgang: number; saldo: number }
  kalium: { zugang: number; abgang: number; saldo: number }
  flaeche: number
  status: 'abgeschlossen' | 'vorlaeufig'
  dokument: string
}

interface SchlagBilanz {
  schlag: string
  kultur: string
  flaeche: number
  nZugang: number
  nAbgang: number
  nSaldo: number
  pZugang: number
  pAbgang: number
  pSaldo: number
}



// Gesetzliche Grenzwerte (kg N/ha im 3-Jahres-Durchschnitt)
const N_GRENZWERT = 50
const P_GRENZWERT = 10

export default function PortalNaehrstoffbilanzen() {
  const [selectedJahr, setSelectedJahr] = useState<string>(String(new Date().getFullYear()))
  const [psmInput, setPsmInput] = useState('')
  const [psmLookup, setPsmLookup] = useState<string | null>(null)
  const [exporting, setExporting] = useState<'csv' | 'pdf' | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)
  const { data: portalBilanzen = [], isLoading, isError, error, refetch } = usePortalNaehrstoffbilanzen()
  const { data: providers } = useSustainabilityProviders()
  const { data: psmResult, isFetching: isPsmLoading, isError: isPsmError, error: psmError } = useSustainabilityPsm(psmLookup)
  const currentYear = new Date().getFullYear()
  const bilanzen: NaehrstoffBilanz[] = portalBilanzen.length > 0
    ? [{
      jahr: currentYear,
      stickstoff: { zugang: 0, abgang: 0, saldo: Number((portalBilanzen.reduce((s, b) => s + b.n_saldo, 0) / portalBilanzen.length).toFixed(1)) },
      phosphor: { zugang: 0, abgang: 0, saldo: Number((portalBilanzen.reduce((s, b) => s + b.p_saldo, 0) / portalBilanzen.length).toFixed(1)) },
      kalium: { zugang: 0, abgang: 0, saldo: Number((portalBilanzen.reduce((s, b) => s + b.k_saldo, 0) / portalBilanzen.length).toFixed(1)) },
      flaeche: 0,
      status: 'vorlaeufig',
      dokument: `naehrstoffbilanz-${currentYear}.pdf`,
    }]
    : []
  const schlagBilanzen: SchlagBilanz[] = portalBilanzen.map((b) => ({
    schlag: b.schlag,
    kultur: b.kultur,
    flaeche: 0,
    nZugang: 0,
    nAbgang: 0,
    nSaldo: b.n_saldo,
    pZugang: 0,
    pAbgang: 0,
    pSaldo: b.p_saldo,
  }))

  const currentBilanz = bilanzen.find(b => b.jahr.toString() === selectedJahr)

  // 3-Jahres-Durchschnitt berechnen
  const dreiJahresDurchschnittN = bilanzen.slice(0, 3).reduce((sum, b) => sum + b.stickstoff.saldo, 0) / Math.min(bilanzen.length, 3)
  const dreiJahresDurchschnittP = bilanzen.slice(0, 3).reduce((sum, b) => sum + b.phosphor.saldo, 0) / Math.min(bilanzen.length, 3)

  const getSaldoColor = (saldo: number, grenzwert: number) => {
    if (saldo < 0) return 'text-blue-600'
    if (saldo > grenzwert * 0.8) return 'text-status-warning'
    if (saldo > grenzwert) return 'text-status-error'
    return 'text-status-success'
  }

  const getSaldoIcon = (saldo: number) => {
    if (saldo > 0) return <TrendingUp className="h-4 w-4" />
    if (saldo < 0) return <TrendingDown className="h-4 w-4" />
    return <Minus className="h-4 w-4" />
  }

  const selectedYearNumber = Number(selectedJahr) || currentYear
  const hasGrenzwertHinweis = dreiJahresDurchschnittN > N_GRENZWERT || dreiJahresDurchschnittP > P_GRENZWERT
  const nextBilanzAction = portalBilanzen.length === 0
    ? 'Noch keine Bilanzdaten vorhanden. Pruefen Sie Feldbuch und Lieferdaten oder laden Sie spaeter erneut.'
    : hasGrenzwertHinweis
      ? 'Grenzwert-Hinweis pruefen und die betroffenen Schlaege in der Uebersicht kontrollieren.'
      : 'Bilanz fuer Ihre Unterlagen als PDF herunterladen oder die schlagbezogene Uebersicht pruefen.'

  const onDownload = async (format: 'csv' | 'pdf', year?: number) => {
    setExportError(null)
    setExporting(format)
    const targetYear = year ?? selectedYearNumber
    try {
      if (format === 'csv') {
        await downloadSalesDeliverySustainabilityCsv(targetYear)
      } else {
        await downloadSalesDeliverySustainabilityPdf(targetYear)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Export fehlgeschlagen'
      setExportError(message)
    } finally {
      setExporting(null)
    }
  }

  if (isLoading) {
    return <NaehrstoffbilanzenSkeleton />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Nährstoffbilanzen</h1>
          <p className="text-muted-foreground">Jahresübersichten gemäß Düngeverordnung</p>
        </div>
        <NativeSelect
          value={selectedJahr}
          onValueChange={setSelectedJahr}
          ariaLabel="Jahr waehlen"
          placeholder="Jahr waehlen"
          options={bilanzen.map((b) => ({ value: b.jahr.toString(), label: String(b.jahr) }))}
        />
      </div>

      <NextActionPanel
        title="Naechster sinnvoller Schritt"
        action={nextBilanzAction}
        tone={hasGrenzwertHinweis ? 'amber' : portalBilanzen.length === 0 ? 'blue' : 'emerald'}
      />

      <Card>
        <CardHeader>
          <CardTitle>Runtime Nachhaltigkeitsquellen</CardTitle>
          <CardDescription>PSM live via BVL, CO₂ via Climatiq (wenn konfiguriert), Nährstoffdaten via FAOSTAT</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {exportError && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Export fehlgeschlagen</AlertTitle>
              <AlertDescription>{exportError}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={providers?.providers.bvl_psm.configured ? 'default' : 'destructive'}>
              BVL {providers?.providers.bvl_psm.configured ? 'aktiv' : 'inaktiv'}
            </Badge>
            <Badge variant={providers?.providers.climatiq.configured ? 'default' : 'secondary'}>
              Climatiq {providers?.providers.climatiq.configured ? 'aktiv' : 'nicht konfiguriert'}
            </Badge>
            <Badge variant={providers?.providers.faostat.configured ? 'default' : 'destructive'}>
              FAOSTAT {providers?.providers.faostat.configured ? 'aktiv' : 'inaktiv'}
            </Badge>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              placeholder="BVL Zulassungsnummer (z. B. 024567-00)"
              value={psmInput}
              onChange={(e) => setPsmInput(e.target.value)}
            />
            <Button
              variant="outline"
              disabled={!psmInput.trim() || isPsmLoading}
              onClick={() => setPsmLookup(psmInput.trim())}
            >
              {isPsmLoading ? 'Suche läuft...' : 'PSM live prüfen'}
            </Button>
          </div>

          {isPsmError && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>PSM-Lookup fehlgeschlagen</AlertTitle>
              <AlertDescription>{(psmError as Error).message}</AlertDescription>
            </Alert>
          )}

          {psmResult && (
            <div className="rounded-lg border p-3 text-sm">
              <div className="font-medium">{String(psmResult.item.mittelname ?? psmResult.item.kennr ?? psmResult.zulassungsnummer)}</div>
              <div className="text-muted-foreground">ZNR: {String(psmResult.item.kennr ?? psmResult.zulassungsnummer)}</div>
              <div className="text-muted-foreground">Wirkstoff/Bezug: {String(psmResult.item.versuchsbez ?? '-')}</div>
              <div className="text-muted-foreground">Zulassung Ende: {String(psmResult.item.zul_ende ?? '-')}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compliance Alert */}
      {dreiJahresDurchschnittN > N_GRENZWERT || dreiJahresDurchschnittP > P_GRENZWERT ? (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Grenzwertüberschreitung</AlertTitle>
          <AlertDescription>
            Der 3-Jahres-Durchschnitt überschreitet die gesetzlichen Grenzwerte. 
            Bitte beachten Sie die Düngeverordnung.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-emerald-200 bg-emerald-50">
          <CheckCircle2 className="h-4 w-4 text-status-success" />
          <AlertTitle className="text-emerald-800">Grenzwerte eingehalten</AlertTitle>
          <AlertDescription className="text-emerald-700">
            Der 3-Jahres-Durchschnitt liegt innerhalb der gesetzlichen Grenzwerte.
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      {currentBilanz && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                    <Droplets className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">N-Saldo {selectedJahr}</p>
                    <p className={`text-2xl font-bold ${getSaldoColor(currentBilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                      {currentBilanz.stickstoff.saldo > 0 ? '+' : ''}{currentBilanz.stickstoff.saldo} kg/ha
                    </p>
                  </div>
                </div>
                {getSaldoIcon(currentBilanz.stickstoff.saldo)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-amber-100 p-2 text-status-warning">
                    <Leaf className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">P-Saldo {selectedJahr}</p>
                    <p className={`text-2xl font-bold ${getSaldoColor(currentBilanz.phosphor.saldo, P_GRENZWERT)}`}>
                      {currentBilanz.phosphor.saldo > 0 ? '+' : ''}{currentBilanz.phosphor.saldo} kg/ha
                    </p>
                  </div>
                </div>
                {getSaldoIcon(currentBilanz.phosphor.saldo)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                  <BarChart3 className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">3-J. Ø Stickstoff</p>
                  <p className={`text-2xl font-bold ${getSaldoColor(dreiJahresDurchschnittN, N_GRENZWERT)}`}>
                    {dreiJahresDurchschnittN > 0 ? '+' : ''}{dreiJahresDurchschnittN.toFixed(1)} kg/ha
                  </p>
                </div>
              </div>
              <Progress 
                value={Math.min((dreiJahresDurchschnittN / N_GRENZWERT) * 100, 100)} 
                className="mt-2 h-2"
              />
              <p className="text-xs text-muted-foreground mt-1">Grenzwert: {N_GRENZWERT} kg/ha</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-emerald-100 p-2 text-status-success">
                  <Calendar className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Fläche {selectedJahr}</p>
                  <p className="text-2xl font-bold">{currentBilanz.flaeche} ha</p>
                </div>
              </div>
              <Badge 
                className={`mt-2 ${currentBilanz.status === 'abgeschlossen' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}
              >
                {currentBilanz.status === 'abgeschlossen' ? 'Abgeschlossen' : 'Vorläufig'}
              </Badge>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detaillierte Bilanz */}
      {currentBilanz && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Nährstoffbilanz {selectedJahr}</CardTitle>
              <CardDescription>Detaillierte Übersicht in kg/ha</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                className="gap-2"
                disabled={exporting !== null}
                onClick={() => { void onDownload('csv') }}
              >
                <Download className="h-4 w-4" />
                {exporting === 'csv' ? 'CSV wird erstellt...' : 'CSV'}
              </Button>
              <Button
                className="gap-2"
                disabled={exporting !== null}
                onClick={() => { void onDownload('pdf') }}
              >
                <Download className="h-4 w-4" />
                {exporting === 'pdf' ? 'PDF wird erstellt...' : 'PDF herunterladen'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nährstoff</TableHead>
                  <TableHead className="text-right">Zugang</TableHead>
                  <TableHead className="text-right">Abgang</TableHead>
                  <TableHead className="text-right">Saldo</TableHead>
                  <TableHead className="text-right">Grenzwert</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Stickstoff (N)</TableCell>
                  <TableCell className="text-right">{currentBilanz.stickstoff.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.stickstoff.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${getSaldoColor(currentBilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                    {currentBilanz.stickstoff.saldo > 0 ? '+' : ''}{currentBilanz.stickstoff.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right">{N_GRENZWERT} kg/ha (3-J.Ø)</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Phosphor (P₂O₅)</TableCell>
                  <TableCell className="text-right">{currentBilanz.phosphor.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.phosphor.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${getSaldoColor(currentBilanz.phosphor.saldo, P_GRENZWERT)}`}>
                    {currentBilanz.phosphor.saldo > 0 ? '+' : ''}{currentBilanz.phosphor.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right">{P_GRENZWERT} kg/ha (3-J.Ø)</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Kalium (K₂O)</TableCell>
                  <TableCell className="text-right">{currentBilanz.kalium.zugang} kg/ha</TableCell>
                  <TableCell className="text-right">{currentBilanz.kalium.abgang} kg/ha</TableCell>
                  <TableCell className={`text-right font-bold ${currentBilanz.kalium.saldo < 0 ? 'text-blue-600' : 'text-status-success'}`}>
                    {currentBilanz.kalium.saldo > 0 ? '+' : ''}{currentBilanz.kalium.saldo} kg/ha
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">-</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Schlagbezogene Bilanz */}
      <Card>
        <CardHeader>
          <CardTitle>Schlagbezogene Übersicht {selectedJahr}</CardTitle>
          <CardDescription>Nährstoffsalden je Schlag in kg/ha</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Schlag</TableHead>
                <TableHead>Kultur</TableHead>
                <TableHead className="text-right">Fläche</TableHead>
                <TableHead className="text-right">N-Saldo</TableHead>
                <TableHead className="text-right">P-Saldo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {schlagBilanzen.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="py-8">
                    <EmptyStateWithAction
                      title="Noch keine schlagbezogenen Bilanzdaten"
                      description="Sobald Feldbuch- oder Lieferdaten vorhanden sind, sehen Sie hier die Salden je Schlag."
                    />
                  </TableCell>
                </TableRow>
              ) : schlagBilanzen.map((sb) => (
                <TableRow key={sb.schlag}>
                  <TableCell className="font-medium">{sb.schlag}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{sb.kultur}</Badge>
                  </TableCell>
                  <TableCell className="text-right">{sb.flaeche} ha</TableCell>
                  <TableCell className={`text-right font-medium ${getSaldoColor(sb.nSaldo, N_GRENZWERT)}`}>
                    {sb.nSaldo > 0 ? '+' : ''}{sb.nSaldo}
                  </TableCell>
                  <TableCell className={`text-right font-medium ${getSaldoColor(sb.pSaldo, P_GRENZWERT)}`}>
                    {sb.pSaldo > 0 ? '+' : ''}{sb.pSaldo}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Historische Bilanzen */}
      <Card>
        <CardHeader>
          <CardTitle>Historische Bilanzen</CardTitle>
          <CardDescription>Alle verfügbaren Jahresbilanzen</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            {bilanzen.map((bilanz) => (
              <Card key={bilanz.jahr} className="transition-all hover:shadow-md">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-lg font-bold">{bilanz.jahr}</span>
                    <Badge 
                      className={bilanz.status === 'abgeschlossen' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}
                    >
                      {bilanz.status === 'abgeschlossen' ? 'Abgeschlossen' : 'Vorläufig'}
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">N-Saldo:</span>
                      <span className={`font-medium ${getSaldoColor(bilanz.stickstoff.saldo, N_GRENZWERT)}`}>
                        {bilanz.stickstoff.saldo > 0 ? '+' : ''}{bilanz.stickstoff.saldo} kg/ha
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">P-Saldo:</span>
                      <span className={`font-medium ${getSaldoColor(bilanz.phosphor.saldo, P_GRENZWERT)}`}>
                        {bilanz.phosphor.saldo > 0 ? '+' : ''}{bilanz.phosphor.saldo} kg/ha
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Fläche:</span>
                      <span className="font-medium">{bilanz.flaeche} ha</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-3 gap-2"
                    disabled={exporting !== null}
                    onClick={() => {
                      setSelectedJahr(String(bilanz.jahr))
                      void onDownload('pdf', bilanz.jahr)
                    }}
                  >
                    <Download className="h-4 w-4" />
                    {exporting === 'pdf' ? 'PDF wird erstellt...' : 'PDF'}
                  </Button>
                </CardContent>
              </Card>
            ))}
            {bilanzen.length === 0 && (
              <EmptyStateWithAction
                title="Noch keine Jahresbilanz"
                description="Fuer das gewaehlte Jahr liegen noch keine zusammengefassten Naehrstoffdaten vor."
              />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Info */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Hinweis zur Düngeverordnung</AlertTitle>
        <AlertDescription>
          Die Nährstoffbilanzen werden gemäß DüV erstellt. Der 3-Jahres-Durchschnitt für Stickstoff 
          darf 50 kg N/ha und für Phosphor 10 kg P₂O₅/ha nicht überschreiten.
        </AlertDescription>
      </Alert>
    </div>
  )
}

function NaehrstoffbilanzenSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-10 w-[150px]" />
      </div>
      <Skeleton className="h-20 w-full" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-16 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}



