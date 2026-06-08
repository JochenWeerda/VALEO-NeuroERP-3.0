import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient } from '@/lib/api-client'
import { toast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { summarizeCustomerOperations } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'


const createKontaktListConfig = (handlers: {
  exportSelected: (items: any[]) => void
  emailSelected: (items: any[]) => void
  callSelected: (items: any[]) => void
  meetingSelected: (items: any[]) => void
  deactivateSelected: (items: any[]) => void
}): ListConfig => ({
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
          <div className="text-sm text-muted-foreground">{row.position || row.funktion || '-'}</div>
        </div>
      ),
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
      },
    },
    {
      key: 'email',
      label: 'E-Mail',
      filterable: true,
      render: (value) => (value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'),
    },
    {
      key: 'telefon',
      label: 'Telefon',
      render: (value) => value || '-',
    },
    {
      key: 'mobil',
      label: 'Mobil',
      render: (value) => value || '-',
    },
    {
      key: 'abteilung',
      label: 'Abteilung',
      filterable: true,
      render: (value) => value || '-',
    },
    {
      key: 'prioritaet',
      label: 'Prioritaet',
      sortable: true,
      filterable: true,
      render: (value) => {
        const priorities = {
          a: { label: 'A - Sehr wichtig', color: 'bg-red-100 text-red-800' },
          b: { label: 'B - Wichtig', color: 'bg-orange-100 text-orange-800' },
          c: { label: 'C - Normal', color: 'bg-yellow-100 text-yellow-800' },
          d: { label: 'D - Niedrig', color: 'bg-green-100 text-green-800' },
        }
        const priority = priorities[value as keyof typeof priorities] || priorities.c
        return <Badge className={priority.color}>{priority.label}</Badge>
      },
    },
    {
      key: 'letzterKontakt',
      label: 'Letzter Kontakt',
      sortable: true,
      render: (value) => (value ? new Date(value).toLocaleDateString('de-DE') : '-'),
    },
    {
      key: 'naechsterKontakt',
      label: 'Naechster Kontakt',
      sortable: true,
      render: (value) => {
        if (!value) return '-'
        const date = new Date(value)
        const daysUntil = Math.ceil((date.getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        let color = 'text-gray-600'
        if (daysUntil < 0) color = 'text-red-600'
        else if (daysUntil <= 7) color = 'text-orange-600'
        else if (daysUntil <= 30) color = 'text-blue-600'
        return <span className={color}>{date.toLocaleDateString('de-DE')}</span>
      },
    },
    {
      key: 'kontaktart',
      label: 'Kontaktart',
      filterable: true,
      render: (value) => {
        const types = {
          telefon: 'Telefon',
          email: 'E-Mail',
          besuch: 'Besuch',
          messe: 'Messe',
          webinar: 'Webinar',
          social: 'Social Media',
        }
        return types[value as keyof typeof types] || value || '-'
      },
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statuses = {
          aktiv: { label: 'Aktiv', variant: 'default' as const },
          inaktiv: { label: 'Inaktiv', variant: 'secondary' as const },
          gesperrt: { label: 'Gesperrt', variant: 'destructive' as const },
        }
        const status = statuses[value as keyof typeof statuses] || statuses.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      },
    },
    {
      key: 'notizen',
      label: 'Notizen',
      render: (value) => (value ? <span title={value}>Vorhanden</span> : '-'),
    },
  ],
  filters: [
    {
      name: 'prioritaet',
      label: 'Prioritaet',
      type: 'select',
      options: [
        { value: 'a', label: 'A - Sehr wichtig' },
        { value: 'b', label: 'B - Wichtig' },
        { value: 'c', label: 'C - Normal' },
        { value: 'd', label: 'D - Niedrig' },
      ],
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
        { value: 'social', label: 'Social Media' },
      ],
    },
    {
      name: 'abteilung',
      label: 'Abteilung',
      type: 'select',
      options: [
        { value: 'geschaeftsfuehrung', label: 'Geschaeftsfuehrung' },
        { value: 'einkauf', label: 'Einkauf' },
        { value: 'verkauf', label: 'Verkauf' },
        { value: 'technik', label: 'Technik' },
        { value: 'qualitaet', label: 'Qualitaet' },
        { value: 'logistik', label: 'Logistik' },
      ],
    },
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'aktiv', label: 'Aktiv' },
        { value: 'inaktiv', label: 'Inaktiv' },
        { value: 'gesperrt', label: 'Gesperrt' },
      ],
    },
    {
      name: 'firma',
      label: 'Firma',
      type: 'text',
    },
  ],
  bulkActions: [
    { key: 'export', label: 'Exportieren', type: 'secondary', onClick: handlers.exportSelected },
    { key: 'email', label: 'E-Mail senden', type: 'secondary', onClick: handlers.emailSelected },
    { key: 'call', label: 'Anruf planen', type: 'secondary', onClick: handlers.callSelected },
    { key: 'meeting', label: 'Meeting planen', type: 'secondary', onClick: handlers.meetingSelected },
    { key: 'deactivate', label: 'Deaktivieren', type: 'danger', onClick: handlers.deactivateSelected },
  ],
  defaultSort: { field: 'prioritaet', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/crm/contacts',
    endpoints: {
      list: '/api/v1/crm/contacts',
      get: '/api/v1/crm/contacts/{id}',
      create: '/api/v1/crm/contacts',
      update: '/api/v1/crm/contacts/{id}',
      delete: '/api/v1/crm/contacts/{id}',
    },
  },
  permissions: ['crm.read', 'contacts.read'],
  actions: [],
})

