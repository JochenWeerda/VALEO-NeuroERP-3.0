import { type ReactElement, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { mutationKeys, queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/api-client'

const TICKET_STATUSES = ['Draft', 'InProgress', 'Completed', 'Cancelled'] as const
const SKELETON_ROWS = 4

type WeighingTicket = {
  id: string
  ticketNumber: string
  status: (typeof TICKET_STATUSES)[number]
  contractId?: string
  netWeight: number
  createdAt: string
}

type TicketSummary = {
  total: number
  completed: number
  inProgress: number
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : null

const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' && value.length > 0 ? value : fallback)
const asNumber = (value: unknown): number => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0)
const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])

const isTicketStatus = (value: unknown): value is WeighingTicket['status'] =>
  typeof value === 'string' && TICKET_STATUSES.includes(value as WeighingTicket['status'])

const extractList = (payload: unknown): unknown[] => {
  const record = asRecord(payload)
  if (!record) {
    return []
  }

  return asArray(record.data ?? record.items)
}

const normalizeTicket = (value: unknown): WeighingTicket | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const id = asString(record.id)
  const ticketNumber = asString(record.ticketNumber)
  if (!id || !ticketNumber) {
    return null
  }

  return {
    id,
    ticketNumber,
    status: isTicketStatus(record.status) ? record.status : 'Draft',
    contractId: asString(record.contractId) || undefined,
    netWeight: asNumber(record.netWeight),
    createdAt: asString(record.createdAt, new Date(0).toISOString()),
  }
}

const fetchTodayTickets = async (): Promise<WeighingTicket[]> => {
  const now = new Date()
  const startOfDay = new Date(now)
  startOfDay.setHours(0, 0, 0, 0)

  const payload = await apiClient.get<unknown>('/weighing/api/v1/tickets', {
    params: {
      from: startOfDay.toISOString(),
      to: now.toISOString(),
    },
  })

  return extractList(payload.data).map(normalizeTicket).filter((value): value is WeighingTicket => value !== null)
}

const approveTicket = async (ticketId: string): Promise<void> => {
  await apiClient.post(`/weighing/api/v1/tickets/${ticketId}/approve`)
}

const reduceSummary = (tickets: WeighingTicket[]): TicketSummary => {
  return tickets.reduce<TicketSummary>(
    (accumulator, ticket) => {
      const nextTotal = accumulator.total + 1
      const nextCompleted = ticket.status === 'Completed' ? accumulator.completed + 1 : accumulator.completed
      const nextInProgress = ticket.status === 'InProgress' ? accumulator.inProgress + 1 : accumulator.inProgress

      return {
        total: nextTotal,
        completed: nextCompleted,
        inProgress: nextInProgress,
      }
    },
    { total: 0, completed: 0, inProgress: 0 }
  )
}

const statusBadgeClasses: Record<(typeof TICKET_STATUSES)[number], string> = {
  Draft: 'bg-muted text-foreground',
  InProgress: 'bg-[hsl(var(--accent)/0.14)] text-[hsl(var(--accent-foreground))]',
  Completed: 'bg-primary/10 text-primary',
  Cancelled: 'bg-destructive/10 text-destructive',
}

const dateFormatter = new Intl.DateTimeFormat('de-DE', {
  hour: '2-digit',
  minute: '2-digit',
})

export default function Weighing(): ReactElement {
  const queryClient = useQueryClient()

  const {
    data: tickets = [],
    isPending,
    isError,
    refetch,
  } = useQuery({
    queryKey: queryKeys.weighing.ticketList({ scope: 'today' }),
    queryFn: fetchTodayTickets,
  })

  const summary = useMemo(() => reduceSummary(tickets), [tickets])

  const approveMutation = useMutation({
    mutationKey: mutationKeys.weighing.approve,
    mutationFn: approveTicket,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.weighing.ticketList({ scope: 'today' }) })
    },
  })

  const handleApprove = (ticketId: string): void => {
    approveMutation.mutate(ticketId)
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">Wiegescheine</h1>
          <Button variant="outline" onClick={() => void refetch()}>
            Erneut laden
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertTitle>Wiegedaten nicht verfuegbar</AlertTitle>
          <AlertDescription>Bitte Verbindung pruefen und erneut versuchen.</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Wiegescheine</h1>
          <p className="text-sm text-muted-foreground">Uebersicht der heutigen Tickets</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tickets heute</CardTitle>
            <CardDescription>Anzahl der erfassten Tickets</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{summary.total}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-[hsl(var(--accent))] shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
            <CardDescription>Tickets mit laufendem Wiegevorgang</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold tabular-nums text-[hsl(var(--accent-foreground))]">{summary.inProgress}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
            <CardDescription>Heute finalisierte Tickets</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold tabular-nums text-primary">{summary.completed}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Heute erfasste Tickets</CardTitle>
          <CardDescription>Mit Status und optionaler Vertragszuordnung</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isPending
              ? Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <div key={index} className="rounded-(--radius) border border-border p-4">
                    <Skeleton className="h-5 w-32" />
                    <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  </div>
                ))
              : tickets.map((ticket) => (
                  <div key={ticket.id} className="rounded-(--radius) border border-border p-4 transition-colors hover:bg-primary/5">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-sm font-semibold text-foreground">{ticket.ticketNumber}</h3>
                          <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusBadgeClasses[ticket.status]}`}>
                            {ticket.status}
                          </span>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Vertrag:{' '}
                          {ticket.contractId ?? 'kein Bezug'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Erstellt: {dateFormatter.format(new Date(ticket.createdAt))}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={approveMutation.isPending}
                          onClick={() => handleApprove(ticket.id)}
                        >
                          Freigeben
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
            {!isPending && tickets.length === 0 ? (
              <div className="rounded-(--radius) border border-dashed border-border bg-muted p-6 text-center">
                <p className="text-sm font-medium text-foreground">Keine Tickets fuer heute</p>
                <p className="text-xs text-muted-foreground">Neue Wiegevorgaenge erscheinen automatisch.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
