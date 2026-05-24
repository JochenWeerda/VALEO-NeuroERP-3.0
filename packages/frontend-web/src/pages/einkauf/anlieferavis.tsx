import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { summarizeProcurementMatch } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const anlieferavisConfig: MaskConfig = {
  title: 'Anlieferavis',
  subtitle: 'Lieferavis fuer Wareneingangsvorbereitung',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'bestellungId',
          label: 'Bestellung',
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/purchase-orders?status=FREIGEGEBEN',
          displayField: 'purchaseOrderNumber',
          valueField: 'id'
        },
        { name: 'avisNummer', label: 'Avis-Nummer', type: 'text', required: true },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'GESENDET', label: 'Gesendet' },
            { value: 'BESTAETIGT', label: 'Bestaetigt' },
            { value: 'STORNIERT', label: 'Storniert' }
          ]
        },
        { name: 'geplantesAnlieferDatum', label: 'Geplantes Anlieferdatum', type: 'datetime', required: true }
      ]
    },
    {
      key: 'fahrzeug',
      label: 'Fahrzeug & Fahrer',
      fields: [
        { name: 'fahrzeug.kennzeichen', label: 'Kennzeichen', type: 'text', required: true },
        { name: 'fahrzeug.fahrer', label: 'Fahrer', type: 'text', required: true },
        { name: 'fahrzeug.telefon', label: 'Telefon', type: 'text' }
      ]
    },
    {
      key: 'positionen',
      label: 'Positionen',
      fields: [
        {
          name: 'positionen',
          label: 'Avis-Positionen',
          type: 'table',
          required: true,
          columns: [
            { key: 'positionId', label: 'Bestellposition', type: 'text', required: true },
            { key: 'menge', label: 'Menge', type: 'number', required: true },
            { key: 'chargenNummer', label: 'Charge-Nr.', type: 'text' },
            { key: 'verpackung', label: 'Verpackung', type: 'text' }
          ] as any,
          helpText: 'Zu erwartende Lieferpositionen'
        }
      ]
    },
    {
      key: 'belege',
      label: 'Belege',
      fields: [
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusaetzliche Informationen zum Avis...'
        }
      ]
    }
  ],
  actions: [
    { key: 'senden', label: 'Avis senden', type: 'primary' },
    { key: 'bestaetigen', label: 'Bestaetigen', type: 'secondary' },
    { key: 'stornieren', label: 'Stornieren', type: 'danger' }
  ],
  api: {
    baseUrl: '/api/v1/einkauf/anlieferavis',
    endpoints: {
      list: '/api/v1/einkauf/anlieferavis',
      get: '/api/v1/einkauf/anlieferavis/{id}',
      create: '/api/v1/einkauf/anlieferavis',
      update: '/api/v1/einkauf/anlieferavis/{id}',
      delete: '/api/v1/einkauf/anlieferavis/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'warehouse.read']
}

export default function AnlieferavisPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: anlieferavisConfig.api.baseUrl,
    id: id || undefined
  })

  const { handleAction, loadingActionKey } = useMaskActions(async (actionKey: string) => {
          if (!id || !actionMap[actionKey]) {
            toast({ title: 'Aktion nicht moeglich', description: 'Das Avis muss zuerst gespeichert werden.', variant: 'destructive' })
            return
          }
          try {
            await apiClient.post(`/api/v1/einkauf/anlieferavis/${encodeURIComponent(id)}/${actionMap[actionKey]}`)
            toast({ title: 'Aktion ausgefuehrt', description: `Anlieferavis ${id} wurde aktualisiert.` })
            navigate('/einkauf/anlieferavis')
          } catch (error: any) {
            toast({ title: 'Aktion fehlgeschlagen', description: error.response?.data?.detail || error.message, variant: 'destructive' })
          }
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/anlieferavis')
    } catch (error: any) {
      toast({ variant: 'destructive', title: 'Fehler beim Speichern', description: error?.message })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Aenderungen wirklich verwerfen?')) {
      navigate('/einkauf/anlieferavis')
    }
  }

  const actionMap: Record<string, string> = {
    senden: 'send',
    bestaetigen: 'confirm',
    stornieren: 'cancel',
  }
  const operationalStatus = normalizeOperationalStatus(data?.status)
  const avisOps = summarizeProcurementMatch({
    exceptionsCount: Array.isArray(data?.positionen) ? data.positionen.filter((row: any) => !row?.chargenNummer).length : 0,
    variancePercentage: data?.status === 'STORNIERT' ? 12 : data?.status === 'BESTAETIGT' ? 0 : 5,
    autoApprovalEligible: data?.status === 'BESTAETIGT',
    hasGoodsReceipt: Boolean(data?.bestellungId),
  })
  const operationalBlocker = data?.status === 'STORNIERT'
    ? 'Das Avis ist storniert. Fuer weitere Schritte braucht es ein neues oder korrigiertes Avis.'
    : !data?.bestellungId
      ? 'Dem Avis fehlt noch eine zugeordnete Bestellung.'
      : null
  const contextSections = [
    {
      title: 'Avis',
      items: [
        { label: 'Avis-Nummer', value: String(data?.avisNummer ?? 'Neu') },
        { label: 'Bestellung', value: String(data?.bestellungId ?? 'Noch offen') },
        { label: 'Status', value: String(data?.status ?? 'GESENDET') },
      ],
    },
    {
      title: 'Logistik',
      items: [
        { label: 'Anlieferdatum', value: String(data?.geplantesAnlieferDatum ?? 'Nicht gesetzt') },
        { label: 'Kennzeichen', value: String(data?.fahrzeug?.kennzeichen ?? 'Noch offen') },
        { label: 'Fahrer', value: String(data?.fahrzeug?.fahrer ?? 'Noch offen') },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Avis-Fall aktiv', detail: String(data?.avisNummer ?? 'Neues Avis') },
    ...(data?.geplantesAnlieferDatum ? [{ label: 'Geplante Anlieferung', detail: String(data.geplantesAnlieferDatum) }] : []),
    { label: 'Naechster Schritt', detail: data?.status === 'BESTAETIGT' ? 'Wareneingang vorbereiten' : 'Avis senden oder bestaetigen' },
  ]

  return (
    <div className="space-y-6">
      <ModuleToolbar backTarget="/einkauf/anlieferavis" closeTarget="/einkauf/anlieferavis" title="Anlieferavis" />
      <OperationalCaseHeader
        title="Anlieferavis steuern"
        description="Das Avis bleibt eine Fachmaske, bekommt aber oben einen kompakten Logistik- und Blockerkontext."
        status={operationalStatus}
        owner="Einkauf / Wareneingang"
        blocker={operationalBlocker}
        nextAction={avisOps.nextAction}
        caseLabel={String(data?.avisNummer ?? 'Anlieferavis')}
        tags={['Einkauf', 'Logistik']}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTimeline title="Avisverlauf" items={timelineItems} />
        <OperationalContextPanel title="Aviskontext" sections={contextSections} />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Abweichungsdruck</CardTitle></CardHeader>
          <CardContent><Badge variant={avisOps.exceptionPressure === 'hoch' ? 'destructive' : 'outline'}>{avisOps.exceptionPressure}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Positionsreife</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{Array.isArray(data?.positionen) ? `${data.positionen.length} Positionen` : 'noch offen'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Fallaktion</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{avisOps.nextAction}</div></CardContent>
        </Card>
      </div>
      <ObjectPage
        config={anlieferavisConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={handleAction}
        loadingActionKey={loadingActionKey}
      />
    </div>
  )
}
