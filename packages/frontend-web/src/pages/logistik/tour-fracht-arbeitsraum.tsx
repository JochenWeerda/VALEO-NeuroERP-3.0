import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
/**
 * Kombinierter Dispo-Arbeitsraum Tour + Frachtbrief.
 * Die Definition zeichnet die Lage. Die Seite laedt Daten und loest Aktionen aus.
 */
import { useCallback, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CrudCapabilityChecklist,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { useTenant } from '@/hooks/useTenant'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { cancelFreightTariff, listFreightTariffs, simulateFreightCost, type FreightTariffRow } from '@/lib/api/logistics-freight'
import { useFrachtbriefe, useTouren, type Tour } from '@/lib/api/misc-modules'
import { dispositionsstand } from '@/lib/logistik/disposition'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { tourFrachtArbeitsraumScreen } from '@/masks/capture-screens'

type CombinedRoleFocus = 'all' | 'dispatch' | 'fracht' | 'chain'

const combinedRoleProfiles: Array<{ id: CombinedRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Touren, Frachtbriefe und Kettenrisiko in einem Blick.' },
  { id: 'dispatch', label: 'Disposition', description: 'Fokus auf Tourenplanung, Transit und operative Freigabe.' },
  { id: 'fracht', label: 'Fracht / Doku', description: 'Fokus auf Frachtbriefe, Versand und Frachtkosten-Check.' },
  { id: 'chain', label: 'Objektkette', description: 'Fokus auf Annahme, Waage, Sperren und Kettenfokus.' },
]

function tourStatusShort(t: Tour): string {
  if (t.status === 'unterwegs') return 'Unterwegs'
  if (t.status === 'abgeschlossen') return 'Abgeschlossen'
  if (t.status === 'storniert') return 'Storniert'
  return 'Geplant'
}

function isTariffActive(row: FreightTariffRow): boolean {
  return (row.status ?? 'AKTIV').toString().toUpperCase() === 'AKTIV'
}

function canCancelOwnTariff(row: FreightTariffRow, tenant: string): boolean {
  if (!isTariffActive(row)) return false
  const tid = row.tenant_id
  if (tid == null || tid === '') return false
  return tid === tenant
}

export default function TourFrachtArbeitsraumPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const { tenantId } = useTenant()
  const [roleFocus, setRoleFocus] = useState<CombinedRoleFocus>('all')
  const [probeBusy, setProbeBusy] = useState(false)
  const [probeText, setProbeText] = useState('—')
  const [cancelTarget, setCancelTarget] = useState<FreightTariffRow | null>(null)
  const [cancelBusy, setCancelBusy] = useState(false)

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
  const activeTariffs = useMemo(() => tariffRows.filter((row) => isTariffActive(row)), [tariffRows])
  const firstCarrierId = useMemo(() => {
    const carrier = activeTariffs[0]?.carrier_id
    return typeof carrier === 'string' && carrier.length > 0 ? carrier : null
  }, [activeTariffs])

  const stand = useMemo(() => dispositionsstand(
    (touren?.tourenListe ?? []).map((tour) => ({
      datum: tour.datum,
      status: tour.status,
      fahrzeug: tour.vehicleLabel,
      fahrer: tour.fahrer,
    })),
    (chain?.blockedCharges ?? 0) > 0,
  ), [chain?.blockedCharges, touren])

  const workflow = useMemo<WorkflowState>(() => {
    const ohneBestand = stand.status === 'keine' && list.length === 0
    const label = stand.status === 'gesperrt' || stand.status === 'offen'
      ? 'Disposition offen'
      : ohneBestand
        ? 'Kein Bestand'
        : 'Operative Bearbeitung möglich'
    const naechste = stand.status === 'gesperrt'
      ? 'Gesperrte Charge klären.'
      : frachtErstellt > 0
        ? `${frachtErstellt} Frachtbriefe auf Versand prüfen.`
        : stand.naechste
    return {
      status: {
        currentStatus: ohneBestand ? 'keine' : stand.status,
        statusLabel: label,
        tone: stand.tone === 'success' && !ohneBestand ? 'success' : stand.status === 'gesperrt' ? 'danger' : 'warning',
      },
      nextAllowedActions: [{ actionKey: 'touren', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: label === 'Operative Bearbeitung möglich' ? [] : [{ code: stand.status, message: naechste, blocking: true }],
      auditTrail: [],
      policyHints: [],
      isBlocked: stand.status === 'gesperrt',
      isTerminal: false,
    }
  }, [frachtErstellt, list.length, stand])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...tourFrachtArbeitsraumScreen,
    layout: {
      ...tourFrachtArbeitsraumScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (tourFrachtArbeitsraumScreen.summary ?? []).map((item) => {
      const wert = item.key === 'heute'
        ? touren?.heute
        : item.key === 'geplant'
          ? touren?.offen
          : item.key === 'fracht'
            ? list.length
            : item.key === 'tarife'
              ? activeTariffs.length
              : probeText
      return { ...item, value: item.key === 'probe' ? probeText : String(wert ?? 0) }
    }),
    actions: (tourFrachtArbeitsraumScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'probe' ? probeBusy || !firstCarrierId || tariffsLoading : false,
    })),
  }), [activeTariffs.length, firstCarrierId, isTouch, list.length, probeBusy, probeText, tariffsLoading, touren])

  const permissions = useScreenPermissions(schema)
  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema, { permissions }), [schema, permissions])

  const handleFreightProbe = useCallback(async () => {
    if (!firstCarrierId) {
      toast({ title: 'Kein Tarif', description: 'Kein Spediteur in der Tarifliste.', variant: 'destructive' })
      return
    }
    setProbeBusy(true)
    try {
      const res = await simulateFreightCost({
        carrier_id: firstCarrierId,
        distance_km: 100,
        weight_kg: 100,
        postal_code_from: '10115',
        postal_code_to: '20095',
      })
      const text = `${res.freight_cost_eur} €`
      setProbeText(res.zone ? `${text}, ${res.zone}` : text)
      toast({ title: 'Simulation', description: `${res.freight_cost_eur} € (${res.carrier_id})` })
    } catch (e) {
      toast({ title: 'Simulation fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setProbeBusy(false)
    }
  }, [firstCarrierId, toast])

  const handleConfirmTariffCancel = useCallback(async () => {
    const id = typeof cancelTarget?.id === 'string' ? cancelTarget.id : ''
    if (!id) return
    setCancelBusy(true)
    try {
      await cancelFreightTariff(id, { grund: 'Dispo-Arbeitsraum' })
      toast({ title: 'Tarif storniert', description: 'Die Zeile wird nicht mehr fuer Kostenberechnungen verwendet.' })
      await queryClient.invalidateQueries({ queryKey: ['logistik', 'freight-tariffs'] })
      setCancelTarget(null)
    } catch (e) {
      toast({ title: 'Storno fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setCancelBusy(false)
    }
  }, [cancelTarget?.id, queryClient, toast])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'touren') {
      navigate('/logistik/tourenplanung')
      return
    }
    if (key === 'fracht') {
      navigate('/logistik/frachtbriefe')
      return
    }
    if (key === 'tabellen') {
      navigate('/logistik/frachttabellen')
      return
    }
    if (key === 'probe') {
      await handleFreightProbe()
      return
    }
    if (key === 'storno') {
      const row = tariffRows.find((tariff) => tariff.id === payload.id)
      if (row && canCancelOwnTariff(row, tenantId)) setCancelTarget(row)
    }
  }, [handleFreightProbe, navigate, tariffRows, tenantId])

  if (tourenLoading || frachtLoading || !touren) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="min-h-touch h-40" />
      </div>
    )
  }

  const lage = chain ?? { blockedCharges: 0, waitingInbound: 0, openWeighingTickets: 0, activeVehiclePlates: [] as string[] }
  const transportBlocked = lage.blockedCharges > 0
  const taskItems: UxTaskItem[] = [
    { label: 'Touren disponieren', done: touren.heute > 0, hint: touren.heute > 0 ? `${touren.heute} Tour(en) heute in der Liste.` : 'Tourenplanung oeffnen und Tagesplan pflegen.' },
    { label: 'Frachtbriefe versenden', done: frachtErstellt === 0 && list.length > 0, hint: frachtErstellt > 0 ? `${frachtErstellt} Frachtbrief(e) noch nicht versendet.` : 'Keine offenen Frachtbriefe in der Sicht.' },
    { label: 'Transit ueberwachen', done: touren.unterwegs > 0 || frachtTransit > 0, hint: `${touren.unterwegs} Tour(en) unterwegs, ${frachtTransit} Frachtbrief(e) in Transit.` },
    { label: 'Kettenfokus', done: !transportBlocked, hint: transferSummary.nextAction },
  ]
  const filteredTasks = roleFocus === 'dispatch'
    ? [taskItems[0], taskItems[2], taskItems[3]]
    : roleFocus === 'fracht'
      ? [taskItems[1], taskItems[2]]
      : roleFocus === 'chain'
        ? [taskItems[2], taskItems[3]]
        : taskItems
  const timelineItems = [
    { label: 'Tourenlage', detail: touren.tourenListe.slice(0, 3).map((tour) => `${tour.vehicleLabel || tour.id.slice(0, 8)}: ${tourStatusShort(tour)}`).join(' · ') || 'Keine Touren in der API-Sicht.' },
    { label: 'Frachtlage', detail: list.length > 0 ? `${frachtErstellt} erstellt, ${frachtTransit} unterwegs` : 'Keine Frachtbriefe in der API-Sicht.' },
    { label: 'Kettenrisiko', detail: `${transferSummary.handoverRisk} offene Kettenpunkte — ${transferSummary.nextAction}` },
  ]

  return (
    <div className="space-y-6 p-3 md:p-6">
      <UniversalMaskRenderer
        plan={plan}
        allowedPermissions={permissions}
        workflowState={workflow}
        tables={{
          touren: touren.tourenListe.map((tour) => ({
            id: tour.id,
            ziel: tour.zieladresse || tour.id.slice(0, 8),
            status: tour.status,
            fahrzeug: tour.vehicleLabel ?? '',
            stopps: tour.stopps,
          })),
          fracht: list.map((brief) => ({
            id: brief.id,
            nummer: brief.nummer,
            status: brief.status,
            kennzeichen: brief.kennzeichen,
            empfaenger: brief.empfaenger,
          })),
          tarife: tariffRows.map((row) => ({
            id: typeof row.id === 'string' ? row.id : String(row.carrier_id ?? ''),
            carrier: typeof row.carrier_id === 'string' ? row.carrier_id : '',
            status: isTariffActive(row) ? 'aktiv' : 'storniert',
            preis: row.price_per_100kg ?? '',
            stornierbar: canCancelOwnTariff(row, tenantId),
          })),
        }}
        onAction={handleAction}
      />

      <AlertDialog open={cancelTarget != null} onOpenChange={(open) => { if (!open && !cancelBusy) setCancelTarget(null) }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Fracht-Tarif stornieren?</AlertDialogTitle>
            <AlertDialogDescription>
              Spediteur <span className="font-mono">{typeof cancelTarget?.carrier_id === 'string' ? cancelTarget.carrier_id : ''}</span>. Stornierte Zeilen fallen aus der Simulation.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="min-h-touch" disabled={cancelBusy}>Abbrechen</AlertDialogCancel>
            <Button type="button" variant="destructive" className="min-h-touch" disabled={cancelBusy} onClick={() => void handleConfirmTariffCancel()}>
              {cancelBusy ? 'Wird ausgefuehrt…' : 'Stornieren'}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {!isTouch ? (
        <>
          <RoleFocusBar roles={combinedRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 4 : 1} totalCount={4} />
          <OperationalTaskPlan title="Kombinierte Dispo-Checks" items={filteredTasks} />
          <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
            <OperationalTimeline title="Lage in einem Blick" items={roleFocus === 'dispatch' ? [timelineItems[0]] : roleFocus === 'fracht' ? [timelineItems[1]] : roleFocus === 'chain' ? [timelineItems[2]] : timelineItems} />
            <OperationalContextPanel sections={[
              { title: 'Touren', items: [{ label: 'Heute', value: String(touren.heute) }, { label: 'Geplant', value: String(touren.offen) }] },
              { title: 'Fracht', items: [{ label: 'Gesamt', value: String(list.length) }, { label: 'Erstellt', value: String(frachtErstellt) }] },
              { title: 'Kette', items: [{ label: 'Gesperrte Chargen', value: String(lage.blockedCharges) }] },
            ]} />
          </div>
          <CrudCapabilityChecklist capabilities={[
            { key: 'tour-read', label: 'Touren lesen', available: true, hint: 'API /logistik/tours.' },
            { key: 'fracht-read', label: 'Frachtbriefe lesen', available: list.length > 0, hint: 'Liste und Detailnavigation.' },
            { key: 'freight-sim', label: 'Frachtkosten simulieren', available: activeTariffs.length > 0, hint: 'GET /freight-cost/simulate.' },
            { key: 'freight-tariff-storno', label: 'Fracht-Tarif stornieren', available: tariffRows.some((row) => canCancelOwnTariff(row, tenantId)), hint: 'Nur Mandanten-Tarife.' },
          ]} />
        </>
      ) : null}
    </div>
  )
}
