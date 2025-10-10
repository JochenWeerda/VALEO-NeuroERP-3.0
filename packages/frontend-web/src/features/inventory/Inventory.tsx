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
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'

const QUALITY_STATES = ['good', 'blocked', 'pending'] as const
const SKELETON_ROWS = 4

const inventoryLotSchema = z.object({
  id: z.string().min(1),
  lotNumber: z.string().min(1),
  commodity: z.string().min(1),
  quantity: z.number().nonnegative(),
  unit: z.string().min(1),
  location: z.string().min(1),
  qualityStatus: z.enum(QUALITY_STATES).default('pending'),
  expiryDate: z.string().datetime({ offset: true }).or(z.string().min(1)),
  supplier: z.string().min(1).optional().default('unbekannt'),
})

const inventoryResponseSchema = z
  .object({
    data: z.array(inventoryLotSchema).optional(),
    items: z.array(inventoryLotSchema).optional(),
    results: z.array(inventoryLotSchema).optional(),
  })
  .transform((payload) => payload.data ?? payload.items ?? payload.results ?? [])

const quantityFormatter = new Intl.NumberFormat('de-DE', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
})

const dateFormatter = new Intl.DateTimeFormat('de-DE')

const qualityConfig: Record<(typeof QUALITY_STATES)[number], { label: string; badge: string; icon: ReactElement }> = {
  good: {
    label: 'Gut',
    badge: 'bg-green-100 text-green-800',
    icon: <CheckCircle className="h-4 w-4 text-green-500" />,
  },
  blocked: {
    label: 'Blockiert',
    badge: 'bg-red-100 text-red-800',
    icon: <AlertTriangle className="h-4 w-4 text-red-500" />,
  },
  pending: {
    label: 'Ausstehend',
    badge: 'bg-yellow-100 text-yellow-800',
    icon: <Clock className="h-4 w-4 text-yellow-500" />,
  },
}

const fetchInventory = async (): Promise<InventoryLot[]> => {
  const payload = await apiClient.get<unknown>('/inventory/api/v1/lots')
  const parsed = inventoryResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }
  return []
}

type InventoryLot = z.infer<typeof inventoryLotSchema>

type InventorySummary = {
  totalQuantity: number
  blockedQuantity: number
  goodQuantity: number
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
    queryKey: queryKeys.inventory.lots(),
    queryFn: fetchInventory,
  })

  const summary = useMemo(() => reduceSummary(lots), [lots])

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Inventar</h1>
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
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Inventar</h1>
          <p className="text-sm text-slate-500">Lagerbestaende nach Los und Qualitaetsstatus</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtbestand</CardTitle>
            <CardDescription>Alle verfuegbaren Mengen</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold text-slate-900">
                {quantityFormatter.format(summary.totalQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigegeben</CardTitle>
            <CardDescription>Qualitaetsgepruefte Lose</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold text-green-600">
                {quantityFormatter.format(summary.goodQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Blockiert</CardTitle>
            <CardDescription>Qualitaetsprobleme</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p className="text-2xl font-semibold text-red-600">
                {quantityFormatter.format(summary.blockedQuantity)} t
              </p>
            )}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lose insgesamt</CardTitle>
            <CardDescription>Anzahl aktiver Lagerlose</CardDescription>
          </CardHeader>
          <CardContent>
            {isPending ? <Skeleton className="h-8 w-16" /> : <p className="text-2xl font-semibold">{lots.length}</p>}
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl shadow-sm">
        <CardHeader>
          <CardTitle>Lageruebersicht</CardTitle>
          <CardDescription>Alle Lose mit Menge, Standort und Qualitaet</CardDescription>
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
                  <div key={lot.id} className="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-slate-900">{lot.lotNumber}</h3>
                          <div className="flex items-center gap-2">
                            {qualityConfig[lot.qualityStatus].icon}
                            <span className={`rounded-full px-2 py-1 text-xs font-medium ${qualityConfig[lot.qualityStatus].badge}`}>
                              {qualityConfig[lot.qualityStatus].label}
                            </span>
                          </div>
                        </div>
                        <div className="grid grid-cols-1 gap-2 text-sm text-slate-600 sm:grid-cols-2 md:grid-cols-4">
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
                        <div className="text-sm text-slate-600">
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
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
                <p className="text-sm font-medium text-slate-700">Keine Lagerlose vorhanden</p>
                <p className="text-xs text-slate-500">Sobald Bestaende erfasst sind, erscheinen sie hier.</p>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


