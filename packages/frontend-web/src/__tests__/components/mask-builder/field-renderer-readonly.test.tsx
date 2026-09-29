import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FieldRenderer, formatReadOnlyValue } from '@/components/mask-builder/renderers/FieldRenderer'
import { formatCellValue } from '@/components/mask-builder/renderers/FastTableRenderer'
import { statusLabel } from '@/components/mask-builder/renderers/status-labels'

describe('Read-only field display', () => {
  it('formats amounts, numbers, percentages and dates the German way', () => {
    expect(formatReadOnlyValue('currency', 19315)).toMatch(/^19\.315,00\s€$/)
    expect(formatReadOnlyValue('currency', '1817.65')).toMatch(/^1\.817,65\s€$/)
    expect(formatReadOnlyValue('number', 1234.5)).toBe('1.234,5')
    expect(formatReadOnlyValue('percentage', 7)).toBe('7 %')
    expect(formatReadOnlyValue('date', '2026-09-15')).toBe('15.09.2026')
    expect(formatReadOnlyValue('date', '2026-09-15T00:00:00Z')).toBe('15.09.2026')
    expect(formatReadOnlyValue('boolean', false)).toBe('Nein')
    expect(formatReadOnlyValue('boolean', true)).toBe('Ja')
  })

  it('keeps empty and unreadable values instead of inventing numbers', () => {
    expect(formatReadOnlyValue('currency', null)).toBe('')
    expect(formatReadOnlyValue('date', undefined)).toBe('')
    expect(formatReadOnlyValue('currency', 'offen')).toBe('offen')
    expect(formatReadOnlyValue('date', 'Ende Q3')).toBe('Ende Q3')
    expect(formatReadOnlyValue('text', 'RE-1001')).toBe('RE-1001')
  })

  it('shows a read-only amount formatted and an editable amount as the raw value', () => {
    const { rerender } = render(
      <FieldRenderer field={{ key: 'net_amount', label: 'Netto', type: 'currency', readOnly: true }} value={19315} />,
    )
    expect((screen.getByLabelText('Netto') as HTMLInputElement).value).toMatch(/^19\.315,00\s€$/)

    rerender(
      <FieldRenderer
        field={{ key: 'net_amount', label: 'Netto', type: 'currency' }}
        value={19315}
        onChange={() => undefined}
        voiceEnabled={false}
      />,
    )
    expect(screen.getByLabelText('Netto')).toHaveValue('19315')
  })

  it('names a read-only status instead of showing its key', () => {
    const { rerender } = render(
      <FieldRenderer field={{ key: 'status', label: 'Status', type: 'text', readOnly: true }} value="in_delivery" />,
    )
    expect(screen.getByLabelText('Status')).toHaveValue('In Lieferung')

    rerender(<FieldRenderer field={{ key: 'status', label: 'Status', type: 'text', readOnly: true }} value="entwurf" />)
    expect(screen.getByLabelText('Status')).toHaveValue('Entwurf')

    rerender(<FieldRenderer field={{ key: 'status', label: 'Status', type: 'text', readOnly: true }} value="Sonderfreigabe" />)
    expect(screen.getByLabelText('Status')).toHaveValue('Sonderfreigabe')
  })

  it('names a status chip in a table cell', () => {
    render(<>{formatCellValue('cancelled', 'status')}</>)
    expect(screen.getByText('Storniert')).toBeInTheDocument()
  })

  it('reads status keys regardless of case and separator', () => {
    expect(statusLabel('in-bearbeitung')).toBe('In Bearbeitung')
    expect(statusLabel('PENDING_APPROVAL')).toBe('Genehmigung ausstehend')
    expect(statusLabel(' partially allocated ')).toBe('Teilweise zugeordnet')
    expect(statusLabel('In Pruefung beim Amt')).toBe('In Pruefung beim Amt')
  })

  it('does not show a browser date placeholder for an empty read-only date', () => {
    render(<FieldRenderer field={{ key: 'due_date', label: 'Faellig', type: 'date', readOnly: true }} value={null} />)
    const input = screen.getByLabelText('Faellig')
    expect(input).toHaveAttribute('type', 'text')
    expect(input).toHaveValue('')
  })
})
