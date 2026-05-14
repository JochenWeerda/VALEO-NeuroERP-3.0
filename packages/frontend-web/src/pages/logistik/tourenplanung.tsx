import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, MapPin, Truck } from 'lucide-react'
import { useTouren } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'

type LogisticsRoleFocus = 'all' | 'dispatch' | 'driver' | 'warehouse-scale' | 'quality' | 'management'

const logisticsRoleProfiles: Array<{ id: LogisticsRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Tourenlage fuer Disposition, Fahrer, Lager/Waage, QS und Leitung.',
  },
  {
    id: 'dispatch',
    label: 'Disposition',
    description: 'Fokus auf offene Touren, Ressourcen und naechste Dispo-Entscheidung.',
  },
  {
    id: 'driver',
    label: 'Fahrer',
    description: 'Fokus auf aktive Touren, Stopps, Kilometer und Status.',
  },
  {
    id: 'warehouse-scale',
    label: 'Lager/Waage',
    description: 'Fokus auf wartende Annahmen, offene Wiegungen und aktive Kennzeichen.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf gesperrte Chargen und Transportblocker.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Auslastung, Engpaesse und operative Prioritaet.',
  },
]

export default function TourenplanungPage(): JSX.Element {
  const [roleFocus, setRoleFocus] = useState<LogisticsRoleFocus>('all')
  const { data: touren, isLoading } = useTouren()
  const { data: chain } = useSupplyChainOverview()
  const transferSummary = summarizeSupplyTransfer(chain)

  if (isLoading || !touren) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }
  const operationalStatus = normalizeOperationalStatus(
    touren.unterwegs > 0 ? 'in_pruefung' : touren.offen > 0 ? 'wartet_auf_mensch' : 'abgeschlossen'
  )
  const transportBlocked = chain.blockedCharges > 0
  const nextTourAction = transportBlocked
    ? 'Gesperrte Chargen klaeren, bevor betroffene Touren starten.'
    : touren.offen > 0
      ? 'Geplante Touren disponieren und Fahrer/Ressourcen zuordnen.'
      : touren.unterwegs > 0
        ? 'Aktive Touren ueberwachen und Rueckmeldungen sichern.'
        : 'Neue Tour anlegen oder Tagesplanung pruefen.'
  const tourTaskItems: UxTaskItem[] = [
    {
      label: 'Tour planen',
      done: touren.heute > 0,
      hint: touren.heute > 0 ? `${touren.heute} Touren fuer heute vorhanden.` : 'Neue Tour fuer den Tag anlegen.',
    },
    {
      label: 'Ressourcen klaeren',
      done: chain.waitingInbound === 0 && chain.openWeighingTickets === 0,
      hint: chain.waitingInbound + chain.openWeighingTickets > 0
        ? `${chain.waitingInbound} wartende Annahmen und ${chain.openWeighingTickets} offene Wiegungen beachten.`
        : 'Keine offenen Annahme-/Waagepunkte in der Sicht.',
    },
    {
      label: 'Unterwegs ueberwachen',
      done: touren.unterwegs > 0,
      hint: touren.unterwegs > 0 ? `${touren.unterwegs} Touren sind unterwegs.` : 'Keine aktive Tour unterwegs.',
    },
    {
      label: 'Abschliessen',
      done: touren.abgeschlossen > 0 && touren.offen === 0,
      hint: touren.abgeschlossen > 0 ? `${touren.abgeschlossen} Touren abgeschlossen.` : 'Rueckmeldung, Dokumente und Status nach Abschluss sichern.',
    },
  ]
  const tourCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Touren koennen ueber die Tourenplanung gestartet werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Touren, Fahrer, Stopps, Kilometer, Status und Ressourcenlage sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Disponieren',
      available: touren.offen + touren.unterwegs > 0,
      hint: 'Offene und laufende Touren bilden den aktiven Dispo-Bestand.',
    },
    {
      key: 'delete',
      label: 'Storno',
      available: touren.offen > 0,
      hint: 'Geplante Touren koennen fachlich storniert oder umdisponiert werden.',
    },
    {
      key: 'approve',
      label: 'Transportfreigabe',
      available: !transportBlocked,
      hint: transportBlocked ? 'Gesperrte Chargen blockieren betroffene Transportfreigaben.' : 'Keine Chargensperre blockiert die aktuelle Sicht.',
    },
    {
      key: 'export',
      label: 'Nachweis',
      available: touren.tourenListe.length > 0,
      hint: 'Tourenstatus, Fahrer, Stopps und Kilometer bilden den operativen Transportnachweis.',
    },
    {
      key: 'audit',
      label: 'Nachverfolgung',
      available: true,
      hint: 'Tourstatus, Ressourcenlage und Kettenfokus bleiben als Dispo-Spur sichtbar.',
    },
  ]
  const contextSections = [
    {
      title: 'Disposition',
      items: [
        { label: 'Touren heute', value: String(touren.heute) },
        { label: 'Geplant', value: String(touren.offen) },
        { label: 'Unterwegs', value: String(touren.unterwegs) },
      ],
    },
    {
      title: 'Ressourcenlage',
      items: [
        { label: 'Wartende Annahmen', value: String(chain.waitingInbound) },
        { label: 'Offene Wiegungen', value: String(chain.openWeighingTickets) },
        { label: 'Aktive Fahrzeuge', value: String(chain.activeVehiclePlates.length) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Gesperrte Chargen', value: String(chain.blockedCharges) },
        { label: 'Naechste Aktion', value: nextTourAction },
      ],
    },
  ]
  const timelineItems = touren.tourenListe.slice(0, 4).map((tour) => ({
    label: `${tour.id} - ${tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}`,
    detail: `${tour.fahrer}, ${tour.stopps} Stopps, ${tour.km} km`,
  }))

  return (
    <div className="space-y-6 p-3 md:p-6">
      <OperationalCaseHeader
        title="Tourenplanung"
        description="Disposition, Fahrzeugbelegung und Status laufender Liefertouren."
        status={operationalStatus}
        owner="Logistikdisposition"
        blocker={transportBlocked ? 'Gesperrte Chargen koennen Touren beeinflussen.' : null}
        nextAction={nextTourAction}
        caseLabel="Disposition"
        tags={['Logistik', 'Tour']}
      />
      <RoleFocusBar
        roles={logisticsRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: !transportBlocked && touren.heute > 0,
          allowedLabel: 'Disponierbar',
          blockedLabel: transportBlocked ? 'Transport blockiert' : 'Keine Tour',
          summary: transportBlocked
            ? `${chain.blockedCharges} gesperrte Chargen koennen Touren blockieren. Bitte QS-Klaerung vor Transportstart abschliessen.`
            : touren.heute > 0
              ? `Heute sind ${touren.heute} Touren geplant. ${nextTourAction}`
              : 'Es gibt noch keine Tour fuer heute. Legen Sie eine neue Tour an oder pruefen Sie die Tagesplanung.',
          blockerCount: transportBlocked ? chain.blockedCharges : touren.heute > 0 ? 0 : 1,
          nextFocus: nextTourAction,
          template: {
            label: 'Neue Tour anlegen',
            href: '/logistik/tourenplanung',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Dispo-Aufgabenplan" items={tourTaskItems} />
        <NextActionPanel
          action={nextTourAction}
          tone={transportBlocked ? 'red' : touren.offen > 0 || touren.unterwegs > 0 ? 'amber' : touren.heute > 0 ? 'blue' : 'red'}
        />
      </div>
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Tourenlage" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <CrudCapabilityChecklist capabilities={tourCrudCapabilities} />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tourenplanung</h1>
          <p className="text-muted-foreground">Liefertouren & Disposition</p>
        </div>
        <Button className="gap-2">
          <Truck className="h-4 w-4" />
          Neue Tour
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Touren Heute</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{touren.heute}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Geplant</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{touren.offen}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{touren.unterwegs}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-green-600">{touren.abgeschlossen}</span></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Wartende Annahmen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.waitingInbound}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Wiegungen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.openWeighingTickets}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesperrte Chargen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.blockedCharges}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktive Fahrzeuge</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.activeVehiclePlates.length}</span></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Uebergaberisiko</CardTitle></CardHeader>
          <CardContent><div className="text-lg font-semibold">{transferSummary.transferPressure}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Kettenpunkte</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{transferSummary.handoverRisk}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kettenfokus</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{transferSummary.nextAction}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Aktive Touren
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {touren.tourenListe.map((tour) => (
              <div key={tour.id} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{tour.id} - Fahrer: {tour.fahrer}</div>
                  <div className="text-sm text-muted-foreground">{tour.stopps} Stopps - {tour.km} km</div>
                </div>
                <Badge variant={tour.status === 'unterwegs' ? 'secondary' : tour.status === 'abgeschlossen' ? 'outline' : 'default'}>
                  {tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
