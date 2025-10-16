import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Lieferanten
const apiClient = createApiClient('/api/crm')

// Konfiguration für Lieferanten ListReport
const lieferantenListConfig: ListConfig = {
  title: 'Lieferanten-Liste',
  subtitle: 'Übersicht aller Lieferanten und deren Konditionen',
  type: 'list-report',
  columns: [
    {
      key: 'firma',
      label: 'Firma',
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          {row.nachname && <div className="text-sm text-muted-foreground">{row.vorname} {row.nachname}</div>}
        </div>
      )
    },
    {
      key: 'ort',
      label: 'Ort',
      sortable: true,
      filterable: true,
      render: (value, row) => `${row.plz} ${value}`
    },
    {
      key: 'land',
      label: 'Land',
      filterable: true,
      render: (value) => {
        const countries = {
          'DE': '🇩🇪 Deutschland',
          'AT': '🇦🇹 Österreich',
          'CH': '🇨🇭 Schweiz',
          'NL': '🇳🇱 Niederlande',
          'DK': '🇩🇰 Dänemark',
          'PL': '🇵🇱 Polen',
          'FR': '🇫🇷 Frankreich',
          'IT': '🇮🇹 Italien'
        }
        return countries[value as keyof typeof countries] || value
      }
    },
    {
      key: 'telefon',
      label: 'Telefon',
      render: (value) => value || '-'
    },
    {
      key: 'email',
      label: 'E-Mail',
      render: (value) => value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'
    },
    {
      key: 'zahlungsbedingungen',
      label: 'Z-Bedingungen',
      sortable: true,
      filterable: true,
      render: (value) => value || '30 Tage'
    },
    {
      key: 'rabatt',
      label: 'Rabatt',
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    },
    {
      key: 'mindestbestellwert',
      label: 'Min.-Bestellwert',
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'lieferzeit',
      label: 'Lieferzeit',
      sortable: true,
      render: (value) => value ? `${value} Tage` : '-'
    },
    {
      key: 'qualitaetszertifikat',
      label: 'QS-Zert.',
      render: (value) => value ? <Badge variant="outline">✅</Badge> : <Badge variant="secondary">❌</Badge>
    },
    {
      key: 'bioZertifiziert',
      label: 'Bio-Zert.',
      render: (value) => value ? <Badge variant="outline">🌱</Badge> : <Badge variant="secondary">❌</Badge>
    },
    {
      key: 'produkte',
      label: 'Produkte',
      render: (value) => {
        if (!value || value.length === 0) return '-'
        const productLabels = {
          'getreide': '🌾',
          'oelsaat': '🥜',
          'protein': '🥩',
          'mineralstoff': '🧂',
          'biostimulanzien': '🌱',
          'pflanzenschutz': '🌿',
          'duenger': '🌱',
          'saatgut': '🌱'
        }
        return (
          <div className="flex gap-1">
            {value.slice(0, 3).map((produkt: string, i: number) =>
              <span key={i} title={produkt}>{productLabels[produkt as keyof typeof productLabels] || '📦'}</span>
            )}
            {value.length > 3 && <span title={`+${value.length - 3} weitere`}>...</span>}
          </div>
        )
      }
    },
    {
      key: 'umsatzGesamt',
      label: 'Gesamtumsatz',
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'letzteLieferung',
      label: 'Letzte Lieferung',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'aktiv': { label: 'Aktiv', variant: 'default' as const },
          'inaktiv': { label: 'Inaktiv', variant: 'secondary' as const },
          'gesperrt': { label: 'Gesperrt', variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || statusLabels.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    }
  ],
  filters: [
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'aktiv', label: 'Aktiv' },
        { value: 'inaktiv', label: 'Inaktiv' },
        { value: 'gesperrt', label: 'Gesperrt' }
      ]
    },
    {
      name: 'land',
      label: 'Land',
      type: 'select',
      options: [
        { value: 'DE', label: 'Deutschland' },
        { value: 'AT', label: 'Österreich' },
        { value: 'CH', label: 'Schweiz' },
        { value: 'NL', label: 'Niederlande' },
        { value: 'DK', label: 'Dänemark' },
        { value: 'PL', label: 'Polen' },
        { value: 'FR', label: 'Frankreich' },
        { value: 'IT', label: 'Italien' }
      ]
    },
    {
      name: 'qualitaetszertifikat',
      label: 'QS-zertifiziert',
      type: 'select',
      options: [
        { value: 'true', label: 'Ja' },
        { value: 'false', label: 'Nein' }
      ]
    },
    {
      name: 'bioZertifiziert',
      label: 'Bio-zertifiziert',
      type: 'select',
      options: [
        { value: 'true', label: 'Ja' },
        { value: 'false', label: 'Nein' }
      ]
    },
    {
      name: 'zahlungsbedingungen',
      label: 'Zahlungsbedingungen',
      type: 'select',
      options: [
        { value: 'sofort', label: 'Sofort' },
        { value: '7 Tage', label: '7 Tage' },
        { value: '14 Tage', label: '14 Tage' },
        { value: '30 Tage', label: '30 Tage' },
        { value: '60 Tage', label: '60 Tage' },
        { value: '90 Tage', label: '90 Tage' }
      ]
    },
    {
      name: 'produkte',
      label: 'Produktbereich',
      type: 'select',
      options: [
        { value: 'getreide', label: 'Getreide' },
        { value: 'oelsaat', label: 'Ölsaaten' },
        { value: 'protein', label: 'Proteinfuttermittel' },
        { value: 'mineralstoff', label: 'Mineralstoffe' },
        { value: 'biostimulanzien', label: 'Biostimulanzien' },
        { value: 'pflanzenschutz', label: 'Pflanzenschutzmittel' },
        { value: 'duenger', label: 'Dünger' },
        { value: 'saatgut', label: 'Saatgut' }
      ]
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => console.log('Export clicked')
    },
    {
      key: 'newsletter',
      label: 'Newsletter senden',
      type: 'secondary',
      onClick: () => console.log('Newsletter clicked')
    },
    {
      key: 'audit',
      label: 'Qualitätsaudit',
      type: 'secondary',
      onClick: () => console.log('Audit clicked')
    },
    {
      key: 'block',
      label: 'Sperren',
      type: 'danger',
      onClick: () => console.log('Block clicked')
    }
  ],
  defaultSort: { field: 'firma', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/crm/lieferanten',
    endpoints: {
      list: '/api/crm/lieferanten',
      get: '/api/crm/lieferanten/{id}',
      create: '/api/crm/lieferanten',
      update: '/api/crm/lieferanten/{id}',
      delete: '/api/crm/lieferanten/{id}'
    }
  },
  permissions: ['crm.read', 'supplier.read'],
  actions: []
}

export default function LieferantenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/lieferanten/stamm/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Lieferanten "${item.firma}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/lieferanten/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          alert('Fehler beim Löschen')
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/lieferanten')
      if (response.success) {
        setData((response.data as any).data || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Daten:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/crm/lieferanten/stamm/new')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    alert('Export-Funktion wird implementiert')
  }

  return (
    <ListReport
      config={lieferantenListConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => alert('Import-Funktion wird implementiert')}
      isLoading={loading}
    />
  )
}