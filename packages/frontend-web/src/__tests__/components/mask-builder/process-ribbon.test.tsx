/**
 * UIX-091: Prozessband-Compiler + Renderer.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/test-router'
import { compileProcessRibbon, type ProcessChain } from '@/components/mask-builder/renderers/process-ribbon'
import { ProcessRibbonRenderer } from '@/components/mask-builder/renderers/ProcessRibbonRenderer'

const mockNavigate = vi.fn()
vi.mock('@/app/routing/typed-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/app/routing/typed-router')>()
  return { ...actual, useNavigate: () => mockNavigate }
})

const CHAINS: Record<string, ProcessChain> = {
  k2_verkauf: {
    label: 'Verkauf',
    steps: [
      { key: 'auftrag', label: 'Auftrag', screenId: 'sales/sales-order' },
      { key: 'lieferschein', label: 'Lieferschein', screenId: 'sales/delivery-note' },
      { key: 'zahlung', label: 'Zahlung', screenId: 'finance/payment-run' },
    ],
  },
}

const routes: Record<string, string> = {
  'sales/sales-order': '/verkauf/auftraege',
  'sales/delivery-note': '/verkauf/lieferschein-erfassung',
  'finance/payment-run': '/fibu/zahlungslaeufe',
}
const resolve = (id: string) => routes[id]

describe('compileProcessRibbon', () => {
  it('kompiliert Kette + markiert aktuellen Schritt', () => {
    const { ribbon, warnings } = compileProcessRibbon('k2_verkauf', 'lieferschein', CHAINS, resolve)
    expect(warnings).toEqual([])
    expect(ribbon).not.toBeNull()
    expect(ribbon!.steps.map((s) => s.state)).toEqual(['upcoming', 'current', 'upcoming'])
    expect(ribbon!.steps[0].routePath).toBe('/verkauf/auftraege')
  })

  it('unbekannte chainId → kein Ribbon + Warnung', () => {
    const { ribbon, warnings } = compileProcessRibbon('gibtsnicht', 'x', CHAINS, resolve)
    expect(ribbon).toBeNull()
    expect(warnings).toContain('unknown_chain:gibtsnicht')
  })

  it('unbekannter stepKey → Warnung, kein current', () => {
    const { ribbon, warnings } = compileProcessRibbon('k2_verkauf', 'phantom', CHAINS, resolve)
    expect(warnings).toContain('unknown_step:k2_verkauf:phantom')
    expect(ribbon!.steps.every((s) => s.state !== 'current')).toBe(true)
  })

  it('nicht aufloesbare Route → Warnung + leerer routePath', () => {
    const { ribbon, warnings } = compileProcessRibbon('k2_verkauf', 'auftrag', CHAINS, () => undefined)
    expect(warnings.some((w) => w.startsWith('unresolved_route:'))).toBe(true)
    expect(ribbon!.steps[0].routePath).toBe('')
  })
})

describe('ProcessRibbonRenderer', () => {
  beforeEach(() => mockNavigate.mockClear())

  it('rendert Schritte, markiert current und navigiert bei Klick', () => {
    const { ribbon } = compileProcessRibbon('k2_verkauf', 'lieferschein', CHAINS, resolve)
    render(
      <MemoryRouter>
        <ProcessRibbonRenderer ribbon={ribbon} />
      </MemoryRouter>,
    )
    expect(screen.getByTestId('ribbon-step-lieferschein')).toHaveAttribute('data-state', 'current')
    fireEvent.click(screen.getByTestId('ribbon-step-auftrag'))
    expect(mockNavigate).toHaveBeenCalledWith('/verkauf/auftraege')
  })

  it('Schritt ohne Route ist deaktiviert', () => {
    const { ribbon } = compileProcessRibbon('k2_verkauf', 'auftrag', CHAINS, () => undefined)
    render(
      <MemoryRouter>
        <ProcessRibbonRenderer ribbon={ribbon} />
      </MemoryRouter>,
    )
    expect(screen.getByTestId('ribbon-step-auftrag')).toBeDisabled()
  })

  it('null-Ribbon rendert nichts', () => {
    const { container } = render(
      <MemoryRouter>
        <ProcessRibbonRenderer ribbon={null} />
      </MemoryRouter>,
    )
    expect(container.querySelector('[data-testid="process-ribbon"]')).toBeNull()
  })
})
