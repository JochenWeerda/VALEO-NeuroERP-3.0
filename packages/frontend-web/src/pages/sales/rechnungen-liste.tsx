import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, Receipt, Search } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

type Rechnung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  auftragsNr: string
  betrag: number
  faelligAm: string
  status: 'offen' | 'teilbezahlt' | 'bezahlt' | 'ueberfaellig' | 'storniert'
}

const mockRechnungen: Rechnung[] = [
  {
    id: '1',
    nummer: 'RE-2025-0001',
    datum: '2025-10-11',
    kunde: 'Landhandel Nord GmbH',
    auftragsNr: 'SO-2025-0001',
    betrag: 12500.0,
    faelligAm: '2025-11-10',
    status: 'offen',
  },
  {
    id: '2',
    nummer: 'RE-2025-0002',
    datum: '2025-10-10',
    kunde: 'Agrar-Zentrum Süd',
    auftragsNr: 'SO-2025-0002',
    betrag: 8750.5,
    faelligAm: '2025-11-09',
    status: 'bezahlt',
  },
  {
    id: '3',
    nummer: 'RE-2025-0003',
    datum: '2025-09-15',
    kunde: 'Müller Landwirtschaft',
    auftragsNr: 'SO-2024-0890',
    betrag: 5200.0,
    faelligAm: '2025-10-15',
    status: 'ueberfaellig',
  },
]

const statusVariantMap: Record<
  Rechnung['status'],
  'default' | 'outline' | 'secondary' | 'destructive'
> = {
  offen: 'default',
  teilbezahlt: 'secondary',
  bezahlt: 'outline',
  ueberfaellig: 'destructive',
  storniert: 'destructive',
}

export default function RechnungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'invoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnung')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Rechnung['status'] | 'alle'>('alle')

  const getStatusLabelLocal = (status: Rechnung['status']): string => {
    const statusMap: Record<Rechnung['status'], string> = {
      offen: t('status.pending'),
      teilbezahlt: t('status.partial'),
      bezahlt: t('status.paid'),
      ueberfaellig: t('status.overdue'),
      storniert: t('status.cancelled'),
    }
    return statusMap[status] || status
  }

  const filteredRechnungen = mockRechnungen.filter((rechnung) => {
    const matchesSearch =
      rechnung.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rechnung.kunde.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rechnung.auftragsNr.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || rechnung.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.invoiceNumber'),
      render: (rechnung: Rechnung) => (
        <button
          onClick={() => navigate(`/sales/invoice-editor?id=${rechnung.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {rechnung.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.invoiceDate'),
      render: (rechnung: Rechnung) => new Date(rechnung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'auftragsNr' as const,
      label: t('crud.entities.salesOrder'),
      render: (rechnung: Rechnung) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${rechnung.auftragsNr}`)}
          className="text-sm text-blue-600 hover:underline"
        >
          {rechnung.auftragsNr}
        </button>
      ),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (rechnung: Rechnung) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
          rechnung.betrag
        ),
    },
    {
      key: 'faelligAm' as const,
      label: t('crud.fields.paymentDue'),
      render: (rechnung: Rechnung) => new Date(rechnung.faelligAm).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (rechnung: Rechnung) => (
        <Badge variant={statusVariantMap[rechnung.status]}>{getStatusLabelLocal(rechnung.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{pageTitle}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/invoice-editor')} className="gap-2">
          <Receipt className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.filter')} & {t('crud.actions.search')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.actions.search') + '...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Rechnung['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="offen">{t('status.pending')}</option>
              <option value="teilbezahlt">{t('status.partial')}</option>
              <option value="bezahlt">{t('status.paid')}</option>
              <option value="ueberfaellig">{t('status.overdue')}</option>
              <option value="storniert">{t('status.cancelled')}</option>
            </select>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredRechnungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredRechnungen.length, total: mockRechnungen.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
