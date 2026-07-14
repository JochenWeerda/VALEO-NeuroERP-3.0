import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { useFrachtbriefe, type Frachtbrief } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type FreightRoleFocus = 'all' | 'dispatch' | 'driver' | 'warehouse-scale' | 'documentation' | 'management'

const freightRoleProfiles: Array<{ id: FreightRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt Frachtbriefarbeit fuer Disposition, Fahrer, Lager/Waage, Dokumentation und Leitung.',
  },
  {
    id: 'dispatch',
    label: 'Disposition',
    description: 'Fokus auf Versandstatus, Transit und naechste Transportaktion.',
  },
  {
    id: 'driver',
    label: 'Fahrer',
    description: 'Fokus auf Kennzeichen, Strecke, Artikel und Zustellung.',
  },
  {
    id: 'warehouse-scale',
    label: 'Lager/Waage',
    description: 'Fokus auf Annahme, Waage, Charge und aktive Kennzeichen.',
  },
  {
    id: 'documentation',
    label: 'Dokumentation',
    description: 'Fokus auf Frachtbriefnummer, Status, Export und Nachweis.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Dokumentdruck, Bottleneck und Kettenrisiko.',
  },
]

export default function FrachtbriefePage(): JSX.Element {
  const navigate = useNavigate()
  const { data: chain } = useSupplyChainOverview()
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<FreightRoleFocus>('all')
  const { data: frachtbriefe, isLoading } = useFrachtbriefe()
  const list = useMemo(() => frachtbriefe ?? [], [frachtbriefe])
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])
  const transferSummary = useMemo(() => summarizeSupplyTransfer(chain), [chain])

  const fallkopf = useMemo(() => {
    const unterwegs = list.filter((f) => f.status === 'unterwegs').length
    const erstellt = list.filter((f) => f.status === 'erstellt').length
    const total = list.length
    return {
      status: erstellt > 0 ? `${erstellt} Frachtbrief(e) noch nicht versendet` : unterwegs > 0 ? `${unterwegs} unterwegs` : 'Keine offenen Frachtbriefe',
      statusColor: erstellt > 0 ? 'text-amber-700 bg-amber-50 border-amber-300' : unterwegs > 0 ? 'text-blue-700 bg-blue-50 border-blue-300' : 'text-green-700 bg-green-50 border-green-300',
      blocker: erstellt > 0 ? `${erstellt} Dokument(e) warten auf Versand` : 'Kein Blocker',
      dokumentdruck: total > 0 ? `${total} Frachtbriefe gesamt, ${unterwegs} in Transit` : 'Keine Dokumente',
      naechsteAktion: erstellt > 0 ? 'Erstellte Frachtbriefe pruefen und versenden' : unterwegs > 0 ? 'Zustellung verfolgen' : 'Neuen Frachtbrief anlegen',
    }
  }, [list])

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Frachtbrief-Nr.',
      render: (f: Frachtbrief) => (
        <button onClick={() => navigate(`/logistik/frachtbrief/${f.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {f.nummer}
        </button>
      ),
    },
    { key: 'kennzeichen' as const, label: 'LKW', render: (f: Frachtbrief) => <span className="font-mono">{f.kennzeichen}</span> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (f: Frachtbrief) => `${f.menge} t` },
    {
      key: 'empfaenger' as const,
      label: 'Von / Nach',
      render: (f: Frachtbrief) => (
        <div className="text-sm">
          <div>{f.absender}</div>
          <div className="text-muted-foreground">{'->'} {f.empfaenger}</div>
        </div>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (f: Frachtbrief) => new Date(f.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: Frachtbrief) => (
        <Badge variant={f.status === 'zugestellt' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>
          {f.status === 'erstellt' ? 'Erstellt' : f.status === 'unterwegs' ? 'Unterwegs' : 'Zugestellt'}
        </Badge>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const operationalStatus = normalizeOperationalStatus(
    list.some((f) => f.status === 'erstellt')
      ? 'wartet_auf_mensch'
      : list.some((f) => f.status === 'unterwegs')
        ? 'in_pruefung'
        : 'offen',
  )
  const contextSections = [
    {
      title: 'Frachtlage',
      items: [
        { label: 'Frachtbriefe gesamt', value: `${list.length}` },
        { label: 'Unterwegs', value: `${list.filter((f) => f.status === 'unterwegs').length}` },
        { label: 'Erstellt', value: `${list.filter((f) => f.status === 'erstellt').length}` },
      ],
    },
    {
      title: 'Objektkette',
      items: [
        { label: 'Wartende Annahmen', value: `${chain.waitingInbound}` },
        { label: 'Offene Wiegungen', value: `${chain.openWeighingTickets}` },
        { label: 'Gesperrte Chargen', value: `${chain.blockedCharges}` },
      ],
    },
    {
      title: 'Naechster Schritt',
      items: [
        { label: 'Frachtoperator', value: fallkopf.naechsteAktion },
        { label: 'Kettenblick', value: transferSummary.nextAction },
        { label: 'Bottleneck', value: supplyOps.bottleneck },
      ],
    },
  ]
  const timelineItems = [
    {
      label: list.some((f) => f.status === 'erstellt') ? 'Versandfaehige Frachtbriefe offen' : 'Kein offener Versand',
      detail: `${list.filter((f) => f.status === 'erstellt').length} Dokumente warten auf Versand.`,
    },
    {
      label: list.some((f) => f.status === 'unterwegs') ? 'Transporte unterwegs' : 'Keine Transporte unterwegs',
      detail: `${list.filter((f) => f.status === 'unterwegs').length} Frachtbriefe sind in Transit.`,
    },
    {
      label: 'Physische Kette',
      detail: transferSummary.nextAction,
    },
  ]
  const createdCount = list.filter((f) => f.status === 'erstellt').length
  const inTransitCount = list.filter((f) => f.status === 'unterwegs').length
  const deliveredCount = list.filter((f) => f.status === 'zugestellt').length
  const freightBlocked = chain.blockedCharges > 0
  const nextFreightAction = freightBlocked
    ? 'Gesperrte Chargen klaeren, bevor betroffene Frachtbriefe weiterlaufen.'
    : createdCount > 0
      ? 'Erstellte Frachtbriefe pruefen und versenden.'
      : inTransitCount > 0
        ? 'Transporte verfolgen und Zustellung sichern.'
        : 'Neuen Frachtbrief anlegen oder Filter pruefen.'
  const freightTaskItems: UxTaskItem[] = [
    {
      label: 'Frachtbrief erstellen',
      done: list.length > 0,
      hint: list.length > 0 ? `${list.length} Frachtbriefe in der aktuellen Sicht.` : 'Neuen Frachtbrief anlegen.',
    },
    {
      label: 'Versenden',
      done: createdCount === 0 && list.length > 0,
      hint: createdCount > 0 ? `${createdCount} Frachtbriefe warten auf Versand.` : 'Keine erstellten, unversendeten Frachtbriefe in der Sicht.',
    },
    {
      label: 'Transport verfolgen',
      done: inTransitCount > 0,
      hint: inTransitCount > 0 ? `${inTransitCount} Frachtbriefe sind unterwegs.` : 'Keine Frachtbriefe in Transit.',
    },
    {
      label: 'Zustellung sichern',
      done: deliveredCount > 0,
      hint: deliveredCount > 0 ? `${deliveredCount} Frachtbriefe sind zugestellt.` : 'Zustellung und Nachweis nach Transportende sichern.',
    },
  ]
  const freightCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Frachtbriefe koennen aus der Seite angelegt werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Nummer, Kennzeichen, Artikel, Menge, Strecke, Datum und Status sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: list.length > 0,
      hint: 'Frachtbriefe koennen ueber die Detailnavigation geoeffnet werden.',
    },
    {
      key: 'delete',
      label: 'Storno',
      available: createdCount > 0,
      hint: 'Erstellte, noch nicht zugestellte Frachtbriefe koennen fachlich korrigiert oder storniert werden.',
    },
    {
      key: 'approve',
      label: 'Transportnachweis',
      available: !freightBlocked,
      hint: freightBlocked ? 'Chargensperren muessen vor betroffener Transportfreigabe geklaert werden.' : 'Keine Chargensperre blockiert die aktuelle Sicht.',
    },
    {
      key: 'export',
      label: 'Export',
      available: list.length > 0,
      hint: 'Suche, Status und Frachtbriefdaten bilden die Export-/Nachweisgrundlage.',
    },
    {
      key: 'audit',
      label: 'Nachverfolgung',
      available: true,
      hint: 'Frachtstatus, Kettenblick und Bottleneck bleiben nachvollziehbar.',
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <OperationalCaseHeader
        title="Frachtbriefe steuern"
        description="Versandstatus, Dokumentdruck und physische Kettenlage bleiben oben als ein kompakter Frachtfall sichtbar."
        status={operationalStatus}
        owner="Logistik / Disposition"
        blocker={fallkopf.blocker !== 'Kein Blocker' ? fallkopf.blocker : null}
        nextAction={nextFreightAction}
        caseLabel="Frachtfall"
        tags={['Logistik', 'Fracht']}
      />
      <RoleFocusBar
        roles={freightRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: list.length > 0 && !freightBlocked,
          allowedLabel: 'Nachweisfaehig',
          blockedLabel: freightBlocked ? 'Transport blockiert' : 'Kein Frachtbrief',
          summary: freightBlocked
            ? `${chain.blockedCharges} gesperrte Chargen koennen Frachtbriefe blockieren. Bitte QS-Klaerung vor Versand oder Zustellung abschliessen.`
            : list.length > 0
              ? `${list.length} Frachtbriefe sind in der aktuellen Sicht. ${nextFreightAction}`
              : 'In der aktuellen Sicht gibt es keine Frachtbriefe. Legen Sie einen neuen Frachtbrief an oder passen Sie die Suche an.',
          blockerCount: freightBlocked ? chain.blockedCharges : list.length > 0 ? 0 : 1,
          nextFocus: nextFreightAction,
          template: {
            label: 'Frachtbrief anlegen',
            href: '/logistik/frachtbrief/neu',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Dokument-Follow-up-Plan" items={freightTaskItems} />
        <NextActionPanel
          action={nextFreightAction}
          tone={freightBlocked ? 'red' : createdCount > 0 || inTransitCount > 0 ? 'amber' : list.length > 0 ? 'blue' : 'red'}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTimeline title="Frachtverlauf" items={timelineItems} />
        <OperationalContextPanel title="Frachtkontext" sections={contextSections} />
      </div>
      <CrudCapabilityChecklist capabilities={freightCrudCapabilities} />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Frachtbriefe</h1>
          <p className="text-muted-foreground">Transport-Dokumentation</p>
        </div>
        <Button onClick={() => navigate('/logistik/frachtbrief/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Frachtbrief
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Frachtbriefe Heute</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{list.filter((f) => f.status === 'unterwegs').length}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Zugestellt</CardTitle></CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{list.filter((f) => f.status === 'zugestellt').length}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Annahme offen</div><div className="text-2xl font-semibold">{chain.waitingInbound}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Wiegungen offen</div><div className="text-2xl font-semibold">{chain.openWeighingTickets}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Chargen gesperrt / Prüfung</div><div className="text-2xl font-semibold">{chain.blockedCharges}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Aktive Kennzeichen</div><div className="text-sm font-semibold">{chain.activeVehiclePlates.slice(0, 3).join(', ') || 'n/a'}</div></CardContent></Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bottleneck</CardTitle></CardHeader><CardContent><div className="text-2xl font-semibold">{supplyOps.bottleneck}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Druck</CardTitle></CardHeader><CardContent><Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : 'outline'}>{supplyOps.pressure}</Badge></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle></CardHeader><CardContent><div className="text-sm font-semibold">{supplyOps.nextAction}</div></CardContent></Card>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Uebergabedruck</CardTitle></CardHeader><CardContent><Badge variant={transferSummary.transferPressure === 'hoch' ? 'destructive' : 'outline'}>{transferSummary.transferPressure}</Badge></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Kettenpunkte</CardTitle></CardHeader><CardContent><div className="text-2xl font-semibold">{transferSummary.handoverRisk}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Naechster Kettenpfad</CardTitle></CardHeader><CardContent><div className="text-sm font-semibold">{transferSummary.nextAction}</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