export default function KontaktManagementPage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const importInputRef = useRef<HTMLInputElement>(null)

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/api/v1/crm/contacts')
      setData((response.data as any).data || (response.data as any).items || [])
      setTotal((response.data as any).total || 0)
    } catch (error: any) {
      toast({ variant: 'destructive', title: 'Fehler beim Laden der Kontakte', description: error?.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadData()
  }, [])

  const [pendingRows, setPendingRows] = useState<Set<string>>(new Set())

  async function withPending(key: string, fn: () => Promise<void>) {
    if (pendingRows.has(key)) return
    setPendingRows(prev => new Set(prev).add(key))
    try { await fn() } finally {
      setPendingRows(prev => { const s = new Set(prev); s.delete(key); return s })
    }
  }

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/kontakte/${item.id}`)
    }
  })

  const handleCreate = () => navigate('/crm/kontakte/new')
  const handleEdit = (item: any) => { void handleAction('edit', item) }
  const handleDelete = (item: any) => {
    if (!confirm(`Kontakt "${item.name}" wirklich loeschen?`)) return
    void withPending(String(item.id), async () => {
      try {
        await apiClient.delete(`/api/v1/crm/contacts/${item.id}`)
        await loadData()
      } catch {
        toast({
          variant: 'destructive',
          title: 'Fehler beim Loeschen',
          description: 'Der Kontakt konnte nicht geloescht werden.',
        })
      }
    })
  }

  const handleExport = (rows: any[] = data) => {
    try {
      const csvHeader = 'Name;Firma;E-Mail;Telefon;Mobil;Abteilung;Prioritaet;Status\n'
      const csvContent = rows
        .map(
          (kontakt: any) =>
            `"${kontakt.name}";"${kontakt.firma || ''}";"${kontakt.email || ''}";"${kontakt.telefon || ''}";"${kontakt.mobil || ''}";"${kontakt.abteilung || ''}";"${kontakt.prioritaet || ''}";"${kontakt.status || 'aktiv'}"`,
        )
        .join('\n')

      const blob = new Blob([csvHeader + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `kontakt-management-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: 'Export erfolgreich',
        description: `${rows.length} Kontakte wurden exportiert.`,
      })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Export fehlgeschlagen',
        description: 'Beim Exportieren ist ein Fehler aufgetreten.',
      })
    }
  }

  const ensureSelection = (items: any[]): boolean => {
    if (items.length > 0) return true
    toast({
      variant: 'destructive',
      title: 'Keine Auswahl',
      description: 'Bitte mindestens einen Kontakt auswaehlen.',
    })
    return false
  }

  const handleImportFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await api.post('/api/v1/crm/import/kunden', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const { created = 0, updated = 0, errors = [] } = (res.data as any) ?? {}
      toast({
        title: 'Import abgeschlossen',
        description: `${created} neu, ${updated} aktualisiert${errors.length ? `, ${errors.length} Fehler` : ''}.`,
      })
      await loadData()
    } catch (err: any) {
      toast({ title: 'Import fehlgeschlagen', description: err.response?.data?.detail ?? err.message, variant: 'destructive' })
    }
    e.target.value = ''
  }

  const kontaktListConfig = useMemo(
    () =>
      createKontaktListConfig({
        exportSelected: (items) => {
          if (!ensureSelection(items)) return
          handleExport(items)
        },
        emailSelected: (items) => {
          if (!ensureSelection(items)) return
          const recipients = items
            .map((item) => item.email)
            .filter((value): value is string => typeof value === 'string' && value.trim().length > 0)

          if (recipients.length === 0) {
            toast({
              variant: 'destructive',
              title: 'Keine E-Mail-Adressen',
              description: 'In der Auswahl sind keine gueltigen E-Mail-Adressen vorhanden.',
            })
            return
          }

          window.location.href = `mailto:?bcc=${encodeURIComponent(recipients.join(';'))}`
        },
        callSelected: (items) => {
          if (!ensureSelection(items)) return
          if (items.length === 1) {
            const phone = items[0].mobil || items[0].telefon
            if (phone) {
              window.location.href = `tel:${String(phone).replace(/\s+/g, '')}`
              return
            }
          }
          navigate('/crm/aktivitaet/neu')
          toast({
            title: 'Aktivitaet vorbereitet',
            description: 'Bitte den geplanten Kontakt im Aktivitaetsarbeitsplatz dokumentieren.',
          })
        },
        meetingSelected: (items) => {
          if (!ensureSelection(items)) return
          navigate('/crm/aktivitaet/neu')
        },
        deactivateSelected: async (items) => {
          if (!ensureSelection(items)) return
          try {
            await Promise.all(items.map((item) => apiClient.put(`/api/v1/crm/contacts/${item.id}`, { status: 'inaktiv' })))
            toast({
              title: 'Kontakte deaktiviert',
              description: `${items.length} Kontakt(e) wurden auf inaktiv gesetzt.`,
              variant: 'destructive',
            })
            await loadData()
          } catch {
            toast({
              variant: 'destructive',
              title: 'Deaktivierung fehlgeschlagen',
              description: 'Die ausgewaehlten Kontakte konnten nicht aktualisiert werden.',
            })
          }
        },
      }),
    [data, navigate],
  )

  const duplicateCount = useMemo(() => {
    const seen = new Set<string>()
    let duplicates = 0
    for (const item of data) {
      const key = `${item.email || ''}|${item.telefon || ''}`.toLowerCase()
      if (!key || key === '|') continue
      if (seen.has(key)) duplicates += 1
      else seen.add(key)
    }
    return duplicates
  }, [data])
  const inactiveCount = useMemo(() => data.filter((item) => item.status === 'inaktiv').length, [data])
  const dueContacts = useMemo(
    () =>
      data.filter((item) => {
        if (!item.naechsterKontakt) return false
        return new Date(item.naechsterKontakt).getTime() < Date.now()
      }).length,
    [data],
  )
  const customerOps = summarizeCustomerOperations({
    duplicateCount,
    hasOwner: data.some((item) => Boolean(item.assigned_to || item.owner_id || item.verantwortlich)),
    hasReachableContact: data.some((item) => Boolean(item.email || item.telefon || item.mobil)),
    nextActions: dueContacts,
  })
  const operationalStatus = normalizeOperationalStatus(
    dueContacts > 0 ? 'wartet_auf_mensch' : duplicateCount > 0 ? 'in_pruefung' : 'offen',
  )
  const contextSections = [
    {
      title: 'Kontaktlage',
      items: [
        { label: 'Kontakte', value: `${total}` },
        { label: 'Faellige Folgekontakte', value: `${dueContacts}` },
        { label: 'Inaktive', value: `${inactiveCount}` },
      ],
    },
    {
      title: 'Ownership',
      items: [
        { label: 'Dubletten', value: `${duplicateCount}` },
        { label: 'Naechste Aktion', value: customerOps.nextAction },
        { label: 'Follow-up-Druck', value: `${dueContacts}` },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Kontaktbestand geladen', detail: `${total} Kontakte im Arbeitsraum.` },
    { label: dueContacts > 0 ? 'Faellige Folgekontakte offen' : 'Keine ueberfaelligen Folgekontakte', detail: `${dueContacts} Kontakte mit faelligem naechsten Kontakt.` },
    { label: 'Ownership-Pfad', detail: customerOps.nextAction },
  ]

  return (
    <>
      <input ref={importInputRef} type="file" accept=".csv" className="hidden" onChange={handleImportFile} />
      <div className="space-y-4 p-6">
        <OperationalCaseHeader
          title="Kontaktmanagement steuern"
          description="Ownership, Dubletten und faellige Folgekontakte werden ueber der Listenarbeit verdichtet."
          status={operationalStatus}
          owner="CRM / Vertrieb"
          blocker={duplicateCount > 0 ? 'Dubletten oder uneinheitliche Kontaktkanaele sollten vor neuer Folgearbeit bereinigt werden.' : null}
          nextAction={customerOps.nextAction}
          caseLabel="Kontakt-Arbeitsraum"
          tags={['CRM', 'Kontakte']}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="Kontaktverlauf" items={timelineItems} />
          <OperationalContextPanel title="Kontaktkontext" sections={contextSections} />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Ownership-Risiko</CardTitle></CardHeader>
            <CardContent><Badge variant={customerOps.ownershipRisk === 'hoch' ? 'destructive' : 'outline'}>{customerOps.ownershipRisk}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Dubletten</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-semibold">{duplicateCount}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Fallaktion</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{customerOps.nextAction}</div></CardContent>
          </Card>
        </div>
      </div>
      <ListReport
        config={kontaktListConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        pendingRows={pendingRows}
        onExport={() => handleExport()}
        onImport={() => importInputRef.current?.click()}
        isLoading={loading}
      />
    </>
  )
}
