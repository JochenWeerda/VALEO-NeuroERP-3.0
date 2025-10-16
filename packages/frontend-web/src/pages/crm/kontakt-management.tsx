import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Kontakte
const apiClient = createApiClient('/api/crm')

// Konfiguration für Kontakt-Management ListReport
const kontaktListConfig: ListConfig = {
  title: 'Kontakt-Management',
  subtitle: 'Zentrales Management aller Kunden- und Lieferanten-Kontakte',
  type: 'list-report',
  columns: [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-muted-foreground">{row.position || row.funktion}</div>
        </div>
      )
    },
    {
      key: 'firma',
      label: 'Firma',
      sortable: true,
      filterable: true,
      render: (value, row) => {
        if (!value) return '-'
        return (
          <div>
            <div className="font-medium">{value}</div>
            <div className="text-sm text-muted-foreground">{row.kundeId ? 'Kunde' : 'Lieferant'}</div>
          </div>
        )
      }
    },
    {
      key: 'email',
      label: 'E-Mail',
      filterable: true,
      render: (value) => value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'
    },
    {
      key: 'telefon',
      label: 'Telefon',
      render: (value) => value || '-'
    },
    {
      key: 'mobil',
      label: 'Mobil',
      render: (value) => value || '-'
    },
    {
      key: 'abteilung',
      label: 'Abteilung',
      filterable: true,
      render: (value) => value || '-'
    },
    {
      key: 'prioritaet',
      label: 'Priorität',
      sortable: true,
      filterable: true,
      render: (value) => {
        const priorities = {
          'a': { label: 'A - Sehr wichtig', color: 'bg-red-100 text-red-800' },
          'b': { label: 'B - Wichtig', color: 'bg-orange-100 text-orange-800' },
          'c': { label: 'C - Normal', color: 'bg-yellow-100 text-yellow-800' },
          'd': { label: 'D - Niedrig', color: 'bg-green-100 text-green-800' }
        }
        const priority = priorities[value as keyof typeof priorities] || priorities.c
        return <Badge className={priority.color}>{priority.label}</Badge>
      }
    },
    {
      key: 'letzterKontakt',
      label: 'Letzter Kontakt',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'naechsterKontakt',
      label: 'Nächster Kontakt',
      sortable: true,
      render: (value) => {
        if (!value) return '-'
        const date = new Date(value)
        const today = new Date()
        const daysUntil = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

        let color = 'text-gray-600'
        if (daysUntil < 0) color = 'text-red-600'
        else if (daysUntil <= 7) color = 'text-orange-600'
        else if (daysUntil <= 30) color = 'text-blue-600'

        return <span className={color}>{date.toLocaleDateString('de-DE')}</span>
      }
    },
    {
      key: 'kontaktart',
      label: 'Kontaktart',
      filterable: true,
      render: (value) => {
        const types = {
          'telefon': '📞 Telefon',
          'email': '📧 E-Mail',
          'besuch': '🏢 Besuch',
          'messe': '🎪 Messe',
          'webinar': '💻 Webinar',
          'social': '📱 Social Media'
        }
        return types[value as keyof typeof types] || value
      }
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statuses = {
          'aktiv': { label: 'Aktiv', variant: 'default' as const },
          'inaktiv': { label: 'Inaktiv', variant: 'secondary' as const },
          'gesperrt': { label: 'Gesperrt', variant: 'destructive' as const }
        }
        const status = statuses[value as keyof typeof statuses] || statuses.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'notizen',
      label: 'Notizen',
      render: (value) => value ? <span title={value}>📝</span> : '-'
    }
  ],
  filters: [
    {
      name: 'prioritaet',
      label: 'Priorität',
      type: 'select',
      options: [
        { value: 'a', label: 'A - Sehr wichtig' },
        { value: 'b', label: 'B - Wichtig' },
        { value: 'c', label: 'C - Normal' },
        { value: 'd', label: 'D - Niedrig' }
      ]
    },
    {
      name: 'kontaktart',
      label: 'Kontaktart',
      type: 'select',
      options: [
        { value: 'telefon', label: 'Telefon' },
        { value: 'email', label: 'E-Mail' },
        { value: 'besuch', label: 'Besuch' },
        { value: 'messe', label: 'Messe' },
        { value: 'webinar', label: 'Webinar' },
        { value: 'social', label: 'Social Media' }
      ]
    },
    {
      name: 'abteilung',
      label: 'Abteilung',
      type: 'select',
      options: [
        { value: 'geschaeftsfuehrung', label: 'Geschäftsführung' },
        { value: 'einkauf', label: 'Einkauf' },
        { value: 'verkauf', label: 'Verkauf' },
        { value: 'technik', label: 'Technik' },
        { value: 'qualitaet', label: 'Qualität' },
        { value: 'logistik', label: 'Logistik' }
      ]
    },
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
      name: 'firma',
      label: 'Firma',
      type: 'text'
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
      key: 'email',
      label: 'E-Mail senden',
      type: 'secondary',
      onClick: () => console.log('Email clicked')
    },
    {
      key: 'call',
      label: 'Anruf planen',
      type: 'secondary',
      onClick: () => console.log('Call clicked')
    },
    {
      key: 'meeting',
      label: 'Meeting planen',
      type: 'secondary',
      onClick: () => console.log('Meeting clicked')
    },
    {
      key: 'deactivate',
      label: 'Deaktivieren',
      type: 'danger',
      onClick: () => console.log('Deactivate clicked')
    }
  ],
  defaultSort: { field: 'prioritaet', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/crm/kontakte',
    endpoints: {
      list: '/api/crm/kontakte',
      get: '/api/crm/kontakte/{id}',
      create: '/api/crm/kontakte',
      update: '/api/crm/kontakte/{id}',
      delete: '/api/crm/kontakte/{id}'
    }
  },
  permissions: ['crm.read', 'contacts.read'],
  actions: []
}

export default function KontaktManagementPage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/kontakte/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Kontakt "${item.name}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/kontakte/${item.id}`)
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
      const response = await apiClient.get('/kontakte')
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
    navigate('/crm/kontakte/new')
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
      config={kontaktListConfig}
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