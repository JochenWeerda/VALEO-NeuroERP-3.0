import { type ReactElement, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
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
import { apiClient } from '@/lib/api-client'

const CONTRACT_STATUSES = ['active', 'pending', 'completed', 'cancelled'] as const
const POSITION_TYPES = ['long', 'short'] as const
const SKELETON_ROWS = 3

type Contract = {
  id: string
  contractNumber: string
  customer: string
  commodity: string
  quantity: number
  unit: string
  price: number
  currency: string
  deliveryDate: string
  status: (typeof CONTRACT_STATUSES)[number]
  type: (typeof POSITION_TYPES)[number]
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : null

const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' && value.length > 0 ? value : fallback)
const asNumber = (value: unknown): number => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0)
const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])

const isContractStatus = (value: unknown): value is Contract['status'] =>
  typeof value === 'string' && CONTRACT_STATUSES.includes(value as Contract['status'])

const isPositionType = (value: unknown): value is Contract['type'] =>
  typeof value === 'string' && POSITION_TYPES.includes(value as Contract['type'])

const normalizeContract = (value: unknown): Contract | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const id = asString(record.id)
  const contractNumber = asString(record.contractNumber)
  if (!id || !contractNumber) {
    return null
  }

  return {
    id,
    contractNumber,
    customer: asString(record.customer, 'Unbekannt'),
    commodity: asString(record.commodity, 'Unbekannt'),
    quantity: asNumber(record.quantity),
    unit: asString(record.unit, 't'),
    price: asNumber(record.price),
    currency: asString(record.currency, 'EUR'),
    deliveryDate: asString(record.deliveryDate, new Date(0).toISOString()),
    status: isContractStatus(record.status) ? record.status : 'pending',
    type: isPositionType(record.type) ? record.type : 'long',
  }
}

const extractList = (payload: unknown): unknown[] => {
  const record = asRecord(payload)
  if (!record) {
    return []
  }

  return asArray(record.data ?? record.items ?? record.results)
}

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
  return extractList(payload.data).map(normalizeContract).filter((value): value is Contract => value !== null)
}

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
    active: 'bg-primary/10 text-primary',
    pending: 'bg-[hsl(var(--accent)/0.14)] text-[hsl(var(--accent-foreground))]',
    completed: 'bg-muted text-foreground',
    cancelled: 'bg-destructive/10 text-destructive',
  }

  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusClasses[contract.status]}`}>
      {contract.status}
    </span>
  )
}

const renderTypeBadge = (contract: Contract): ReactElement => {
  const typeClasses: Record<(typeof POSITION_TYPES)[number], string> = {
    long: 'bg-primary/10 text-primary',
    short: 'bg-[hsl(var(--accent)/0.14)] text-[hsl(var(--accent-foreground))]',
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
          <h1 className="text-xl font-bold text-foreground">Vertraege</h1>
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
    <div className="space-y-8">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Vertraege</h1>
          <p className="text-sm text-muted-foreground">Uebersicht der aktiven Liefer- und Abnahmevertraege</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
            <CardDescription>Alle erfassten Vertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.total}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-[hsl(var(--accent))] shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Long Positionen</CardTitle>
            <CardDescription>Kaufvertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.long}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Short Positionen</CardTitle>
            <CardDescription>Verkaufsvertraege</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totals.short}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Vertragsliste</CardTitle>
          <CardDescription>Neueste Kontrakte inklusive Menge und Termin</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isPending
              ? Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <div key={index} className="rounded-(--radius) border border-border p-4">
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
                  <div key={contract.id} className="rounded-(--radius) border border-border p-4 transition-colors hover:bg-primary/5">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-foreground">{contract.contractNumber}</h3>
                          {renderStatusBadge(contract)}
                          {renderTypeBadge(contract)}
                        </div>
                        <div className="grid grid-cols-1 gap-2 text-sm text-muted-foreground sm:grid-cols-2 md:grid-cols-4">
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
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Lieferdatum:</span>{' '}
                          {dateFormatter.format(new Date(contract.deliveryDate))}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold tabular-nums text-foreground">
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
              <div className="rounded-(--radius) border border-dashed border-border bg-muted p-6 text-center">
                <p className="text-sm font-medium text-foreground">Keine Vertraege vorhanden</p>
                <p className="text-xs text-muted-foreground">Sobald Kontrakte angelegt sind, erscheinen diese hier.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
