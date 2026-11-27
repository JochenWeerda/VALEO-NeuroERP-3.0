import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FlowSpineWorkspaceRenderer } from '@/components/mask-builder/renderers/FlowSpineWorkspaceRenderer'
import type { FlowSpineWorkspaceRuntime } from '@/components/mask-builder/runtime/useFlowSpineWorkspaceRuntime'

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-panel" />,
}))
vi.mock('@/components/mask-builder/renderers/FlowSpineWorkspaceDialogs', () => ({
  FlowSpineWorkspaceDialogs: () => null,
}))

function runtime(partial: Partial<FlowSpineWorkspaceRuntime> = {}): FlowSpineWorkspaceRuntime {
  const fn = vi.fn()
  return {
    processKey: 'order-to-cash',
    instanceId: null,
    navigate: fn,
    location: { pathname: '/flow', search: '' },
    startConfig: {
      dialogTitle: 'Neue Instanz',
      dialogDescription: 'Starten',
      partnerLabel: 'Partner',
      subjectLabel: 'Betreff',
      labelLabel: 'Label',
      labelPlaceholder: 'Kurzlabel',
      submitLabel: 'Anlegen',
      buttonLabel: 'Neu',
      explanation: 'Praxislogik-Text',
      entryModes: [{ value: 'manual', description: 'Manuell' }],
    },
    workspaceQuery: { isLoading: false, isError: false, data: null, error: null },
    workspace: null,
    nodes: [],
    selectedNode: null,
    processNavItems: [],
    viewMode: 'fokus',
    setViewMode: fn,
    showNodeDetails: false,
    showSideFlaechen: false,
    copilotOpen: false,
    setCopilotOpen: fn,
    progressWidth: 0,
    go: fn,
    handleAction: fn,
    handleAgentAction: fn,
    handleCreateInstance: fn,
    openLifecycleDialog: fn,
    closeLifecycleDialog: fn,
    handleSaveLifecycle: fn,
    handleResumeLifecycle: fn,
    handleSubmitLifecycleDialog: fn,
    setSelectedNodeId: fn,
    showNewInstanceDialog: false,
    setShowNewInstanceDialog: fn,
    newInstanceLabel: '',
    setNewInstanceLabel: fn,
    newInstancePartnerName: '',
    setNewInstancePartnerName: fn,
    newInstanceSubject: '',
    setNewInstanceSubject: fn,
    newInstanceEntryMode: 'manual',
    setNewInstanceEntryMode: fn,
    newInstanceCustomer: null,
    setNewInstanceCustomer: fn,
    showAdvancedCustomerSearch: false,
    setShowAdvancedCustomerSearch: fn,
    createInstance: { isPending: false },
    executeAction: { isPending: false },
    executeAgentAction: { isPending: false },
    instanceSearch: '',
    setInstanceSearch: fn,
    instancesQuery: { data: [] },
    timelineQuery: { data: [] },
    saveInstance: { isPending: false },
    resumeInstance: { isPending: false },
    holdInstance: { isPending: false },
    completeInstance: { isPending: false },
    cancelInstance: { isPending: false },
    failInstance: { isPending: false },
    lifecycleDialog: null,
    setLifecycleDialog: fn,
    ...partial,
  } as unknown as FlowSpineWorkspaceRuntime
}

const sampleWorkspace = {
  schema_version: 1,
  manifest_kind: 'flow-spine',
  generated_at: '2026-11-27T00:00:00Z',
  process_key: 'order-to-cash',
  title: 'Auftrag bis Zahlung',
  subtitle: 'O2C',
  instance_label: 'Beleg',
  breadcrumb: ['Verkauf', 'Auftrag bis Zahlung'],
  search_placeholder: 'Suchen…',
  mode: 'workspace',
  user_role: 'clerk',
  left_navigation: { processes: [], favorites: [], recent_items: [], role_switches: [] },
  badges: [
    { label: 'OK', tone: 'ok' },
    { label: 'Warn', tone: 'warning' },
    { label: 'Kritisch', tone: 'critical' },
    { label: 'Aktiv', tone: 'active' },
    { label: 'Neutral', tone: 'neutral' },
  ],
  focus_node_id: 'n1',
  progress_percent: 40,
  lifecycle_status: 'in_progress' as const,
  reason_note: '',
  footer_items: ['Hilfe', { label: 'Doku', href: '/docs' }],
  footer_cards: [
    { title: 'Naechste Schritte', items: ['Auftrag prüfen'], tone: 'ok' },
  ],
  kpis: [],
  documents: [],
  timeline: [],
  nodes: [
    {
      id: 'n1',
      label: 'Auftrag',
      status: 'done',
      tone: 'ok',
      icon: 'FileText',
      insight: 'Erfasst und geprüft',
      description: 'Erfasst',
      metric: '1 Beleg',
      submetric: 'offen',
      detail_rows: [{ label: 'Menge', value: '12 t' }],
      actions: [{ key: 'open', label: 'Öffnen', kind: 'navigate', target: '/verkauf/auftraege' }],
      documents: [],
      checklist: [],
    },
  ],
  side_panels: [],
  agent_hints: [],
}

