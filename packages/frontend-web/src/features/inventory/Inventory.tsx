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
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'

const QUALITY_STATES = ['good', 'blocked', 'pending'] as const
const SKELETON_ROWS = 4

type InventoryLot = {
  id: string
  lotNumber: string
  commodity: string
  quantity: number
  unit: string
  location: string
  qualityStatus: (typeof QUALITY_STATES)[number]
  expiryDate: string
  supplier: string
}

type InventorySummary = {
  totalQuantity: number
  blockedQuantity: number
  goodQuantity: number
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : null

const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' && value.length > 0 ? value : fallback)
const asNumber = (value: unknown): number => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0)
const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])

const isQualityState = (value: unknown): value is InventoryLot['qualityStatus'] =>
  typeof value === 'string' && QUALITY_STATES.includes(value as InventoryLot['qualityStatus'])

const normalizeInventoryLot = (value: unknown): InventoryLot | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const id = asString(record.id)
  const lotNumber = asString(record.lotNumber)
  if (!id || !lotNumber) {
    return null
  }

  return {
    id,
    lotNumber,
    commodity: asString(record.commodity, 'Unbekannt'),
    quantity: asNumber(record.quantity),
    unit: asString(record.unit, 't'),
    location: asString(record.location, 'Unbekannt'),
    qualityStatus: isQualityState(record.qualityStatus) ? record.qualityStatus : 'pending',
    expiryDate: asString(record.expiryDate, new Date(0).toISOString()),
    supplier: asString(record.supplier, 'unbekannt'),
  }
}

const extractList = (payload: unknown): unknown[] => {
  const record = asRecord(payload)
  if (!record) {
    return []
  }

  return asArray(record.data ?? record.items ?? record.results)
}

const quantityFormatter = new Intl.NumberFormat('de-DE', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
})

const dateFormatter = new Intl.DateTimeFormat('de-DE')

const qualityConfig: Record<(typeof QUALITY_STATES)[number], { label: string; badge: string; icon: ReactElement }> = {
  good: {
    label: 'Gut',
    badge: 'bg-primary/10 text-primary',
    icon: <CheckCircle className="h-4 w-4 text-primary" />,
  },
  blocked: {
    label: 'Blockiert',
    badge: 'bg-destructive/10 text-destructive',
    icon: <AlertTriangle className="h-4 w-4 text-destructive" />,
  },
  pending: {
    label: 'Ausstehend',
    badge: 'bg-[hsl(var(--accent)/0.14)] text-[hsl(var(--accent-foreground))]',
    icon: <Clock className="h-4 w-4 text-[hsl(var(--accent))]" />,
  },
}

const fetchInventory = async (): Promise<InventoryLot[]> => {
  const payload = await apiClient.get<unknown>('/inventory/api/v1/lots')
  return extractList(payload.data).map(normalizeInventoryLot).filter((value): value is InventoryLot => value !== null)
}

const reduceSummary = (lots: InventoryLot[]): InventorySummary => {
  return lots.reduce<InventorySummary>(
    (accumulator, lot) => {
      const nextTotal = accumulator.totalQuantity + lot.quantity
      const nextGood = lot.qualityStatus === 'good' ? accumulator.goodQuantity + lot.quantity : accumulator.goodQuantity
      const nextBlocked =
        lot.qualityStatus === 'blocked' ? accumulator.blockedQuantity + lot.quantity : accumulator.blockedQuantity

      return {
        totalQuantity: nextTotal,
        goodQuantity: nextGood,
        blockedQuantity: nextBlocked,
      }
    },
    { totalQuantity: 0, goodQuantity: 0, blockedQuantity: 0 }
  )
}

export default function Inventory(): ReactElement {
  const {
    data: lots = [],
    isPending,
    isError,
    refetch,
  } = useQuery({
    queryKey: queryKeys.inventory.articles.all,
    queryFn: fetchInventory,
  })

  const summary = useMemo(() => reduceSummary(lots), [lots])

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">Inventar</h1>
          <Button variant="outline" onClick={() => void refetch()}>
            Erneut laden
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertTitle>Lagerdaten nicht verfuegbar</AlertTitle>
          <AlertDescription>Bitte pruefen Sie die Verbindung und versuchen Sie es erneut.</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Inventar</h1>
          <p className="text-sm text-muted-foreground">Lagerbestaende nach Los und Qualitaetsstatus</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtbestand</CardTitle>
            <CardDescription>Alle verfuegbaren Mengen</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold tabular-nums text-foreground">
                {quantityFormatter.format(summary.totalQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigegeben</CardTitle>
            <CardDescription>Qualitaetsgepruefte Lose</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold tabular-nums text-primary">
                {quantityFormatter.format(summary.goodQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-destructive shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Blockiert</CardTitle>
            <CardDescription>Qualitaetsprobleme</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold tabular-nums text-destructive">
                {quantityFormatter.format(summary.blockedQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-[hsl(var(--accent))] shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lose insgesamt</CardTitle>
            <CardDescription>Anzahl aktiver Lagerlose</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-16" /> : <p className="text-2xl font-semibold">{lots.length}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Lageruebersicht</CardTitle>
          <CardDescription>Alle Lose mit Menge, Standort und Qualitaet</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isPending
              ? Array.from({ length: SKELETON_ROWS }).map((_, index) => (
                  <div key={index} className="rounded-[var(--radius)] border border-border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-6 w-32" />
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <Skeleton className="h-4 w-24" />
                          <Skeleton className="h-4 w-24" />
                          <Skeleton className="h-4 w-20" />
                          <Skeleton className="h-4 w-20" />
                        </div>
                      </div>
                      <Skeleton className="h-8 w-16" />
                    </div>
                  </div>
                ))
              : lots.map((lot) => (
                  <div key={lot.id} className="rounded-[var(--radius)] border border-border p-4 transition-colors hover:bg-primary/5">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-foreground">{lot.lotNumber}</h3>
                          <div className="flex items-center gap-2">
                            {qualityConfig[lot.qualityStatus].icon}
                            <span className={`rounded-full px-2 py-1 text-xs font-medium ${qualityConfig[lot.qualityStatus].badge}`}>
                              {qualityConfig[lot.qualityStatus].label}
                            </span>
                          </div>
                        </div>
                        <div className="grid grid-cols-1 gap-2 text-sm text-muted-foreground sm:grid-cols-2 md:grid-cols-4">
                          <div>
                            <span className="font-medium">Ware:</span> {lot.commodity}
                          </div>
                          <div>
                            <span className="font-medium">Menge:</span> {quantityFormatter.format(lot.quantity)} {lot.unit}
                          </div>
                          <div>
                            <span className="font-medium">Lagerort:</span> {lot.location}
                          </div>
                          <div>
                            <span className="font-medium">Lieferant:</span> {lot.supplier}
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Verfallsdatum:</span>{' '}
                          {dateFormatter.format(new Date(lot.expiryDate))}
                        </div>
                      </div>
                      <div className="text-right">
                        <Button size="sm" variant="outline">
                          Details
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
            {!isPending && lots.length === 0 ? (
              <div className="rounded-[var(--radius)] border border-dashed border-border bg-muted p-6 text-center">
                <p className="text-sm font-medium text-foreground">Keine Lagerlose vorhanden</p>
                <p className="text-xs text-muted-foreground">Sobald Bestaende erfasst sind, erscheinen sie hier.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
