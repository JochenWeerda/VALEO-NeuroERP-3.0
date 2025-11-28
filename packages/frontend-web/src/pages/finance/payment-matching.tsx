/**
 * Payment Matching UI
 * FIBU-AR-03: Zahlungseingänge & Matching
 * Payment-Match-UI für Bankimport und OP-Zuordnung
 */

import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Upload, Search, CheckCircle2, XCircle, AlertCircle, Link2, FileDown } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { useToast } from '@/hooks/use-toast'

type PaymentEntry = {
  id: string
  tenant_id: string
  bank_account: string
  booking_date: string
  value_date: string
  amount: number
  currency: string
  reference?: string
  remittance_info?: string
  creditor_name?: string
  matched_op_id?: string
  match_status: 'UNMATCHED' | 'MATCHED' | 'PARTIAL' | 'MANUAL'
}

type OpenItemMatch = {
  op_id: string
  document_number: string
  customer_id: string
  customer_name: string
  amount: number
  open_amount: number
  due_date: string
  currency: string
  status: string
}

type MatchResult = {
  payment_id: string
  matched_op_id?: string
  match_type: string
  matched_amount: number
  remaining_amount: number
  confidence: number
  match_reason: string
}

export default function PaymentMatchingPage(): JSX.Element {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [payments, setPayments] = useState<PaymentEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false)
  const [isMatchDialogOpen, setIsMatchDialogOpen] = useState(false)
  const [selectedPayment, setSelectedPayment] = useState<PaymentEntry | null>(null)
  const [openItems, setOpenItems] = useState<OpenItemMatch[]>([])
  const [selectedOpId, setSelectedOpId] = useState<string>('')
  const [bankAccount, setBankAccount] = useState('')
  const [csvFile, setCsvFile] = useState<File | null>(null)

  useEffect(() => {
    fetchUnmatchedPayments()
  }, [])

  async function fetchUnmatchedPayments(): Promise<void> {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/finance/payments/unmatched?limit=100')
      if (!response.ok) {
        throw new Error('Failed to fetch payments')
      }
      const data: PaymentEntry[] = await response.json()
      setPayments(data)
    } catch (_error) {
      // API nicht erreichbar - Benutzer wird per Toast benachrichtigt
      toast({
        title: t('common.error'),
        description: t('crud.feedback.fetchError', { entityType: 'Zahlungen' }),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  async function handleCsvImport(): Promise<void> {
    if (!csvFile || !bankAccount) {
      toast({
        title: t('common.error'),
        description: t('finance.payments.importError'),
        variant: 'destructive',
      })
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', csvFile)
      
      const response = await fetch(
        `/api/v1/finance/payments/import/csv?bank_account=${encodeURIComponent(bankAccount)}`,
        {
          method: 'POST',
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error('Failed to import CSV')
      }

      const data: PaymentEntry[] = await response.json()
      toast({
        title: t('common.success'),
        description: t('finance.payments.importSuccess', { count: data.length }),
      })
      setIsImportDialogOpen(false)
      setCsvFile(null)
      setBankAccount('')
      await fetchUnmatchedPayments()
    } catch (_error) {
      // Import fehlgeschlagen - Benutzer wird per Toast benachrichtigt
      toast({
        title: t('common.error'),
        description: t('finance.payments.importError'),
        variant: 'destructive',
      })
    }
  }

  async function fetchOpenItems(customerId: string): Promise<void> {
    try {
      const response = await fetch(`/api/v1/finance/payments/open-items/${customerId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch open items')
      }
      const data: OpenItemMatch[] = await response.json()
      setOpenItems(data)
    } catch (_error) {
      // Keine offenen Posten gefunden oder API nicht erreichbar
      setOpenItems([])
    }
  }

  async function matchPayment(): Promise<void> {
    if (!selectedPayment || !selectedOpId) return

    try {
      const response = await fetch(
        `/api/v1/finance/payments/match/${selectedPayment.id}?op_id=${selectedOpId}&match_type=MANUAL`
      )

      if (!response.ok) {
        throw new Error('Failed to match payment')
      }

      const result: MatchResult = await response.json()
      toast({
        title: t('common.success'),
        description: t('finance.payments.matchSuccess', { 
          payment: selectedPayment.id,
          op: result.matched_op_id 
        }),
      })
      setIsMatchDialogOpen(false)
      setSelectedPayment(null)
      setSelectedOpId('')
      setOpenItems([])
      await fetchUnmatchedPayments()
    } catch (error: unknown) {
      // Matching fehlgeschlagen - Benutzer wird per Toast benachrichtigt
      const errorMessage = error instanceof Error ? error.message : t('finance.payments.matchError')
      toast({
        title: t('common.error'),
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }

  async function autoMatch(): Promise<void> {
    try {
      const response = await fetch('/api/v1/finance/payments/auto-match')
      if (!response.ok) {
        throw new Error('Failed to auto-match')
      }
      const results: MatchResult[] = await response.json()
      toast({
        title: t('common.success'),
        description: t('finance.payments.autoMatchSuccess', { count: results.length }),
      })
      await fetchUnmatchedPayments()
    } catch (_error) {
      // Auto-Matching fehlgeschlagen - Benutzer wird per Toast benachrichtigt
      toast({
        title: t('common.error'),
        description: t('finance.payments.autoMatchError'),
        variant: 'destructive',
      })
    }
  }

  const getMatchStatusColor = (status: string): string => {
    switch (status) {
      case 'MATCHED':
        return 'bg-green-100 text-green-800'
      case 'PARTIAL':
        return 'bg-yellow-100 text-yellow-800'
      case 'MANUAL':
        return 'bg-blue-100 text-blue-800'
      case 'UNMATCHED':
      default:
        return 'bg-red-100 text-red-800'
    }
  }

  const getMatchStatusLabel = (status: string): string => {
    switch (status) {
      case 'MATCHED':
        return t('finance.payments.status.matched')
      case 'PARTIAL':
        return t('finance.payments.status.partial')
      case 'MANUAL':
        return t('finance.payments.status.manual')
      case 'UNMATCHED':
      default:
        return t('finance.payments.status.unmatched')
    }
  }

  const columns = [
    {
      accessorKey: 'booking_date',
      header: t('finance.payments.bookingDate'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <div className="text-sm">
          {format(new Date(row.original.booking_date), 'dd.MM.yyyy', { locale: de })}
        </div>
      ),
    },
    {
      accessorKey: 'amount',
      header: t('crud.fields.amount'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <div className="font-medium">
          {new Intl.NumberFormat('de-DE', { 
            style: 'currency', 
            currency: row.original.currency || 'EUR' 
          }).format(row.original.amount)}
        </div>
      ),
    },
    {
      accessorKey: 'reference',
      header: t('finance.payments.reference'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <div className="text-sm">{row.original.reference || '-'}</div>
      ),
    },
    {
      accessorKey: 'remittance_info',
      header: t('finance.payments.remittanceInfo'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <div className="text-sm max-w-xs truncate">{row.original.remittance_info || '-'}</div>
      ),
    },
    {
      accessorKey: 'match_status',
      header: t('crud.fields.status'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <Badge className={getMatchStatusColor(row.original.match_status)}>
          {getMatchStatusLabel(row.original.match_status)}
        </Badge>
      ),
    },
    {
      id: 'actions',
      header: t('crud.fields.actions'),
      cell: ({ row }: { row: { original: PaymentEntry } }) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setSelectedPayment(row.original)
            if (row.original.creditor_name) {
              fetchOpenItems(row.original.creditor_name)
            }
            setIsMatchDialogOpen(true)
          }}
          disabled={row.original.match_status === 'MATCHED'}
        >
          <Link2 className="h-4 w-4 mr-1" />
          {t('finance.payments.match')}
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">{t('finance.payments.title')}</h2>
          <p className="text-muted-foreground">{t('finance.payments.description')}</p>
        </div>
        <div className="flex items-center space-x-2">
          <Dialog open={isImportDialogOpen} onOpenChange={setIsImportDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                {t('finance.payments.import')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('finance.payments.importTitle')}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium">{t('finance.payments.bankAccount')}</label>
                  <Input
                    value={bankAccount}
                    onChange={(e) => setBankAccount(e.target.value)}
                    placeholder="DE89 3704 0044 0532 0130 00"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">{t('finance.payments.csvFile')}</label>
                  <Input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {t('finance.payments.csvFormat')}
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsImportDialogOpen(false)}>
                  {t('common.cancel')}
                </Button>
                <Button onClick={handleCsvImport} disabled={!csvFile || !bankAccount}>
                  {t('finance.payments.import')}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button onClick={autoMatch}>
            <CheckCircle2 className="h-4 w-4 mr-2" />
            {t('finance.payments.autoMatch')}
          </Button>
        </div>
      </div>

      {/* Payments Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t('finance.payments.paymentsList')}</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={payments} loading={loading} />
        </CardContent>
      </Card>

      {/* Match Dialog */}
      <Dialog open={isMatchDialogOpen} onOpenChange={setIsMatchDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('finance.payments.matchTitle')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {selectedPayment && (
              <div className="space-y-2">
                <p className="text-sm font-medium">{t('finance.payments.selectedPayment')}</p>
                <div className="bg-muted p-3 rounded-md">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">{t('finance.payments.bookingDate')}:</span>{' '}
                      {format(new Date(selectedPayment.booking_date), 'dd.MM.yyyy', { locale: de })}
                    </div>
                    <div>
                      <span className="text-muted-foreground">{t('crud.fields.amount')}:</span>{' '}
                      {new Intl.NumberFormat('de-DE', { 
                        style: 'currency', 
                        currency: selectedPayment.currency || 'EUR' 
                      }).format(selectedPayment.amount)}
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground">{t('finance.payments.reference')}:</span>{' '}
                      {selectedPayment.reference || '-'}
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div>
              <label className="text-sm font-medium">{t('finance.payments.selectOpenItem')}</label>
              <Select value={selectedOpId} onValueChange={setSelectedOpId}>
                <SelectTrigger>
                  <SelectValue placeholder={t('finance.payments.selectOpenItemPlaceholder')} />
                </SelectTrigger>
                <SelectContent>
                  {openItems.map((op) => (
                    <SelectItem key={op.op_id} value={op.op_id}>
                      {op.document_number} - {op.customer_name} -{' '}
                      {new Intl.NumberFormat('de-DE', { 
                        style: 'currency', 
                        currency: op.currency 
                      }).format(op.open_amount)} offen
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsMatchDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={matchPayment} disabled={!selectedOpId}>
              <Link2 className="h-4 w-4 mr-2" />
              {t('finance.payments.match')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

