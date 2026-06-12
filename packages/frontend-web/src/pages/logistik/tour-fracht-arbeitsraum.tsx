/**
 * Kombinierter Dispo-Arbeitsraum Tour + Frachtbrief (Wave-Audit Punkt 5).
 * Kompakte Lage; Detailarbeit in Tourenplanung bzw. Frachtbriefe.
 */
import { useCallback, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { useToast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { listFreightTariffs, simulateFreightCost } from '@/lib/api/logistics-freight'
import { useFrachtbriefe, useTouren, type Frachtbrief, type Tour } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { Calculator, LayoutGrid, MapPin, Truck } from 'lucide-react'

type CombinedRoleFocus = 'all' | 'dispatch' | 'fracht' | 'chain'

const combinedRoleProfiles: Array<{ id: CombinedRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Touren, Frachtbriefe und Kettenrisiko in einem Blick.',
  },
  {
    id: 'dispatch',
    label: 'Disposition',
    description: 'Fokus auf Tourenplanung, Transit und operative Freigabe.',
  },
  {
    id: 'fracht',
    label: 'Fracht / Doku',
    description: 'Fokus auf Frachtbriefe, Versand und Frachtkosten-Check.',
  },
  {
    id: 'chain',
    label: 'Objektkette',
    description: 'Fokus auf Annahme, Waage, Sperren und Kettenfokus.',
  },
]

function tourStatusShort(t: Tour): string {
  if (t.status === 'unterwegs') return 'Unterwegs'
  if (t.status === 'abgeschlossen') return 'Abgeschlossen'
  if (t.status === 'storniert') return 'Storniert'
  return 'Geplant'
}

export default function TourFrachtArbeitsraumPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [roleFocus, setRoleFocus] = useState<CombinedRoleFocus>('all')
  const [probeBusy, setProbeBusy] = useState(false)
  const [probeResult, setProbeResult] = useState<{ eur: number; carrier: string; zone?: string } | null>(null)

  const { data: touren, isLoading: tourenLoading } = useTouren()
  const { data: frachtRaw, isLoading: frachtLoading } = useFrachtbriefe()
  const { data: chain } = useSupplyChainOverview()
  const list = useMemo(() => frachtRaw ?? [], [frachtRaw])
  const transferSummary = summarizeSupplyTransfer(chain)

  const { data: tariffRows = [], isLoading: tariffsLoading } = useQuery({
    queryKey: ['logistik', 'freight-tariffs'],
    queryFn: listFreightTariffs,
    staleTime: 60 * 1000,
  })

  const frachtErstellt = useMemo(() => list.filter((f) => f.status === 'erstellt').length, [list])
  const frachtTransit = useMemo(() => list.filter((f) => f.status === 'unterwegs').length, [list])
  const frachtZugestellt = useMemo(() => list.filter((f) => f.status === 'zugestellt').length, [list])

  const firstCarrierId = useMemo(() => {
    const c = tariffRows[0]?.carrier_id
    return typeof c === 'string' && c.length > 0 ? c : null
  }, [tariffRows])

  const handleFreightProbe = useCallback(async () => {
    if (!firstCarrierId) {
      toast({ title: 'Kein Tarif', description: 'Kein Spediteur in der Tarifliste — zuerst Tarif anlegen oder Seeding.', variant: 'destructive' })
      return
    }
    setProbeBusy(true)
    setProbeResult(null)
    try {
      const res = await simulateFreightCost({
        carrier_id: firstCarrierId,
        distance_km: 100,
        weight_kg: 100,
        postal_code_from: '10115',
        postal_code_to: '20095',
      })
      setProbeResult({
        eur: res.freight_cost_eur,
        carrier: res.carrier_id,
        zone: typeof res.zone === 'string' ? res.zone : undefined,
      })
      toast({ title: 'Simulation', description: `${res.freight_cost_eur} € (${res.carrier_id})` })
    } catch (e) {
      toast({ title: 'Simulation fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setProbeBusy(false)
    }
  }, [firstCarrierId, toast])

  if (tourenLoading || frachtLoading || !touren) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      </div>
    )
  }

  const transportBlocked = chain.blockedCharges > 0
  const nextAction = transportBlocked
    ? 'Gesperrte Chargen klaeren — betrifft Touren und Fracht gleichermassen.'
    : frachtErstellt > 0
      ? `${frachtErstellt} Frachtbrief(e) auf Versand pruefen; Tourenlage parallel abstimmen.`
      : touren.offen > 0
        ? `${touren.offen} Tour(en) geplant; Frachtbriefe und Stopps abstimmen.`
        : touren.unterwegs > 0 || frachtTransit > 0
          ? 'Laufende Transporte (Tour/Fracht) ueberwachen und Rueckmeldungen sichern.'
          : 'Keine kritischen offenen Punkte in der kombinierten Sicht — Detailseiten pruefen.'

  const operationalStatus = normalizeOperationalStatus(
    transportBlocked
      ? 'blockiert'
      : frachtErstellt > 0 || touren.offen > 0
        ? 'wartet_auf_mensch'
        : touren.unterwegs > 0 || frachtTransit > 0
          ? 'in_pruefung'
          : 'offen',
  )

  const taskItems: UxTaskItem[] = [
    {
      label: 'Touren disponieren',
      done: touren.heute > 0,
      hint: touren.heute > 0 ? `${touren.heute} Tour(en) heute in der Liste.` : 'Tourenplanung oeffnen und Tagesplan pflegen.',
    },
    {
      label: 'Frachtbriefe versenden',
      done: frachtErstellt === 0 && list.length > 0,
      hint:
        frachtErstellt > 0
          ? `${frachtErstellt} Frachtbrief(e) noch nicht versendet.`
          : 'Keine erstellten, offenen Frachtbriefe in der Sicht.',
    },
    {
      label: 'Transit ueberwachen',
      done: touren.unterwegs > 0 || frachtTransit > 0,
      hint: `${touren.unterwegs} Tour(en) unterwegs, ${frachtTransit} Frachtbrief(e) in Transit.`,
    },
    {
      label: 'Kettenfokus',
      done: !transportBlocked,
      hint: transferSummary.nextAction,
    },
  ]

  const filteredTasks: UxTaskItem[] =
    roleFocus === 'dispatch'
      ? [taskItems[0], taskItems[2], taskItems[3]]
      : roleFocus === 'fracht'
        ? [taskItems[1], taskItems[2]]
        : roleFocus === 'chain'
          ? [taskItems[2], taskItems[3]]
          : taskItems

  const contextSections = [
    {
      title: 'Touren (Kurz)',
      items: [
        { label: 'Heute', value: String(touren.heute) },
        { label: 'Geplant', value: String(touren.offen) },
        { label: 'Unterwegs', value: String(touren.unterwegs) },
      ],
    },
    {
      title: 'Fracht (Kurz)',
      items: [
        { label: 'Gesamt', value: String(list.length) },
        { label: 'Erstellt', value: String(frachtErstellt) },
        { label: 'Unterwegs', value: String(frachtTransit) },
      ],
    },
    {
      title: 'Kette',
      items: [
        { label: 'Gesperrte Chargen', value: String(chain.blockedCharges) },
        { label: 'Naechster Schritt', value: transferSummary.nextAction },
      ],
    },
  ]

  const filteredContext =
    roleFocus === 'dispatch'
      ? [contextSections[0], contextSections[1]]
      : roleFocus === 'fracht'
        ? [contextSections[1], contextSections[2]]
        : roleFocus === 'chain'
          ? [contextSections[2], contextSections[0]]
          : contextSections

  const timelineItems = [
    {
      label: 'Tourenlage',
      detail: touren.tourenListe.length
        ? touren.tourenListe
            .slice(0, 3)
            .map((t) => `${t.vehicleLabel || t.id.slice(0, 8)}: ${tourStatusShort(t)}`)
            .join(' · ')
        : 'Keine Touren in der API-Sicht.',
    },
    {
      label: 'Frachtlage',
      detail:
        list.length > 0
          ? `${frachtErstellt} erstellt, ${frachtTransit} unterwegs, ${frachtZugestellt} zugestellt`
          : 'Keine Frachtbriefe in der API-Sicht.',
    },
    {
      label: 'Kettenrisiko',
      detail: `${transferSummary.handoverRisk} offene Kettenpunkte — ${transferSummary.nextAction}`,
    },
  ]

  const filteredTimeline =
    roleFocus === 'dispatch'
      ? [timelineItems[0]]
      : roleFocus === 'fracht'
        ? [timelineItems[1]]
        : roleFocus === 'chain'
          ? [timelineItems[2]]
          : timelineItems

  const capabilities = [
    { key: 'tour-read', label: 'Touren lesen', available: true, hint: 'API /logistik/tours.' },
    { key: 'tour-storno', label: 'Tour-Storno', available: touren.offen > 0, hint: 'In der Tourenplanung (GEPLANT, fail-closed).' },
    { key: 'fracht-read', label: 'Frachtbriefe lesen', available: list.length > 0, hint: 'Liste und Detailnavigation.' },
    { key: 'ls-resolve', label: 'Lieferschein-Resolve', available: true, hint: 'Tourenplanung: Referenz zu domain_sales.' },
    {
      key: 'freight-sim',
      label: 'Frachtkosten simulieren',
      available: tariffRows.length > 0,
      hint: 'domain_logistics.freight_tariffs; GET /freight-cost/simulate.',
    },
  ]

  const hasWorkload = touren.heute > 0 || list.length > 0
  const decisionAllowed = !transportBlocked && hasWorkload

  return (
    <div className="space-y-6 p-3 md:p-6">
      <OperationalCaseHeader
        title="Tour & Fracht — Dispo-Arbeitsraum"
        description="Gemeinsame operative Sicht auf Liefertouren und Frachtbriefe; Details in den Unterseiten."
        status={operationalStatus}
        owner="Logistikdisposition"
        blocker={transportBlocked ? `${chain.blockedCharges} gesperrte Chargen.` : null}
        nextAction={nextAction}
        caseLabel="Physische Kette"
        tags={['Logistik', 'Tour', 'Fracht']}
      />

      <RoleFocusBar
        roles={combinedRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 4 : 1}
        totalCount={4}
      />

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <OperationalTaskPlan title="Kombinierte Dispo-Checks" items={filteredTasks} />
        <NextActionPanel
          action={nextAction}
          tone={
            transportBlocked ? 'red' : frachtErstellt > 0 || touren.offen > 0 ? 'amber' : touren.unterwegs > 0 || frachtTransit > 0 ? 'blue' : 'emerald'
          }
        />
      </div>

      <ManagementDecisionPanel
        decision={{
          allowed: decisionAllowed,
          allowedLabel: 'Operative Bearbeitung moeglich',
          blockedLabel: transportBlocked ? 'Transport blockiert' : 'Kein Dispo-Bestand sichtbar',
          summary: transportBlocked
            ? 'Charge-Sperren haben Vorrang vor Versand und Tourstart.'
            : hasWorkload
              ? 'Touren und Frachtbriefe sind in der API-Sicht vorhanden — Abstimmung in den Detailmasken.'
              : 'Wenig oder keine Daten — Seeds oder Stammdaten pruefen.',
          blockerCount: transportBlocked ? chain.blockedCharges : hasWorkload ? 0 : 1,
          nextFocus: nextAction,
          template: { label: 'Tourenplanung oeffnen', href: '/logistik/tourenplanung' },
        }}
      />

      <div className="flex flex-wrap gap-2">
        <Button type="button" variant="outline" size="sm" onClick={() => navigate('/logistik/frachtbriefe')}>
          Zu Frachtbriefen
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => navigate('/logistik/frachttabellen')}>
          Frachttabellen
        </Button>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <OperationalTimeline title="Lage in einem Blick" items={filteredTimeline} />
        <OperationalContextPanel sections={filteredContext} />
      </div>

      <CrudCapabilityChecklist capabilities={capabilities} />

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Calculator className="h-5 w-5" />
              Frachtkosten (Kurz)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              Tarife in <code className="rounded bg-muted px-1 text-xs">domain_logistics</code>
              {tariffsLoading ? ' — wird geladen…' : `: ${tariffRows.length} Zeile(n).`}
            </p>
            {firstCarrierId ? (
              <p className="text-xs text-muted-foreground">
                Probe mit erstem Spediteur <span className="font-mono">{firstCarrierId}</span>, 100 kg, 100 km,
                PLZ 10115→20095.
              </p>
            ) : null}
            <Button type="button" size="sm" disabled={probeBusy || !firstCarrierId} onClick={() => void handleFreightProbe()}>
              {probeBusy ? 'Rechnet…' : 'Probe berechnen'}
            </Button>
            {probeResult ? (
              <div className="rounded-md border bg-muted/40 p-2 text-xs">
                <div>
                  <span className="font-medium">Kosten:</span> {probeResult.eur} €
                </div>
                {probeResult.zone ? (
                  <div>
                    <span className="font-medium">Zone:</span> {probeResult.zone}
                  </div>
                ) : null}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Truck className="h-5 w-5" />
              Touren
            </CardTitle>
            <Button type="button" variant="outline" size="sm" onClick={() => navigate('/logistik/tourenplanung')}>
              Zur Tourenplanung
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {touren.tourenListe.slice(0, 5).map((t) => (
              <div key={t.id} className="flex items-center justify-between rounded border px-3 py-2 text-sm">
                <span className="font-medium">{t.vehicleLabel || t.id.slice(0, 8)}</span>
                <Badge variant="outline">{tourStatusShort(t)}</Badge>
              </div>
            ))}
            {touren.tourenListe.length === 0 ? (
              <p className="text-sm text-muted-foreground">Keine Touren gelistet.</p>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <MapPin className="h-5 w-5" />
              Frachtbriefe
            </CardTitle>
            <Button type="button" variant="outline" size="sm" onClick={() => navigate('/logistik/frachtbriefe')}>
              Zu Frachtbriefen
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {list.slice(0, 5).map((f: Frachtbrief) => (
              <div key={f.id} className="flex items-center justify-between rounded border px-3 py-2 text-sm">
                <span className="font-mono font-medium">{f.nummer}</span>
                <Badge variant={f.status === 'zugestellt' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>
                  {f.status === 'erstellt' ? 'Erstellt' : f.status === 'unterwegs' ? 'Unterwegs' : 'Zugestellt'}
                </Badge>
              </div>
            ))}
            {list.length === 0 ? <p className="text-sm text-muted-foreground">Keine Frachtbriefe gelistet.</p> : null}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <LayoutGrid className="h-4 w-4" />
        <span>Vollstaendige Frachtkosten-API: POST /freight-cost/calculate vs. GET simulate (ohne Buchung).</span>
      </div>
    </div>
  )
}
