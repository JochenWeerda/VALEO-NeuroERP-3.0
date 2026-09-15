import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { SourceProposalRenderer, type SourceProposalContext } from '@/components/mask-builder/renderers/SourceProposalRenderer'

/**
 * FSX-SOURCE-PROPOSALS — Anzeige der Kontrakt- und Fremdlagervorschlaege.
 *
 * Die fachlich heikelste Aussage dieser Flaeche ist nicht die Menge, sondern die
 * **Eigentumsart**: kundeneigene Ware wird bei der Auslagerung nicht nochmals
 * verkauft. Wer das uebersieht, stellt dem Kunden seine eigene Ware in Rechnung.
 *
 * Uebernommen von Codex (Pause), deren Slice-Abnahme Tests verlangt.
 */

const postMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { post: postMock },
}))

const context: SourceProposalContext = {
  party_id: 'p1',
  direction: 'outgoing',
  document_date: '2026-09-15',
  lines: [{ line_id: 'L1', article_id: 'a-weizen', article_number: '10001', quantity: 100, unit: 't' }],
}

function antwort(overrides: Record<string, unknown> = {}) {
  return {
    data: {
      notice: 'Vorschlag aus gebuchter Restmenge; keine Reservierung oder Buchung.',
      lines: [
        {
          line_id: 'L1',
          article_number: '10001',
          unit: 't',
          groups: [
            {
              kind: 'contract',
              uncovered_quantity: '40',
              proposals: [
                {
                  source_id: 'c1',
                  reference: 'K-2026-001',
                  quantity: '60',
                  unit: 't',
                  recorded_remaining: '60',
                  reason: 'Partner, Artikel, Kontraktseite und Zeitraum passen',
                  billing: 'goods',
                },
              ],
            },
            {
              kind: 'foreign_stock',
              uncovered_quantity: '0',
              proposals: [
                {
                  source_id: 's1',
                  reference: 'E-4711',
                  quantity: '40',
                  unit: 't',
                  recorded_remaining: '40',
                  owner_id: 'p1',
                  warehouse_id: 'L1',
                  charge: 'CH-1',
                  reason: 'Kundeneigentum, Artikel und Lagerbestand passen',
                  billing: 'services_only',
                },
              ],
            },
          ],
        },
      ],
      ...overrides,
    },
  }
}

describe('SourceProposalRenderer', () => {
  beforeEach(() => {
    postMock.mockReset()
    vi.useRealTimers()
  })

  it('zeigt ohne Kontext nichts an', () => {
    const { container } = render(<SourceProposalRenderer context={undefined} />)
    expect(container).toBeEmptyDOMElement()
    expect(postMock).not.toHaveBeenCalled()
  })

  it('fragt nicht an, solange Partner und Positionen fehlen', () => {
    render(<SourceProposalRenderer context={{ ...context, lines: [] }} />)
    expect(screen.getByText(/Partner, Artikel, Menge und Einheit erfassen/)).toBeInTheDocument()
    expect(postMock).not.toHaveBeenCalled()
  })

  it('zeigt Teilmengen je Quelle mit Referenz und Begruendung', async () => {
    postMock.mockResolvedValue(antwort())
    render(<SourceProposalRenderer context={context} />)

    expect(await screen.findByText('K-2026-001')).toBeInTheDocument()
    expect(screen.getByText('60 t')).toBeInTheDocument()
    expect(screen.getByText(/Kontraktseite und Zeitraum passen/)).toBeInTheDocument()
  })

  it('weist kundeneigene Ware als andere Eigentumsart aus, nicht als Warenverkauf', async () => {
    postMock.mockResolvedValue(antwort())
    render(<SourceProposalRenderer context={context} />)

    await screen.findByText('E-4711')
    // Die Ueberschrift trennt die Gruppe bereits fachlich.
    expect(screen.getByText(/Kundeneigene Ware/)).toBeInTheDocument()
    // Und die Zeile sagt ausdruecklich, dass keine Warenrechnung entsteht.
    expect(screen.getByText(/Keine Warenrechnung; Leistungen separat/)).toBeInTheDocument()
    expect(screen.getByText(/Eigentuemer p1/)).toBeInTheDocument()
  })

  it('benennt die ungedeckte Restmenge', async () => {
    postMock.mockResolvedValue(antwort())
    render(<SourceProposalRenderer context={context} />)

    expect(await screen.findByText(/Nicht gedeckt: 40 t/)).toBeInTheDocument()
  })

  it('sagt, dass nichts reserviert wurde', async () => {
    postMock.mockResolvedValue(antwort())
    render(<SourceProposalRenderer context={context} />)

    expect(await screen.findByText(/keine Reservierung oder Buchung/)).toBeInTheDocument()
  })

  it('meldet einen Abrufsfehler sichtbar, statt leer zu bleiben', async () => {
    postMock.mockRejectedValue(new Error('Netz weg'))
    render(<SourceProposalRenderer context={context} />)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/konnten nicht geprueft werden/)
  })

  it('zeigt eine leere Gruppe als "keine nachgewiesene Quelle", nicht als Luecke', async () => {
    postMock.mockResolvedValue(
      antwort({
        lines: [
          {
            line_id: 'L1',
            unit: 't',
            groups: [{ kind: 'contract', uncovered_quantity: '100', proposals: [] }],
          },
        ],
      }),
    )
    render(<SourceProposalRenderer context={context} />)

    expect(await screen.findByText(/Keine nachgewiesene passende Quelle/)).toBeInTheDocument()
  })

  it('fragt bei unveraendertem Kontext nicht erneut an', async () => {
    postMock.mockResolvedValue(antwort())
    const { rerender } = render(<SourceProposalRenderer context={context} />)
    await screen.findByText('K-2026-001')

    rerender(<SourceProposalRenderer context={{ ...context }} />)
    await waitFor(() => {
      expect(postMock).toHaveBeenCalledTimes(1)
    })
  })
})
