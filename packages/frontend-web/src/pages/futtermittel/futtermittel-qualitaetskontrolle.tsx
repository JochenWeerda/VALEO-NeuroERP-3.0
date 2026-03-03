import { useState, useEffect } from 'react'
import { Worklist } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { WorklistConfig, WorklistItem } from '@/components/mask-builder/types'
import { useFutterQualitaet } from '@/lib/api/futter'
import { toast } from '@/hooks/use-toast'

// Konfiguration fuer Qualitaetskontrolle Worklist
const qualityControlConfig: WorklistConfig = {
  title: 'Futtermittel-Qualitaetskontrolle',
  subtitle: 'Laboranalysen und Qualitaetspruefungen nach QS-Standards',
  type: 'worklist',
  groupBy: 'status',
  itemTemplate: (item: WorklistItem) => <div>{item.title}</div>,
  api: {
    baseUrl: '/api/futtermittel/quality-control',
    endpoints: {
      list: '/api/futtermittel/quality-control'
    }
  },
  permissions: ['futtermittel.quality', 'lab.read'],
  actions: [
    {
      key: 'approve',
      label: 'Freigeben',
      type: 'primary',
      condition: (item: WorklistItem) => item.status === 'pending' || item.status === 'in-progress',
      onClick: () => {}
    },
    {
      key: 'reject',
      label: 'Ablehnen',
      type: 'danger',
      condition: (item: WorklistItem) => item.status === 'pending' || item.status === 'in-progress',
      onClick: () => {}
    },
    {
      key: 'analyze',
      label: 'Analyse anfordern',
      type: 'secondary',
      condition: (item: WorklistItem) => item.status === 'pending',
      onClick: () => {}
    },
    {
      key: 'escalate',
      label: 'Eskalieren',
      type: 'secondary',
      condition: (item: WorklistItem) => item.priority === 'urgent',
      onClick: () => {}
    }
  ],
  filters: [
    { name: 'status', label: 'Status', type: 'select' },
    { name: 'priority', label: 'Prioritaet', type: 'select' },
    { name: 'assignedTo', label: 'Zugewiesen an', type: 'text' }
  ]
}

function mapQualitaetToWorklistItems(data: ReturnType<typeof useFutterQualitaet>['data']): WorklistItem[] {
  if (!data) return []
  return data.map(q => ({
    id: q.id,
    title: `${q.produkt} Charge ${q.chargenId}`,
    description: `${q.pruefung}: ${q.ergebnis}`,
    status: q.status === 'bestanden' ? 'completed' as const
      : q.status === 'nicht-bestanden' ? 'overdue' as const
      : 'pending' as const,
    priority: q.status === 'nicht-bestanden' ? 'urgent' as const : 'medium' as const,
    assignedTo: 'Labor',
    dueDate: q.datum,
    metadata: {
      charge: q.chargenId,
      parameter: q.pruefung,
      ergebnis: q.ergebnis
    }
  }))
}

export default function FuttermittelQualitaetskontrollePage(): JSX.Element {
  const { data: qualitaetData, isLoading } = useFutterQualitaet()
  const apiItems = mapQualitaetToWorklistItems(qualitaetData)
  const [items, setItems] = useState<WorklistItem[]>([])

  useEffect(() => {
    if (apiItems.length > 0 && items.length === 0) {
      setItems(apiItems)
    }
  }, [apiItems, items.length])

  const { handleAction } = useMaskActions(async (action: string, item: WorklistItem) => {
    if (!item) return

    switch (action) {
      case 'approve':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, status: 'completed' as const } : i
        ))
        toast({ title: 'Freigegeben', description: `${item.title} wurde freigegeben.` })
        break

      case 'reject':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, status: 'completed' as const } : i
        ))
        toast({ title: 'Abgelehnt', description: `${item.title} wurde abgelehnt.`, variant: 'destructive' })
        break

      case 'analyze':
        toast({ title: 'Analyse angefordert', description: `Analyse für ${item.title} wurde angefordert.` })
        break

      case 'escalate':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, priority: 'urgent' as const } : i
        ))
        toast({ title: 'Eskaliert', description: `${item.title} wurde eskaliert.`, variant: 'destructive' })
        break

      default:
        break
    }
  })

  const handleActionClick = (item: WorklistItem, action: string) => {
    handleAction(action, item)
  }

  return (
    <Worklist
      config={qualityControlConfig}
      items={items}
      onAction={handleActionClick}
      isLoading={isLoading}
    />
  )
}
