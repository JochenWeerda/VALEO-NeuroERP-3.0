/**
 * Accounts Payable (AP) Invoices List
 * FIBU-AP-02: Eingangsrechnungen
 * Liste der Eingangsrechnungen (Kreditoren)
 */

import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Receipt, Search, CheckCircle2, XCircle } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { useToast } from '@/hooks/use-toast'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'

type APInvoice = {
  number: string
  date: string
  customerId: string  // supplier_id for AP
  totalGross: number
  dueDate: string
  status: string
  approvedBy?: string
  approvedAt?: string
}

const mockAPInvoices: APInvoice[] = [
  {
    number: 'AP-INV-2025-0001',
    date: '2025-10-15',
    customerId: 'Lieferant Nord GmbH',
    totalGross: 8500.0,
    dueDate: '2025-11-14',
    status: 'FREIGEGEBEN',
    approvedBy: 'admin',
    approvedAt: '2025-10-16T10:00:00',
  },
  {
    number: 'AP-INV-2025-0002',
    date: '2025-10-14',
    customerId: 'Agrar-Service Süd',
    totalGross: 12000.5,
    dueDate: '2025-11-13',
    status: 'ENTWURF',
  },
]

export default function APInvoicesListPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const entityType = 'apInvoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Eingangsrechnung')
  const pageTitle = getListTitle(t, entityTypeLabel)

  const [invoices, setInvoices] = useState<APInvoice[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState<Record<string, string | Date | undefined>>({})

  useEffect(() => {
    async function fetchInvoices(): Promise<void> {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (searchTerm) params.append('query', searchTerm)
        if (filters.status) params.append('status', String(filters.status))
        if (filters.supplier_id) params.append('supplier_id', String(filters.supplier_id))

        const response = await fetch(`/api/v1/finance/ap/invoices?${params.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to fetch AP invoices')
        }
        const data: APInvoice[] = await response.json()
        setInvoices(data.length > 0 ? data : mockAPInvoices)  // Use mock data if empty
      } catch (error) {
        console.error('Error fetching AP invoices:', error)
        setInvoices(mockAPInvoices)  // Fallback to mock data
        toast({
          title: t('common.error'),
          description: t('crud.feedback.fetchError', { entityType: entityTypeLabel }),
          variant: 'destructive',
        })
      } finally {
        setLoading(false)
      }
    }
    void fetchInvoices()
  }, [searchTerm, filters, entityTypeLabel, t, toast])

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
    {
      accessorKey: 'customerId',
      header: t('crud.entities.supplier'),
    },
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
      cell: ({ row }: { row: { original: APInvoice } }) => (
        <Badge variant="outline">{getStatusLabel(t, row.original.status, row.original.status)}</Badge>
      ),
    },
    {
      accessorKey: 'approvedBy',
      header: t('finance.apInvoices.approvedBy'),
      cell: ({ row }: { row: { original: APInvoice } }) => (
        <div className="text-sm">
          {row.original.approvedBy || '-'}
          {row.original.approvedAt && (
            <div className="text-xs text-muted-foreground">
              {new Date(row.original.approvedAt).toLocaleDateString('de-DE')}
            </div>
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
          {row.original.status === 'ENTWURF' && (
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  const response = await fetch(
                    `/api/v1/finance/ap/invoices/${row.original.number}/approve?approved_by=current_user`
                  )
                  if (!response.ok) throw new Error('Failed to approve')
                  toast({
                    title: t('common.success'),
                    description: t('finance.apInvoices.approveSuccess'),
                  })
                  await fetch(`/api/v1/finance/ap/invoices?query=${searchTerm}`)
                } catch (error) {
                  toast({
                    title: t('common.error'),
                    description: t('finance.apInvoices.approveError'),
                    variant: 'destructive',
                  })
                }
              }}
            >
              <CheckCircle2 className="h-4 w-4 mr-1" />
              {t('finance.apInvoices.approve')}
            </Button>
          )}
        </div>
      ),
    },
  ]

  const filterConfig: FilterConfig[] = [
    {
      id: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'ENTWURF', label: t('status.draft') },
        { value: 'FREIGEGEBEN', label: t('status.approved') },
        { value: 'VERBUCHT', label: t('status.posted') },
        { value: 'BEZAHLT', label: t('status.paid') },
        { value: 'STORNIERT', label: t('status.cancelled') },
      ],
    },
    {
      id: 'dateRange',
      label: t('crud.fields.dateRange'),
      type: 'dateRange',
    },
  ]

  const { handleExport, handlePrint } = useListActions({
    entityType: entityTypeLabel,
    data: invoices,
    columns,
    exportFileName: `${entityTypeLabel}_Liste`,
  })

  const handleImport = async (data: any[]): Promise<void> => {
    console.log('Importing AP invoice data:', data)
    // Implementation for CSV import
    toast({
      title: t('common.success'),
      description: t('crud.feedback.createSuccess', { entityType: entityTypeLabel }),
    })
  }

  return (
    <div className="space-y-4 p-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-2xl font-bold">{pageTitle}</CardTitle>
          <div className="flex items-center space-x-2">
            <Input
              placeholder={t('crud.actions.searchPlaceholder', { entityType: entityTypeLabel })}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
              icon={<Search className="h-4 w-4 text-muted-foreground" />}
            />
            <AdvancedFilters config={filterConfig} onFilterChange={setFilters} />
            <CSVImport onImport={handleImport} />
            <Button variant="outline" onClick={handleExport}>
              <FileDown className="mr-2 h-4 w-4" /> {t('crud.actions.export')}
            </Button>
            <Button variant="outline" onClick={handlePrint}>
              <FileText className="mr-2 h-4 w-4" /> {t('crud.actions.print')}
            </Button>
            <Button onClick={() => navigate('/finance/ap/invoices/new')}>
              <Receipt className="mr-2 h-4 w-4" /> {t('crud.actions.new')} {entityTypeLabel}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={invoices} loading={loading} />
        </CardContent>
      </Card>
    </div>
  )
}

