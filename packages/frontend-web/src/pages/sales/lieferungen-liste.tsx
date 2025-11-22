import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, Search, Truck } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

type Lieferung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  auftragsNr: string
  menge: number
  status: 'geplant' | 'unterwegs' | 'zugestellt' | 'storniert'
}

const mockLieferungen: Lieferung[] = [
  {
    id: '1',
    nummer: 'LF-2025-0001',
    datum: '2025-10-11',
    kunde: 'Landhandel Nord GmbH',
    auftragsNr: 'SO-2025-0001',
    menge: 25,
    status: 'unterwegs',
  },
  {
    id: '2',
    nummer: 'LF-2025-0002',
    datum: '2025-10-10',
    kunde: 'Agrar-Zentrum Süd',
    auftragsNr: 'SO-2025-0002',
    menge: 15,
    status: 'zugestellt',
  },
  {
    id: '3',
    nummer: 'LF-2025-0003',
    datum: '2025-10-12',
    kunde: 'Müller Landwirtschaft',
    auftragsNr: 'SO-2025-0003',
    menge: 10,
    status: 'geplant',
  },
]

const statusVariantMap: Record<Lieferung['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  geplant: 'default',
  unterwegs: 'secondary',
  zugestellt: 'outline',
  storniert: 'destructive',
}

export default function LieferungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'delivery'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lieferung')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Lieferung['status'] | 'alle'>('alle')

  const getStatusLabelLocal = (status: Lieferung['status']): string => {
    const statusMap: Record<Lieferung['status'], string> = {
      geplant: t('status.planned'),
      unterwegs: t('status.inTransit'),
      zugestellt: t('status.delivered'),
      storniert: t('status.cancelled'),
    }
    return statusMap[status] || status
  }

  const filteredLieferungen = mockLieferungen.filter((lieferung) => {
    const matchesSearch =
      lieferung.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lieferung.kunde.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lieferung.auftragsNr.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || lieferung.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.number'),
      render: (lieferung: Lieferung) => (
        <button
          onClick={() => navigate(`/sales/delivery-editor?id=${lieferung.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {lieferung.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.deliveryDate'),
      render: (lieferung: Lieferung) => new Date(lieferung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'auftragsNr' as const,
      label: t('crud.entities.salesOrder'),
      render: (lieferung: Lieferung) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${lieferung.auftragsNr}`)}
          className="text-sm text-blue-600 hover:underline"
        >
          {lieferung.auftragsNr}
        </button>
      ),
    },
    {
      key: 'menge' as const,
      label: t('crud.fields.items'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (lieferung: Lieferung) => (
        <Badge variant={statusVariantMap[lieferung.status]}>{getStatusLabelLocal(lieferung.status)}</Badge>
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
        <Button onClick={() => navigate('/sales/delivery-editor')} className="gap-2">
          <Truck className="h-4 w-4" />
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
              onChange={(e) => setStatusFilter(e.target.value as Lieferung['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="geplant">{t('status.planned')}</option>
              <option value="unterwegs">{t('status.inTransit')}</option>
              <option value="zugestellt">{t('status.delivered')}</option>
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
          <DataTable data={filteredLieferungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredLieferungen.length, total: mockLieferungen.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
