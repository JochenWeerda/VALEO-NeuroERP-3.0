import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineProcureToPayPage from '@/pages/workflow/flow-spine-procure-to-pay'

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

describe('FlowSpineProcureToPayPage', () => {
  it('rendert den Procure-to-Pay Arbeitsraum', () => {
    render(
      <MemoryRouter>
        <FlowSpineProcureToPayPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Flow Spine - Procure-to-Pay', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Globale Suche')).toBeInTheDocument()
    expect(screen.getByText('Procure-to-Pay / Bestellung PO-2026-188')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Agent' })).toBeInTheDocument()
    expect(screen.getAllByTestId('agent-process-panel').length).toBeGreaterThan(0)
  })
})
