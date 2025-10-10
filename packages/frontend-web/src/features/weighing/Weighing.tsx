import { type ReactElement, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
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
import { apiClient } from '@/lib/axios'

const TICKET_STATUSES = ['Draft', 'InProgress', 'Completed', 'Cancelled'] as const
const SKELETON_ROWS = 4

const weighingTicketSchema = z.object({
  id: z.string().min(1),
  ticketNumber: z.string().min(1),
  status: z.enum(TICKET_STATUSES),
  contractId: z.string().optional(),
  netWeight: z.number().nonnegative().optional().default(0),
  createdAt: z.string().datetime({ offset: true }).or(z.string().min(1)),
})

const ticketsResponseSchema = z
  .object({
    data: z.array(weighingTicketSchema).optional(),
    items: z.array(weighingTicketSchema).optional(),
  })
  .transform((payload) => payload.data ?? payload.items ?? [])

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

  const parsed = ticketsResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }
  return []
}

const approveTicket = async (ticketId: string): Promise<void> => {
  await apiClient.post(`/weighing/api/v1/tickets/${ticketId}/approve`)
}

type WeighingTicket = z.infer<typeof weighingTicketSchema>

type TicketSummary = {
  total: number
  completed: number
  inProgress: number
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
  Draft: 'bg-slate-100 text-slate-700',
  InProgress: 'bg-yellow-100 text-yellow-800',
  Completed: 'bg-green-100 text-green-700',
  Cancelled: 'bg-red-100 text-red-700',
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
          <h1 className="text-2xl font-bold text-slate-900">Wiegescheine</h1>
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
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Wiegescheine</h1>
          <p className="text-sm text-slate-500">Uebersicht der heutigen Tickets</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tickets heute</CardTitle>
            <CardDescription>Anzahl der erfassten Tickets</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{summary.total}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle>
            <CardDescription>Tickets mit laufendem Wiegevorgang</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold text-yellow-700">{summary.inProgress}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
            <CardDescription>Heute finalisierte Tickets</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold text-green-700">{summary.completed}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl shadow-sm">
        <CardHeader>
          <CardTitle>Heute erfasste Tickets</CardTitle>
          <CardDescription>Mit Status und optionaler Vertragszuordnung</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isPending
              ? Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <div key={index} className="rounded-xl border border-slate-200 p-4">
                    <Skeleton className="h-5 w-32" />
                    <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  </div>
                ))
              : tickets.map((ticket) => (
                  <div key={ticket.id} className="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-sm font-semibold text-slate-900">{ticket.ticketNumber}</h3>
                          <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusBadgeClasses[ticket.status]}`}>
                            {ticket.status}
                          </span>
                        </div>
                        <div className="text-sm text-slate-600">
                          Vertrag:{' '}
                          {ticket.contractId ?? 'kein Bezug'}
                        </div>
                        <div className="text-sm text-slate-500">
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
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
                <p className="text-sm font-medium text-slate-700">Keine Tickets fuer heute</p>
                <p className="text-xs text-slate-500">Neue Wiegevorgaenge erscheinen automatisch.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}





