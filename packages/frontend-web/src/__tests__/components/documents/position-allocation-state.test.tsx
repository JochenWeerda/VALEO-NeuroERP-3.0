import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { PositionAllocationState } from '@/components/documents/PositionAllocationState'

/**
 * FSX-MENGENMODELL — K5 an der Position.
 *
 * Die Zeile, um die es geht: "100 dt geliefert · 60 dt berechnet · 40 dt offen".
 * Und darunter aufklappbar, **welche** Rechnung die 60 dt genommen hat —
 * Anzeigen ist nicht Aufloesen.
 */

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock },
}))

function antwort(overrides: Record<string, unknown> = {}) {
  return {
    data: {
      lines: [
        {
          line_id: '1',
          article_id: 'ART-WEIZEN',
          unit: 'dt',
          quantity: '100',
          allocated_quantity: '60',
          open_quantity: '40',
          status: 'teilweise',
          allocations: [
            {
              id: 'a1',
              target_document_type: 'sales_invoice',
              target_document_id: 'RE-X',
              target_line_id: '1',
              quantity: '60',
              unit: 'dt',
              entered_quantity: '60',
              entered_unit: 'dt',
              reason: 'teilrechnung',
            },
          ],
        },
      ],
      ...overrides,
    },
  }
}

function renderState(props: Record<string, unknown> = {}) {
  return render(
    <PositionAllocationState documentType="delivery_note" documentId="LS-1" {...props} />,
  )
}

describe('PositionAllocationState', () => {
  beforeEach(() => {
    getMock.mockReset()
  })

  it('zeigt geliefert, berechnet und offen in einer Zeile', async () => {
    getMock.mockResolvedValue(antwort())
    renderState()

    const zeile = await screen.findByTestId('allocation-summary-1')
    expect(zeile).toHaveTextContent('100 dt geliefert')
    expect(zeile).toHaveTextContent('60 dt berechnet')
    expect(zeile).toHaveTextContent('40 dt offen')
  })

  it('klappt die Zuordnungen auf — welche Rechnung welche Menge genommen hat', async () => {
    getMock.mockResolvedValue(antwort())
    const user = userEvent.setup()
    renderState()

    await screen.findByTestId('allocation-summary-1')
    // Vor dem Aufklappen steht die Zielrechnung nicht da.
    expect(screen.queryByText('RE-X')).not.toBeInTheDocument()

    await user.click(screen.getByTestId('allocation-summary-1'))

    expect(screen.getByText('RE-X')).toBeInTheDocument()
    expect(screen.getByText('teilrechnung', { exact: false })).toBeInTheDocument()
  })

  it('zeigt die Eingabe neben der umgerechneten Menge', async () => {
    getMock.mockResolvedValue(
      antwort({
        lines: [
          {
            line_id: '1',
            unit: 'dt',
            quantity: '100',
            allocated_quantity: '12',
            open_quantity: '88',
            status: 'teilweise',
            allocations: [
              {
                id: 'a1',
                target_document_type: 'sales_invoice',
                target_document_id: 'RE-X',
                target_line_id: '1',
                quantity: '12',
                unit: 'dt',
                entered_quantity: '2',
                entered_unit: 'big_bag',
              },
            ],
          },
        ],
      }),
    )
    const user = userEvent.setup()
    renderState()

    await screen.findByTestId('allocation-summary-1')
    await user.click(screen.getByTestId('allocation-summary-1'))

    // Niemand soll die umgerechnete Zahl fuer die eingegebene halten.
    expect(screen.getByText('2 big_bag (= 12 dt)')).toBeInTheDocument()
  })

  it('laesst sich nicht aufklappen, wenn es nichts aufzuklappen gibt', async () => {
    getMock.mockResolvedValue(
      antwort({
        lines: [
          {
            line_id: '1',
            unit: 'dt',
            quantity: '100',
            allocated_quantity: '0',
            open_quantity: '100',
            status: 'offen',
            allocations: [],
          },
        ],
      }),
    )
    renderState()

    const knopf = await screen.findByTestId('allocation-summary-1')
    expect(knopf.closest('button')).toBeDisabled()
  })

  it('filtert auf eine Position, wenn eine genannt ist', async () => {
    getMock.mockResolvedValue(
      antwort({
        lines: [
          { line_id: '1', unit: 'dt', quantity: '100', allocated_quantity: '0', open_quantity: '100', status: 'offen', allocations: [] },
          { line_id: '2', unit: 'dt', quantity: '50', allocated_quantity: '0', open_quantity: '50', status: 'offen', allocations: [] },
        ],
      }),
    )
    renderState({ lineId: '2' })

    await screen.findByTestId('allocation-line-2')
    expect(screen.queryByTestId('allocation-line-1')).not.toBeInTheDocument()
  })

  it('behauptet nach einem Abrufsfehler nichts', async () => {
    getMock.mockRejectedValue(new Error('Netz weg'))
    const { container } = renderState()

    await waitFor(() => {
      expect(getMock).toHaveBeenCalled()
    })
    // Kein Fehlerkasten ueber einer funktionierenden Position, und auch keine
    // Behauptung, es gaebe keine Mengen.
    expect(container).toBeEmptyDOMElement()
  })

  it('zeigt nichts, solange kein Beleg benannt ist', () => {
    const { container } = render(
      <PositionAllocationState documentType="delivery_note" documentId="" />,
    )
    expect(getMock).not.toHaveBeenCalled()
    expect(container).toBeEmptyDOMElement()
  })
})
