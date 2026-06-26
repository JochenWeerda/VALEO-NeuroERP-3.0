import { useMemo, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { unwrapCrmListPage, type CrmListEnvelope } from '@/lib/api/crm-list-response'
import { toast } from '@/hooks/use-toast'

// Konfiguration für Lieferanten ListReport
const createLieferantenListConfig = (t: any): ListConfig => ({
  title: t('crud.entities.suppliers', { defaultValue: 'Lieferanten-Liste' }),
  subtitle: t('crud.subtitles.manageSuppliers', { defaultValue: 'Übersicht aller Lieferanten und deren Konditionen' }),
  type: 'list-report',
  columns: [
    {
      key: 'firma',
      label: t('crud.fields.company', { defaultValue: 'Firma' }),
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
      label: t('crud.fields.location', { defaultValue: 'Ort' }),
      sortable: true,
      filterable: true,
      render: (value, row) => `${row.plz} ${value}`
    },
    {
      key: 'land',
      label: t('crud.fields.country', { defaultValue: 'Land' }),
      filterable: true,
      render: (value) => {
        const countries: Record<string, string> = {
          'DE': 'Deutschland',
          'AT': 'Österreich',
          'CH': 'Schweiz',
          'NL': 'Niederlande',
          'DK': 'Dänemark',
          'PL': 'Polen',
          'FR': 'Frankreich',
          'IT': 'Italien'
        }
        return countries[value as string] || value
      }
    },
    {
      key: 'telefon',
      label: t('crud.fields.phone', { defaultValue: 'Telefon' }),
      render: (value) => value || '-'
    },
    {
      key: 'email',
      label: t('crud.fields.email', { defaultValue: 'E-Mail' }),
      render: (value) => value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'
    },
    {
      key: 'zahlungsbedingungen',
      label: t('crud.fields.paymentTerms', { defaultValue: 'Z-Bedingungen' }),
      sortable: true,
      filterable: true,
      render: (value) => value || '30 Tage'
    },
    {
      key: 'rabatt',
      label: t('crud.fields.discount', { defaultValue: 'Rabatt' }),
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    },
    {
      key: 'mindestbestellwert',
      label: t('crud.fields.minOrderValue', { defaultValue: 'Min.-Bestellwert' }),
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'lieferzeit',
      label: t('crud.fields.deliveryTime', { defaultValue: 'Lieferzeit' }),
      sortable: true,
      render: (value) => value ? `${value} ${t('crud.fields.days', { defaultValue: 'Tage' })}` : '-'
    },
    {
      key: 'qualitaetszertifikat',
      label: t('crud.fields.qsCert', { defaultValue: 'QS-Zert.' }),
      render: (value) => value ? <Badge variant="outline">Ja</Badge> : <Badge variant="secondary">Nein</Badge>
    },
    {
      key: 'bioZertifiziert',
      label: t('crud.fields.bioCert', { defaultValue: 'Bio-Zert.' }),
      render: (value) => value ? <Badge variant="outline">Ja</Badge> : <Badge variant="secondary">Nein</Badge>
    },
    {
      key: 'produkte',
      label: t('crud.fields.products', { defaultValue: 'Produkte' }),
      render: (value) => {
        if (!value || value.length === 0) return '-'
        return (
          <div className="flex gap-1">
            {value.slice(0, 3).map((produkt: string, i: number) =>
              <Badge key={i} variant="outline" className="text-xs">{produkt}</Badge>
            )}
            {value.length > 3 && <Badge variant="outline" className="text-xs">+{value.length - 3}</Badge>}
          </div>
        )
      }
    },
    {
      key: 'umsatzGesamt',
      label: t('crud.fields.totalRevenue', { defaultValue: 'Gesamtumsatz' }),
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'letzteLieferung',
      label: t('crud.fields.lastDelivery', { defaultValue: 'Letzte Lieferung' }),
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'status',
      label: t('crud.fields.status', { defaultValue: 'Status' }),
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'aktiv': { label: t('status.active', { defaultValue: 'Aktiv' }), variant: 'default' as const },
          'inaktiv': { label: t('status.inactive', { defaultValue: 'Inaktiv' }), variant: 'secondary' as const },
          'gesperrt': { label: t('status.blocked', { defaultValue: 'Gesperrt' }), variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || statusLabels.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    }
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status', { defaultValue: 'Status' }),
      type: 'select',
      options: [
        { value: 'aktiv', label: t('status.active', { defaultValue: 'Aktiv' }) },
        { value: 'inaktiv', label: t('status.inactive', { defaultValue: 'Inaktiv' }) },
        { value: 'gesperrt', label: t('status.blocked', { defaultValue: 'Gesperrt' }) }
      ]
    },
    {
      name: 'land',
      label: t('crud.fields.country', { defaultValue: 'Land' }),
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
      label: t('crud.fields.qsCert', { defaultValue: 'QS-zertifiziert' }),
      type: 'select',
      options: [
        { value: 'true', label: t('common.yes', { defaultValue: 'Ja' }) },
        { value: 'false', label: t('common.no', { defaultValue: 'Nein' }) }
      ]
    },
    {
      name: 'bioZertifiziert',
      label: t('crud.fields.bioCert', { defaultValue: 'Bio-zertifiziert' }),
      type: 'select',
      options: [
        { value: 'true', label: t('common.yes', { defaultValue: 'Ja' }) },
        { value: 'false', label: t('common.no', { defaultValue: 'Nein' }) }
      ]
    },
    {
      name: 'zahlungsbedingungen',
      label: t('crud.fields.paymentTerms', { defaultValue: 'Zahlungsbedingungen' }),
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
      label: t('crud.fields.productArea', { defaultValue: 'Produktbereich' }),
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
      label: t('crud.actions.export', { defaultValue: 'Exportieren' }),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'newsletter',
      label: t('crud.actions.sendNewsletter', { defaultValue: 'Newsletter senden' }),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'audit',
      label: t('crud.actions.qualityAudit', { defaultValue: 'Qualitätsaudit' }),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'block',
      label: t('crud.actions.block', { defaultValue: 'Sperren' }),
      type: 'danger',
      onClick: () => {}
    }
  ],
  defaultSort: { field: 'firma', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/crm/business-partners',
    endpoints: {
      list: '/api/v1/crm/business-partners',
      get: '/api/v1/crm/business-partners/{id}',
      create: '/api/v1/crm/business-partners',
      update: '/api/v1/crm/business-partners/{id}',
      delete: '/api/v1/crm/business-partners/{id}'
    }
  },
  permissions: ['crm.read', 'supplier.read'],
  actions: []
})

export default function LieferantenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const importInputRef = useRef<HTMLInputElement>(null)
  const baseConfig = createLieferantenListConfig(t) as ListConfig & {
    bulkActions: NonNullable<ListConfig['bulkActions']>
  }

  const { data: queryData, isLoading } = useQuery({
    queryKey: ['crm', 'lieferanten'],
    queryFn: async () => {
      try {
        const r = await apiClient.get<CrmListEnvelope<Record<string, unknown>>>('/api/v1/crm/business-partners')
        return unwrapCrmListPage(r.data)
      } catch {
        /* API nicht erreichbar */
      }
      return { items: [], total: 0 }
    },
    staleTime: 2 * 60 * 1000,
  })

  const data = queryData?.items || []
  const total = queryData?.total || 0

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['crm', 'lieferanten'] })

  const lieferantenListConfig = useMemo(() => {
    const onExportBulk = async (items: any[]) => {
      const exportData = items.length > 0 ? items : data
      if (exportData.length === 0) {
        toast({ title: t('crud.list.noSelection', { defaultValue: 'Keine Auswahl' }) })
        return
      }
      const header = 'Firma;Ort;Land;E-Mail;Zahlungsbedingungen;Rabatt;Status\n'
      const rows = exportData.map((l: any) =>
        `"${l.firma}";"${l.plz || ''} ${l.ort || ''}";"${l.land || ''}";"${l.email || ''}";"${l.zahlungsbedingungen || '30 Tage'}";"${l.rabatt || 0}";"${l.status || 'aktiv'}"`
      ).join('\n')
      const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `lieferanten_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'Export erstellt', description: `${exportData.length} Lieferanten exportiert.` })
    }

    const onNewsletter = async (items: any[]) => {
      if (items.length === 0) {
        toast({ title: t('crud.list.noSelection', { defaultValue: 'Keine Auswahl' }) })
        return
      }
      const emails = items.map((l: any) => l.email).filter(Boolean)
      if (emails.length === 0) {
        toast({ title: 'Keine E-Mail-Adressen', description: 'Für die ausgewählten Lieferanten sind keine E-Mail-Adressen hinterlegt.', variant: 'destructive' })
        return
      }
      try {
        await apiClient.post('/api/v1/crm/kommunikation/newsletter', {
          empfaenger: emails,
          typ: 'lieferanten',
          betreff: 'Information von VALEO',
        })
        toast({ title: 'Newsletter versendet', description: `Versand an ${emails.length} Empfänger initiiert.` })
      } catch (e: unknown) {
        toast({
          title: 'Versand fehlgeschlagen',
          description: getAxiosErrorMessage(e),
          variant: 'destructive',
        })
      }
    }

    const onAudit = async (items: any[]) => {
      if (items.length === 0) {
        toast({ title: t('crud.list.noSelection', { defaultValue: 'Keine Auswahl' }) })
        return
      }
      // Audit-Planung: navigiere zu Audit-Erstellung mit vorausgefüllten Lieferanten
      const ids = items.map((l: any) => l.id).filter(Boolean)
      navigate(`/crm/audits/neu?lieferanten=${ids.join(',')}`)
    }

    const onBlock = async (items: any[]) => {
      if (items.length === 0) {
        toast({ title: t('crud.list.noSelection', { defaultValue: 'Keine Auswahl' }) })
        return
      }
      try {
        await Promise.all(
          items.map((l: { id: string }) =>
            apiClient.put(`/api/v1/crm/business-partners/${l.id}`, { status: 'inactive' }),
          ),
        )
        toast({ title: 'Gesperrt', description: `${items.length} Lieferant(en) gesperrt.`, variant: 'destructive' })
        invalidate()
      } catch (e: unknown) {
        toast({
          title: 'Fehler beim Sperren',
          description: getAxiosErrorMessage(e),
          variant: 'destructive',
        })
      }
    }

    return {
      ...baseConfig,
      bulkActions: [
        { ...baseConfig.bulkActions[0], onClick: onExportBulk },
        { ...baseConfig.bulkActions[1], onClick: onNewsletter },
        { ...baseConfig.bulkActions[2], onClick: onAudit },
        { ...baseConfig.bulkActions[3], onClick: onBlock },
      ],
    }
  }, [t, data])

  const handleCreate = () => {
    navigate('/crm/lieferanten/stamm/new')
  }

  const handleEdit = (item: any) => {
    navigate(`/crm/lieferanten/stamm/${item.id}`)
  }

  const handleDelete = async (item: any) => {
    if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: 'Lieferant', defaultValue: `Lieferanten "${item.firma}" wirklich löschen?` }))) {
      try {
        await apiClient.delete(`/api/v1/crm/business-partners/${item.id}`)
        invalidate()
      } catch {
        toast({
          variant: 'destructive',
          title: t('crud.messages.deleteError', { defaultValue: 'Fehler beim Löschen' })
        })
      }
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = 'Firma;Ort;Land;Telefon;E-Mail;Z-Bedingungen;Rabatt;Min-Bestellwert;Lieferzeit;QS-Zert;Bio-Zert;Gesamtumsatz;Status\n'
      const csvContent = data.map((lieferant: any) =>
        `"${lieferant.firma}";"${lieferant.plz} ${lieferant.ort}";"${lieferant.land || ''}";"${lieferant.telefon || ''}";"${lieferant.email || ''}";"${lieferant.zahlungsbedingungen || '30 Tage'}";"${lieferant.rabatt || 0}";"${lieferant.mindestbestellwert || 0}";"${lieferant.lieferzeit || 0}";"${lieferant.qualitaetszertifikat ? 'Ja' : 'Nein'}";"${lieferant.bioZertifiziert ? 'Ja' : 'Nein'}";"${lieferant.umsatzGesamt || 0}";"${lieferant.status || 'aktiv'}"`
      ).join('\n')

      const csv = csvHeader + csvContent

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `lieferanten-liste-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess', { defaultValue: 'Export erfolgreich' }),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: 'Lieferanten', defaultValue: `${data.length} Lieferanten wurden exportiert.` }),
      })
    } catch {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError', { defaultValue: 'Export fehlgeschlagen' }),
        description: t('crud.messages.exportFailed', { defaultValue: 'Beim Exportieren ist ein Fehler aufgetreten.' }),
      })
    }
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await apiClient.post<{ created?: number; updated?: number; errors?: string[] }>(
        '/api/v1/crm/import/lieferanten',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      const { created = 0, updated = 0, errors = [] } = res.data ?? {}
      toast({
        title: t('crud.messages.importSuccess', { defaultValue: 'Import abgeschlossen' }),
        description: `${created} neu, ${updated} aktualisiert${errors.length ? `, ${errors.length} Fehler` : ''}.`,
      })
      queryClient.invalidateQueries({ queryKey: ['crm', 'lieferanten'] })
    } catch (err: unknown) {
      toast({
        title: t('crud.messages.importError', { defaultValue: 'Import fehlgeschlagen' }),
        description: getAxiosErrorMessage(err),
        variant: 'destructive',
      })
    }
    e.target.value = ''
  }

  return (
    <>
      <input ref={importInputRef} type="file" accept=".csv" className="hidden" onChange={handleImportFile} />
      <ListReport
        config={lieferantenListConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => importInputRef.current?.click()}
        isLoading={isLoading}
      />
    </>
  )
}
