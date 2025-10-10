import { type ReactElement, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
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
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/axios'

const CONTRACT_STATUSES = ['active', 'pending', 'completed', 'cancelled'] as const
const POSITION_TYPES = ['long', 'short'] as const
const SKELETON_ROWS = 3

const contractSchema = z.object({
  id: z.string().min(1),
  contractNumber: z.string().min(1),
  customer: z.string().min(1),
  commodity: z.string().min(1),
  quantity: z.number().nonnegative(),
  unit: z.string().min(1),
  price: z.number().nonnegative(),
  currency: z.string().min(1).default('EUR'),
  deliveryDate: z.string().datetime({ offset: true }).or(z.string().min(1)),
  status: z.enum(CONTRACT_STATUSES).default('pending'),
  type: z.enum(POSITION_TYPES).default('long'),
})

const contractsResponseSchema = z
  .object({
    data: z.array(contractSchema).optional(),
    items: z.array(contractSchema).optional(),
    results: z.array(contractSchema).optional(),
  })
  .transform((payload) => payload.data ?? payload.items ?? payload.results ?? [])

const monetaryFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const quantityFormatter = new Intl.NumberFormat('de-DE', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
})

const dateFormatter = new Intl.DateTimeFormat('de-DE')

const fetchContracts = async (): Promise<Contract[]> => {
  const payload = await apiClient.get<unknown>('/contracts/api/v1/contracts')
  const parsed = contractsResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }
  return []
}

type Contract = z.infer<typeof contractSchema>

const computeTotals = (contracts: Contract[]): { total: number; long: number; short: number } => {
  return contracts.reduce(
    (accumulator, contract) => {
      if (contract.type === 'long') {
        return {
          total: accumulator.total + 1,
          long: accumulator.long + 1,
          short: accumulator.short,
        }
      }

      return {
        total: accumulator.total + 1,
        long: accumulator.long,
        short: accumulator.short + 1,
      }
    },
    { total: 0, long: 0, short: 0 }
  )
}

const renderStatusBadge = (contract: Contract): ReactElement => {
  const statusClasses: Record<(typeof CONTRACT_STATUSES)[number], string> = {
    active: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusClasses[contract.status]}`}>
      {contract.status}
    </span>
  )
}

const renderTypeBadge = (contract: Contract): ReactElement => {
  const typeClasses: Record<(typeof POSITION_TYPES)[number], string> = {
    long: 'bg-blue-100 text-blue-800',
    short: 'bg-orange-100 text-orange-800',
  }

  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${typeClasses[contract.type]}`}>
      {contract.type}
    </span>
  )
}

export default function Contracts(): ReactElement {
  const {
    data: contracts = [],
    isPending,
    isError,
    refetch,
  } = useQuery({
    queryKey: queryKeys.contracts.lists(),
    queryFn: fetchContracts,
  })

  const totals = useMemo(() => computeTotals(contracts), [contracts])

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Vertraege</h1>
          <Button onClick={() => void refetch()} variant="outline">
            Erneut laden
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertTitle>Fehler beim Laden</AlertTitle>
          <AlertDescription>
            Die Vertragsdaten konnten nicht geladen werden. Bitte versuchen Sie es erneut.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Vertraege</h1>
          <p className="text-sm text-slate-500">Uebersicht der aktiven Liefer- und Abnahmevertraege</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
            <CardDescription>Alle erfassten Vertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.total}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Long Positionen</CardTitle>
            <CardDescription>Kaufvertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.long}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Short Positionen</CardTitle>
            <CardDescription>Verkaufsvertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.short}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl shadow-sm">
        <CardHeader>
          <CardTitle>Vertragsliste</CardTitle>
          <CardDescription>Neueste Kontrakte inklusive Menge und Termin</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isPending
              ? Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <div key={index} className="rounded-xl border border-slate-200 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-6 w-32" />
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <Skeleton className="h-4 w-24" />
                          <Skeleton className="h-4 w-20" />
                          <Skeleton className="h-4 w-16" />
                          <Skeleton className="h-4 w-24" />
                        </div>
                      </div>
                      <Skeleton className="h-8 w-20" />
                    </div>
                  </div>
                ))
              : contracts.map((contract) => (
                  <div key={contract.id} className="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-slate-900">{contract.contractNumber}</h3>
                          {renderStatusBadge(contract)}
                          {renderTypeBadge(contract)}
                        </div>
                        <div className="grid grid-cols-1 gap-2 text-sm text-slate-600 sm:grid-cols-2 md:grid-cols-4">
                          <div>
                            <span className="font-medium">Kunde:</span> {contract.customer}
                          </div>
                          <div>
                            <span className="font-medium">Ware:</span> {contract.commodity}
                          </div>
                          <div>
                            <span className="font-medium">Menge:</span>{' '}
                            {quantityFormatter.format(contract.quantity)} {contract.unit}
                          </div>
                          <div>
                            <span className="font-medium">Preis:</span>{' '}
                            {monetaryFormatter.format(contract.price)} {contract.currency}
                          </div>
                        </div>
                        <div className="text-sm text-slate-600">
                          <span className="font-medium">Lieferdatum:</span>{' '}
                          {dateFormatter.format(new Date(contract.deliveryDate))}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-slate-900">
                          {monetaryFormatter.format(contract.quantity * contract.price)}
                        </p>
                        <Button className="mt-2" size="sm" variant="outline">
                          Details
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
            {!isPending && contracts.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
                <p className="text-sm font-medium text-slate-700">Keine Vertraege vorhanden</p>
                <p className="text-xs text-slate-500">Sobald Kontrakte angelegt sind, erscheinen diese hier.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

