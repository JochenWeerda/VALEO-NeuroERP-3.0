import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { NativeSelect } from '@/components/ui/native-select'
import { AlertTriangle, CheckCircle, Search, Upload, Link2, Sparkles } from 'lucide-react'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useTenant } from '@/hooks/useTenant'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'

type Zahlungseingang = {
  id: string
  booking_date: string
  amount: number
  remittance_info?: string
  reference?: string
  creditor_name?: string
  debtor_name?: string
  match_status: 'UNMATCHED' | 'MATCHED' | 'PARTIAL' | 'MANUAL'
  matched_op_id?: string
  confidence?: number
  match_reason?: string
}

type OpenItem = {
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

const statusVariantMap: Record<
  Zahlungseingang['match_status'],
  'default' | 'outline' | 'secondary' | 'destructive'
> = {
  MATCHED: 'outline',
  UNMATCHED: 'default',
  PARTIAL: 'secondary',
  MANUAL: 'outline',
}

const statusIconMap: Record<Zahlungseingang['match_status'], JSX.Element> = {
  MATCHED: <CheckCircle className="h-4 w-4 text-green-600" />,
  UNMATCHED: <AlertTriangle className="h-4 w-4 text-orange-600" />,
  PARTIAL: <AlertTriangle className="h-4 w-4 text-yellow-600" />,
  MANUAL: <Link2 className="h-4 w-4 text-blue-600" />,
}

export default function ZahlungseingangsPage(): JSX.Element {
  const { t } = useTranslation()
  const { tenantId } = useTenant()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Zahlungseingang['match_status'] | 'alle'>('alle')
  const [selectedPayment, setSelectedPayment] = useState<Zahlungseingang | null>(null)
  const [openItems, setOpenItems] = useState<OpenItem[]>([])
  const [matchDialogOpen, setMatchDialogOpen] = useState(false)
  const [autoMatching, setAutoMatching] = useState(false)
  const [bankImportOpen, setBankImportOpen] = useState(false)
  const [bankImportFile, setBankImportFile] = useState<File | null>(null)
  const [bankImportFormat, setBankImportFormat] = useState<'CAMT' | 'MT940' | 'CSV'>('CAMT')
  const [bankImportAccountId, setBankImportAccountId] = useState<string>('')
  const [bankImportSubmitting, setBankImportSubmitting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const {
    data: zahlungen = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['finance', 'payment-matching', 'unmatched', tenantId],
    queryFn: async () => {
      const response = await apiClient.get<Zahlungseingang[]>(
        `/api/v1/finance/payments/unmatched?tenant_id=${tenantId}&limit=100`,
      )
      return response.data
    },
    staleTime: 60 * 1000,
  })

  const { data: bankAccounts = [] } = useQuery({
    queryKey: ['finance', 'bank-accounts'],
    queryFn: async () => {
      const response = await apiClient.get<{ id: string; account_number?: string; account_name?: string }[]>(
        '/api/v1/finance/bank-accounts',
      )
      return Array.isArray(response.data) ? response.data : []
    },
    enabled: bankImportOpen,
  })
  useEffect(() => {
    if (bankImportOpen && bankAccounts.length > 0 && !bankImportAccountId) {
      setBankImportAccountId(bankAccounts[0].id)
    }
  }, [bankImportOpen, bankAccounts, bankImportAccountId])

  const handleBankImportClick = () => setBankImportOpen(true)

  const handleBankImportSubmit = async () => {
    if (!bankImportFile || !bankImportAccountId) {
      toast({ variant: 'destructive', title: t('crud.messages.paymentMatching.bankImport'), description: 'Bitte Datei und Konto auswählen.' })
      return
    }
    setBankImportSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('file', bankImportFile)
      await apiClient.post(
        `/api/v1/finance/bank-statements/import?format=${bankImportFormat}&bank_account_id=${encodeURIComponent(bankImportAccountId)}&tenant_id=${tenantId}&auto_match=false`,
        formData,
      )
      toast({ title: t('crud.messages.paymentMatching.bankImport'), description: 'Kontoauszug importiert. Liste wird aktualisiert.' })
      setBankImportOpen(false)
      setBankImportFile(null)
      setBankImportAccountId('')
      void refetch()
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Bank-Import fehlgeschlagen',
        description: err instanceof Error ? err.message : String(err),
      })
    } finally {
      setBankImportSubmitting(false)
    }
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const filteredZahlungen = zahlungen.filter((zahlung) => {
    const matchesSearch =
      (zahlung.remittance_info || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (zahlung.creditor_name || zahlung.debtor_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (zahlung.reference || '').toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || zahlung.match_status === statusFilter
    return matchesSearch && matchesStatus
  })

  const offeneZahlungen = zahlungen.filter((z) => z.match_status === 'UNMATCHED').length
  const gesamtBetrag = filteredZahlungen.reduce((sum, z) => sum + z.amount, 0)
  const matchedCount = zahlungen.filter((z) => z.match_status === 'MATCHED').length
  const matchRate = zahlungen.length > 0 ? Math.round((matchedCount / zahlungen.length) * 100) : 0

  const handleAutoMatch = async () => {
    setAutoMatching(true)
    try {
      const response = await apiClient.post<unknown[]>(
        `/api/v1/finance/payments/auto-match?tenant_id=${tenantId}`,
      )
      const results = Array.isArray(response.data) ? response.data : []
      toast({
        title: t('crud.messages.autoMatchSuccess'),
        description: t('crud.messages.autoMatchSuccessDesc', { count: results.length })
      })
      await refetch()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.autoMatchError'),
        description: error instanceof Error ? error.message : String(error)
      })
    } finally {
      setAutoMatching(false)
    }
  }

  const handleMatch = async (payment: Zahlungseingang) => {
    setSelectedPayment(payment)
    // Load open items for customer
    try {
      // Extract customer ID from payment (would need to be determined from creditor/debtor)
      const response = await apiClient.get<OpenItem[]>(
        `/api/v1/finance/payments/match-suggestions/${payment.id}?tenant_id=${tenantId}`,
      )
      setOpenItems(response.data)
      setMatchDialogOpen(true)
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.matchError'),
        description: error instanceof Error ? error.message : String(error),
      })
    }
  }

  const handleConfirmMatch = async (opId: string) => {
    if (!selectedPayment) return

    try {
      await apiClient.post(
        `/api/v1/finance/payments/match/${selectedPayment.id}?op_id=${opId}&match_type=MANUAL&tenant_id=${tenantId}`,
      )
      toast({
        title: t('crud.messages.matchSuccess'),
        description: t('crud.messages.matchSuccessDesc')
      })
      setMatchDialogOpen(false)
      setSelectedPayment(null)
      await refetch()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.matchError'),
        description: error instanceof Error ? error.message : String(error)
      })
    }
  }

  const columns = [
    {
      key: 'status' as const,
      label: '',
      render: (zahlung: Zahlungseingang) => statusIconMap[zahlung.match_status],
    },
    {
      key: 'booking_date' as const,
      label: t('crud.messages.paymentMatching.columns.date'),
      render: (zahlung: Zahlungseingang) => new Date(zahlung.booking_date).toLocaleDateString('de-DE'),
    },
    {
      key: 'kontoinhaber' as const,
      label: t('crud.messages.paymentMatching.columns.accountHolder'),
      render: (zahlung: Zahlungseingang) => (
        <div>
          <div className="font-medium">{zahlung.creditor_name || zahlung.debtor_name || '-'}</div>
          <div className="text-sm text-muted-foreground">{zahlung.remittance_info || zahlung.reference || ''}</div>
        </div>
      ),
    },
    {
      key: 'amount' as const,
      label: t('crud.messages.paymentMatching.columns.amount'),
      render: (zahlung: Zahlungseingang) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(zahlung.amount)}
        </span>
      ),
    },
    {
      key: 'reference' as const,
      label: t('crud.messages.paymentMatching.columns.reference'),
      render: (zahlung: Zahlungseingang) =>
        zahlung.reference ? (
          <span className="text-sm text-blue-600">{zahlung.reference}</span>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'confidence' as const,
      label: t('crud.messages.paymentMatching.columns.confidence'),
      render: (zahlung: Zahlungseingang) =>
        zahlung.confidence !== undefined ? (
          <div className="flex items-center gap-1">
            <span className="text-sm font-medium">{Math.round(zahlung.confidence * 100)}%</span>
            {zahlung.confidence > 0.8 && <CheckCircle className="h-3 w-3 text-green-600" />}
          </div>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'statusBadge' as const,
      label: t('crud.messages.paymentMatching.columns.status'),
      render: (zahlung: Zahlungseingang) => (
        <Badge variant={statusVariantMap[zahlung.match_status]}>
          {getStatusLabel(t, zahlung.match_status, zahlung.match_status)}
        </Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: t('crud.messages.paymentMatching.columns.actions'),
      render: (zahlung: Zahlungseingang) => (
        <div className="flex gap-2">
          {zahlung.match_status === 'UNMATCHED' && (
            <Button size="sm" variant="outline" onClick={() => handleMatch(zahlung)}>
              {t('crud.messages.paymentMatching.match')}
            </Button>
          )}
          {zahlung.match_status === 'PARTIAL' && (
            <Button size="sm" variant="outline" onClick={() => handleMatch(zahlung)}>
              {t('crud.messages.paymentMatching.clarify')}
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.messages.paymentMatching.title')}</h1>
          <p className="text-muted-foreground">{t('crud.messages.paymentMatching.subtitle')}</p>
        </div>
        <Button className="gap-2" onClick={handleBankImportClick}>
          <Upload className="h-4 w-4" />
          {t('crud.messages.paymentMatching.bankImport')}
        </Button>
      </div>

      <Dialog open={bankImportOpen} onOpenChange={setBankImportOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t('crud.messages.paymentMatching.bankImport')}</DialogTitle>
            <DialogDescription>CAMT.053, MT940 oder CSV. Nach dem Import können Sie die Zuordnung prüfen.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Datei</Label>
              <Input
                type="file"
                accept=".xml,.csv,.940,.sta"
                ref={fileInputRef}
                onChange={(e) => setBankImportFile(e.target.files?.[0] ?? null)}
                className="mt-1"
              />
            </div>
            <div>
              <Label>Format</Label>
              <NativeSelect
                value={bankImportFormat}
                onValueChange={(v) => setBankImportFormat(v as 'CAMT' | 'MT940' | 'CSV')}
                options={[
                  { value: 'CAMT', label: 'CAMT.053 (XML)' },
                  { value: 'MT940', label: 'MT940' },
                  { value: 'CSV', label: 'CSV' },
                ]}
              />
            </div>
            <div>
              <Label>Bankkonto</Label>
              <NativeSelect
                value={bankImportAccountId || (bankAccounts[0]?.id ?? '')}
                onValueChange={setBankImportAccountId}
                placeholder="Konto waehlen"
                options={bankAccounts.map((acc) => ({
                  value: acc.id,
                  label: acc.account_name || acc.account_number || acc.id,
                }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBankImportOpen(false)}>Abbrechen</Button>
            <Button onClick={handleBankImportSubmit} disabled={bankImportSubmitting || !bankImportFile || !bankImportAccountId}>
              {bankImportSubmitting ? 'Importiere…' : 'Importieren'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.messages.paymentMatching.unmatchedPayments')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{offeneZahlungen}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.messages.paymentMatching.totalFiltered')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.messages.paymentMatching.autoMatchRate')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{matchRate}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.messages.paymentMatching.filterAndSearch')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.messages.paymentMatching.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <NativeSelect
              className="w-[180px]"
              value={statusFilter}
              onValueChange={(value) => setStatusFilter(value as Zahlungseingang['match_status'] | 'alle')}
              placeholder={t('crud.messages.paymentMatching.columns.status')}
              options={[
                { value: 'alle', label: t('crud.messages.paymentMatching.allStatus') },
                { value: 'MATCHED', label: t('crud.messages.paymentMatching.matched') },
                { value: 'UNMATCHED', label: t('crud.messages.paymentMatching.unmatched') },
                { value: 'PARTIAL', label: t('crud.messages.paymentMatching.partial') },
                { value: 'MANUAL', label: t('crud.messages.paymentMatching.manual') },
              ]}
            />
            <Button variant="outline" onClick={handleAutoMatch} disabled={autoMatching}>
              <Sparkles className="h-4 w-4 mr-2" />
              {autoMatching ? t('crud.messages.paymentMatching.matching') : t('crud.messages.paymentMatching.startAutoMatch')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="text-center py-8">{t('crud.messages.paymentMatching.loading')}</div>
          ) : (
            <>
              <DataTable data={filteredZahlungen} columns={columns} />
              <div className="mt-4 text-sm text-muted-foreground">
                {t('crud.messages.paymentMatching.showing', { filtered: filteredZahlungen.length, total: zahlungen.length })}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Match Dialog */}
      <Dialog open={matchDialogOpen} onOpenChange={setMatchDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.messages.paymentMatching.matchDialog.title')}</DialogTitle>
            <DialogDescription>
              {t('crud.messages.paymentMatching.matchDialog.description', { 
                reference: selectedPayment?.reference || selectedPayment?.remittance_info || '' 
              })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedPayment && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">{t('crud.messages.paymentMatching.matchDialog.amount')}</div>
                    <div className="font-semibold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(selectedPayment.amount)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">{t('crud.messages.paymentMatching.matchDialog.date')}</div>
                    <div className="font-semibold">{new Date(selectedPayment.booking_date).toLocaleDateString('de-DE')}</div>
                  </div>
                </div>
              </div>
            )}
            <div className="max-h-96 overflow-y-auto">
              {openItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.paymentMatching.matchDialog.noOpenItems')}</div>
              ) : (
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">{t('crud.messages.paymentMatching.matchDialog.invoice')}</th>
                      <th className="text-left p-2">{t('crud.messages.paymentMatching.matchDialog.customer')}</th>
                      <th className="text-right p-2">{t('crud.messages.paymentMatching.matchDialog.open')}</th>
                      <th className="text-right p-2">{t('crud.messages.paymentMatching.matchDialog.due')}</th>
                      <th className="text-center p-2">{t('crud.messages.paymentMatching.matchDialog.action')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {openItems.map((op) => (
                      <tr key={op.op_id} className="border-b hover:bg-muted/50">
                        <td className="p-2">{op.document_number}</td>
                        <td className="p-2">{op.customer_name}</td>
                        <td className="p-2 text-right">
                          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.open_amount)}
                        </td>
                        <td className="p-2 text-right">{new Date(op.due_date).toLocaleDateString('de-DE')}</td>
                        <td className="p-2 text-center">
                          <Button size="sm" onClick={() => handleConfirmMatch(op.op_id)}>
                            {t('crud.messages.paymentMatching.match')}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setMatchDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
