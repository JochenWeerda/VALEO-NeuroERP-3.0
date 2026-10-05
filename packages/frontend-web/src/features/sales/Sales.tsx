import type { ReactElement } from 'react'
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

const LIST_SKELETON_ROWS = 4

type SalesOrder = {
  id: string
  orderNumber: string
  customer: string
  amount: number
  currency: string
  status: string
  createdAt: string
}

type SalesInvoice = {
  id: string
  invoiceNumber: string
  customer: string
  amount: number
  currency: string
  status: string
  issuedAt: string
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : null

const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' && value.length > 0 ? value : fallback)
const asNumber = (value: unknown): number => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0)
const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])

const extractList = (payload: unknown): unknown[] => {
  const record = asRecord(payload)
  if (!record) {
    return []
  }

  return asArray(record.data ?? record.items)
}

const normalizeOrder = (value: unknown): SalesOrder | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const id = asString(record.id)
  const orderNumber = asString(record.orderNumber)
  if (!id || !orderNumber) {
    return null
  }

  return {
    id,
    orderNumber,
    customer: asString(record.customer, 'Unbekannt'),
    amount: asNumber(record.amount),
    currency: asString(record.currency, 'EUR'),
    status: asString(record.status, 'open'),
    createdAt: asString(record.createdAt, new Date(0).toISOString()),
  }
}

const normalizeInvoice = (value: unknown): SalesInvoice | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const id = asString(record.id)
  const invoiceNumber = asString(record.invoiceNumber)
  if (!id || !invoiceNumber) {
    return null
  }

  return {
    id,
    invoiceNumber,
    customer: asString(record.customer, 'Unbekannt'),
    amount: asNumber(record.amount),
    currency: asString(record.currency, 'EUR'),
    status: asString(record.status, 'open'),
    issuedAt: asString(record.issuedAt, new Date(0).toISOString()),
  }
}

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const dateFormatter = new Intl.DateTimeFormat('de-DE')

const fetchOrders = async (): Promise<SalesOrder[]> => {
  const payload = await apiClient.get<unknown>('/sales/api/v1/orders')
  return extractList(payload.data).map(normalizeOrder).filter((value): value is SalesOrder => value !== null)
}

const fetchInvoices = async (): Promise<SalesInvoice[]> => {
  const payload = await apiClient.get<unknown>('/sales/api/v1/invoices')
  return extractList(payload.data).map(normalizeInvoice).filter((value): value is SalesInvoice => value !== null)
}

export default function Sales(): ReactElement {
  const {
    data: orders = [],
    isPending: ordersLoading,
    isError: ordersError,
    refetch: refetchOrders,
  } = useQuery({
    queryKey: queryKeys.sales.orders.all,
    queryFn: fetchOrders,
  })

  const {
    data: invoices = [],
    isPending: invoicesLoading,
    isError: invoicesError,
    refetch: refetchInvoices,
  } = useQuery({
    queryKey: queryKeys.sales.invoices.all,
    queryFn: fetchInvoices,
  })

  const isError = ordersError || invoicesError

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">Sales</h1>
          <Button variant="outline" onClick={() => {
            void refetchOrders()
            void refetchInvoices()
          }}>
            Erneut laden
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertTitle>Verkaufsdaten nicht verfuegbar</AlertTitle>
          <AlertDescription>Bitte Verbindung pruefen und erneut versuchen.</AlertDescription>
        </Alert>
      </div>
    )
  }

  const totalOpenOrders = orders.filter((order) => order.status !== 'completed').length
  const totalInvoicesAmount = invoices.reduce((total, invoice) => total + invoice.amount, 0)

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Sales</h1>
          <p className="text-sm text-muted-foreground">Uebersicht der Auftraege und Rechnungen</p>
        </div>
        <Button variant="outline" onClick={() => {
          void refetchOrders()
          void refetchInvoices()
        }}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auftraege gesamt</CardTitle>
            <CardDescription>Summe aller erfassten Auftraege</CardDescription>
          </CardHeader>
          <CardContent>
            {ordersLoading ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{orders.length}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-[hsl(var(--accent))] shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Auftraege</CardTitle>
            <CardDescription>Status nicht abgeschlossen</CardDescription>
          </CardHeader>
          <CardContent>
            {ordersLoading ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totalOpenOrders}</p>}
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rechnungssumme</CardTitle>
            <CardDescription>Gebuchte Rechnungen</CardDescription>
          </CardHeader>
          <CardContent>
            {invoicesLoading ? (
              <Skeleton className="h-8 w-32" />
            ) : (
              <p className="text-2xl font-semibold tabular-nums text-foreground">
                {currencyFormatter.format(totalInvoicesAmount)}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Auftraege</CardTitle>
            <CardDescription>Neueste Kundenauftraege mit Status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {ordersLoading
                ? Array.from({ length: LIST_SKELETON_ROWS }).map((_, index) => (
                    <div key={index} className="rounded-(--radius) border border-border p-4">
                      <Skeleton className="h-5 w-40" />
                      <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                    </div>
                  ))
                : orders.map((order) => (
                    <div key={order.id} className="rounded-(--radius) border border-border p-4 transition-colors hover:bg-primary/5">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-foreground">{order.orderNumber}</h3>
                          <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium text-foreground">
                            {order.status}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{order.customer}</p>
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span>{dateFormatter.format(new Date(order.createdAt))}</span>
                          <span>{currencyFormatter.format(order.amount)} {order.currency}</span>
                        </div>
                      </div>
                    </div>
                  ))}
              {!ordersLoading && orders.length === 0 ? (
                <div className="rounded-(--radius) border border-dashed border-border bg-muted p-6 text-center">
                  <p className="text-sm font-medium text-foreground">Keine Auftraege vorhanden</p>
                  <p className="text-xs text-muted-foreground">Sobald Auftraege erfasst sind, erscheinen sie hier.</p>
                </div>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Rechnungen</CardTitle>
            <CardDescription>Gebuchte Rechnungen nach Kunde</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {invoicesLoading
                ? Array.from({ length: LIST_SKELETON_ROWS }).map((_, index) => (
                    <div key={index} className="rounded-(--radius) border border-border p-4">
                      <Skeleton className="h-5 w-40" />
                      <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                    </div>
                  ))
                : invoices.map((invoice) => (
                    <div key={invoice.id} className="rounded-(--radius) border border-border p-4 transition-colors hover:bg-primary/5">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-foreground">{invoice.invoiceNumber}</h3>
                          <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium text-foreground">
                            {invoice.status}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{invoice.customer}</p>
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span>{dateFormatter.format(new Date(invoice.issuedAt))}</span>
                          <span>{currencyFormatter.format(invoice.amount)} {invoice.currency}</span>
                        </div>
                      </div>
                    </div>
                  ))}
              {!invoicesLoading && invoices.length === 0 ? (
                <div className="rounded-(--radius) border border-dashed border-border bg-muted p-6 text-center">
                  <p className="text-sm font-medium text-foreground">Keine Rechnungen vorhanden</p>
                  <p className="text-xs text-muted-foreground">Sobald Rechnungen gebucht sind, erscheinen sie hier.</p>
                </div>
              ) : null}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
