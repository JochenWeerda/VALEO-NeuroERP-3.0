import { useCallback, useMemo, useRef, useState } from 'react'
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import { useQuery } from '@tanstack/react-query'
import { useTouren, type Tour } from '@/lib/api/misc-modules'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { useTenant } from '@/hooks/useTenant'
import type { User } from '@/lib/auth'
import { orderDragId, resolveBoardDrop, resourceDropId, timelineDropId } from './board-dnd'
import { fetchOpenAbrufe } from './load-abrufe'
import {
  TIMELINE_FIELD_MISSING,
  axisFromLanes,
  fetchTimelineLanes,
  formatStopLatLng,
  markerOffset,
  type TimelineLane,
} from './load-timeline'
import { OPS_AUTH_ERROR, fetchOpenScaleOccupancy, mergeOpsSignals } from './ops-signals'
import { DispositionAssignmentError, postDispositionAssignment } from './post-assignment'
import { DispositionStopMap } from './stop-map'
import { DISPOSITION_BOARD_EVENTS, type SpecializedComponentProps } from './types'
import { useWorkspaceTourCreated } from './workspace-tour-sse'

export type DispositionOrderCard = {
  id: string
  label: string
  quantity: number
  contractId?: string
  abrufId?: string
}

export type DispositionResourceLane = {
  id: string
  label: string
  driver?: string
  vehicle?: string
  status?: string
}

export type DispositionOperationItem = {
  id: string
  label: string
  value: string
  tone: 'neutral' | 'warning' | 'danger'
}

export type DispositionBoardModel = {
  orders: DispositionOrderCard[]
  resources: DispositionResourceLane[]
  operations: DispositionOperationItem[]
}

const EXISTING_TAFEL_ROUTE = '/logistik/tourenplanung'

// The assignment API is not mounted or approved yet. Releasing this requires
// the server capability and its authorization contract to be accepted first.
export const DISPOSITION_ASSIGNMENT_WRITE_RELEASED = false

export function hasDispositionWriteClaim(user: User | null): boolean {
  if (!user) return false
  const scopes = new Set(user.scopes ?? [])
  const roles = new Set((user.roles ?? []).map((role) => role.toLowerCase().replace(':', '.')))
  return scopes.has('logistics.write') || scopes.has('logistics:write') || scopes.has('admin:all')
    || ['admin', 'logistics', 'logistics.write', 'dispatcher', 'disponent', 'fuhrpark']
      .some((role) => roles.has(role))
}

function toursToModel(
  tours: Tour[],
  operations: DispositionOperationItem[],
  orders: DispositionOrderCard[],
): DispositionBoardModel {
  const unassigned = tours.filter((tour) => !(tour.vehicleLabel ?? '').trim() || tour.fahrer === '—')
  const assigned = tours.filter((tour) => !unassigned.includes(tour))
  return {
    orders,
    resources: (assigned.length > 0 ? assigned : tours).map((tour) => ({
      id: tour.id,
      label: tour.vehicleLabel || `Tour ${tour.id.slice(0, 8)}`,
      driver: tour.fahrer,
      vehicle: tour.vehicleLabel ?? undefined,
      status: tour.status,
    })),
    operations,
  }
}

function toneClass(tone: DispositionOperationItem['tone']): string {
  if (tone === 'danger') return 'text-status-error'
  if (tone === 'warning') return 'text-status-warning'
  return 'text-muted-foreground'
}

