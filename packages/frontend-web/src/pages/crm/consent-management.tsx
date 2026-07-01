import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient } from '@/lib/api-client'
import { recordArrayFromResponse, renderValue, stringValue } from '@/lib/record-utils'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { ErrorState } from '@/components/ErrorState'

// Konfiguration für Consent-Management ListReport
const createConsentConfig = (t: TFunction, entityTypeLabel: string): ListConfig => ({
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
        const channel = stringValue(value)
        const channelLabels: Record<string, string> = {
          email: t('crud.channels.email'),
          sms: t('crud.channels.sms'),
          phone: t('crud.channels.phone'),
          postal: t('crud.channels.postal'),
        }
        return <Badge variant="outline">{channelLabels[channel] || channel}</Badge>
      }
    },
    {
      key: 'consent_type',
      label: t('crud.fields.consentType'),
      labelKey: 'crud.fields.consentType',
      sortable: true,
      render: (value) => {
        const consentType = stringValue(value)
        const typeLabels: Record<string, string> = {
          marketing: t('crud.consentTypes.marketing'),
          service: t('crud.consentTypes.service'),
          required: t('crud.consentTypes.required'),
        }
        return typeLabels[consentType] || consentType
      }
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      render: (value) => {
        const status = stringValue(value)
        const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
          pending: 'secondary',
          granted: 'default',
          denied: 'destructive',
          revoked: 'outline',
        }
        return (
          <Badge variant={statusVariants[status] || 'secondary'}>
            {getStatusLabel(t, status, status)}
          </Badge>
        )
      }
    },
    {
      key: 'granted_at',
      label: t('crud.fields.grantedAt'),
      labelKey: 'crud.fields.grantedAt',
      sortable: true,
      render: (value) => value ? formatDate(stringValue(value)) : '-'
    },
    {
      key: 'double_opt_in_confirmed_at',
      label: t('crud.fields.confirmedAt'),
      labelKey: 'crud.fields.confirmedAt',
      sortable: true,
      render: (value) => value ? formatDate(stringValue(value)) : '-'
    },
    {
      key: 'source',
      label: t('crud.fields.source'),
      labelKey: 'crud.fields.source',
      sortable: true,
      render: (value) => {
        const source = stringValue(value)
        const sourceLabels: Record<string, string> = {
          web_form: t('crud.sources.webForm'),
          api: t('crud.sources.api'),
          import: t('crud.sources.import'),
          manual: t('crud.sources.manual'),
        }
        return sourceLabels[source] || source
      }
    },
    {
      key: 'created_at',
      label: t('crud.fields.createdAt'),
      labelKey: 'crud.fields.createdAt',
      sortable: true,
      render: (value) => formatDate(stringValue(value))
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
    baseUrl: '/api/v1/crm/consents',
    endpoints: {
      list: '/api/v1/crm/consents',
      get: '/api/v1/crm/consents/{id}',
      create: '/api/v1/crm/consents',
      update: '/api/v1/crm/consents/{id}',
      delete: '/api/v1/crm/consents/{id}'
    }
  },
  permissions: ['crm.read', 'consent.read', 'consent.write']
})

function getSuccessMessage(t: TFunction, action: string, entityType: string): string {
  return t(`crud.messages.${action}Success`, { entityType })
}

function getErrorMessage(t: TFunction, action: string, entityType: string): string {
  return t(`crud.messages.${action}Error`, { entityType })
}

export default function ConsentManagementPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const entityType = 'consent'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Consent')
  const consentConfig = createConsentConfig(t, entityTypeLabel)

  const { data: queryData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['crm', 'consents'],
    queryFn: async () => {
      const r = await apiClient.get('/api/v1/crm/consents')
      const items = recordArrayFromResponse(r.data)
      return { items, total: items.length }
    },
    staleTime: 2 * 60 * 1000,
  })

  const [pendingRows, setPendingRows] = useState<Set<string>>(new Set())

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['crm', 'consents'] })

  async function withPending(key: string, fn: () => Promise<void>) {
    if (pendingRows.has(key)) return
    setPendingRows(prev => new Set(prev).add(key))
    try { await fn() } finally {
      setPendingRows(prev => { const s = new Set(prev); s.delete(key); return s })
    }
  }

  const { handleAction } = useMaskActions(async (action: string, item: Record<string, unknown>) => {
    if (action === 'edit' && item) {
      navigate(`/crm/consent/${stringValue(item.id)}`)
    } else if (action === 'delete' && item) {
      if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
      await withPending(stringValue(item.id), async () => {
        try {
          await apiClient.delete(`/api/v1/crm/consents/${stringValue(item.id)}`)
          toast({ title: getSuccessMessage(t, 'delete', entityType) })
          invalidate()
        } catch {
          toast({ variant: 'destructive', title: getErrorMessage(t, 'delete', entityType) })
        }
      })
    } else if (action === 'revoke' && item) {
      await withPending(stringValue(item.id), async () => {
        try {
          await apiClient.post(`/api/v1/crm/consents/${stringValue(item.id)}/revoke`)
          toast({ title: t('crud.messages.consentRevoked') })
          invalidate()
        } catch {
          toast({ variant: 'destructive', title: t('crud.messages.consentRevokeError') })
        }
      })
    }
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const data = queryData?.items || []
  const total = queryData?.total || 0

  const handleCreate = () => {
    navigate('/crm/consent/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.contact')};${t('crud.fields.channel')};${t('crud.fields.consentType')};${t('crud.fields.status')};${t('crud.fields.grantedAt')};${t('crud.fields.source')}\n`
      const csvContent = data.map(item =>
        `"${renderValue(item.contact_id)}";"${renderValue(item.channel)}";"${renderValue(item.consent_type)}";"${renderValue(item.status)}";"${renderValue(item.granted_at)}";"${renderValue(item.source)}"`
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
    } catch {
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
      loading={isLoading}
      pendingRows={pendingRows}
      onAction={handleAction}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}
