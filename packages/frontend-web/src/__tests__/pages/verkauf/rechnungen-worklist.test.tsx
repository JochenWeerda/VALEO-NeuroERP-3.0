import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'

/**
 * FSX-RECHNUNGSMASKE-MERIDIAN — die Faktura-Worklist.
 *
 * Geprueft wird das, was die Seite beitraegt, und nur das: Sie holt die
 * ScreenDefinition, reicht den Plan an den Renderer und exportiert **die
 * sichtbaren Zeilen**. Die Maske selbst gehoert dem Builder und wird hier
 * nicht nachgestellt.
 */

const useScreenDefinitionMock = vi.hoisted(() => vi.fn())
const useUniversalMaskRuntimeMock = vi.hoisted(() => vi.fn())
const handleExportMock = vi.hoisted(() => vi.fn())
const useListActionsMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: useScreenDefinitionMock }))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: useUniversalMaskRuntimeMock,
  UniversalMaskRenderer: ({ onAction }: { onAction?: (_key: string) => void }) => (
    <button type="button" onClick={() => onAction?.('export')}>
      Liste exportieren
    </button>
  ),
}))
vi.mock('@/hooks/useListActions', () => ({ useListActions: useListActionsMock }))

import RechnungenWorklistPage from '@/pages/verkauf/rechnungen-worklist'

function runtime(overrides: Record<string, unknown> = {}) {
  return {
    plan: { shell: {} },
    entityData: undefined,
    entityError: null,
    tableRows: {
      list: [
        {
          id: 'RE-ID',
          invoice_number: 'RE-0001',
          customer_id: 'K-100',
          invoice_date: '2026-09-15',
          due_date: null,
          line_count: 2,
          net_amount: '2500',
          gross_amount: '2675',
          status: 'entwurf',
        },
      ],
    },
    tableQueryStates: {},
    tableTotals: { list: 1 },
    messages: [],
    setTableQuery: vi.fn(),
    updateUserOverlay: vi.fn(),
    resetUserOverlay: vi.fn(),
    lookupBindings: {},
    refetch: vi.fn(),
    ...overrides,
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  useScreenDefinitionMock.mockReturnValue({ data: { id: 'sales/invoices' }, isLoading: false, error: null })
  useUniversalMaskRuntimeMock.mockReturnValue(runtime())
  useListActionsMock.mockReturnValue({ handleExport: handleExportMock, handlePrint: vi.fn() })
})

describe('RechnungenWorklistPage', () => {
  it('rendert die Maske aus der ScreenDefinition sales/invoices', () => {
    render(<RechnungenWorklistPage />)
    expect(useScreenDefinitionMock).toHaveBeenCalledWith('sales/invoices')
    expect(screen.getByTestId('sales-invoices-worklist')).toBeInTheDocument()
  })

  it('exportiert die sichtbaren Zeilen, nicht den ganzen Bestand', async () => {
    render(<RechnungenWorklistPage />)
    // Was gefiltert wurde, soll gefiltert in der Datei landen: exportiert wird
    // genau das, was der Renderer gerade zeigt.
    const argumente = useListActionsMock.mock.calls[0][0] as { data: Record<string, string>[] }
    expect(argumente.data).toEqual([
      {
        Rechnungsnummer: 'RE-0001',
        Kunde: 'K-100',
        Rechnungsdatum: '2026-09-15',
        'Fällig am': '',
        Positionen: '2',
        Netto: '2500',
        Brutto: '2675',
        Status: 'entwurf',
      },
    ])

    await userEvent.click(screen.getByRole('button', { name: 'Liste exportieren' }))
    expect(handleExportMock).toHaveBeenCalledTimes(1)
  })

  it('macht ein fehlendes Faelligkeitsdatum nicht zu einem Datum', () => {
    render(<RechnungenWorklistPage />)
    const argumente = useListActionsMock.mock.calls[0][0] as { data: Record<string, string>[] }
    expect(argumente.data[0]['Fällig am']).toBe('')
  })

  it('sagt es, wenn die Rechnungen nicht geladen werden konnten', () => {
    useUniversalMaskRuntimeMock.mockReturnValue(runtime({ entityError: new Error('kaputt') }))
    render(<RechnungenWorklistPage />)
    expect(screen.getByRole('alert')).toHaveTextContent('Rechnungen konnten nicht geladen werden.')
  })

  it('behauptet nichts, solange der Plan fehlt', () => {
    useUniversalMaskRuntimeMock.mockReturnValue(runtime({ plan: null }))
    render(<RechnungenWorklistPage />)
    expect(screen.getByText('Rechnungsliste wird geladen…')).toBeInTheDocument()
    expect(screen.queryByTestId('sales-invoices-worklist')).toBeNull()
  })
})
