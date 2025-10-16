import { useState } from 'react'
import { Worklist } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { WorklistConfig, WorklistItem } from '@/components/mask-builder/types'

// Mock-Daten für Qualitätskontrolle
const mockQualityItems: WorklistItem[] = [
  {
    id: 'qc-001',
    title: 'Weizenmehl Charge W-2024-001',
    description: 'Aflatoxin-Gehalt überschreitet Grenzwert',
    status: 'overdue',
    priority: 'urgent',
    assignedTo: 'Dr. Müller',
    dueDate: '2024-10-20',
    metadata: {
      charge: 'W-2024-001',
      parameter: 'Aflatoxin',
      wert: '15.2 µg/kg',
      grenzwert: '10 µg/kg'
    }
  },
  {
    id: 'qc-002',
    title: 'Mais Charge M-2024-015',
    description: 'Feuchtigkeitsgehalt zu hoch',
    status: 'pending',
    priority: 'high',
    assignedTo: 'Labor',
    dueDate: '2024-10-18',
    metadata: {
      charge: 'M-2024-015',
      parameter: 'Feuchtigkeit',
      wert: '16.5%',
      grenzwert: '15%'
    }
  },
  {
    id: 'qc-003',
    title: 'Sojaextraktionsschrot Charge S-2024-008',
    description: 'Rohproteingehalt unter Spezifikation',
    status: 'in-progress',
    priority: 'medium',
    assignedTo: 'Qualitätsmanagement',
    dueDate: '2024-10-25',
    metadata: {
      charge: 'S-2024-008',
      parameter: 'Rohprotein',
      wert: '45.2%',
      grenzwert: '48%'
    }
  },
  {
    id: 'qc-004',
    title: 'Milchviehfutter Premium Charge MP-2024-012',
    description: 'Routinekontrolle fällig',
    status: 'pending',
    priority: 'low',
    assignedTo: 'Automatisch',
    dueDate: '2024-10-30',
    metadata: {
      charge: 'MP-2024-012',
      parameter: 'Routinekontrolle',
      naechstePruefung: '2024-10-30'
    }
  }
]

// Konfiguration für Qualitätskontrolle Worklist
const qualityControlConfig: WorklistConfig = {
  title: 'Futtermittel-Qualitätskontrolle',
  subtitle: 'Laboranalysen und Qualitätsprüfungen nach QS-Standards',
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
    { name: 'priority', label: 'Priorität', type: 'select' },
    { name: 'assignedTo', label: 'Zugewiesen an', type: 'text' }
  ]
}

export default function FuttermittelQualitaetskontrollePage(): JSX.Element {
  const [items, setItems] = useState<WorklistItem[]>(mockQualityItems)

  const { handleAction } = useMaskActions(async (action: string, item: WorklistItem) => {
    if (!item) return

    switch (action) {
      case 'approve':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, status: 'completed' as const } : i
        ))
        alert(`${item.title} wurde freigegeben.`)
        break

      case 'reject':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, status: 'completed' as const } : i
        ))
        alert(`${item.title} wurde abgelehnt.`)
        break

      case 'analyze':
        alert(`Analyse für ${item.title} wurde angefordert.`)
        break

      case 'escalate':
        setItems(prev => prev.map(i =>
          i.id === item.id ? { ...i, priority: 'urgent' as const } : i
        ))
        alert(`${item.title} wurde eskaliert.`)
        break

      default:
        console.log('Action:', action, item)
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
      isLoading={false}
    />
  )
}