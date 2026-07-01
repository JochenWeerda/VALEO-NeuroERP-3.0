import { useState, useEffect } from 'react'
import { Worklist } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { WorklistConfig, WorklistItem } from '@/components/mask-builder/types'
import { useFutterQualitaet } from '@/lib/api/futter'
import { toast } from '@/hooks/use-toast'
import { EvidenceTemplateLink, NextActionPanel, OperationalTaskPlan } from '@/components/workflow'

function toWorklistItem(item: Record<string, unknown>): WorklistItem | null {
  if (!(typeof item.id === 'string'
    && typeof item.title === 'string'
    && (item.status === 'pending' || item.status === 'in-progress' || item.status === 'completed' || item.status === 'overdue')
    && (item.priority === 'low' || item.priority === 'medium' || item.priority === 'high' || item.priority === 'urgent'))) {
    return null
  }
  return {
    id: item.id,
    title: item.title,
    description: typeof item.description === 'string' ? item.description : undefined,
    status: item.status,
    priority: item.priority,
    dueDate: typeof item.dueDate === 'string' ? item.dueDate : undefined,
    assignedTo: typeof item.assignedTo === 'string' ? item.assignedTo : undefined,
    metadata: typeof item.metadata === 'object' && item.metadata !== null ? item.metadata as Record<string, unknown> : undefined,
  }
}

// Konfiguration fuer Qualitaetskontrolle Worklist
const qualityControlConfig: WorklistConfig = {
  title: 'Futtermittel-Qualitaetskontrolle',
  subtitle: 'Laboranalysen und Qualitaetspruefungen nach QS-Standards',
  type: 'worklist',
  groupBy: 'status',
  itemTemplate: (item: WorklistItem) => <div>{item.title}</div>,
  api: {
    baseUrl: '/api/v1/futter/quality-control',
    endpoints: {
      list: '/api/v1/futter/quality-control'
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
  const offenePruefungen = items.filter((item) => item.status === 'pending' || item.status === 'in-progress').length
  const gesperrteChargen = items.filter((item) => item.status === 'overdue' || item.priority === 'urgent').length
  const nextQualityAction = gesperrteChargen > 0
    ? 'Gesperrte oder auffaellige Charge zuerst pruefen, Entscheidung dokumentieren und erst danach freigeben.'
    : offenePruefungen > 0
      ? 'Offene Laborpruefungen nach Faelligkeit bearbeiten und Ergebnis an der Charge festhalten.'
      : 'Keine offene Qualitaetspruefung. Neue Wareneingaenge und Laborrueckmeldungen beobachten.'

  useEffect(() => {
    if (apiItems.length > 0 && items.length === 0) {
      setItems(apiItems)
    }
  }, [apiItems, items.length])

  const { handleAction } = useMaskActions(async (action: string, payload: Record<string, unknown>) => {
    const item = toWorklistItem(payload)
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
    handleAction(action, { ...item })
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <NextActionPanel
          title="Naechste Pruefaktion"
          action={nextQualityAction}
          tone={gesperrteChargen > 0 ? 'red' : offenePruefungen > 0 ? 'amber' : 'emerald'}
        />
        <EvidenceTemplateLink link={{ label: 'QS-Pruefprotokoll Futtermittel', href: '/docs/futtermittel/qs-pruefprotokoll.md' }} />
      </div>
      <OperationalTaskPlan
        title="Kompakter QS-Ablauf"
        items={[
          { label: 'Charge identifizieren', done: items.length > 0, hint: 'Produkt, Charge und Pruefparameter muessen eindeutig sein.' },
          { label: 'Laborergebnis bewerten', done: gesperrteChargen === 0 && offenePruefungen === 0 && items.length > 0, hint: 'Auffaellige Werte bleiben gesperrt oder werden eskaliert.' },
          { label: 'Freigabe oder Ablehnung dokumentieren', done: items.some((item) => item.status === 'completed'), hint: 'Entscheidung direkt an der Worklist-Aktion ausloesen.' },
        ]}
      />
      <Worklist
        config={qualityControlConfig}
        items={items}
        onAction={handleActionClick}
        isLoading={isLoading}
      />
    </div>
  )
}
