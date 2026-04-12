/**
 * Accounts Payable (AP) Invoices List
 * FIBU-AP-02: Eingangsrechnungen
 */

import { useMemo, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Receipt, CheckCircle2 } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { useToast } from '@/hooks/use-toast'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'
import { buildDecisionView } from '@/policy/decision-view'
import { CompactDecisionCard } from '@/components/workflow/CompactDecisionCard'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type APInvoice = {
  number: string
  date: string
  customerId: string
  totalGross: number
  dueDate: string
  status: string
  semantic_status?: string
  approvedBy?: string
  approvedAt?: string
  approval_status?: string
  approval_current_approvals?: number
  approval_required_approvals?: number
  approval_can_post?: boolean
  approval_explainability?: unknown
}

export default function APInvoicesListPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const entityType = 'apInvoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Eingangsrechnung')
  const pageTitle = getListTitle(t, entityTypeLabel)

  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState<Record<string, string | Date | undefined>>({})

  const queryKey = useMemo(() => ['finance', 'ap', 'invoices', searchTerm, filters], [searchTerm, filters])
  const {
    data: invoices = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey,
    queryFn: async () => {
      const params = new URLSearchParams()
      if (searchTerm) params.append('query', searchTerm)
      if (filters.status) params.append('status', String(filters.status))
      if (filters.supplier_id) params.append('supplier_id', String(filters.supplier_id))
      return await apiClient.get<APInvoice[]>(`/api/v1/finance/ap/invoices?${params.toString()}`)
    },
    staleTime: 2 * 60 * 1000,
  })

  const columns = [
    {
      accessorKey: 'number',
      header: t('crud.fields.invoiceNumber'),
      cell: ({ row }: { row: { original: APInvoice } }) => (
        <Link to={`/finance/ap/invoices/${row.original.number}`} className="text-primary hover:underline">
          {row.original.number}
        </Link>
      ),
    },
    {
      accessorKey: 'date',
      header: t('crud.fields.date'),
      cell: ({ row }: { row: { original: APInvoice } }) => formatDateForExport(row.original.date),
    },
    { accessorKey: 'customerId', header: t('crud.entities.supplier') },
    {
      accessorKey: 'totalGross',
      header: t('crud.fields.amount'),
      cell: ({ row }: { row: { original: APInvoice } }) => formatCurrencyForExport(row.original.totalGross, 'EUR'),
    },
    {
      accessorKey: 'dueDate',
      header: t('crud.fields.dueDate'),
      cell: ({ row }: { row: { original: APInvoice } }) => formatDateForExport(row.original.dueDate),
    },
    {
      accessorKey: 'status',
      header: t('crud.fields.status'),
      cell: ({ row }: { row: { original: APInvoice } }) => {
        const invoice = row.original
        const displayStatus = invoice.semantic_status ?? invoice.status
        const decisionView = buildDecisionView(invoice.approval_explainability)
        return (
          <div className="space-y-1">
            <Badge variant="outline">{getStatusLabel(t, displayStatus, displayStatus)}</Badge>
            {typeof invoice.approval_current_approvals === 'number' &&
            typeof invoice.approval_required_approvals === 'number' &&
            invoice.approval_required_approvals > 0 ? (
              <div className="text-xs text-muted-foreground">
                {invoice.approval_current_approvals}/{invoice.approval_required_approvals} Freigaben
              </div>
            ) : null}
            {decisionView !== null ? (
              <CompactDecisionCard view={decisionView} pageDomain="finance-approval" showDetails={false} />
            ) : null}
          </div>
        )
      },
    },
    {
      accessorKey: 'approvedBy',
      header: t('finance.apInvoices.approvedBy'),
      cell: ({ row }: { row: { original: APInvoice } }) => (
        <div className="text-sm">
          {row.original.approvedBy || '-'}
          {row.original.approvedAt && (
            <div className="text-xs text-muted-foreground">{new Date(row.original.approvedAt).toLocaleDateString('de-DE')}</div>
          )}
        </div>
      ),
    },
    {
      id: 'actions',
      header: t('crud.fields.actions'),
      cell: ({ row }: { row: { original: APInvoice } }) => (
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="sm" onClick={() => navigate(`/finance/ap/invoices/${row.original.number}`)}>
            {t('crud.actions.view')}
          </Button>
          {(row.original.semantic_status ?? row.original.status) === 'ENTWURF' && (
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  await apiClient.post('/api/v1/ap/approval-workflow/request', {
                    invoice_id: row.original.number,
                    requested_by: 'current_user',
                  })
                  toast({
                    title: t('common.success'),
                    description: t('finance.apInvoices.requestApprovalSuccess', {
                      defaultValue: 'Freigabe wurde angefordert',
                    }),
                  })
                  await refetch()
                } catch (e: any) {
                  const msg =
                    e?.response?.data?.detail ||
                    t('finance.apInvoices.requestApprovalError', {
                      defaultValue: 'Freigabeanforderung fehlgeschlagen',
                    })
                  toast({ title: t('common.error'), description: msg, variant: 'destructive' })
                }
              }}
            >
              <CheckCircle2 className="h-4 w-4 mr-1" />
              {t('finance.apInvoices.requestApproval', { defaultValue: 'Freigabe anfordern' })}
            </Button>
          )}
          {row.original.approval_can_post === true && (
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  await apiClient.post(`/api/v1/finance/ap/invoices/${row.original.number}/post?posted_by=current_user`)
                  toast({ title: t('common.success'), description: t('finance.apInvoices.postSuccess', { defaultValue: 'Eingangsrechnung verbucht' }) })
                  await refetch()
                } catch (e: any) {
                  const msg = e?.response?.data?.detail || t('finance.apInvoices.postError', { defaultValue: 'Verbuchen fehlgeschlagen' })
                  toast({ title: t('common.error'), description: msg, variant: 'destructive' })
                }
              }}
            >
              <CheckCircle2 className="h-4 w-4 mr-1" />
              {t('crud.actions.post', { defaultValue: 'Verbuchen' })}
            </Button>
          )}
        </div>
      ),
    },
  ]

  const filterConfig: FilterConfig[] = [
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'ENTWURF', label: t('status.draft') },
        {
          value: 'ZUR_FREIGABE',
          label: t('finance.apInvoices.pendingApproval', { defaultValue: 'Zur Freigabe' }),
        },
        { value: 'FREIGEGEBEN', label: t('status.approved') },
        { value: 'VERBUCHT', label: t('status.posted') },
        { value: 'BEZAHLT', label: t('status.paid') },
        { value: 'STORNIERT', label: t('status.cancelled') },
      ],
    },
    { key: 'dateRange', label: t('crud.fields.dateRange'), type: 'dateRange' },
  ]

  const exportColumns: Array<{ key: keyof APInvoice; label: string }> = [
    { key: 'number', label: t('crud.fields.invoiceNumber') },
    { key: 'date', label: t('crud.fields.date') },
    { key: 'customerId', label: t('crud.entities.supplier') },
    { key: 'totalGross', label: t('crud.fields.amount') },
    { key: 'dueDate', label: t('crud.fields.dueDate') },
    { key: 'status', label: t('crud.fields.status') },
    { key: 'approvedBy', label: t('finance.apInvoices.approvedBy') },
  ]

  const { handleExport, handlePrint } = useListActions({
    entityName: entityTypeLabel,
    data: invoices,
    columns: exportColumns,
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const pendingApproval = invoices.filter((invoice) => (invoice.semantic_status ?? invoice.status) === 'ZUR_FREIGABE').length
  const readyToPost = invoices.filter((invoice) => invoice.approval_can_post === true).length
  const operationalStatus = normalizeOperationalStatus(
    pendingApproval > 0 ? 'wartet_auf_mensch' : readyToPost > 0 ? 'in_pruefung' : invoices.length > 0 ? 'abgeschlossen' : 'offen',
  )
  const contextSections = [
    {
      title: 'Pruef- und Freigabelage',
      items: [
        { label: 'Rechnungen', value: `${invoices.length}` },
        { label: 'Zur Freigabe', value: `${pendingApproval}` },
        { label: 'Buchbar', value: `${readyToPost}` },
      ],
    },
    {
      title: 'Folgepfad',
      items: [
        { label: 'Suchbegriff', value: searchTerm || 'Keine Einschraenkung' },
        { label: 'Statusfilter', value: String(filters.status || 'Alle') },
        { label: 'Naechste Aktion', value: pendingApproval > 0 ? 'Freigabestau abbauen' : readyToPost > 0 ? 'Buchbare Rechnungen verbuchen' : 'Neue Eingangsrechnung anlegen oder importieren' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: pendingApproval > 0 ? 'Freigabestau aktiv' : 'Keine offene Freigabestufe',
      detail: pendingApproval > 0
        ? `${pendingApproval} Eingangsrechnungen warten derzeit auf eine menschliche Freigabeentscheidung.`
        : 'Der aktuelle Listenstand zeigt keinen offenen Freigabestau.',
    },
    {
      label: readyToPost > 0 ? 'Buchbare Rechnungen vorhanden' : 'Kein Buchungspuffer aktiv',
      detail: readyToPost > 0
        ? `${readyToPost} Rechnungen koennen direkt in den Buchungspfad uebergehen.`
        : 'Im aktuellen Ausschnitt ist keine unmittelbar buchbare Rechnung sichtbar.',
    },
  ]

  const handleImport = async (): Promise<void> => {
    toast({ title: t('common.success'), description: t('crud.feedback.createSuccess', { entityType: entityTypeLabel }) })
  }

  return (
    <div className="space-y-4 p-4">
      <OperationalCaseHeader
        title="AP Invoices"
        description="Eingangsrechnungen werden als Pruef-, Freigabe- und Buchungsstauplatz gefuehrt."
        status={operationalStatus}
        owner="Kreditorenbuchhaltung"
        blocker={pendingApproval > 0 ? `${pendingApproval} Rechnungen blockieren den naechsten Buchungsschritt.` : null}
        nextAction={pendingApproval > 0 ? 'Freigaben einholen' : readyToPost > 0 ? 'Rechnungen verbuchen' : 'Neue Rechnung importieren oder erfassen'}
        caseLabel="Vorgang: AP-Invoices"
        tags={['FIBU', 'AP', 'Freigabe']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="AP-Verlauf" items={timelineItems} />
        <OperationalContextPanel title="AP-Kontext" sections={contextSections} />
      </div>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-2xl font-bold">{pageTitle}</CardTitle>
          <div className="flex items-center space-x-2">
            <Input
              placeholder={t('crud.actions.searchPlaceholder', { entityType: entityTypeLabel })}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
            <AdvancedFilters filters={filterConfig} values={filters} onChange={setFilters} onReset={() => setFilters({})} />
            <CSVImport onImport={handleImport} entityName={entityTypeLabel} />
            <Button variant="outline" onClick={handleExport}><FileDown className="mr-2 h-4 w-4" /> {t('crud.actions.export')}</Button>
            <Button variant="outline" onClick={handlePrint}><FileText className="mr-2 h-4 w-4" /> {t('crud.actions.print')}</Button>
            <Button onClick={() => navigate('/finance/ap/invoices/new')}><Receipt className="mr-2 h-4 w-4" /> {t('crud.actions.new')} {entityTypeLabel}</Button>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={invoices} loading={isLoading} />
        </CardContent>
      </Card>
    </div>
  )
}