describe('FlowSpineWorkspaceRenderer', () => {
  it('zeigt Lade-Skeleton', () => {
    render(
      <FlowSpineWorkspaceRenderer
        state={runtime({ workspaceQuery: { isLoading: true, isError: false, data: null, error: null } as never })}
      />,
    )
    expect(document.querySelector('[data-page-surface="flow-spine-order-to-cash"]')).toBeTruthy()
    expect(document.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0)
  })

  it('zeigt Fehlerdetail bei Query-Error', () => {
    render(
      <FlowSpineWorkspaceRenderer
        state={runtime({
          workspaceQuery: {
            isLoading: false,
            isError: true,
            data: null,
            error: new Error('Backend down'),
          } as never,
        })}
      />,
    )
    expect(screen.getByText(/Backend down/)).toBeInTheDocument()
    expect(screen.getByText(/Flow Spine nicht verfuegbar/)).toBeInTheDocument()
  })

  it('zeigt leere Workspace-Warnung', () => {
    render(
      <FlowSpineWorkspaceRenderer
        state={runtime({
          workspaceQuery: { isLoading: false, isError: false, data: {}, error: null } as never,
          workspace: null,
          nodes: [],
          selectedNode: null,
        })}
      />,
    )
    expect(screen.getByText(/Ungueltige oder leere Workspace-Daten/)).toBeInTheDocument()
  })

  it('rendert Workspace mit Badges und Lifecycle', () => {
    const node = sampleWorkspace.nodes[0]
    render(
      <FlowSpineWorkspaceRenderer
        state={runtime({
          workspaceQuery: { isLoading: false, isError: false, data: sampleWorkspace, error: null } as never,
          workspace: sampleWorkspace as never,
          nodes: sampleWorkspace.nodes as never,
          selectedNode: node as never,
          progressWidth: '40%',
          viewMode: 'fokus',
          showNodeDetails: true,
          instanceId: 'inst-1',
          processNavItems: [{ key: 'order-to-cash', label: 'O2C', route_path: '/o2c', active: true }],
          instancesQuery: { data: [], isLoading: false } as never,
        })}
      />,
    )
    expect(screen.getByText('Verkauf')).toBeInTheDocument()
    expect(screen.getAllByText('Auftrag bis Zahlung').length).toBeGreaterThan(0)
    expect(screen.getByText('OK')).toBeInTheDocument()
    expect(screen.getByText('Warn')).toBeInTheDocument()
    expect(screen.getByText('Kritisch')).toBeInTheDocument()
    expect(screen.getByText(/Status Details: Auftrag/)).toBeInTheDocument()
  })

  it('zeigt Pausiert-Hinweis bei hold Lifecycle', () => {
    const held = {
      ...sampleWorkspace,
      lifecycle_status: 'on_hold' as const,
      reason_note: 'Wartet auf Freigabe',
    }
    render(
      <FlowSpineWorkspaceRenderer
        state={runtime({
          workspaceQuery: { isLoading: false, isError: false, data: held, error: null } as never,
          workspace: held as never,
          nodes: held.nodes as never,
          selectedNode: held.nodes[0] as never,
          viewMode: 'fokus',
          showNodeDetails: false,
          instanceId: 'inst-2',
          instancesQuery: { data: [], isLoading: false } as never,
        })}
      />,
    )
    expect(screen.getAllByText(/Wartet auf Freigabe|Pausiert/).length).toBeGreaterThan(0)
  })
})
