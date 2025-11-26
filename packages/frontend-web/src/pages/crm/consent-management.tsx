import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client
const apiClient = createApiClient('/api/crm-consent')

// Konfiguration für Consent-Management ListReport
const createConsentConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageConsents'),
  subtitleKey: 'crud.subtitles.manageConsents',
  type: 'list-report',
  columns: [
    {
      key: 'contact_id',
      label: t('crud.entities.contact'),
      labelKey: 'crud.entities.contact',
      sortable: true,
    },
    {
      key: 'channel',
      label: t('crud.fields.channel'),
      labelKey: 'crud.fields.channel',
      sortable: true,
      render: (value) => {
        const channelLabels: Record<string, string> = {
          email: t('crud.channels.email'),
          sms: t('crud.channels.sms'),
          phone: t('crud.channels.phone'),
          postal: t('crud.channels.postal'),
        }
        return <Badge variant="outline">{channelLabels[value] || value}</Badge>
      }
    },
    {
      key: 'consent_type',
      label: t('crud.fields.consentType'),
      labelKey: 'crud.fields.consentType',
      sortable: true,
      render: (value) => {
        const typeLabels: Record<string, string> = {
          marketing: t('crud.consentTypes.marketing'),
          service: t('crud.consentTypes.service'),
          required: t('crud.consentTypes.required'),
        }
        return typeLabels[value] || value
      }
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      render: (value) => {
        const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
          pending: 'secondary',
          granted: 'default',
          denied: 'destructive',
          revoked: 'outline',
        }
        return (
          <Badge variant={statusVariants[value] || 'secondary'}>
            {getStatusLabel(t, value, value)}
          </Badge>
        )
      }
    },
    {
      key: 'granted_at',
      label: t('crud.fields.grantedAt'),
      labelKey: 'crud.fields.grantedAt',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
    },
    {
      key: 'double_opt_in_confirmed_at',
      label: t('crud.fields.confirmedAt'),
      labelKey: 'crud.fields.confirmedAt',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
    },
    {
      key: 'source',
      label: t('crud.fields.source'),
      labelKey: 'crud.fields.source',
      sortable: true,
      render: (value) => {
        const sourceLabels: Record<string, string> = {
          web_form: t('crud.sources.webForm'),
          api: t('crud.sources.api'),
          import: t('crud.sources.import'),
          manual: t('crud.sources.manual'),
        }
        return sourceLabels[value] || value
      }
    },
    {
      key: 'created_at',
      label: t('crud.fields.createdAt'),
      labelKey: 'crud.fields.createdAt',
      sortable: true,
      render: (value) => formatDate(value)
    }
  ],
  filters: [
    {
      key: 'channel',
      label: t('crud.fields.channel'),
      type: 'select',
      options: [
        { value: 'email', label: t('crud.channels.email') },
        { value: 'sms', label: t('crud.channels.sms') },
        { value: 'phone', label: t('crud.channels.phone') },
        { value: 'postal', label: t('crud.channels.postal') },
      ]
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'pending', label: t('status.pending') },
        { value: 'granted', label: t('status.granted') },
        { value: 'denied', label: t('status.denied') },
        { value: 'revoked', label: t('status.revoked') },
      ]
    },
    {
      key: 'consent_type',
      label: t('crud.fields.consentType'),
      type: 'select',
      options: [
        { value: 'marketing', label: t('crud.consentTypes.marketing') },
        { value: 'service', label: t('crud.consentTypes.service') },
        { value: 'required', label: t('crud.consentTypes.required') },
      ]
    }
  ],
  bulkActions: [
    {
      key: 'revoke',
      label: t('crud.actions.revoke'),
      action: 'revoke'
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      action: 'export'
    }
  ],
  actions: [
    {
      key: 'create',
      label: t('crud.actions.create'),
      type: 'primary'
    },
    {
      key: 'edit',
      label: t('crud.actions.edit'),
      type: 'default'
    },
    {
      key: 'delete',
      label: t('crud.actions.delete'),
      type: 'destructive'
    }
  ],
  api: {
    baseUrl: '/api/crm-consent/consents',
    endpoints: {
      list: '/api/crm-consent/consents',
      get: '/api/crm-consent/consents/{id}',
      create: '/api/crm-consent/consents',
      update: '/api/crm-consent/consents/{id}',
      delete: '/api/crm-consent/consents/{id}'
    }
  },
  permissions: ['crm.read', 'consent.read', 'consent.write']
})

export default function ConsentManagementPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'consent'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Consent')
  const consentConfig = createConsentConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/consent/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/consents/${item.id}`)
          toast({
            title: getSuccessMessage(t, 'delete', entityType),
          })
          loadData()
        } catch (error) {
          toast({
            variant: 'destructive',
            title: getErrorMessage(t, 'delete', entityType),
          })
        }
      }
    } else if (action === 'revoke' && item) {
      try {
        await apiClient.post(`/consents/${item.id}/revoke`)
        toast({
          title: t('crud.messages.consentRevoked'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.consentRevokeError'),
        })
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/consents', {
        params: {
          tenant_id: '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context
        }
      })
      
      if (response.success) {
        const items = response.data || []
        setData(items)
        setTotal(items.length)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Consents:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError')
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/crm/consent/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.contact')};${t('crud.fields.channel')};${t('crud.fields.consentType')};${t('crud.fields.status')};${t('crud.fields.grantedAt')};${t('crud.fields.source')}\n`
      const csvContent = data.map((item: any) =>
        `"${item.contact_id || ''}";"${item.channel || ''}";"${item.consent_type || ''}";"${item.status || ''}";"${item.granted_at || ''}";"${item.source || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `consents-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
      })
    }
  }

  return (
    <ListReport
      config={consentConfig}
      data={data}
      total={total}
      loading={loading}
      onAction={handleAction}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}

// Helper functions
function getSuccessMessage(t: any, action: string, entityType: string): string {
  return t(`crud.messages.${action}Success`, { entityType })
}

function getErrorMessage(t: any, action: string, entityType: string): string {
  return t(`crud.messages.${action}Error`, { entityType })
}

