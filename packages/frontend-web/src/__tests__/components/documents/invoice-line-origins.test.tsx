import type React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

// Die Quelle ist verlinkt; der Router gehoert zur Maske, nicht zum Baustein.
vi.mock('@/app/routing/typed-router', () => ({
  Link: ({ to, children, ...rest }: { to: string; children?: React.ReactNode }) => (
    <a href={to} {...rest}>
      {children}
    </a>
  ),
}))
import {
  InvoiceLineOrigins,
  bewerteHerkunft,
} from '@/components/documents/InvoiceLineOrigins'
import type { InvoiceLineOrigin } from '@/lib/api/sales-invoices'

/**
 * FSX-RECHNUNGSMASKE — die Herkunft der berechneten Menge.
 *
 * Geprueft wird die Aussage, nicht das Aussehen: Eine Rechnungsposition, deren
 * Menge nur teilweise aus Zuordnungen stammt, muss sich von einer belegten
 * unterscheiden — und beide von einer ganz ohne Herkunft.
 */

function herkunft(overrides: Partial<InvoiceLineOrigin> = {}): InvoiceLineOrigin {
  return {
    source_document_type: 'delivery_note',
    source_document_id: 'LS-1',
    source_line_id: '1',
    quantity: '100',
    unit: 'dt',
    reason: 'rechnung_aus_lieferschein',
    ...overrides,
  }
}

describe('bewerteHerkunft', () => {
  it('nennt eine gedeckte Menge belegt', () => {
    expect(bewerteHerkunft('100', 'dt', [herkunft()])).toEqual({ art: 'belegt', quellen: 1 })
  })

  it('addiert mehrere Quellen derselben Einheit', () => {
    const deckung = bewerteHerkunft('100', 'dt', [
      herkunft({ quantity: '60' }),
      herkunft({ source_document_id: 'LS-2', quantity: '40' }),
    ])
    expect(deckung).toEqual({ art: 'belegt', quellen: 2 })
  })

  it('benennt die Luecke, wenn die Quellen die Menge nicht decken', () => {
    const deckung = bewerteHerkunft('100', 'dt', [herkunft({ quantity: '60' })])
    expect(deckung).toEqual({ art: 'teilweise', quellen: 1, fehlend: '40' })
  })

  it('haelt einen Rundungsrest nicht fuer eine Luecke', () => {
    expect(bewerteHerkunft('100', 'dt', [herkunft({ quantity: '99.9999' })])).toEqual({
      art: 'belegt',
      quellen: 1,
    })
  })

  it('rechnet Einheiten nicht um, sondern sagt es', () => {
    // 100 kg und 1 dt sind dasselbe — aber das hier zu wissen hiesse, eine
    // Umrechnung in der Anzeige zu erfinden.
    const deckung = bewerteHerkunft('1', 'dt', [herkunft({ quantity: '100', unit: 'kg' })])
    expect(deckung).toEqual({ art: 'unvergleichbar', quellen: 1 })
  })

  it('unterscheidet "keine Herkunft" von allem anderen', () => {
    expect(bewerteHerkunft('100', 'dt', [])).toEqual({ art: 'ohne' })
  })
})

describe('InvoiceLineOrigins', () => {
  it('zeigt die Quellen erst nach dem Aufklappen', async () => {
    render(<InvoiceLineOrigins lineNo="1" quantity="100" unit="dt" origins={[herkunft()]} />)

    expect(screen.getByTestId('invoice-origin-summary-1')).toHaveTextContent('Herkunft: 1 Quelle')
    expect(screen.queryByText('LS-1')).toBeNull()

    await userEvent.click(screen.getByRole('button'))
    expect(screen.getByText('LS-1')).toBeInTheDocument()
    expect(screen.getByText('Lieferschein')).toBeInTheDocument()
    expect(screen.getByText('Position 1')).toBeInTheDocument()
    expect(screen.getByText('100 dt')).toBeInTheDocument()
  })

  it('macht die ungedeckte Menge in der Zusammenfassung sichtbar', () => {
    render(
      <InvoiceLineOrigins
        lineNo="2"
        quantity="100"
        unit="dt"
        origins={[herkunft({ quantity: '60' })]}
      />,
    )
    expect(screen.getByTestId('invoice-origin-summary-2')).toHaveTextContent(
      '40 dt ohne Zuordnung',
    )
  })

  it('sagt bei fehlender Zuordnung nichts Beruhigendes', () => {
    render(<InvoiceLineOrigins lineNo="3" quantity="100" unit="dt" origins={[]} />)
    expect(screen.getByTestId('invoice-origin-summary-3')).toHaveTextContent(
      'Keine Herkunft hinterlegt',
    )
    // Nichts aufzuklappen: Der Knopf bleibt gesperrt statt eine leere Liste zu zeigen.
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('verschweigt eine unbekannte Belegart nicht', async () => {
    render(
      <InvoiceLineOrigins
        lineNo="4"
        quantity="10"
        unit="dt"
        origins={[herkunft({ source_document_type: 'weighing_ticket', quantity: '10' })]}
      />,
    )
    await userEvent.click(screen.getByRole('button'))
    expect(screen.getByText('Wiegeschein')).toBeInTheDocument()
  })
})
