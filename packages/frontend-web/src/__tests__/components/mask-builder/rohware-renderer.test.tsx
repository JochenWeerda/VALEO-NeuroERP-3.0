import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { RohwareRenderer } from '@/components/mask-builder/specialized/intake/rohware-renderer'
import type { RohwareState } from '@/components/mask-builder/specialized/intake/rohware-controller'

const navigateMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/navigation/ModuleToolbar', () => ({
  ModuleToolbar: () => <div data-testid="module-toolbar" />,
}))
vi.mock('@/components/agent', () => ({
  AgentSuggestionBadge: () => null,
  AgentProcessPanel: () => null,
}))

function successState(): RohwareState {
  return {
    navigate: navigateMock,
    isTouch: false,
    chain: { waitingInbound: 2, openWeighingTickets: 1, blockedCharges: 0, freightInTransit: 0 },
    supplyOps: {},
    transferSummary: null,
    form: {
      lieferant: 'LW-1',
      kennzeichen: 'EL-AB 123',
      artikel: 'Weizen',
      lagerZiel: 'Silo-A',
      feuchtePct: '14',
      besatzPct: '1.2',
      fallzahl: '280',
      datum: '2026-11-26',
      bruttoKg: 25000,
      taraKg: 10000,
      lieferscheinNr: 'LS-1',
      customer_id: '',
    },
    updateField: vi.fn(),
    nettoKg: 15000,
    operationalStatus: 'ok',
    operationalBlocker: null,
    operationalNextAction: 'Qualitätsprüfung',
    contextSections: [],
    timelineItems: [],
    acceptanceResult: { id: 'ha-1', acceptance_number: 'A-99' },
    submitting: false,
    validateRohwareStep: vi.fn(() => null),
    handleRohwareStepValidationError: vi.fn(),
    handleFinish: vi.fn(),
    shortcuts: {},
    plan: { screenId: 'annahme/rohware', fieldsByKey: {} },
  } as unknown as RohwareState
}

describe('RohwareRenderer', () => {
  beforeEach(() => {
    navigateMock.mockReset()
  })

  it('zeigt Erfolgsansicht und navigiert zur Abrechnung mit Qualitätswerten', () => {
    render(<RohwareRenderer state={successState()} />)
    expect(screen.getByText('Rohware erfolgreich angenommen')).toBeTruthy()
    expect(screen.getByText('A-99')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Zur Abrechnung' }))
    expect(navigateMock).toHaveBeenCalledWith('/annahme/abrechnung', {
      state: {
        fromQualitaetsCheck: true,
        artikel: 'Weizen',
        feuchtigkeit: 14,
        verunreinigung: 1.2,
      },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Zur Warteschlange' }))
    expect(navigateMock).toHaveBeenCalledWith('/annahme/warteschlange')
  })
})
