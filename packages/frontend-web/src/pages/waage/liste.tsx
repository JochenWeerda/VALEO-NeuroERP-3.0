import { useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { useWaagen, type Waage } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'
import { AlertTriangle, FileDown, Plus, Scale, Search } from 'lucide-react'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type ScaleListRoleFocus = 'all' | 'scale' | 'yard' | 'dispatch' | 'quality' | 'management'

const scaleListRoleProfiles: Array<{ id: ScaleListRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt die Waagenliste fuer Waage, Hof, Disposition, QS und Leitung.' },
  { id: 'scale', label: 'Waage', description: 'Fokus auf Waagenbestand, Status und Eichfaelligkeit.' },
  { id: 'yard', label: 'Hof', description: 'Fokus auf offene Annahmen und Waageverfuegbarkeit.' },
  { id: 'dispatch', label: 'Disposition', description: 'Fokus auf Kettenlage, Bottleneck und naechste Aktion.' },
  { id: 'quality', label: 'QS', description: 'Fokus auf Eichung, gesperrte Chargen und Prueftermine.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, Auslastung und Exportnachweis.' },
]

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-48" /><Skeleton className="h-4 w-32 mt-2" /></div>
        <Skeleton className="h-10 w-36" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}><CardHeader className="pb-2"><Skeleton className="h-4 w-24" /></CardHeader><CardContent><Skeleton className="h-8 w-16" /></CardContent></Card>
        ))}
      </div>
      <Card><CardHeader><Skeleton className="h-5 w-32" /></CardHeader><CardContent><div className="flex gap-4"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-32" /></div></CardContent></Card>
      <Card><CardContent className="pt-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: Error | null; onRetry: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
      <h2 className="text-xl font-semibold text-red-600 mb-2">Backend nicht erreichbar</h2>
      <p className="text-muted-foreground mb-4">
        {error?.message || 'Die Waagen-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="gap-2">
        <Scale className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

export default function WaageListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: chain } = useSupplyChainOverview()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<ScaleListRoleFocus>('all')
  const { data: waagen = [], isLoading, isError, error, refetch } = useWaagen()
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])
  const transferSummary = useMemo(() => summarizeSupplyTransfer(chain), [chain])

  const filteredWaagen = useMemo(() => {
    if (!searchTerm) return waagen
    const term = searchTerm.toLowerCase()
    return waagen.filter((w) =>
      [w.standort, w.id, w.typ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term)),
    )
  }, [waagen, searchTerm])

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/waage/neu'),
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => {
      void refetch()
    },
  })
  useKeyboardShortcuts(shortcuts)

  // Error State: Keine Mock-Daten als Fallback!
  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const columns = [
    { key: 'standort' as const, label: 'Standort', render: (w: Waage) => <div><div className="font-medium">{w.standort}</div><div className="text-sm text-muted-foreground">{w.id}</div></div> },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'maxKapazitaet' as const, label: 'Max. Kapazitaet (t)' },
    { key: 'naechsteEichung' as const, label: 'Naechste Eichung', render: (w: Waage) => new Date(w.naechsteEichung).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (w: Waage) => <Badge variant={w.status === 'aktiv' || w.status === 'geeicht' ? 'outline' : 'secondary'}>{w.status === 'aktiv' ? 'Aktiv' : w.status === 'wartung' ? 'Wartung' : 'Geeicht'}</Badge> },
  ]

  const handleExport = (): void => {
    const header = 'ID;Standort;Typ;Max_Kapazitaet_t;Letzte_Eichung;Naechste_Eichung;Status\n'
    const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = filteredWaagen.map((w) =>
      [w.id, w.standort, w.typ, w.maxKapazitaet, w.letzteEichung, w.naechsteEichung, w.status].map(esc).join(';')
    ).join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Waagen_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredWaagen.length} Waagen exportiert.` })
  }
  const dueCalibrations = filteredWaagen.filter((w) => new Date(w.naechsteEichung) <= new Date()).length
  const activeScales = filteredWaagen.filter((w) => w.status === 'aktiv').length
  const hasScales = filteredWaagen.length > 0
  const scaleListWorkable = hasScales && dueCalibrations === 0 && supplyOps.pressure !== 'hoch'
  const scaleListNextAction = !hasScales
    ? 'Waage anlegen oder Suchfilter zuruecksetzen.'
    : dueCalibrations > 0
      ? `${dueCalibrations} faellige Eichtermine pruefen.`
      : supplyOps.pressure === 'hoch'
        ? `Bottleneck ${supplyOps.bottleneck} entlasten.`
        : supplyOps.nextAction
  const scaleListTaskItems: UxTaskItem[] = [
    { label: 'Waagenbestand pruefen', done: hasScales, hint: hasScales ? `${filteredWaagen.length} Waagen sichtbar, ${activeScales} aktiv.` : 'Keine Waage im aktuellen Filter.' },
    { label: 'Eichung klaeren', done: dueCalibrations === 0, hint: dueCalibrations > 0 ? `${dueCalibrations} Eichtermine sind faellig.` : 'Keine faellige Eichung im aktuellen Ausschnitt.' },
    { label: 'Kettenlage bewerten', done: supplyOps.pressure !== 'hoch', hint: `Druck ${supplyOps.pressure}, Bottleneck ${supplyOps.bottleneck}.` },
    { label: 'Nachweis exportieren', done: filteredWaagen.length > 0, hint: filteredWaagen.length > 0 ? 'CSV-Export ist fuer den aktuellen Ausschnitt verfuegbar.' : 'Export braucht sichtbare Waagen.' },
  ]
  const scaleListCrudCapabilities = [
    { key: 'create', label: 'Neue Waage', available: true, hint: 'Neue Waage kann per Button oder Ctrl+N angelegt werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Waagen, Status, Eichung und Kettenlage sind sichtbar.' },
    { key: 'filter', label: 'Suchen', available: true, hint: 'Suche filtert nach Standort, Waagen-ID oder Typ.' },
    { key: 'export', label: 'Export/Nachweis', available: filteredWaagen.length > 0, hint: filteredWaagen.length > 0 ? 'CSV-Export dokumentiert den aktuellen Stand.' : 'Kein Export ohne sichtbare Waagen.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Eichstatus, Exportzeitpunkt und Kettenlage bilden die Pruefsicht.' },
  ]
  const operationalStatus = normalizeOperationalStatus(
    supplyOps.pressure === 'hoch'
      ? 'eskaliert'
      : dueCalibrations > 0
        ? 'wartet_auf_mensch'
        : filteredWaagen.length > 0
          ? 'in_pruefung'
          : 'offen',
  )
  const contextSections = [
    {
      title: 'Waagenlage',
      items: [
        { label: 'Standorte', value: `${filteredWaagen.length}` },
        { label: 'Eichung faellig', value: `${dueCalibrations}` },
        { label: 'Bottleneck', value: supplyOps.bottleneck },
      ],
    },
    {
      title: 'Physische Kette',
      items: [
        { label: 'Annahme offen', value: `${chain?.waitingInbound ?? 0}` },
        { label: 'Wiegungen offen', value: `${chain?.openWeighingTickets ?? 0}` },
        { label: 'Naechste Aktion', value: supplyOps.nextAction },
      ],
    },
  ]
  const timelineItems = [
    {
      label: supplyOps.pressure === 'hoch' ? 'Hoher physischer Druck' : 'Kettenlage stabil',
      detail: `Druck ${supplyOps.pressure}, Bottleneck ${supplyOps.bottleneck}, Fracht unterwegs ${chain?.freightInTransit ?? 0}.`,
    },
    {
      label: dueCalibrations > 0 ? 'Eichpruefung faellig' : 'Eichlage unkritisch',
      detail: dueCalibrations > 0
        ? `${dueCalibrations} Waagen sollten vor weiterer Belastung neu geprueft oder eingeplant werden.`
        : 'Im aktuellen Ausschnitt gibt es keine ueberfaelligen Eichtermine.',
    },
  ]

  return (
    <PageSurface data-page-surface="waage-liste" contentClassName="space-y-6">
      <PageSection
        description="Bestandsseite rueckwirkend auf den DS-Surface, Keyboard-first und touch-feste Bedienung gezogen."
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold">Waagen</h1>
            <p className="text-muted-foreground">Waagen-Management und Eichfaelligkeit.</p>
          </div>
          <Button onClick={() => navigate('/waage/neu')} className="min-h-touch gap-2 touch-manipulation">
            <Plus className="h-4 w-4" />Neue Waage
          </Button>
        </div>
      </PageSection>

      <PageSection>
        <div className="mb-4 space-y-4">
          <RoleFocusBar roles={scaleListRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
          <ManagementDecisionPanel
            decision={{
              allowed: scaleListWorkable,
              allowedLabel: 'Arbeitsfaehig',
              blockedLabel: 'Stopper offen',
              summary: scaleListWorkable ? `${filteredWaagen.length} Waagen sichtbar, ${activeScales} aktiv, keine faellige Eichung.` : `Vor weiterer Planung ist noch etwas offen: ${scaleListNextAction}`,
              blockerCount: [!hasScales, dueCalibrations > 0, supplyOps.pressure === 'hoch'].filter(Boolean).length,
              nextFocus: scaleListNextAction,
              template: { label: 'Hofliste oeffnen', href: '/waage/hofliste' },
            }}
          />
          <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <OperationalTaskPlan title="Waagen-Prioritaetsplan" items={scaleListTaskItems} />
            <div className="space-y-3">
              <NextActionPanel action={scaleListNextAction} tone={scaleListWorkable ? 'emerald' : dueCalibrations > 0 || supplyOps.pressure === 'hoch' ? 'red' : 'blue'} />
              <EvidenceTemplateLink link={{ label: 'Waage Export vorbereiten', href: '/waage/liste' }} />
            </div>
          </div>
          <CrudCapabilityChecklist capabilities={scaleListCrudCapabilities} />
        </div>
        <OperationalCaseHeader
          title="Waagensteuerung"
          description="Die Waagenliste fuehrt die physische Kette als kompakten Vorgang zwischen Annahme, Wiegung, Charge und Fracht."
          status={operationalStatus}
          owner="Waagenleitstand"
          blocker={supplyOps.pressure === 'hoch' ? `Bottleneck ${supplyOps.bottleneck} erzeugt aktuell hohen operativen Druck.` : dueCalibrations > 0 ? `${dueCalibrations} Waagen haben einen faelligen Eichtermin.` : null}
          nextAction={supplyOps.nextAction}
          caseLabel="Vorgang: Wiegung"
          tags={['Waage', 'Physische Kette', 'Operator']}
        />
        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Kettenverlauf" items={timelineItems} />
          <OperationalContextPanel title="Waagen-Kontext" sections={contextSections} />
        </div>
      </PageSection>

      <PageSection title="Uebersicht" description="Live-Zahlen fuer Waagenbestand, Aktivstatus und fällige Eichungen.">
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Waagen Gesamt</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-blue-600" />
                <span className="text-2xl font-bold">{filteredWaagen.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-green-600">
                {filteredWaagen.filter((w) => w.status === 'aktiv').length}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Eichung faellig</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">
                {filteredWaagen.filter((w) => new Date(w.naechsteEichung) <= new Date()).length}
              </span>
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Kettenlage" description="Einheitliche Sicht auf Annahme, Wiegung, Charge und Fracht direkt an der Waage.">
        <div className="grid gap-4 md:grid-cols-4">
          <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Annahme offen</div><div className="text-2xl font-semibold">{chain?.waitingInbound ?? 0}</div></CardContent></Card>
          <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Wiegungen offen</div><div className="text-2xl font-semibold">{chain?.openWeighingTickets ?? 0}</div></CardContent></Card>
          <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Chargen in Prüfung</div><div className="text-2xl font-semibold">{chain?.blockedCharges ?? 0}</div></CardContent></Card>
          <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Fracht unterwegs</div><div className="text-2xl font-semibold">{chain?.freightInTransit ?? 0}</div></CardContent></Card>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Bottleneck</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold capitalize">{supplyOps.bottleneck}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Druck</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : supplyOps.pressure === 'mittel' ? 'secondary' : 'outline'}>
                {supplyOps.pressure}
              </Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-semibold">{supplyOps.nextAction}</div>
            </CardContent>
          </Card>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Uebergaberisiko</CardTitle></CardHeader>
            <CardContent><div className="text-lg font-semibold">{transferSummary.transferPressure}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Uebergaben</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-semibold">{transferSummary.handoverRisk}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kettenfokus</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{transferSummary.nextAction}</div></CardContent>
          </Card>
        </div>
      </PageSection>

      <PageSection title="Suche und Liste" description="Ctrl+F fokussiert die Suche, Ctrl+N legt eine neue Waage an, F5 aktualisiert die Liste.">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-4">
            <div className="relative min-w-[18rem] flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                ref={searchInputRef}
                aria-label="Suche Waagen"
                placeholder="Standort, Waagen-ID oder Typ suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
              <FileDown className="h-4 w-4" />Export
            </Button>
          </div>
          <Card>
            <CardContent className="pt-6">
              <DataTable data={filteredWaagen} columns={columns} />
            </CardContent>
          </Card>
        </div>
      </PageSection>

      <KeyboardShortcutBar shortcuts={shortcuts} />
    </PageSurface>
  )
}