function OrderSource({
  order,
  pending,
  canWrite,
}: {
  order: DispositionOrderCard
  pending: boolean
  canWrite: boolean
}): JSX.Element {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: orderDragId(order.id),
    disabled: !canWrite || pending,
    data: { orderId: order.id, abrufId: order.abrufId },
  })
  const style = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` }
    : undefined
  return (
    <button
      ref={setNodeRef}
      type="button"
      disabled={!canWrite || pending}
      aria-busy={pending}
      style={style}
      className={`flex min-h-touch w-full items-center justify-between rounded-md border bg-background px-3 py-2 text-left text-sm ${canWrite ? 'cursor-grab' : 'cursor-default'} disabled:opacity-70 ${isDragging ? 'opacity-70' : ''}`}
      data-testid={`dispo-order-${order.id}`}
      {...listeners}
      {...attributes}
      draggable={canWrite && !pending}
      onDragStart={(event) => {
        if (!canWrite) return
        event.dataTransfer.setData('text/plain', orderDragId(order.id))
        event.dataTransfer.effectAllowed = 'move'
      }}
    >
      <span>{order.label}</span>
      <span className="text-muted-foreground">{order.quantity}</span>
    </button>
  )
}

function ResourceTarget({
  resource,
  canWrite,
  onDropOrder,
}: {
  resource: DispositionResourceLane
  canWrite: boolean
  onDropOrder: (_orderId: string, _resourceId: string) => void
}): JSX.Element {
  const { setNodeRef, isOver } = useDroppable({
    id: resourceDropId(resource.id),
    disabled: !canWrite,
    data: { resourceId: resource.id },
  })
  return (
    <li
      ref={setNodeRef}
      onDragOver={(event) => {
        if (canWrite) event.preventDefault()
      }}
      onDrop={(event) => {
        if (!canWrite) return
        event.preventDefault()
        const mapped = resolveBoardDrop(event.dataTransfer.getData('text/plain'), resourceDropId(resource.id))
        if (mapped) onDropOrder(mapped.orderId, mapped.resourceId)
      }}
      className={`min-h-touch rounded-md border border-dashed px-3 py-2 text-sm ${isOver ? 'border-solid bg-muted/40' : ''}`}
      data-testid={`dispo-resource-${resource.id}`}
    >
      <div className="font-medium">{resource.label}</div>
      <div className="text-muted-foreground">{resource.driver ?? 'Fahrer offen'} · {resource.status ?? 'geplant'}</div>
    </li>
  )
}

function formatAxisTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

function TimelineLaneRow({
  lane,
  axis,
  canWrite,
  onDropOrder,
}: {
  lane: TimelineLane
  axis: { startMs: number; endMs: number }
  canWrite: boolean
  onDropOrder: (_orderId: string, _resourceId: string) => void
}): JSX.Element {
  const { setNodeRef, isOver } = useDroppable({
    id: timelineDropId(lane.resourceId),
    disabled: !canWrite,
    data: { resourceId: lane.resourceId },
  })
  return (
    <li
      ref={setNodeRef}
      onDragOver={(event) => {
        if (canWrite) event.preventDefault()
      }}
      onDrop={(event) => {
        if (!canWrite) return
        event.preventDefault()
        const mapped = resolveBoardDrop(event.dataTransfer.getData('text/plain'), timelineDropId(lane.resourceId))
        if (mapped) onDropOrder(mapped.orderId, mapped.resourceId)
      }}
      className={`space-y-1 rounded-md border border-dashed px-2 py-2 ${isOver ? 'border-solid bg-muted/40' : ''}`}
      data-testid={`dispo-timeline-${lane.resourceId}`}
    >
      <div className="text-2xs tracking-wide uppercase text-muted-foreground">{lane.resourceLabel}</div>
      <div className="relative h-8 rounded-sm bg-muted">
        {lane.stops.map((stop) => (
          <span
            key={stop.stopId}
            className="absolute top-1 h-6 w-1.5 -translate-x-1/2 rounded-sm bg-foreground"
            style={{ left: `${markerOffset(stop.plannedArrival, axis)}%` }}
            title={`${stop.label} ${formatAxisTime(stop.plannedArrival)}${typeof stop.lat === 'number' && typeof stop.lng === 'number' ? ` ${formatStopLatLng(stop.lat, stop.lng)}` : ''}`}
            data-testid={`dispo-timeline-stop-${stop.stopId}`}
            data-lat={typeof stop.lat === 'number' ? String(stop.lat) : undefined}
            data-lng={typeof stop.lng === 'number' ? String(stop.lng) : undefined}
          />
        ))}
      </div>
    </li>
  )
}

export function DispositionBoard({
  contract,
  onAction,
  model,
}: SpecializedComponentProps & {
  model?: DispositionBoardModel
}): JSX.Element {
  const { toast } = useToast()
  const { user } = useAuth()
  const { tenantId } = useTenant()
  const live = !model
  const toursQuery = useTouren()
  const abrufeQuery = useQuery({
    queryKey: ['disposition', 'kontrakt-abrufe'],
    queryFn: fetchOpenAbrufe,
    enabled: live,
    retry: false,
  })
  const occupancyQuery = useQuery({
    queryKey: ['disposition', 'waagenbelegung'],
    queryFn: fetchOpenScaleOccupancy,
    enabled: live,
    retry: false,
  })
  const derived = useMemo(() => {
    if (model) return model
    return toursToModel(
      toursQuery.data?.tourenListe ?? [],
      [],
      abrufeQuery.data ?? [],
    )
  }, [abrufeQuery.data, model, toursQuery.data])
  const resourceIds = useMemo(() => derived.resources.map((resource) => resource.id), [derived.resources])
  const timelineQuery = useQuery({
    queryKey: ['disposition', 'tour-timeline', resourceIds],
    queryFn: () => fetchTimelineLanes(resourceIds),
    enabled: live && resourceIds.length > 0,
    retry: false,
  })
  const timelineAxis = useMemo(() => axisFromLanes(timelineQuery.data ?? []), [timelineQuery.data])
  const stopCoordinates = useMemo(
    () => (timelineQuery.data ?? []).flatMap((lane) => lane.coordinates),
    [timelineQuery.data],
  )

  const pendingRef = useRef(new Set<string>())
  const [pendingKeys, setPendingKeys] = useState<Set<string>>(() => new Set())
  const [feedback, setFeedback] = useState<string | null>(null)

  const canWrite = DISPOSITION_ASSIGNMENT_WRITE_RELEASED
    && (contract.permissions ?? []).includes('logistics.write')
    && hasDispositionWriteClaim(user)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor),
  )

  const withPending = useCallback(async (entityId: string, work: () => Promise<void>) => {
    if (pendingRef.current.has(entityId)) return
    pendingRef.current.add(entityId)
    setPendingKeys(new Set(pendingRef.current))
    try {
      await work()
    } finally {
      pendingRef.current.delete(entityId)
      setPendingKeys(new Set(pendingRef.current))
    }
  }, [])

  const reloadBoardColumns = useCallback(async () => {
    if (!live) return
    await Promise.allSettled([toursQuery.refetch(), abrufeQuery.refetch(), timelineQuery.refetch()])
  }, [abrufeQuery, live, timelineQuery, toursQuery])

  const persistAssignment = useCallback(async (orderId: string, resourceId: string, abrufId?: string) => {
    await onAction?.(DISPOSITION_BOARD_EVENTS.dropProposed, { orderId, resourceId, quantityPosted: false, abrufId })
    const result = await postDispositionAssignment({
      orderId,
      resourceId,
      tenantId,
      dropQuantity: 1,
      abrufId,
    })
    await onAction?.(DISPOSITION_BOARD_EVENTS.assignmentConfirmed, {
      orderId,
      resourceId,
      quantityPosted: false,
      event: result.event,
      tourId: result.tour_id,
    })
    await reloadBoardColumns()
  }, [onAction, reloadBoardColumns, tenantId])

  const confirmDrop = useCallback((orderId: string, resourceId: string) => {
    if (!canWrite) return
    const abrufId = derived.orders.find((order) => order.id === orderId)?.abrufId
    void withPending(orderId, async () => {
      setFeedback(null)
      try {
        await persistAssignment(orderId, resourceId, abrufId)
        toast({
          title: 'Zuweisung bestätigt',
          description: 'Die Menge wird nicht gebucht — erst beim Wiegen oder der Abrechnung.',
        })
        setFeedback('Zuweisung bestätigt. Mengenbuchung folgt getrennt.')
      } catch (error) {
        const message = error instanceof DispositionAssignmentError
          ? error.message
          : 'Zuweisung abgelehnt.'
        toast({ title: 'Zuweisung nicht übernommen', description: message, variant: 'destructive' })
        setFeedback(message)
      }
    })
  }, [canWrite, derived.orders, persistAssignment, toast, withPending])

  const onDragEnd = useCallback((event: DragEndEvent) => {
    const mapped = resolveBoardDrop(String(event.active.id), event.over ? String(event.over.id) : null)
    if (!mapped) return
    confirmDrop(mapped.orderId, mapped.resourceId)
  }, [confirmDrop])

  const sse = useWorkspaceTourCreated(reloadBoardColumns, live)
  const liveOps = useMemo(
    () => mergeOpsSignals(occupancyQuery.data ?? [], sse.opsSignals),
    [occupancyQuery.data, sse.opsSignals],
  )

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd} autoScroll={false}>
      <section
        data-testid="disposition-board"
        data-specialized-id={contract.id}
        data-live-channel={contract.liveChannel ?? 'disposition.board'}
        className="grid gap-3 xl:grid-cols-3"
        aria-label="LKW-Dispositionstafel"
      >
        {!canWrite ? (
          <p className="xl:col-span-3 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm" role="status" data-testid="dispo-preview-notice">
            Vorschau: Zuweisungen sind noch nicht freigegeben. Aufträge, Touren und Betriebszustände können gelesen werden.
          </p>
        ) : null}
        <article className="rounded-md border p-3" aria-labelledby="dispo-orders-heading">
          <h2 id="dispo-orders-heading" className="text-2xs tracking-wide uppercase text-muted-foreground">Aufträge / Kontrakte</h2>
          <ul className="mt-2 space-y-2">
            {live && abrufeQuery.isLoading ? (
              <li className="text-sm text-muted-foreground">Abrufe werden geladen…</li>
            ) : live && abrufeQuery.isError ? (
              <li className="text-sm text-status-error" role="alert" data-testid="dispo-orders-error">
                {abrufeQuery.error instanceof Error ? abrufeQuery.error.message : 'Abrufe nicht lesbar.'}
              </li>
            ) : derived.orders.length === 0 ? (
              <li className="text-sm text-muted-foreground" data-testid="dispo-orders-empty">
                {live ? 'Keine offenen Kontrakt-Abrufe.' : 'Keine offenen Aufträge in der bestehenden Tourenlage.'}
              </li>
            ) : derived.orders.map((order) => (
              <li key={order.id}>
                <OrderSource order={order} pending={pendingKeys.has(order.id)} canWrite={canWrite} />
              </li>
            ))}
          </ul>
        </article>

        <article className="rounded-md border p-3" aria-labelledby="dispo-resources-heading">
          <h2 id="dispo-resources-heading" className="text-2xs tracking-wide uppercase text-muted-foreground">Ressourcen / Planung</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Adapter auf die bestehende Tafel
            {' '}
            <a className="underline" href={EXISTING_TAFEL_ROUTE}>{EXISTING_TAFEL_ROUTE}</a>
            {' '}
            (Codex-Godfile, nicht dupliziert). Fuhrpark, Spedition, Fahrer als Drop-Ziele.
          </p>
          <ul className="mt-2 space-y-2">
            {live && toursQuery.isError ? (
              <li className="text-sm text-status-error" role="alert" data-testid="dispo-resources-error">
                Touren nicht lesbar: Recht oder Anmeldung fehlt.
              </li>
            ) : derived.resources.length === 0 ? (
              <li className="text-sm text-muted-foreground">Keine Touren geladen. Die Godfile-Tafel bleibt die operative Planung.</li>
            ) : derived.resources.map((resource) => (
              <ResourceTarget
                key={resource.id}
                resource={resource}
                canWrite={canWrite}
                onDropOrder={confirmDrop}
              />
            ))}
          </ul>
          <p className="mt-3 text-xs text-muted-foreground" data-testid="dispo-map-note">
            Stopp-Karte zeichnet nur lat/lng aus der Tour.
          </p>
          {live ? <DispositionStopMap stops={stopCoordinates} /> : null}
          {live && stopCoordinates.length > 0 ? (
            <ul className="mt-1 space-y-1" data-testid="dispo-stop-coordinates" aria-label="Stopp-Koordinaten">
              {stopCoordinates.map((stop) => (
                <li
                  key={stop.stopId}
                  className="text-xs text-muted-foreground"
                  data-testid={`dispo-stop-coord-${stop.stopId}`}
                >
                  {stop.label} {formatStopLatLng(stop.lat, stop.lng)}
                </li>
              ))}
            </ul>
          ) : null}
          {live ? (
            <div className="mt-3 space-y-2" data-testid="dispo-timeline">
              <h3 className="text-2xs tracking-wide uppercase text-muted-foreground">Zeitachse</h3>
              {timelineQuery.isError ? (
                <p className="text-sm text-status-error" role="alert" data-testid="dispo-timeline-error">
                  {timelineQuery.error instanceof Error ? timelineQuery.error.message : 'Zeitachse nicht lesbar.'}
                </p>
              ) : !timelineAxis ? (
                <p className="text-sm text-muted-foreground" data-testid="dispo-timeline-empty">{TIMELINE_FIELD_MISSING}</p>
              ) : (
                <>
                  <div className="flex justify-between text-2xs text-muted-foreground">
                    <span>{formatAxisTime(new Date(timelineAxis.startMs).toISOString())}</span>
                    <span>{formatAxisTime(new Date(timelineAxis.endMs).toISOString())}</span>
                  </div>
                  <ul className="space-y-2">
                    {(timelineQuery.data ?? []).map((lane) => (
                      <TimelineLaneRow
                        key={lane.resourceId}
                        lane={lane}
                        axis={timelineAxis}
                        canWrite={canWrite}
                        onDropOrder={confirmDrop}
                      />
                    ))}
                  </ul>
                </>
              )}
            </div>
          ) : null}
          {live && toursQuery.isLoading ? <p className="text-sm text-muted-foreground">Touren werden geladen…</p> : null}
        </article>

        <article className="rounded-md border p-3" aria-labelledby="dispo-ops-heading">
          <h2 id="dispo-ops-heading" className="text-2xs tracking-wide uppercase text-muted-foreground">Betriebszustände</h2>
          <ul className="mt-2 space-y-2">
            {live && occupancyQuery.isError ? (
              <li className="text-sm text-status-error" role="alert" data-testid="dispo-ops-error">
                {occupancyQuery.error instanceof Error ? occupancyQuery.error.message : OPS_AUTH_ERROR}
              </li>
            ) : null}
            {live && occupancyQuery.isLoading && liveOps.length === 0 ? (
              <li className="text-sm text-muted-foreground">Betriebszustände werden geladen…</li>
            ) : live ? (
              liveOps.length === 0 && !occupancyQuery.isError ? (
                <li className="text-sm text-muted-foreground" data-testid="dispo-ops-empty">
                  Keine aktuellen Betriebszustände.
                </li>
              ) : (
                liveOps.map((item) => (
                  <li key={item.id} className="flex items-center justify-between text-sm" data-testid={`dispo-ops-${item.id.replaceAll(':', '-')}`}>
                    <span>{item.label}{item.detail ? ` ${item.detail}` : ''}</span>
                    <span className="text-muted-foreground">{item.at ? formatAxisTime(item.at) : ''}</span>
                  </li>
                ))
              )
            ) : (
              derived.operations.map((item) => (
                <li key={item.id} className="flex items-center justify-between text-sm">
                  <span>{item.label}</span>
                  <span className={toneClass(item.tone)}>{item.value}</span>
                </li>
              ))
            )}
          </ul>
        </article>

        {sse.error ? (
          <p className="xl:col-span-3 text-sm text-status-error" role="alert" data-testid="dispo-sse-error">
            {sse.error}
          </p>
        ) : null}
        {feedback ? (
          <p className="xl:col-span-3 text-sm" role="status" data-testid="dispo-feedback">{feedback}</p>
        ) : canWrite ? (
          <p className="xl:col-span-3 text-xs text-muted-foreground">
            Drop bestätigt nur die Zuweisung. Event {DISPOSITION_BOARD_EVENTS.quantityPosted} entsteht erst bei Waage oder Abrechnung.
          </p>
        ) : null}
      </section>
    </DndContext>
  )
}
