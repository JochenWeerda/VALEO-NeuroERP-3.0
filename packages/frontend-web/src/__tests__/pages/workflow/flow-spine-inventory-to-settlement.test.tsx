import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineInventoryToSettlementPage from '@/pages/workflow/flow-spine-inventory-to-settlement'

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

describe('FlowSpineInventoryToSettlementPage', () => {
  it('rendert den Inventory-to-Settlement Arbeitsraum', () => {
    render(
      <MemoryRouter>
        <FlowSpineInventoryToSettlementPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Flow Spine - Inventory-to-Settlement', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Globale Suche')).toBeInTheDocument()
    expect(screen.getByText('Inventory-to-Settlement / Welle INV-2026-031')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Agent' })).toBeInTheDocument()
    expect(screen.getAllByTestId('agent-process-panel').length).toBeGreaterThan(0)
  })
})
