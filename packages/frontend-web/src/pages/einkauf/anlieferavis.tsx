import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

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

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/anlieferavis')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
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

  return (
    <ObjectPage
      config={anlieferavisConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
      onAction={async (actionKey) => {
        if (!id || !actionMap[actionKey]) {
          toast({ title: 'Aktion nicht moeglich', description: 'Das Avis muss zuerst gespeichert werden.', variant: 'destructive' })
          return
        }
        setLoading(true)
        try {
          await apiClient.post(`/api/v1/einkauf/anlieferavis/${encodeURIComponent(id)}/${actionMap[actionKey]}`)
          toast({ title: 'Aktion ausgefuehrt', description: `Anlieferavis ${id} wurde aktualisiert.` })
          navigate('/einkauf/anlieferavis')
        } catch (error: any) {
          toast({ title: 'Aktion fehlgeschlagen', description: error.response?.data?.detail || error.message, variant: 'destructive' })
        } finally {
          setLoading(false)
        }
      }}
    />
  )
}
