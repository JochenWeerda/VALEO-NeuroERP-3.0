import { useCallback, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { useTouren, type Tour } from '@/lib/api/misc-modules'
import { streckeText } from '@/lib/logistik/strecke'
import { dispositionsstand, type Dispositionsstand } from '@/lib/logistik/disposition'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import {
  cancelLogisticsTour,
  createLogisticsTour,
  zielortFuerKunde,
  fetchTourWithDeliveryHints,
  resolveSalesDeliveryNoteByRef,
  type DeliveryNoteHint,
} from '@/lib/api/logistics-tours'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { tourenplanungScreen } from '@/masks/capture-screens'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'

const DISPO_ARBEITSRAUM = 'Dispo-Arbeitsraum'
const DISPO_ROUTE = '/logistik/tour-fracht-arbeitsraum'

type LogisticsRoleFocus = 'all' | 'dispatch' | 'driver' | 'warehouse-scale' | 'quality' | 'management'

function tourStatusLabel(status: string): string {
  switch (status) {
    case 'unterwegs':
      return 'Unterwegs'
    case 'geplant':
      return 'Geplant'
    case 'abgeschlossen':
      return 'Abgeschlossen'
    case 'storniert':
      return 'Storniert'
    default:
      return status
  }
}

const logisticsRoleProfiles: Array<{ id: LogisticsRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt die Tourenlage fuer Disposition, Fahrer, Lager/Waage, QS und Leitung.' },
  { id: 'dispatch', label: 'Disposition', description: 'Fokus auf offene Touren, Ressourcen und naechste Dispo-Entscheidung.' },
  { id: 'driver', label: 'Fahrer', description: 'Fokus auf aktive Touren, Stopps, Kilometer und Status.' },
  { id: 'warehouse-scale', label: 'Lager/Waage', description: 'Fokus auf wartende Annahmen, offene Wiegungen und aktive Kennzeichen.' },
  { id: 'quality', label: 'QS', description: 'Fokus auf gesperrte Chargen und Transportblocker.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Auslastung, Engpaesse und operative Prioritaet.' },
]

function workflowAusStand(stand: Dispositionsstand): WorkflowState {
  return {
    status: { currentStatus: stand.status, statusLabel: stand.label, tone: stand.tone },
    nextAllowedActions: [{
      actionKey: stand.status === 'disponierbar' ? 'beladung' : 'anlegen',
      label: stand.naechste,
      dangerLevel: 'safe',
      requiresConfirmation: false,
    }],
    blockingReasons: stand.status === 'disponierbar' ? [] : [{
      code: stand.status,
      message: stand.naechste,
      blocking: true,
    }],
    auditTrail: [],
    policyHints: [],
    isBlocked: stand.status === 'gesperrt',
    isTerminal: false,
  }
}

export default function TourenplanungPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [roleFocus, setRoleFocus] = useState<LogisticsRoleFocus>('all')
  const [lsBusy, setLsBusy] = useState(false)
  const [lsResult, setLsResult] = useState<DeliveryNoteHint | null>(null)
  const [tourBusy, setTourBusy] = useState(false)
  const [hintTourId, setHintTourId] = useState<string | null>(null)
  const [hintText, setHintText] = useState('')
  const [hintBusy, setHintBusy] = useState(false)
  const [tourCancelTarget, setTourCancelTarget] = useState<Tour | null>(null)
  const [tourCancelGrund, setTourCancelGrund] = useState('')
  const [tourCancelSubmitting, setTourCancelSubmitting] = useState(false)
  const { data: touren, isLoading } = useTouren()
  const { data: fahrzeuge = [] } = useQuery({
    queryKey: ['fuhrpark', 'fahrzeuge', 'tour'],
    queryFn: async () => {
      const { data } = await apiClient.get<Array<{ id: string; kennzeichen?: string; status?: string }>>('/api/v1/fuhrpark/fahrzeuge')
      return Array.isArray(data) ? data : []
    },
  })
  const { data: fahrer = [] } = useQuery({
    queryKey: ['transporte', 'fahrer', 'tour'],
    queryFn: async () => {
      const { data } = await apiClient.get<Array<{ id: string; name?: string; vorname?: string }>>('/api/v1/transporte/fahrer')
      return Array.isArray(data) ? data : []
    },
  })
  const { data: chain } = useSupplyChainOverview()

  const schema = useMemo<ScreenDefinition>(() => ({
    ...tourenplanungScreen,
    layout: {
      ...tourenplanungScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    fields: (tourenplanungScreen.fields ?? []).map((field) => {
      if (field.key === 'fahrzeug_id') {
        return {
          ...field,
          options: [
            { value: '', label: 'Kein Fahrzeug' },
            ...fahrzeuge.map((fahrzeug) => ({ value: fahrzeug.id, label: fahrzeug.kennzeichen || fahrzeug.id })),
          ],
        }
      }
      if (field.key === 'fahrer_id') {
        return {
          ...field,
          options: [
            { value: '', label: 'Kein Fahrer' },
            ...fahrer.map((person) => ({
              value: person.id,
              label: [person.vorname, person.name].filter(Boolean).join(' ') || person.id,
            })),
          ],
        }
      }
      return field
    }),
    summary: (tourenplanungScreen.summary ?? []).map((item) => {
      const wert = item.key === 'heute'
        ? touren?.heute
        : item.key === 'geplant'
          ? touren?.offen
          : item.key === 'unterwegs'
            ? touren?.unterwegs
            : item.key === 'abgeschlossen'
              ? touren?.abgeschlossen
              : 0
      return { ...item, value: String(wert ?? 0) }
    }),
    actions: (tourenplanungScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'aufloesen' ? lsBusy || tourBusy : action.key === 'anlegen' ? tourBusy || lsBusy || !lsResult?.delivery_note_number : false,
    })),
  }), [fahrer, fahrzeuge, isTouch, lsBusy, lsResult, tourBusy, touren])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({
    screen: schema,
    initialValues: {
      datum: new Date().toISOString().slice(0, 10),
      tour_id: '',
      tour_status: '',
      ziel: '',
      lieferschein: '',
      fahrzeug_id: '',
      fahrer_id: '',
    },
  })

  const stand = useMemo(() => dispositionsstand(
    (touren?.tourenListe ?? []).map((tour) => ({
      datum: tour.datum,
      status: tour.status,
      fahrzeug: tour.vehicleLabel,
      fahrer: tour.fahrer,
    })),
    (chain?.blockedCharges ?? 0) > 0,
  ), [chain?.blockedCharges, touren])

  const rows = useMemo(() => (touren?.tourenListe ?? []).map((tour) => {
    const fahrzeug = fahrzeuge.find((eintrag) => eintrag.id === tour.vehicleLabel)
    const person = fahrer.find((eintrag) => eintrag.id === tour.fahrer)
    const fahrerName = person
      ? [person.vorname, person.name].filter(Boolean).join(' ')
      : tour.fahrer === '—' ? '' : tour.fahrer
    return {
      id: tour.id,
      datum: tour.datum,
      ziel: tour.zieladresse ?? '',
      kennzeichen: fahrzeug?.kennzeichen || '',
      fahrer_name: fahrerName,
      fahrzeug_id: tour.vehicleLabel ?? '',
      fahrer_id: tour.fahrer === '—' ? '' : tour.fahrer,
      status: tour.status,
      stopps: tour.stopps,
      strecke: streckeText(tour.km),
      lieferscheinRef: tour.lieferscheinRef ?? '',
    }
  }), [fahrer, fahrzeuge, touren])

  const handleResolveLs = useCallback(async () => {
    const ref = String(form.values.lieferschein ?? '').trim()
    if (!ref) {
      toast({ title: 'Referenz fehlt', description: 'Bitte Lieferschein-Nummer oder ID eintragen.', variant: 'destructive' })
      return
    }
    setLsBusy(true)
    setLsResult(null)
    try {
      const h = await resolveSalesDeliveryNoteByRef(ref)
      setLsResult(h)
      const lage = h.customer_id ? await zielortFuerKunde(h.customer_id) : { address: null, lat: null, lng: null }
      form.setValue('lieferschein', h.delivery_note_number || ref)
      form.setValue('ziel', lage.address ?? '')
      if (!form.values.tour_id) form.setValue('tour_status', 'neu')
      toast({ title: 'Lieferschein gefunden', description: h.delivery_note_number || h.id })
    } catch (e) {
      toast({ title: 'Aufloesung fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setLsBusy(false)
    }
  }, [form, toast])

  const handleCreateTour = useCallback(async () => {
    const nr = lsResult?.delivery_note_number?.trim()
    if (!nr) {
      toast({ title: 'Lieferschein fehlt', description: 'Zuerst die Referenz aufloesen.', variant: 'destructive' })
      return
    }
    setTourBusy(true)
    try {
      const lage = lsResult?.customer_id
        ? await zielortFuerKunde(lsResult.customer_id)
        : { address: null, lat: null, lng: null }
      const fahrzeugId = String(form.values.fahrzeug_id ?? '')
      const fahrerId = String(form.values.fahrer_id ?? '')
      const created = await createLogisticsTour({
        date: new Date().toISOString(),
        vehicle_id: fahrzeugId || null,
        driver_id: fahrerId || null,
        notes: `Disposition aus Lieferschein ${  nr}`,
        stops: [{
          stop_order: 0,
          delivery_note_ref: nr,
          customer_id: lsResult?.customer_id ?? null,
          address: lage.address,
          lat: lage.lat,
          lng: lage.lng,
        }],
      })
      await queryClient.invalidateQueries({ queryKey: ['logistik', 'touren'] })
      form.setValue('tour_id', created.id.slice(0, 8))
      form.setValue('tour_status', 'Geplant')
      toast({ title: 'Tour angelegt', description: created.id })
    } catch (e) {
      toast({ title: 'Tour nicht angelegt', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setTourBusy(false)
    }
  }, [form, lsResult, queryClient, toast])

  const handleTourHints = useCallback(async (tourId: string) => {
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
  }, [toast])

  const handleConfirmTourCancel = useCallback(async () => {
    if (!tourCancelTarget) return
    setTourCancelSubmitting(true)
    try {
      const grund = tourCancelGrund.trim()
      await cancelLogisticsTour(tourCancelTarget.id, grund ? { grund } : {})
      await queryClient.invalidateQueries({ queryKey: ['logistik', 'touren'] })
      toast({ title: 'Tour storniert', description: tourCancelTarget.vehicleLabel || tourCancelTarget.id.slice(0, 8) })
      setTourCancelTarget(null)
      setTourCancelGrund('')
    } catch (e) {
      toast({ title: 'Storno fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    } finally {
      setTourCancelSubmitting(false)
    }
  }, [queryClient, toast, tourCancelGrund, tourCancelTarget])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'dispo') {
      navigate(DISPO_ROUTE)
      return
    }
    if (key === 'aufloesen') {
      await handleResolveLs()
      return
    }
    if (key === 'anlegen') {
      await handleCreateTour()
      return
    }
    if (key === 'beladung') {
      const ref = String(payload.lieferscheinRef ?? '').trim()
      if (!ref) {
        toast({ title: 'Kein Lieferschein', description: 'Diese Tour hat keinen Lieferschein.', variant: 'destructive' })
        return
      }
      navigate(`/verladung/lkw-beladung?lieferschein=${encodeURIComponent(ref)}`)
      return
    }
    if (key === 'hinweise') {
      await handleTourHints(String(payload.id ?? ''))
      return
    }
    if (key === 'storno') {
      const tour = touren?.tourenListe.find((eintrag) => eintrag.id === payload.id)
      if (!tour) return
      setTourCancelGrund('')
      setTourCancelTarget(tour)
    }
  }, [handleCreateTour, handleResolveLs, handleTourHints, navigate, toast, touren])

  const screenContext = useMemo(() => createScreenContext({
    data: { tours: rows },
    permissions: { granted: [] },
    state: {
      values: form.values,
      policies: {
        'tour.canCreate': Boolean(lsResult?.delivery_note_number) && !tourBusy && !lsBusy,
      },
    },
    actions: {
      'tour.openWorkspace': (payload) => handleAction('dispo', payload),
      'tour.resolveDeliveryNote': (payload) => handleAction('aufloesen', payload),
      'tour.create': (payload) => handleAction('anlegen', payload),
      'tour.openLoading': (payload) => handleAction('beladung', payload),
      'tour.showHints': (payload) => handleAction('hinweise', payload),
      'tour.cancel': (payload) => handleAction('storno', payload),
    },
    navigation: { push: (route) => navigate(route) },
  }), [form.values, handleAction, lsBusy, lsResult, navigate, rows, tourBusy])

  const selectRow = useCallback((row: Record<string, unknown>) => {
    form.setValue('datum', String(row.datum ?? ''))
    form.setValue('tour_id', String(row.id ?? '').slice(0, 8))
    form.setValue('tour_status', tourStatusLabel(String(row.status ?? '')))
    form.setValue('ziel', String(row.ziel ?? ''))
    form.setValue('lieferschein', String(row.lieferscheinRef ?? ''))
    form.setValue('fahrzeug_id', String(row.fahrzeug_id ?? ''))
    form.setValue('fahrer_id', String(row.fahrer_id ?? ''))
  }, [form])

  if (isLoading || !touren) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  const lage = chain ?? { blockedCharges: 0, waitingInbound: 0, openWeighingTickets: 0, activeVehiclePlates: [] as string[] }
  const transportBlocked = lage.blockedCharges > 0
  const nextTourAction = stand.naechste
  const tourTaskItems: UxTaskItem[] = [
    {
      label: 'Tour planen',
      done: touren.heute > 0,
      hint: touren.heute > 0 ? `${touren.heute} Touren fuer heute vorhanden.` : 'Neue Tour fuer den Tag anlegen.',
    },
    {
      label: 'Ressourcen klaeren',
      done: stand.status === 'disponierbar',
      hint: nextTourAction,
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
        { label: 'Wartende Annahmen', value: String(lage.waitingInbound) },
        { label: 'Offene Wiegungen', value: String(lage.openWeighingTickets) },
        { label: 'Aktive Fahrzeuge', value: String(lage.activeVehiclePlates.length) },
      ],
    },
  ]
  const timelineItems = touren.tourenListe.slice(0, 4).map((tour) => ({
    label: `${tour.vehicleLabel || tour.id.slice(0, 8)} - ${tourStatusLabel(tour.status)}`,
    detail: `${tour.fahrer}, ${tour.stopps} Stopps, ${streckeText(tour.km)}`,
  }))

  return (
    <div className="space-y-6 p-3 md:p-6" data-dispo={DISPO_ARBEITSRAUM}>
      <AlertDialog
        open={tourCancelTarget !== null}
        onOpenChange={(open) => {
          if (!open && !tourCancelSubmitting) {
            setTourCancelTarget(null)
            setTourCancelGrund('')
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Tour stornieren?</AlertDialogTitle>
            <AlertDialogDescription>
              Die API erlaubt Storno nur fuer Touren im Status <strong>GEPLANT</strong> ohne gelieferte Stopps.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-2 py-2">
            <Label htmlFor="tour-storno-grund">Grund (optional)</Label>
            <Input
              id="tour-storno-grund"
              value={tourCancelGrund}
              onChange={(e) => setTourCancelGrund(e.target.value)}
              placeholder="z. B. Umdisposition, Kundenabsage"
              disabled={tourCancelSubmitting}
              className="min-h-touch"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel type="button" disabled={tourCancelSubmitting}>Abbrechen</AlertDialogCancel>
            <Button type="button" variant="destructive" className="min-h-touch" disabled={tourCancelSubmitting} onClick={() => void handleConfirmTourCancel()}>
              {tourCancelSubmitting ? 'Wird storniert…' : 'Stornieren'}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <UniversalMaskRenderer
        plan={plan}
        formState={form}
        hideFormSubmit
        workflowState={workflowAusStand(stand)}
        tables={{ touren: rows }}
        onAction={handleAction}
        screenContext={screenContext}
        onRowSelect={selectRow}
      />

      {hintTourId ? (
        <div className="rounded-md border p-3 text-sm">
          <div className="mb-1 font-medium">Stopps Tour {hintTourId.slice(0, 8)}…</div>
          <pre className="whitespace-pre-wrap font-sans text-xs text-muted-foreground">{hintText}</pre>
          <Button type="button" variant="ghost" className="mt-2 min-h-touch touch-manipulation" disabled={hintBusy} onClick={() => setHintTourId(null)}>
            Hinweis schliessen
          </Button>
        </div>
      ) : null}

      {!isTouch ? (
        <>
          <RoleFocusBar roles={logisticsRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
          <OperationalTaskPlan title="Dispo-Aufgabenplan" items={tourTaskItems} />
          <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
            <OperationalTimeline title="Tourenlage" items={timelineItems} />
            <OperationalContextPanel sections={contextSections} />
          </div>
          <CrudCapabilityChecklist capabilities={[
            { key: 'create', label: 'Anlegen', available: true, hint: 'Eine Tour entsteht aus einem aufgeloesten Lieferschein.' },
            { key: 'read', label: 'Lesen', available: true, hint: 'Touren, Fahrer, Stopps und Status sind sichtbar.' },
            { key: 'update', label: 'Disponieren', available: touren.offen + touren.unterwegs > 0, hint: 'Offene und laufende Touren bilden den aktiven Dispo-Bestand.' },
            { key: 'delete', label: 'Storno', available: touren.offen > 0, hint: 'Geplante Touren koennen storniert werden.' },
            { key: 'approve', label: 'Transportfreigabe', available: !transportBlocked, hint: transportBlocked ? 'Gesperrte Chargen blockieren die Freigabe.' : 'Keine Chargensperre blockiert die aktuelle Sicht.' },
          ]} />
        </>
      ) : null}
    </div>
  )
}
