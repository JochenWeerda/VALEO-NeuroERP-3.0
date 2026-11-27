import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useRohwareController } from '@/components/mask-builder/specialized/intake/rohware-controller'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'

const toastMock = vi.hoisted(() => vi.fn())
const navigateMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: toastMock }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => navigateMock }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/hooks/useKeyboardShortcuts', () => ({
  buildCoreMaskShortcuts: () => ({}),
  useKeyboardShortcuts: () => undefined,
}))
vi.mock('@/lib/axios', () => ({
  api: { post: (...args: unknown[]) => apiPostMock(...args) },
}))
vi.mock('@/lib/api/supply-chain', () => ({
  useSupplyChainOverview: () => ({
    data: {
      waitingInbound: 2,
      openWeighingTickets: 0,
      blockedCharges: 0,
      freightInTransit: 0,
      bottleneck: 'Waage',
      pressure: 'niedrig',
      nextAction: 'Annahme',
    },
  }),
}))
vi.mock('@/components/mask-builder/specialized/intake/domain-runtime', () => ({
  canDomainAction: () => true,
  fieldsEditable: () => true,
  useDomainDispatch: () => undefined,
}))

function plan(): RenderPlan {
  const keys = [
    'lieferant', 'kennzeichen', 'lieferscheinNr', 'datum', 'artikel',
    'bruttoKg', 'taraKg', 'lagerZiel', 'feuchtePct', 'besatzPct', 'fallzahl', 'customer_id',
  ]
  return {
    screenId: 'annahme/rohware',
    fieldsByKey: Object.fromEntries(keys.map((k) => [k, { key: k, visible: true, readOnly: false }])),
  } as RenderPlan
}

describe('useRohwareController', () => {
  beforeEach(() => {
    toastMock.mockReset()
    navigateMock.mockReset()
    apiPostMock.mockReset()
    apiPostMock.mockResolvedValue({ data: { id: 'ha-1', acceptance_number: 'A-1' } })
  })

  it('validiert Schritte und speichert Rohware', async () => {
    const { result } = renderHook(() => useRohwareController(plan()))
    expect(result.current.validateRohwareStep('lieferant-fahrzeug')).toMatch(/Lieferant/)
    act(() => {
      result.current.updateField('lieferant', 'Hof')
      result.current.updateField('kennzeichen', 'AB-1')
      result.current.updateField('artikel', 'Weizen')
      result.current.updateField('lagerZiel', 'Silo 1')
      result.current.updateField('bruttoKg', 1000)
      result.current.updateField('taraKg', 200)
      result.current.updateField('feuchtePct', '14')
      result.current.updateField('besatzPct', '1')
    })
    expect(result.current.validateRohwareStep('lieferant-fahrzeug')).toBeNull()
    expect(result.current.validateRohwareStep('ware-gewicht')).toBeNull()
    expect(result.current.nettoKg).toBe(800)

    await act(async () => {
      result.current.handleFinish()
    })
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/harvest-acceptance/rohware',
        expect.objectContaining({
          artikel: 'Weizen',
          lager_ziel: 'Silo 1',
          brutto_kg: 1000,
          tara_kg: 200,
          netto_kg: 800,
        }),
      )
    })
    expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Rohware-Annahme gespeichert' }))
  })

  it('meldet Speichern-Fehler und navigiert zur Abrechnung', async () => {
    apiPostMock.mockRejectedValueOnce({ response: { data: { detail: '422 detail' } } })
    const { result } = renderHook(() => useRohwareController(plan()))
    act(() => {
      result.current.updateField('lieferant', 'Hof')
      result.current.updateField('kennzeichen', 'AB-1')
      result.current.updateField('artikel', 'Weizen')
      result.current.updateField('lagerZiel', 'Silo 1')
      result.current.updateField('bruttoKg', 500)
      result.current.updateField('taraKg', 0)
      result.current.updateField('feuchtePct', '15')
      result.current.updateField('besatzPct', '2')
    })
    await act(async () => {
      result.current.handleFinish()
    })
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Fehler beim Speichern', description: '422 detail' }),
      )
    })
  })
})
