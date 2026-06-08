/**
 * Payment Matching UI
 * FIBU-AR-03: Zahlungseingänge & Matching
 * Payment-Match-UI für Bankimport und OP-Zuordnung
 */

import { useState, useEffect } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { NativeSelect } from '@/components/ui/native-select'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Upload, CheckCircle2, Link2 } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { normalizeOperationalStatus } from '@/lib/operational-status'

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
  const navigate = useNavigate()
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
  const [isImporting, setIsImporting] = useState(false)
  const [isAutoMatching, setIsAutoMatching] = useState(false)
  const [isMatching, setIsMatching] = useState(false)

  useEffect(() => {
    fetchUnmatchedPayments()
  }, [])

  async function fetchUnmatchedPayments(): Promise<void> {
    setLoading(true)
    try {
      const { data } = await apiClient.get<PaymentEntry[]>('/api/v1/finance/payments/unmatched', { params: { limit: 100 } })
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
    setIsImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', csvFile)

      const { data } = await apiClient.post<PaymentEntry[]>(
        `/api/v1/finance/payments/import/csv?bank_account=${encodeURIComponent(bankAccount)}`,
        formData,
      )
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
    } finally {
      setIsImporting(false)
    }
  }

  async function fetchMatchSuggestions(paymentId: string): Promise<void> {
    try {
      const { data } = await apiClient.get<OpenItemMatch[]>(`/api/v1/finance/payments/match-suggestions/${paymentId}`)
      setOpenItems(data)
    } catch (_error) {
      // Keine offenen Posten gefunden oder API nicht erreichbar
      setOpenItems([])
    }
  }

  async function matchPayment(): Promise<void> {
    if (!selectedPayment || !selectedOpId) return
    setIsMatching(true)
    try {
      const { data: result } = await apiClient.post<MatchResult>(
        `/api/v1/finance/payments/match/${selectedPayment.id}?op_id=${selectedOpId}&match_type=MANUAL`
      )
      // OTC-011-P4: Deep-Link zu OP-Debitoren nach Match
      const matchedOp = result.matched_op_id
      toast({
        title: t('common.success'),
        description: t('finance.payments.matchSuccess', {
          payment: selectedPayment.id,
          op: matchedOp
        }),
        action: matchedOp ? (
          <Button variant="outline" size="sm" onClick={() => navigate(`/finance/op-debitoren?opId=${encodeURIComponent(matchedOp)}`)}>
            OP öffnen
          </Button>
        ) : undefined,
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
    } finally {
      setIsMatching(false)
    }
  }

  async function autoMatch(): Promise<void> {
    setIsAutoMatching(true)
    try {
      const { data: results } = await apiClient.post<MatchResult[]>('/api/v1/finance/payments/auto-match')
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
    } finally {
      setIsAutoMatching(false)
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
            fetchMatchSuggestions(row.original.id)
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
  const openItemOptions = openItems.map((op) => ({
    value: op.op_id,
    label: `${op.document_number} - ${op.customer_name} - ${new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: op.currency,
    }).format(op.open_amount)} offen`,
  }))
  const offeneZahlungen = payments.filter((payment) => payment.match_status === 'UNMATCHED').length
  const gesamtBetrag = payments.reduce((sum, payment) => sum + payment.amount, 0)
  const matchRate = payments.length > 0 ? Math.round((payments.filter((payment) => payment.match_status === 'MATCHED').length / payments.length) * 100) : 0
  const manualReviewCount = payments.filter((payment) => payment.match_status === 'PARTIAL' || payment.match_status === 'MANUAL').length
  const operationalStatus = normalizeOperationalStatus(
    offeneZahlungen > 0 ? (manualReviewCount > 0 ? 'eskaliert' : 'wartet_auf_mensch') : 'abgeschlossen'
  )
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Offene Zahlungen', value: String(offeneZahlungen) },
        { label: 'Manuelle Klaerung', value: String(manualReviewCount) },
        { label: 'Auto-Match-Rate', value: `${matchRate}%` },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        {
          label: 'Gefilterter Betrag',
          value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag),
        },
        { label: 'Importformat', value: 'CSV' },
        { label: 'Bankkonto', value: bankAccount || 'Noch nicht gesetzt' },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: offeneZahlungen > 0 ? 'Zuordnung pruefen oder Auto-Match starten' : 'Abgleich archivieren' },
        { label: 'Blocker', value: selectedPayment ? 'Zahlung wartet auf Zuordnung' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Unmatched-Liste geladen', detail: `${payments.length} Zahlung(en) im Matchingraum` },
    selectedPayment
      ? {
          label: 'Manuelle Zuordnung aktiv',
          detail: `${selectedPayment.id} wartet auf OP-Entscheidung`,
          timestamp: selectedPayment.booking_date,
        }
      : null,
    csvFile
      ? {
          label: 'Import vorbereitet',
          detail: `${csvFile.name} fuer CSV-Import`,
        }
      : null,
  ].filter((item): item is { label: string; detail: string; timestamp?: string } => item !== null)

  return (
    <div className="space-y-6 p-6">
      <OperationalCaseHeader
        title={t('finance.payments.title')}
        description={t('finance.payments.description')}
        status={operationalStatus}
        owner="Debitorenbuchhaltung"
        blocker={selectedPayment ? 'Ausgewaehlte Zahlung ist noch keinem OP zugeordnet.' : offeneZahlungen > 0 ? 'Zahlungseingaenge warten auf Matching.' : null}
        nextAction={offeneZahlungen > 0 ? 'Offene Zahlungen matchen oder Auto-Match ausfuehren' : 'Abgleich dokumentieren'}
        caseLabel="Zahlungseingang"
        tags={['FIBU', 'Matching']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Letzte Aktivitaeten" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
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
                <Button onClick={() => void handleCsvImport()} disabled={isImporting || !csvFile || !bankAccount}>
                  {t('finance.payments.import')}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button onClick={() => void autoMatch()} disabled={isAutoMatching}>
            <CheckCircle2 className="h-4 w-4 mr-2" />
            {isAutoMatching ? t('finance.payments.autoMatching', { defaultValue: 'Matching läuft…' }) : t('finance.payments.autoMatch')}
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
              <NativeSelect
                value={selectedOpId}
                onValueChange={setSelectedOpId}
                options={openItemOptions}
                placeholder={t('finance.payments.selectOpenItemPlaceholder')}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsMatchDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={() => void matchPayment()} disabled={isMatching || !selectedOpId}>
              <Link2 className="h-4 w-4 mr-2" />
              {t('finance.payments.match')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

