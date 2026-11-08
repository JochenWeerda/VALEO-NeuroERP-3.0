import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { StudioVariantPresentation } from '@/features/screen-studio/StudioVariantPresentation'
import { presentationEntries, renamePresentation } from '@/features/screen-studio/studio-presentation'

function fixture(): ScreenDefinition {
  return {
    schemaVersion: 1, id: 'tenant/invoice', domain: 'sales', mode: 'detail', title: 'Rechnung',
    documentVariant: { family: 'beleg', baseVersion: '1.0.0', baseHash: 'a', variantId: 'sales_invoice',
      variantVersion: '1.0.0', variantHash: 'b', materializedHash: 'c' },
    fields: [{ key: 'partner_nummer', label: 'Kunden-Nr.', type: 'text', readOnly: true }],
    tabs: [{ key: 'positionen', label: 'Positionen', tables: [{ key: 'positionen', label: 'Artikel',
      dataSourceKey: 'positionen', columns: [{ key: 'menge', label: 'Menge', numeric: true, renderKind: 'number' }],
    }] }],
    dataSources: [{ key: 'positionen', endpoint: '/api/v1/belege/sales_invoice/{entity_id}/positionen' }],
    actions: [{ key: 'post', label: 'Buchen', permission: 'belege.post', commandEndpoint: '/api/v1/docflow/post',
      forbiddenForAgents: true, dangerLevel: 'critical', requiresConfirmation: true }],
  }
}

describe('Belegvarianten ohne technische Feldnamen gestalten', () => {
  it('lists existing header, tab, table and column labels', () => {
    expect(presentationEntries(fixture()).map(item => item.label)).toEqual(['Kunden-Nr.', 'Positionen', 'Artikel', 'Menge'])
  })
  it('renames exactly the selected nested label and preserves all contracts and origin', () => {
    const source = fixture()
    const snapshot = JSON.stringify(source)
    const next = renamePresentation(source, 'tabs.0.tables.0.columns.0', 'Liefermenge')
    expect(next.tabs?.[0].tables?.[0].columns[0]).toEqual({ key: 'menge', label: 'Liefermenge', numeric: true, renderKind: 'number' })
    expect(next.documentVariant).toBe(source.documentVariant)
    expect(next.actions).toBe(source.actions)
    expect(next.dataSources).toBe(source.dataSources)
    expect(next.fields).toBe(source.fields)
    expect(JSON.stringify(source)).toBe(snapshot)
  })
  it.each(['actions.0', 'documentVariant', 'tabs.4', '__proto__', 'constructor.prototype'])('rejects arbitrary property path %s', id => {
    const source = fixture()
    expect(renamePresentation(source, id, 'Changed')).toBe(source)
  })
  it.each(['', '   ', 'x'.repeat(161)])('rejects empty or excessive labels', label => {
    const source = fixture()
    expect(renamePresentation(source, 'fields.0', label)).toBe(source)
  })
  it('edits visible labels without presenting internal keys or transport controls', () => {
    const onChange = vi.fn()
    render(<StudioVariantPresentation definition={fixture()} disabled={false} onChange={onChange} />)
    const input = screen.getByLabelText('Kopf · Kunden-Nr.')
    fireEvent.change(input, { target: { value: 'Betriebsnummer' } })
    fireEvent.blur(input)
    expect(onChange).toHaveBeenCalledOnce()
    expect(onChange.mock.calls[0][0].fields[0]).toEqual({ key: 'partner_nummer', label: 'Betriebsnummer', type: 'text', readOnly: true })
    expect(screen.queryByText('partner_nummer')).not.toBeInTheDocument()
  })
  it('disables edits when the designer is not authorized', () => {
    render(<StudioVariantPresentation definition={fixture()} disabled onChange={vi.fn()} />)
    expect(screen.getByLabelText('Kopf · Kunden-Nr.')).toBeDisabled()
  })
  it('does not render a variant editor for an unrelated mask', () => {
    const definition = fixture(); delete definition.documentVariant
    const { container } = render(<StudioVariantPresentation definition={definition} disabled={false} onChange={vi.fn()} />)
    expect(container).toBeEmptyDOMElement()
  })
})
