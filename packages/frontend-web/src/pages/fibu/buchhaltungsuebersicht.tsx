/**
 * Buchhaltungsübersicht – FIBU-Maske mit Ribbon, Filtern und Bilanz-/GuV-Grid
 * Entspricht der Referenz: Ribbon, Kopfbereich (Filter), Haupt-Grid (hierarchisch), Detail-Grid, Fußleiste.
 * Systemweit wird kein produktbezogener Markenname verwendet; Bezeichnungen sind neutral (FIBU, Buchhaltung, ASC-Export).
 */

import { useState, useMemo } from 'react'
import { useQueries } from '@tanstack/react-query'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  FileText,
  BarChart3,
  FileDown,
  Printer,
  RefreshCw,
  Sigma,
  Settings,
  HelpCircle,
  LayoutGrid,
  FolderOpen,
  Calculator,
  ArrowLeftRight,
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { financeService, type BalanceSheetItem } from '@/lib/services/finance-service'
import { useToast } from '@/hooks/use-toast'
import { exportToCSV } from '@/lib/export-utils'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

function fmtNum(n: number): string {
  return new Intl.NumberFormat('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)
}

// Hierarchische Zeile für Haupt-Grid
type GridRow = {
  id: string
  label: string
  level: number
  summeJahr: number
  summeVorjahr: number
  months: number[]
}

type BilanzSlice = { assets: BalanceSheetItem[]; equity: BalanceSheetItem[]; liabilities: BalanceSheetItem[] }

/** Erzeugt Monatswerte pro Spalte aus 12 Bilanz-Perioden (Index 0 = Januar … 11 = Dezember). */
function buildHierarchyRows(bilanzPerMonth: (null | BilanzSlice)[]): GridRow[] {
  const getSum = (b: null | BilanzSlice, key: keyof BilanzSlice) =>
    b ? b[key].reduce((s: number, x: BalanceSheetItem) => s + Number(x.balance), 0) : 0

  const rows: GridRow[] = []
  let id = 0
  const add = (label: string, level: number, summeJahrVal: number, summeVorjahr = 0, monthVals: number[] = []): void => {
    rows.push({
      id: `r-${++id}`,
      label,
      level,
      summeJahr: summeJahrVal,
      summeVorjahr,
      months: monthVals.length === 12 ? monthVals : Array(12).fill(0),
    })
  }

  const assetMonths = bilanzPerMonth.map((b) => getSum(b, 'assets'))
  const assetSum = assetMonths.reduce((a, b) => a + b, 0)
  add('I. Forderungen und sonstige Vermögensgegenstände', 0, 0, 0)
  add('Sonstige Vermögensgegenstände', 1, 0, 0)
  add('Forderungen aus Lieferung und Leistung', 1, assetSum, 0, assetMonths)
  add('Schecks, Kassen-, Bankguthaben', 1, 0, 0)
  add('C. Rechnungsabgrenzungsposten', 0, 0, 0)
  add('Rechnungsabgrenzungsposten', 1, 0, 0)
  add('PASSIVA', 0, 0, 0)
  add('A. EIGENKAPITAL', 0, 0, 0)
  add('I. Kapital', 1, 0, 0)
  const first = bilanzPerMonth.find((b): b is BilanzSlice => b != null)
  first?.equity.forEach((e) => {
    const m = bilanzPerMonth.map((b) => (b ? b.equity.find((x) => x.account_number === e.account_number) : null))
    const vals = m.map((x) => (x ? Number(x.balance) : 0))
    add(e.account_name, 1, vals.reduce((a, b) => a + b, 0), 0, vals)
  })
  add('Gewinn oder Verlust', 1, 0, 0)
  add('B. RÜCKSTELLUNGEN', 0, 0, 0)
  add('Rückstellungen', 1, 0, 0)
  add('C. VERBINDLICHKEITEN', 0, 0, 0)
  add('Verbindlichkeiten aus Lieferung und Leistungen', 1, 0, 0)
  add('Verbindlichkeiten LuL mit Restlaufzeit bis 1 Jahr', 1, 0, 0)
  first?.liabilities.forEach((l) => {
    const m = bilanzPerMonth.map((b) => (b ? b.liabilities.find((x) => x.account_number === l.account_number) : null))
    const vals = m.map((x) => (x ? Number(x.balance) : 0))
    add(l.account_name, 1, vals.reduce((a, b) => a + b, 0), 0, vals)
  })
  return rows
}

export default function BuchhaltungsuebersichtPage(): JSX.Element {
  const { toast } = useToast()
  const navigate = useNavigate()
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth()
  const [jahr] = useState(String(currentYear))
  const [monatVon, setMonatVon] = useState('1')
  const [monatBis, setMonatBis] = useState('12')
  const [bilanzStichtag, setBilanzStichtag] = useState(() => {
    const d = new Date(currentYear, 11, 31)
    return d.toISOString().split('T')[0]
  })
  const [abschlussart, setAbschlussart] = useState('100')
  const [abschlussartLabel, setAbschlussartLabel] = useState('Standard-Bilanz')
  const [firma, setFirma] = useState('1 – Muster Firma')
  const [schnittstelle, setSchnittstelle] = useState('FIBU-Schnittstelle (ASC-Export)')
  const [nurBuchungenMitMwSt, setNurBuchungenMitMwSt] = useState(false)
  const [buchungenAnzeigen, setBuchungenAnzeigen] = useState(true)
  const [alleMonateAnzeigen, setAlleMonateAnzeigen] = useState(true)
  const [auswertungsDatum] = useState(() =>
    new Date().toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
  )

  const monthQueries = useQueries({
    queries: Array.from({ length: 12 }, (_, i) => ({
      queryKey: ['fibu', 'bilanz', jahr, String(i + 1).padStart(2, '0')],
      queryFn: () => financeService.getBilanz({ period: `${jahr}-${String(i + 1).padStart(2, '0')}` }),
      staleTime: 2 * 60 * 1000,
    })),
  })
  const bilanzPerMonth = monthQueries.map((q) => q.data ?? null)
  const isLoading = monthQueries.some((q) => q.isLoading)
  const isError = monthQueries.some((q) => q.isError)
  const refetch = (): void => { monthQueries.forEach((q) => void q.refetch()) }
  const bilanz = bilanzPerMonth[currentMonth] ?? bilanzPerMonth[11] ?? null

  const gridRows = useMemo(
    () => (bilanzPerMonth.some(Boolean) ? buildHierarchyRows(bilanzPerMonth) : []),
    [bilanzPerMonth]
  )
  const footerSums = useMemo(() => {
    if (!gridRows.length) return { summeJahr: 0, summeVorjahr: 0, months: Array(12).fill(0) }
    return gridRows.reduce(
      (acc, r) => ({
        summeJahr: acc.summeJahr + r.summeJahr,
        summeVorjahr: acc.summeVorjahr + r.summeVorjahr,
        months: r.months.map((v, i) => acc.months[i] + v),
      }),
      { summeJahr: 0, summeVorjahr: 0, months: Array(12).fill(0) as number[] }
    )
  }, [gridRows])
  const detailRows: { firma: string; sachkonto: string; bezeichnung: string; summeJahr: number; months: number[] }[] = []
  const negativeMonths = footerSums.months.filter((value) => value < 0).length
  const operationalStatus = normalizeOperationalStatus(
    isError ? 'eskaliert' : isLoading ? 'in_pruefung' : negativeMonths > 0 ? 'wartet_auf_mensch' : gridRows.length > 0 ? 'abgeschlossen' : 'offen',
  )
  const contextSections = [
    {
      title: 'Periodenlage',
      items: [
        { label: 'Firma', value: firma },
        { label: 'Bilanzstichtag', value: bilanzStichtag },
        { label: 'Monatsfenster', value: `${monatVon} bis ${monatBis}` },
      ],
    },
    {
      title: 'Revisionslage',
      items: [
        { label: 'Schnittstelle', value: schnittstelle },
        { label: 'Negative Monate', value: `${negativeMonths}` },
        { label: 'Naechste Aktion', value: negativeMonths > 0 ? 'Journal und Umbuchungen fuer Negativmonate pruefen' : 'Auswertung exportieren oder Drilldown nutzen' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: isLoading ? 'Bilanzdaten werden geladen' : 'Auswertung aufgebaut',
      detail: isLoading
        ? 'Die Bilanz- und GuV-Sicht wird fuer die gewaehlte Periode neu berechnet.'
        : `${gridRows.length} Hierarchiezeilen stehen fuer Drilldown und Export bereit.`,
    },
    {
      label: negativeMonths > 0 ? 'Abweichende Monatslagen erkannt' : 'Keine kritische Monatslage',
      detail: negativeMonths > 0
        ? `${negativeMonths} Monatswerte liegen unter Null und sollten vor Abschluss oder Export geprueft werden.`
        : 'Die aktuelle Uebersicht zeigt keine kritischen Monatsabweichungen.',
    },
  ]

  const handleDrilldown = (monthIndex: number): void => {
    const period = `${jahr}-${String(monthIndex + 1).padStart(2, '0')}`
    navigate(`/fibu/buchungsjournal?period=${period}`)
  }

  const handleJetztAuswerten = (): void => {
    void refetch()
    toast({ title: 'Auswertung', description: 'Buchhaltungsübersicht wird aktualisiert.' })
  }

  const handleDrucken = (): void => {
    window.print()
  }

  const handleExcel = (): void => {
    if (!bilanz) return
    const rows = [
      ...bilanz.assets.map((a) => ({ Beschreibung: a.account_name, 'Summe Jahr': Number(a.balance), Typ: 'Aktiva' })),
      ...bilanz.equity.map((e) => ({ Beschreibung: e.account_name, 'Summe Jahr': Number(e.balance), Typ: 'Eigenkapital' })),
      ...bilanz.liabilities.map((l) => ({ Beschreibung: l.account_name, 'Summe Jahr': Number(l.balance), Typ: 'Passiva' })),
    ]
    try {
      exportToCSV(
        rows,
        `Buchhaltungsuebersicht_${jahr}_${auswertungsDatum.replace(/[.\s:]/g, '-')}.csv`,
        [{ key: 'Beschreibung', label: 'Beschreibung' }, { key: 'Summe Jahr', label: 'Summe Jahr' }, { key: 'Typ', label: 'Typ' }]
      )
      toast({ title: 'Export', description: 'Excel-Export gestartet.' })
    } catch (e) {
      toast({ title: 'Export fehlgeschlagen', description: String(e), variant: 'destructive' })
    }
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Ribbon */}
      <div className="border-b bg-muted/30 shrink-0">
        <Tabs defaultValue="auswertungen" className="w-full">
          <TabsList className="w-full justify-start rounded-none h-12 bg-transparent border-0 gap-0 p-0">
            <TabsTrigger value="datei" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">DATEI</TabsTrigger>
            <TabsTrigger value="allgemein" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">ALLGEMEIN</TabsTrigger>
            <TabsTrigger value="postbearbeitung" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">POSTBEARBEITUNG</TabsTrigger>
            <TabsTrigger value="schnittstellen" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">SCHNITTSTELLEN</TabsTrigger>
            <TabsTrigger value="abschluss" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">ABSCHLUSS</TabsTrigger>
            <TabsTrigger value="auswertungen" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">AUSWERTUNGEN</TabsTrigger>
            <TabsTrigger value="fenster" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-background px-4">FENSTER</TabsTrigger>
          </TabsList>
          <TabsContent value="auswertungen" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Button variant="ghost" size="sm" className="gap-1.5" onClick={handleDrucken}>
                <Printer className="h-4 w-4" /> Drucken
              </Button>
              <Button variant="ghost" size="sm" className="gap-1.5" onClick={handleExcel}>
                <FileDown className="h-4 w-4" /> Exportieren
              </Button>
              <Link to="/fibu/buchungsjournal">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <Sigma className="h-4 w-4" /> Summen und Salden
                </Button>
              </Link>
              <Button variant="ghost" size="sm" className="gap-1.5">
                <HelpCircle className="h-4 w-4" /> Hilfebildschirm
              </Button>
              <Link to="/fibu/bwa">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <BarChart3 className="h-4 w-4" /> BWA
                </Button>
              </Link>
              <Link to="/fibu/bilanz">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <FileText className="h-4 w-4" /> Bilanz/GuV
                </Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="schnittstellen" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/schnittstelle-fibu">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <FileDown className="h-4 w-4" /> Buchungsübergabe (ASC)
                </Button>
              </Link>
              <Link to="/fibu/schnittstelle-fibu">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <LayoutGrid className="h-4 w-4" /> Schnittstelle FIBU
                </Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="datei" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/schnittstellen-center">
                <Button variant="ghost" size="sm" className="gap-1.5"><FolderOpen className="h-4 w-4" /> Laden</Button>
              </Link>
              <Button variant="ghost" size="sm" className="gap-1.5" onClick={handleExcel}><FileDown className="h-4 w-4" /> Export</Button>
            </div>
          </TabsContent>
          <TabsContent value="allgemein" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/schnittstellen-center">
                <Button variant="ghost" size="sm" className="gap-1.5"><Settings className="h-4 w-4" /> Einstellungen</Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="postbearbeitung" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/buchungsjournal">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <Sigma className="h-4 w-4" /> Summen und Salden
                </Button>
              </Link>
              <Link to="/finance/buchungserfassung">
                <Button variant="ghost" size="sm" className="gap-1.5"><ArrowLeftRight className="h-4 w-4" /> Umbuchen</Button>
              </Link>
              <Link to="/fibu/bwa">
                <Button variant="ghost" size="sm" className="gap-1.5"><Calculator className="h-4 w-4" /> Deckungsbeitrag Monat</Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="abschluss" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/abschluss-cockpit">
                <Button variant="ghost" size="sm" className="gap-1.5"><FileText className="h-4 w-4" /> Abschlussbuchung</Button>
              </Link>
            </div>
          </TabsContent>
          <TabsContent value="fenster" className="mt-0 border-0 p-0">
            <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-muted/20">
              <Link to="/fibu/monatswerte">
                <Button variant="ghost" size="sm" className="gap-1.5">Fenster anordnen</Button>
              </Link>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Kopfbereich / Filter */}
      <div className="p-4 pb-0">
        <OperationalCaseHeader
          title="Buchhaltungsuebersicht"
          description="Das L3/FIBU-Cockpit zeigt Periodenlage, Revisionskontext und naechste Folgeaktion direkt ueber der Auswertung."
          status={operationalStatus}
          owner="Finanzbuchhaltung"
          blocker={negativeMonths > 0 ? `${negativeMonths} Monate zeigen eine kritische Lage fuer Review oder Umbuchung.` : null}
          nextAction={negativeMonths > 0 ? 'Negativmonate im Journal pruefen und Umbuchungspfad nutzen' : 'Auswertung exportieren oder in Journal/BWA drillen'}
          caseLabel="Vorgang: FIBU-Uebersicht"
          tags={['FIBU', 'L3', 'Periodenabschluss']}
        />
        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Auswertungsverlauf" items={timelineItems} />
          <OperationalContextPanel title="Buchhaltungskontext" sections={contextSections} />
        </div>
      </div>
      <Card className="rounded-none border-x-0 border-t-0 shrink-0">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-4 gap-y-2">
                <div className="flex items-center gap-2">
                  <Label className="text-xs whitespace-nowrap">Abschlussart:</Label>
                  <Input className="w-16 h-8 text-sm" value={abschlussart} onChange={(e) => setAbschlussart(e.target.value)} />
                  <Input className="w-36 h-8 text-sm" value={abschlussartLabel} onChange={(e) => setAbschlussartLabel(e.target.value)} />
                </div>
                <div className="flex items-center gap-2">
                  <Label className="text-xs whitespace-nowrap">Bilanzstichtag:</Label>
                  <Input type="date" className="w-36 h-8 text-sm" value={bilanzStichtag} onChange={(e) => setBilanzStichtag(e.target.value)} />
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-4 gap-y-2">
                <div className="flex items-center gap-2">
                  <Label className="text-xs">Monat von/bis:</Label>
                  <Input className="w-12 h-8 text-sm" value={monatVon} onChange={(e) => setMonatVon(e.target.value)} />
                  <span className="text-xs">bis</span>
                  <Input className="w-12 h-8 text-sm" value={monatBis} onChange={(e) => setMonatBis(e.target.value)} />
                </div>
                <div className="flex items-center gap-2">
                  <Label className="text-xs">Auswertungs-Zeitraum:</Label>
                  <span className="text-sm">{jahr} bis {MONTHS[parseInt(monatBis, 10) - 1] ?? 'Dezember'}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Label className="text-xs">Firma:</Label>
                <Input className="max-w-xs h-8 text-sm" value={firma} onChange={(e) => setFirma(e.target.value)} />
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Label className="text-xs whitespace-nowrap">Berichtsfirma / Schnittstelle:</Label>
                <Input className="max-w-xs h-8 text-sm" value={schnittstelle} onChange={(e) => setSchnittstelle(e.target.value)} list="schnittstelle-list" />
                <datalist id="schnittstelle-list">
                  <option value="FIBU-Schnittstelle (ASC-Export)" />
                  <option value="Buchungsübergabe ASC" />
                </datalist>
              </div>
              <div className="flex flex-wrap items-center gap-4">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <Checkbox checked={nurBuchungenMitMwSt} onCheckedChange={(c) => setNurBuchungenMitMwSt(!!c)} />
                  Nur Buchungen mit MWSt oder freige.
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <Checkbox checked={buchungenAnzeigen} onCheckedChange={(c) => setBuchungenAnzeigen(!!c)} />
                  Buchungen anzeigen
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <Checkbox checked={alleMonateAnzeigen} onCheckedChange={(c) => setAlleMonateAnzeigen(!!c)} />
                  Alle Monate anzeigen
                </label>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-xs text-muted-foreground">Auswertungs-Datum: {auswertungsDatum} Uhr</span>
                <Button size="sm" onClick={handleJetztAuswerten} disabled={isLoading} className="gap-1.5">
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                  Jetzt auswerten
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Haupt-Grid + Detail-Grid mit linker Nav (BWA/Konten) */}
      <div className="flex flex-1 min-h-0">
        <nav className="w-52 shrink-0 border-r bg-muted/20 flex flex-col gap-1 p-2">
          <span className="text-xs font-semibold text-muted-foreground px-2 py-1">Auswertungen</span>
          <Link to="/fibu/buchhaltungsuebersicht">
            <Button variant="default" size="sm" className="w-full justify-start gap-2">
              <FileText className="h-4 w-4" /> Buchhaltungsübersicht
            </Button>
          </Link>
          <Link to="/fibu/monatswerte">
            <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
              <BarChart3 className="h-4 w-4" /> Monatswerte
            </Button>
          </Link>
          <Link to="/fibu/bwa">
            <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
              <BarChart3 className="h-4 w-4" /> BWA
            </Button>
          </Link>
          <Link to="/fibu/bilanz">
            <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
              <FileText className="h-4 w-4" /> Bilanz
            </Button>
          </Link>
          <Link to="/fibu/guv">
            <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
              <FileText className="h-4 w-4" /> GuV
            </Button>
          </Link>
          <Link to="/fibu/buchungsjournal">
            <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
              <Sigma className="h-4 w-4" /> Summen und Salden
            </Button>
          </Link>
        </nav>
        <div className="flex-1 min-h-0 overflow-auto p-4">
        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        )}
        {isError && (
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="p-4 text-amber-800 text-sm">
              Keine Bilanzdaten für die gewählte Periode. Bitte Buchungen erfassen oder andere Parameter wählen.
            </CardContent>
          </Card>
        )}
        {!isLoading && !isError && bilanz && (
          <div className="space-y-4">
            {/* Haupt-Grid: hierarchische Bilanz/GuV mit sticky Spalten und Drilldown */}
            <div className="rounded-md border overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-muted/50">
                    <th className="text-left p-2 font-medium border-b sticky left-0 z-10 bg-muted/50 min-w-[220px] shadow-[2px_0_4px_-2px_rgba(0,0,0,0.1)]">Beschreibung</th>
                    <th className="text-right p-2 font-medium border-b w-28">Summe Jahr</th>
                    <th className="text-right p-2 font-medium border-b w-28">Summe Vorjahr</th>
                    {alleMonateAnzeigen && MONTHS.map((m) => (
                      <th key={m} className="text-right p-2 font-medium border-b w-24">{m}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {gridRows.map((row) => (
                    <tr key={row.id} className={row.level === 0 ? 'font-semibold bg-muted/30' : ''}>
                      <td className="p-2 border-b sticky left-0 z-10 bg-background min-w-[220px] shadow-[2px_0_4px_-2px_rgba(0,0,0,0.08)]" style={{ paddingLeft: `${12 + row.level * 16}px` }}>{row.label}</td>
                      <td className="text-right p-2 border-b tabular-nums w-28">{fmtNum(row.summeJahr)}</td>
                      <td className="text-right p-2 border-b tabular-nums w-28">{fmtNum(row.summeVorjahr)}</td>
                      {alleMonateAnzeigen && row.months.map((v, i) => (
                        <td
                          key={i}
                          className="text-right p-2 border-b tabular-nums cursor-pointer hover:bg-muted/50 w-24"
                          onClick={() => handleDrilldown(i)}
                          title={`Drilldown: Journal ${MONTHS[i]} ${jahr}`}
                        >
                          {fmtNum(v)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="font-semibold bg-muted/50 border-t-2">
                    <td className="p-2 sticky left-0 z-10 bg-muted/50 min-w-[220px] shadow-[2px_0_4px_-2px_rgba(0,0,0,0.1)]">Summe</td>
                    <td className="text-right p-2 tabular-nums">{fmtNum(footerSums.summeJahr)}</td>
                    <td className="text-right p-2 tabular-nums">{fmtNum(footerSums.summeVorjahr)}</td>
                    {alleMonateAnzeigen && footerSums.months.map((v, i) => (
                      <td key={i} className="text-right p-2 tabular-nums">{fmtNum(v)}</td>
                    ))}
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Detail-Grid: Firma, Sachkonto, Bezeichnung, Monate */}
            <div className="rounded-md border overflow-x-auto">
              <div className="bg-muted/50 px-2 py-1.5 text-xs font-medium border-b">Firma · Sachkonto · Bezeichnung</div>
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-muted/30">
                    <th className="text-left p-2 font-medium border-b w-24">Firma</th>
                    <th className="text-left p-2 font-medium border-b w-28">Sachkonto</th>
                    <th className="text-left p-2 font-medium border-b">Bezeichnung</th>
                    <th className="text-right p-2 font-medium border-b w-28">Summe Jahr</th>
                    <th className="text-right p-2 font-medium border-b w-28">Summe Vorjahr</th>
                    {alleMonateAnzeigen && MONTHS.map((m) => (
                      <th key={m} className="text-right p-2 font-medium border-b w-24">{m}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {detailRows.length === 0 ? (
                    <tr>
                      <td colSpan={alleMonateAnzeigen ? 17 : 5} className="p-4 text-center text-muted-foreground text-sm">
                        Keine Detailpositionen. Posten in der Übersicht auswählen für Kontenaufschlüsselung.
                      </td>
                    </tr>
                  ) : (
                    detailRows.map((r, i) => (
                      <tr key={i}>
                        <td className="p-2 border-b">{r.firma}</td>
                        <td className="p-2 border-b">{r.sachkonto}</td>
                        <td className="p-2 border-b">{r.bezeichnung}</td>
                        <td className="text-right p-2 border-b tabular-nums">{fmtNum(r.summeJahr)}</td>
                        <td className="text-right p-2 border-b tabular-nums">0,00</td>
                        {alleMonateAnzeigen && r.months.map((v, j) => (
                          <td key={j} className="text-right p-2 border-b tabular-nums">{fmtNum(v)}</td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        </div>
      </div>

      {/* Fußleiste */}
      <div className="border-t bg-muted/30 px-4 py-2 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Link to="/fibu/schnittstellen-center">
            <Button variant="outline" size="sm">Drucker einrichten</Button>
          </Link>
          <Button variant="outline" size="sm" onClick={handleDrucken}>Drucken</Button>
          <Link to="/fibu/buchungsjournal">
            <Button variant="outline" size="sm">Journal</Button>
          </Link>
          <Button variant="outline" size="sm" onClick={handleExcel}>Excel</Button>
          <Link to="/fibu/hauptbuch">
            <Button variant="outline" size="sm">Kontenbewegung</Button>
          </Link>
          <Link to="/fibu/monatswerte">
            <Button variant="ghost" size="sm">Ende</Button>
          </Link>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-muted-foreground">Soll Mw.: <strong className="tabular-nums">0,00</strong></span>
          <span className="text-muted-foreground">Haben Mw.: <strong className="tabular-nums">0,00</strong></span>
          <span className="text-muted-foreground">Soll ohne Mw.: <strong className="tabular-nums">0,00</strong></span>
          <span className="text-muted-foreground">Haben ohne Mw.: <strong className="tabular-nums">0,00</strong></span>
        </div>
      </div>
    </div>
  )
}
