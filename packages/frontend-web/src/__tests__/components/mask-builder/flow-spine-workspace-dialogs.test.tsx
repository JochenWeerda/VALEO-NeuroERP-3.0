import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FlowSpineWorkspaceDialogs } from '@/components/mask-builder/renderers/FlowSpineWorkspaceDialogs'
import type { FlowSpineWorkspaceRuntime } from '@/components/mask-builder/runtime/useFlowSpineWorkspaceRuntime'

vi.mock('@/components/crm/CustomerCombobox', () => ({
  CustomerCombobox: () => <div data-testid="customer-combobox" />,
}))
vi.mock('@/components/sales/CustomerSelectionDialog', () => ({
  CustomerSelectionDialog: () => null,
}))

function runtime(partial: Partial<FlowSpineWorkspaceRuntime> = {}): FlowSpineWorkspaceRuntime {
  const fn = vi.fn()
  return {
    processKey: 'procure-to-pay',
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
      explanation: 'Praxislogik-Text',
      entryModes: [
        { value: 'manual', description: 'Manuell' },
        { value: 'import', description: 'Import' },
      ],
    },
    workspaceQuery: { isLoading: false, isError: false, data: null },
    workspace: null,
    nodes: [],
    selectedNode: null,
    processNavItems: [],
    viewMode: 'board',
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
    showNewInstanceDialog: true,
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

describe('FlowSpineWorkspaceDialogs', () => {
  it('wechselt Entry-Mode und Partnerfeld für Nicht-O2C', () => {
    const setMode = vi.fn()
    const setPartner = vi.fn()
    const setSubject = vi.fn()
    const setLabel = vi.fn()
    const create = vi.fn()
    render(
      <FlowSpineWorkspaceDialogs
        state={runtime({
          setNewInstanceEntryMode: setMode,
          setNewInstancePartnerName: setPartner,
          setNewInstanceSubject: setSubject,
          setNewInstanceLabel: setLabel,
          handleCreateInstance: create,
          newInstancePartnerName: 'Agrar Nord',
          showNewInstanceDialog: true,
        })}
      />,
    )
    expect(screen.getByText('Neue Instanz')).toBeTruthy()
    expect(screen.getByText('Praxislogik-Text')).toBeTruthy()
    fireEvent.click(screen.getByText('Import'))
    expect(setMode).toHaveBeenCalledWith('import')
    fireEvent.change(screen.getByPlaceholderText('z.B. Agrarhandel Nord eG'), {
      target: { value: 'Agrar Nord GmbH' },
    })
    expect(setPartner).toHaveBeenCalledWith('Agrar Nord GmbH')
    fireEvent.change(screen.getByPlaceholderText(/Themenbeschreibung/), {
      target: { value: 'Bestellung' },
    })
    expect(setSubject).toHaveBeenCalledWith('Bestellung')
    fireEvent.change(screen.getByPlaceholderText('Kurzlabel'), { target: { value: 'L1' } })
    expect(setLabel).toHaveBeenCalledWith('L1')
    fireEvent.click(screen.getByRole('button', { name: 'Anlegen' }))
    expect(create).toHaveBeenCalled()
  })

  it('rendert Lifecycle-Dialog hold inkl. Pflichtfelder und Bestaetigen', () => {
    const setLifecycle = vi.fn()
    const submit = vi.fn()
    const close = vi.fn()
    render(
      <FlowSpineWorkspaceDialogs
        state={runtime({
          showNewInstanceDialog: false,
          setLifecycleDialog: setLifecycle,
          handleSubmitLifecycleDialog: submit,
          closeLifecycleDialog: close,
          lifecycleDialog: {
            mode: 'hold',
            businessStatus: 'warten',
            blockedUntil: '',
            reasonCategory: '',
            reasonCode: '',
            reasonNote: '',
          },
        })}
      />,
    )
    expect(screen.getByText('Vorgang pausieren')).toBeTruthy()
    expect(screen.getAllByText('Pflichtfeld').length).toBeGreaterThan(0)
    fireEvent.change(screen.getByPlaceholderText('z.B. lieferung_blockiert'), {
      target: { value: 'lieferung_blockiert' },
    })
    expect(setLifecycle).toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
    expect(close).toHaveBeenCalled()
  })

  it('rendert complete-Lifecycle ohne Kategorie-Pflicht', () => {
    render(
      <FlowSpineWorkspaceDialogs
        state={runtime({
          showNewInstanceDialog: false,
          lifecycleDialog: {
            mode: 'complete',
            businessStatus: 'fertig',
            blockedUntil: '',
            reasonCategory: '',
            reasonCode: 'workflow_completed',
            reasonNote: 'ok',
          },
        })}
      />,
    )
    expect(screen.getByText('Vorgang abschliessen')).toBeTruthy()
    expect(screen.getByPlaceholderText('z.B. workflow_completed')).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Bestaetigen' })).not.toBeDisabled()
  })
})
