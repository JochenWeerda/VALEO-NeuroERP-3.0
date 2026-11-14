import { describe, expect, it } from 'vitest'
import { docflowConversionOptionsUrl, docflowConvertInput, docflowConversionQuantities } from '@/components/mask-builder/runtime/docflow-convert-input'
import { prepareDocflowCommand } from '@/components/mask-builder/runtime/docflow-command-adapter'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'

const action: ScreenActionDefinition = { key: 'umwandeln:sales_delivery', label: 'Lieferschein erstellen',
  method: 'POST', commandEndpoint: '/api/v1/docflow/{entity_id}/convert',
  inputFields: [{ key: 'quantities_by_source_item_id', label: 'Positionen', type: 'table' }],
  commandBinding: { adapter: 'docflow.v1', command: 'convert', preview: true, defaults: { target_doc_type: 'sales_delivery' } } }
const response = () => ({ source_doc_id: 'doc-1', source_doc_type: 'sales_order', target_doc_type: 'sales_delivery', version: 7,
  items: [{ source_item_id: 'line-1', line_number: 1, article_number: 'FUTTER', description: 'Futter', unit: 'kg', quantity: 10, remaining_quantity: 6 }] })
const seed = () => docflowConvertInput(action, response(), 'doc-1', 7, 'sales_order')

describe('Studio conversion position selection', () => {
  it('fetches the target-specific, price-free selection and starts with no quantities chosen', () => {
    expect(docflowConversionOptionsUrl(action, 'doc/1')).toBe('/api/v1/docflow/doc%2F1/conversion-options?target_doc_type=sales_delivery')
    expect(seed()).toEqual({ quantities_by_source_item_id: [{ source_item_id: 'line-1', line_number: 1,
      article_number: 'FUTTER', description: 'Futter', unit: 'kg', remaining_quantity: 6, quantity: 0 }] })
  })
  it.each([{ version: 8 }, { source_doc_id: 'foreign' }, { target_doc_type: 'sales_invoice' }, { source_doc_type: 'purchase_order' },
    { items: [] }, { items: [...response().items, ...response().items] }])('rejects an incomplete or stale selection %j', change => {
    expect(() => docflowConvertInput(action, { ...response(), ...change }, 'doc-1', 7, 'sales_order')).toThrow()
  })
  it('maps the chosen amount exactly in preview and execute, with the same source version', () => {
    const rows = (seed().quantities_by_source_item_id as Record<string, unknown>[]).map(row => ({ ...row, quantity: 4 }))
    for (const mode of ['dryRun', 'execute'] as const) {
      const result = prepareDocflowCommand(action, { actionKey: action.key, mode, payload: { quantities_by_source_item_id: rows } },
        { screenId: 'beleg/sales-order', entityId: 'doc-1', permissions: [], entityData: { version: 7, aktionen: [{ key: action.key, erlaubt: true }] } }, 'same-intent-key')
      expect(result.body).toEqual({ quantities_by_source_item_id: { 'line-1': 4 }, expected_version: 7,
        idempotency_key: 'same-intent-key', target_doc_type: 'sales_delivery', dry_run: mode === 'dryRun' })
    }
  })
  it.each([undefined, {}, [], { 'line-1': 0 }, { 'line-1': -1 }, { 'line-1': NaN }, { 'line-1': Infinity },
    [{ source_item_id: 'line-1', remaining_quantity: 6, quantity: 7 }],
    [{ source_item_id: 'line-1', remaining_quantity: 6, quantity: null }],
    [{ source_item_id: 'line-1', remaining_quantity: 6, quantity: 1 }, { source_item_id: 'line-1', remaining_quantity: 6, quantity: 1 }],
  ])('never converts missing, zero-only, invalid, duplicate or excessive quantities to full remainder: %j', value => {
    expect(() => docflowConversionQuantities(value)).toThrow()
  })
  it('also accepts the canonical CLI/API dictionary without row metadata', () => {
    expect(docflowConversionQuantities({ 'line-1': 4, 'line-2': 0 })).toEqual({ 'line-1': 4, 'line-2': 0 })
  })
})
