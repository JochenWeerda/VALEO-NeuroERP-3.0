import { useCallback, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, MapPin, Truck } from 'lucide-react'
import { useTouren } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { fetchTourWithDeliveryHints, resolveSalesDeliveryNoteByRef, type DeliveryNoteHint } from '@/lib/api/logistics-tours'
import { useToast } from '@/hooks/use-toast'
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
  const { toast } = useToast()
  const [roleFocus, setRoleFocus] = useState<LogisticsRoleFocus>('all')
  const [lsRef, setLsRef] = useState('DEMO-LS-001')
  const [lsBusy, setLsBusy] = useState(false)
  const [lsResult, setLsResult] = useState<{ nr?: string; status?: string } | null>(null)
  const [hintTourId, setHintTourId] = useState<string | null>(null)
  const [hintText, setHintText] = useState('')
  const [hintBusy, setHintBusy] = useState(false)
  const { data: touren, isLoading } = useTouren()
  const { data: chain } = useSupplyChainOverview()
  const transferSummary = summarizeSupplyTransfer(chain)

  const handleResolveLs = useCallback(async () => {
    const ref = lsRef.trim()
    if (!ref) {
      toast({ title: 'Referenz fehlt', description: 'Bitte Lieferschein-Nummer oder ID eintragen.', variant: 'destructive' })
      return
    }
    setLsBusy(true)
    setLsResult(null)
    try {
      const h = await resolveSalesDeliveryNoteByRef(ref)
      setLsResult({ nr: h.delivery_note_number ?? undefined, status: h.status ?? undefined })
      toast({ title: 'Lieferschein gefunden', description: h.delivery_note_number || h.id })
    } catch (e) {
      toast({ title: 'Aufloesung fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setLsBusy(false)
    }
  }, [lsRef, toast])

  const handleTourHints = useCallback(
    async (tourId: string) => {
      setHintTourId(tourId)
      setHintBusy(true)
      setHintText('…')
      try {
        const t = await fetchTourWithDeliveryHints(tourId)
        const stops = Array.isArray(t.stops) ? t.stops : []
        const lines = stops.map((s) => {
          const ref = String(s.delivery_note_ref || '—')
          const hint = s.delivery_note_hint as DeliveryNoteHint | null | undefined
          const ok = hint
            ? `${String(hint.delivery_note_number ?? hint.id ?? '')} (${String(hint.status ?? '?')})`
            : '—'
          return `${ref} → ${ok}`
        })
        setHintText(lines.length > 0 ? lines.join('\n') : 'Keine Stopps')
      } catch (e) {
        const msg = getAxiosErrorMessage(e)
        setHintText(msg)
        toast({ title: 'Tour-Hints fehlgeschlagen', description: msg, variant: 'destructive' })
      } finally {
        setHintBusy(false)
      }
    },
    [toast],
  )

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
    label: `${tour.vehicleLabel || tour.id.slice(0, 8)} - ${tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}`,
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
          <CardTitle>Lieferschein ↔ Tour (Read-Spine)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Referenz aus Stopp-Feld aufloesen (Nummer oder UUID). Demo: nach{' '}
            <code className="rounded bg-muted px-1">seed_demo_sales.py</code> +{' '}
            <code className="rounded bg-muted px-1">seed_demo_logistics_spine.py</code> existiert{' '}
            <code className="rounded bg-muted px-1">DEMO-LS-001</code> an der Demo-Tour.
          </p>
          <div className="flex flex-wrap items-end gap-2">
            <div className="min-w-[200px] flex-1">
              <label htmlFor="ls-ref" className="mb-1 block text-sm font-medium">
                Lieferschein-Referenz
              </label>
              <Input id="ls-ref" value={lsRef} onChange={(e) => setLsRef(e.target.value)} placeholder="z. B. DEMO-LS-001" />
            </div>
            <Button type="button" disabled={lsBusy} onClick={() => void handleResolveLs()}>
              {lsBusy ? 'Bitte warten…' : 'Aufloesen'}
            </Button>
          </div>
          {lsResult ? (
            <div className="rounded-md border bg-muted/40 p-3 text-sm">
              <div>
                <span className="font-medium">Nummer:</span> {lsResult.nr ?? '—'}
              </div>
              <div>
                <span className="font-medium">Status:</span> {lsResult.status ?? '—'}
              </div>
            </div>
          ) : null}
          {hintTourId ? (
            <div className="rounded-md border p-3 text-sm">
              <div className="mb-1 font-medium">Stopps Tour {hintTourId.slice(0, 8)}…</div>
              <pre className="whitespace-pre-wrap font-sans text-xs text-muted-foreground">{hintText}</pre>
              <Button type="button" variant="ghost" size="sm" className="mt-2" disabled={hintBusy} onClick={() => setHintTourId(null)}>
                Hinweis schliessen
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>

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
              <div key={tour.id} className="flex flex-col gap-2 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="font-semibold">
                    {tour.vehicleLabel || tour.id.slice(0, 8)} — Fahrer: {tour.fahrer}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {tour.stopps} Stopps - {tour.km} km
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={hintBusy && hintTourId === tour.id}
                    onClick={() => void handleTourHints(tour.id)}
                  >
                    Lieferschein-Hints
                  </Button>
                  <Badge variant={tour.status === 'unterwegs' ? 'secondary' : tour.status === 'abgeschlossen' ? 'outline' : 'default'}>
                    {tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
