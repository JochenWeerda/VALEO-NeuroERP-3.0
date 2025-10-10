import type { ReactElement } from 'react'
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

const LIST_SKELETON_ROWS = 4

const orderSchema = z.object({
  id: z.string().min(1),
  orderNumber: z.string().min(1),
  customer: z.string().min(1),
  amount: z.number().nonnegative(),
  currency: z.string().min(1).default('EUR'),
  status: z.string().min(1),
  createdAt: z.string().datetime({ offset: true }).or(z.string().min(1)),
})

const invoiceSchema = z.object({
  id: z.string().min(1),
  invoiceNumber: z.string().min(1),
  customer: z.string().min(1),
  amount: z.number().nonnegative(),
  currency: z.string().min(1).default('EUR'),
  status: z.string().min(1),
  issuedAt: z.string().datetime({ offset: true }).or(z.string().min(1)),
})

const ordersResponseSchema = z
  .object({
    data: z.array(orderSchema).optional(),
    items: z.array(orderSchema).optional(),
  })
  .transform((payload) => payload.data ?? payload.items ?? [])

const invoicesResponseSchema = z
  .object({
    data: z.array(invoiceSchema).optional(),
    items: z.array(invoiceSchema).optional(),
  })
  .transform((payload) => payload.data ?? payload.items ?? [])

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const dateFormatter = new Intl.DateTimeFormat('de-DE')

const fetchOrders = async (): Promise<SalesOrder[]> => {
  const payload = await apiClient.get<unknown>('/sales/api/v1/orders')
  const parsed = ordersResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }
  return []
}

const fetchInvoices = async (): Promise<SalesInvoice[]> => {
  const payload = await apiClient.get<unknown>('/sales/api/v1/invoices')
  const parsed = invoicesResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }
  return []
}

type SalesOrder = z.infer<typeof orderSchema>
type SalesInvoice = z.infer<typeof invoiceSchema>

export default function Sales(): ReactElement {
  const {
    data: orders = [],
    isPending: ordersLoading,
    isError: ordersError,
    refetch: refetchOrders,
  } = useQuery({
    queryKey: queryKeys.sales.orders(),
    queryFn: fetchOrders,
  })

  const {
    data: invoices = [],
    isPending: invoicesLoading,
    isError: invoicesError,
    refetch: refetchInvoices,
  } = useQuery({
    queryKey: queryKeys.sales.invoices(),
    queryFn: fetchInvoices,
  })

  const isError = ordersError || invoicesError

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Sales</h1>
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
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Sales</h1>
          <p className="text-sm text-slate-500">Uebersicht der Auftraege und Rechnungen</p>
        </div>
        <Button variant="outline" onClick={() => {
          void refetchOrders()
          void refetchInvoices()
        }}>
          Aktualisieren
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auftraege gesamt</CardTitle>
            <CardDescription>Summe aller erfassten Auftraege</CardDescription>
          </CardHeader>
          <CardContent>
            {ordersLoading ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{orders.length}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Auftraege</CardTitle>
            <CardDescription>Status nicht abgeschlossen</CardDescription>
          </CardHeader>
          <CardContent>
            {ordersLoading ? <Skeleton className="h-8 w-24" /> : <p className="text-2xl font-semibold">{totalOpenOrders}</p>}
          </CardContent>
        </Card>
        <Card className="rounded-2xl shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rechnungssumme</CardTitle>
            <CardDescription>Gebuchte Rechnungen</CardDescription>
          </CardHeader>
          <CardContent>
            {invoicesLoading ? (
              <Skeleton className="h-8 w-32" />
            ) : (
              <p className="text-2xl font-semibold text-slate-900">
                {currencyFormatter.format(totalInvoicesAmount)}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader>
            <CardTitle>Auftraege</CardTitle>
            <CardDescription>Neueste Kundenauftraege mit Status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {ordersLoading
                ? Array.from({ length: LIST_SKELETON_ROWS }).map((_, index) => (
                    <div key={index} className="rounded-xl border border-slate-200 p-4">
                      <Skeleton className="h-5 w-40" />
                      <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                    </div>
                  ))
                : orders.map((order) => (
                    <div key={order.id} className="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-slate-900">{order.orderNumber}</h3>
                          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                            {order.status}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600">{order.customer}</p>
                        <div className="flex items-center justify-between text-sm text-slate-500">
                          <span>{dateFormatter.format(new Date(order.createdAt))}</span>
                          <span>{currencyFormatter.format(order.amount)} {order.currency}</span>
                        </div>
                      </div>
                    </div>
                  ))}
              {!ordersLoading && orders.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
                  <p className="text-sm font-medium text-slate-700">Keine Auftraege vorhanden</p>
                  <p className="text-xs text-slate-500">Sobald Auftraege erfasst sind, erscheinen sie hier.</p>
                </div>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm">
          <CardHeader>
            <CardTitle>Rechnungen</CardTitle>
            <CardDescription>Gebuchte Rechnungen nach Kunde</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {invoicesLoading
                ? Array.from({ length: LIST_SKELETON_ROWS }).map((_, index) => (
                    <div key={index} className="rounded-xl border border-slate-200 p-4">
                      <Skeleton className="h-5 w-40" />
                      <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                    </div>
                  ))
                : invoices.map((invoice) => (
                    <div key={invoice.id} className="rounded-xl border border-slate-200 p-4 hover:bg-slate-50">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-slate-900">{invoice.invoiceNumber}</h3>
                          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                            {invoice.status}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600">{invoice.customer}</p>
                        <div className="flex items-center justify-between text-sm text-slate-500">
                          <span>{dateFormatter.format(new Date(invoice.issuedAt))}</span>
                          <span>{currencyFormatter.format(invoice.amount)} {invoice.currency}</span>
                        </div>
                      </div>
                    </div>
                  ))}
              {!invoicesLoading && invoices.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
                  <p className="text-sm font-medium text-slate-700">Keine Rechnungen vorhanden</p>
                  <p className="text-xs text-slate-500">Sobald Rechnungen gebucht sind, erscheinen sie hier.</p>
                </div>
              ) : null}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

