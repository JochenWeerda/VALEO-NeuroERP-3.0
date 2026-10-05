/**
 * L3-Maske: Monatswerte für mehrere Monate / BWA für mehrere Monate
 * Referenz: Ribbon, Filter (Liste-Nr., Firma, Wirtschaftsjahr, Zeitraum), linke Liste, Grid (FIBU-Text, Jan–Dez, Gesamt), Fußleiste.
 */

import { useState, useMemo } from 'react'
import { useQueries } from '@tanstack/react-query'
import { Link } from '@/app/routing/typed-router'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  FileText,
  BarChart3,
  FileDown,
  RefreshCw,
  Sigma,
  Calendar,
  Search,
  FileSpreadsheet,
} from 'lucide-react'
import { financeService } from '@/lib/services/finance-service'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { NativeSelect } from '@/components/ui/native-select'
import { exportToCSV } from '@/lib/export-utils'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

function fmtVal(n: number, suffix: 'S' | 'H' = 'S'): string {
  const s = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)
  return `${s} ${suffix}`
}

type GridRow = { position: string; description: string; isTotal: boolean; months: number[]; total: number }
type MonatswerteExportRow = {
  position: string
  description: string
  total: number
} & Record<`m${number}`, number>

export default function MonatswertePage(): JSX.Element {
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const currentYear = new Date().getFullYear()
  const [listeNr, setListeNr] = useState('1301 - Standard-Abc')
  const [firma, setFirma] = useState('Musterstandart')
  const [wirtschaftsjahr, setWirtschaftsjahr] = useState(String(currentYear))
  const [zeitraumVon, setZeitraumVon] = useState('Januar')
  const [zeitraumBis, setZeitraumBis] = useState('Dezember')

  const monthIndices = useMemo(() => {
    const von = MONTHS.indexOf(zeitraumVon) >= 0 ? MONTHS.indexOf(zeitraumVon) : 0
    const bis = MONTHS.indexOf(zeitraumBis) >= 0 ? MONTHS.indexOf(zeitraumBis) : 11
    return Array.from({ length: bis - von + 1 }, (_, i) => von + i)
  }, [zeitraumVon, zeitraumBis])

  const bwaQueries = useQueries({
    queries: monthIndices.map((mi) => ({
      queryKey: ['fibu', 'bwa', wirtschaftsjahr, String(mi + 1).padStart(2, '0')],
      queryFn: () =>
        financeService.getBwa({
          period: `${wirtschaftsjahr}-${String(mi + 1).padStart(2, '0')}`,
        }),
      staleTime: 2 * 60 * 1000,
    })),
  })

  const isLoading = bwaQueries.some((q) => q.isLoading)
  const isError = bwaQueries.some((q) => q.isError)
  const refetch = (): void => {
    bwaQueries.forEach((q) => void q.refetch())
  }

  const gridRows = useMemo((): GridRow[] => {
    const first = bwaQueries[0]?.data
    if (!first?.items?.length) return []

    const rows: GridRow[] = []
    const monthData = bwaQueries.map((q) => q.data)
    first.items.forEach((item, idx) => {
      const months = monthIndices.map((_, dataIdx) => {
        const d = monthData[dataIdx]
        const row = d?.items?.[idx]
        return row ? Number(row.current_period) : 0
      })
      const total = months.reduce((a, b) => a + b, 0)
      rows.push({
        position: item.position,
        description: item.description,
        isTotal: idx === first.items.length - 1,
        months,
        total,
      })
    })
    return rows
  }, [bwaQueries, monthIndices])

  const displayedMonths = monthIndices.map((i) => MONTHS[i])
  const negativeRows = gridRows.filter((row) => row.total < 0).length
  const operationalStatus = normalizeOperationalStatus(
    isError ? 'eskaliert' : isLoading ? 'in_pruefung' : negativeRows > 0 ? 'wartet_auf_mensch' : gridRows.length > 0 ? 'abgeschlossen' : 'offen',
  )
  const contextSections = [
    {
      title: 'L3/FIBU-Kontext',
      items: [
        { label: 'Wirtschaftsjahr', value: wirtschaftsjahr },
        { label: 'Zeitraum', value: `${zeitraumVon} bis ${zeitraumBis}` },
        { label: 'Monate', value: `${displayedMonths.length}` },
      ],
    },
    {
      title: 'Auswertungslage',
      items: [
        { label: 'BWA-Zeilen', value: `${gridRows.length}` },
        { label: 'Negative Positionen', value: `${negativeRows}` },
        { label: 'Naechste Aktion', value: isError ? 'Filter pruefen und neu laden' : negativeRows > 0 ? 'Negative Positionen in Journal pruefen' : 'Auswertung exportieren oder Drilldown nutzen' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: isLoading ? 'Monatswerte werden geladen' : 'Monatswerte geladen',
      detail: isLoading
        ? 'Die ausgewaehlten Monate werden aus BWA-Daten zusammengestellt.'
        : `${gridRows.length} Positionen fuer ${displayedMonths.length} Monat(e) aufbereitet.`,
    },
    {
      label: isError ? 'Datenluecke erkannt' : 'Drilldown verfuegbar',
      detail: isError
        ? 'Fuer den gewaehlten Zeitraum liegen derzeit keine gueltigen Daten vor.'
        : 'Buchungsjournal, BWA und Bilanzpfade sind direkt aus dem Raum erreichbar.',
    },
  ]

  const handleAnwenden = (): void => {
    refetch()
    toast({ title: 'Filter', description: 'Monatswerte werden aktualisiert.' })
  }

  const handleExcel = (): void => {
    const cols: Array<{ key: keyof MonatswerteExportRow; label: string }> = [
      { key: 'position', label: 'Pos.' },
      { key: 'description', label: 'BWA Text' },
      ...displayedMonths.map((m, i) => ({ key: `m${i}` as keyof MonatswerteExportRow, label: m })),
      { key: 'total', label: 'Gesamt' },
    ]
    const rows: MonatswerteExportRow[] = gridRows.map((r) => ({
      position: r.position,
      description: r.description,
      ...(Object.fromEntries(displayedMonths.map((_, i) => [`m${i}`, r.months[i]])) as Record<`m${number}`, number>),
      total: r.total,
    }))
    try {
      exportToCSV(
        rows,
        `Monatswerte_${wirtschaftsjahr}_${listeNr.replace(/\s+/g, '-')}.csv`,
        cols
      )
      toast({ title: 'Export', description: 'Excel-Export gestartet.' })
    } catch (e) {
      toast({ title: 'Export fehlgeschlagen', description: String(e), variant: 'destructive' })
    }
  }

  const leftListItems = [
    'Sonstige Erlöse',
    'Erlösschmälerungen',
    'Skontoaufwand',
    'ERLÖSE GESAMT',
    'WARENEINSATZ GESAMT',
    'Übrige betriebl. Aufwendungen',
    'Zinserträge',
    'Zinsaufwendungen',
  ]

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Ribbon */}
      <div className="border-b bg-muted/30 shrink-0">
        <Tabs defaultValue="auswertungen" className="w-full">
          <TabsList className="w-full justify-start rounded-none h-12 bg-transparent border-0 gap-0 p-0">
            <TabsTrigger value="datei" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">DATEI</TabsTrigger>
            <TabsTrigger value="allgemein" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">ALLGEMEIN</TabsTrigger>
            <TabsTrigger value="offene-posten" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">OFFENE POSTEN</TabsTrigger>
            <TabsTrigger value="kostenrechnung" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">KOSTENRECHNUNG</TabsTrigger>
            <TabsTrigger value="schnittstellen" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">SCHNITTSTELLEN</TabsTrigger>
            <TabsTrigger value="abschluss" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">ABSCHLUSS</TabsTrigger>
            <TabsTrigger value="auswertungen" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">AUSWERTUNGEN</TabsTrigger>
            <TabsTrigger value="register" className="min-h-touch rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">REGISTER</TabsTrigger>
          </TabsList>
          <TabsContent value="auswertungen" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/buchungsjournal">
                <Button variant="ghost" className="min-h-touch gap-1.5"><Calendar className="h-4 w-4" /> Kontenauszüge</Button>
              </Link>
              <Link to="/fibu/buchungsjournal">
                <Button variant="ghost" className="min-h-touch gap-1.5"><FileText className="h-4 w-4" /> Buchungs-Journal</Button>
              </Link>
              <Link to="/fibu/buchungsjournal">
                <Button variant="ghost" className="min-h-touch gap-1.5"><Sigma className="h-4 w-4" /> Summen und Salden</Button>
              </Link>
              <Link to="/fibu/bwa">
                <Button variant="ghost" className="min-h-touch gap-1.5"><BarChart3 className="h-4 w-4" /> BWA</Button>
              </Link>
              <Link to="/fibu/bilanz">
                <Button variant="ghost" className="min-h-touch gap-1.5"><FileText className="h-4 w-4" /> Bilanz/GuV</Button>
              </Link>
              <Link to="/export/ustva">
                <Button variant="ghost" className="min-h-touch gap-1.5"><FileText className="h-4 w-4" /> USt-Voranmeldung</Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="abschluss" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/buchungsjournal"><Button variant="ghost" className="min-h-touch gap-1.5"><FileText className="h-4 w-4" /> Buchungs-Journal</Button></Link>
              <Link to="/fibu/bwa"><Button variant="ghost" className="min-h-touch gap-1.5"><BarChart3 className="h-4 w-4" /> BWA</Button></Link>
              <Link to="/fibu/bilanz"><Button variant="ghost" className="min-h-touch gap-1.5"><BarChart3 className="h-4 w-4" /> Bilanz/GuV</Button></Link>
            </div>
          </TabsContent>
          <TabsContent value="datei" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Button variant="ghost" className="min-h-touch gap-1.5" onClick={() => toast({ title: 'Export', description: 'Nutzen Sie Excel in der Fußleiste für den CSV-Export.' })}><FileDown className="h-4 w-4" /> Export</Button>
            </div>
          </TabsContent>
          <TabsContent value="allgemein" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Button variant="ghost" className="min-h-touch gap-1.5" onClick={() => toast({ title: 'Suche nicht angebunden', description: 'Monatswerte filtern über Liste-Nr., Firma und Zeitraum.' })}><Search className="h-4 w-4" /> Suchen</Button>
            </div>
          </TabsContent>
          <TabsContent value="offene-posten" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/offene-posten"><Button variant="ghost" className="min-h-touch gap-1.5">Offene Posten</Button></Link>
            </div>
          </TabsContent>
          <TabsContent value="schnittstellen" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/schnittstelle-fibu"><Button variant="ghost" className="min-h-touch gap-1.5"><FileDown className="h-4 w-4" /> Buchungsübergabe</Button></Link>
            </div>
          </TabsContent>
          <TabsContent value="kostenrechnung" className="mt-0 border-0 p-0" />
          <TabsContent value="register" className="mt-0 border-0 p-0" />
        </Tabs>
      </div>

      {/* Titel + Filter */}
      <div className="shrink-0 border-b bg-muted/20 px-4 py-2">
        <h1 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Monatswerte für mehrere Monate</h1>
      </div>
      <Card className="rounded-none border-x-0 border-t-0 shrink-0">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex items-center gap-2">
              <Label className="text-xs whitespace-nowrap">Liste-Nr.:</Label>
              <Input
                className="w-48 min-h-touch text-sm"
                value={listeNr}
                onChange={(e) => setListeNr(e.target.value)}
                list="liste-nr-list"
              />
              <datalist id="liste-nr-list">
                <option value="1301 - Standard-Abc" />
                <option value="1001 - Standard-BWA" />
                <option value="1001 - Standard-GuV" />
              </datalist>
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Firma:</Label>
              <Input className="w-40 min-h-touch text-sm" value={firma} onChange={(e) => setFirma(e.target.value)} />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Wirtschaftsjahr:</Label>
              <Input className="w-20 min-h-touch text-sm" type="number" value={wirtschaftsjahr} onChange={(e) => setWirtschaftsjahr(e.target.value)} aria-label="Wirtschaftsjahr" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Zeitraum:</Label>
              <NativeSelect
                ariaLabel="Zeitraum von"
                className="w-32"
                value={zeitraumVon}
                onChange={(e) => setZeitraumVon(e.target.value)}
              >
                {MONTHS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </NativeSelect>
              <span className="text-xs">bis</span>
              <NativeSelect
                ariaLabel="Zeitraum bis"
                className="w-32"
                value={zeitraumBis}
                onChange={(e) => setZeitraumBis(e.target.value)}
              >
                {MONTHS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </NativeSelect>
            </div>
            <Button onClick={handleAnwenden} disabled={isLoading} className="min-h-touch gap-1.5">
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Anwenden
            </Button>
          </div>
        </CardContent>
      </Card>

      {!isTouch ? (
      <div className="px-4 pb-4 space-y-4">
        <OperationalCaseHeader
          title="Monatswerte fuer mehrere Monate"
          description="Der Raum bildet den L3/FIBU-Auswertungsfall mit Zeitraum, Risikoindikatoren und naechster Aktion kompakt ab."
          status={operationalStatus}
          owner="FIBU / Controlling"
          blocker={isError ? 'Fuer den gewaehlten Zeitraum fehlen auswertbare Buchungsdaten.' : null}
          nextAction={isError ? 'Zeitraum anpassen und erneut laden' : negativeRows > 0 ? 'Negative Positionen im Journal pruefen' : 'Auswertung exportieren'}
          caseLabel="Vorgang: Monatswerte"
          tags={['L3', 'FIBU']}
        />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Auswertungsverlauf" items={timelineItems} />
          <OperationalContextPanel title="Monatswerte-Kontext" sections={contextSections} />
        </div>
      </div>
      ) : null}

      {/* Inhalt: linke Liste + Grid */}
      <div className="flex-1 min-h-0 flex overflow-hidden">
        <aside className="w-52 border-r bg-muted/20 shrink-0 overflow-y-auto py-2">
          <p className="px-3 text-xs font-semibold uppercase text-muted-foreground mb-2">Positionen</p>
          <ul className="space-y-0.5 text-sm">
            {leftListItems.map((item) => (
              <li key={item} className="px-3 py-1 hover:bg-muted/50 cursor-pointer truncate">
                {item}
              </li>
            ))}
          </ul>
        </aside>
        <div className="flex-1 min-w-0 overflow-auto p-4">
          <p className="text-xs font-semibold uppercase text-muted-foreground mb-2">Ergebnis</p>
          {isLoading && (
            <Skeleton className="h-64 w-full" />
          )}
          {isError && (
            <Card className="border-status-warning/40 bg-status-warning/10">
              <CardContent className="p-4 text-status-warning text-sm">
                Keine Daten für das gewählte Wirtschaftsjahr bzw. Zeitraum. Bitte Filter anpassen.
              </CardContent>
            </Card>
          )}
          {!isLoading && !isError && gridRows.length > 0 && (
            <div className="rounded-md border overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-muted/60">
                    <th className="text-left p-2 font-medium border-b w-12">Pos.</th>
                    <th className="text-left p-2 font-medium border-b min-w-[200px]">FIBU-Text / BWA Text</th>
                    {displayedMonths.map((m) => (
                      <th key={m} className="text-right p-2 font-medium border-b w-28">{m}</th>
                    ))}
                    <th className="text-right p-2 font-medium border-b w-28">Gesamt</th>
                  </tr>
                </thead>
                <tbody>
                  {gridRows.map((row, i) => (
                    <tr key={i} className={row.isTotal ? 'font-semibold bg-muted/30' : ''}>
                      <td className="p-2 border-b">{row.position}</td>
                      <td className="p-2 border-b">{row.description}</td>
                      {row.months.map((v, j) => (
                        <td key={j} className="text-right p-2 border-b tabular-nums">{fmtVal(v)}</td>
                      ))}
                      <td className="text-right p-2 border-b tabular-nums font-medium">{fmtVal(row.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Fußleiste */}
      <div className="border-t bg-muted/30 px-4 py-2 flex items-center gap-2 shrink-0">
        <Button variant="outline" className="min-h-touch" onClick={() => toast({ title: 'Drucker nicht angebunden', description: 'Druckereinrichtung ist in dieser Maske nicht verfügbar.' })}>Drucker einrichten</Button>
        <Button variant="outline" className="min-h-touch" onClick={() => toast({ title: 'Druck nicht angebunden', description: 'Nutzen Sie Excel für den Export oder das Browser-Druckfenster über Strg+P.' })}>Drucken</Button>
        <Button variant="outline" className="min-h-touch" onClick={() => toast({ title: 'Vorschau nicht angebunden', description: 'Eine Druckvorschau gibt es in Monatswerte nicht.' })}>Vorschau</Button>
        <Button variant="outline" onClick={handleExcel} className="min-h-touch gap-1.5">
          <FileSpreadsheet className="h-4 w-4" /> Excel
        </Button>
      </div>
    </div>
  )
}
