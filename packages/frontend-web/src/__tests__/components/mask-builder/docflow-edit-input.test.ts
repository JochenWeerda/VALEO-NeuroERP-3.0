import { describe, expect, it } from 'vitest'
import { docflowEditInput } from '@/components/mask-builder/runtime/docflow-edit-input'
import { prepareDocflowCommand, docflowCommandResult } from '@/components/mask-builder/runtime/docflow-command-adapter'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'

const action: ScreenActionDefinition = { key: 'bearbeiten', label: 'Beleg bearbeiten', method: 'PUT',
  commandEndpoint: '/api/v1/docflow/{entity_id}', enabledWhen: 'aktion_bearbeiten',
  commandBinding: { adapter: 'docflow.v1', command: 'update', preview: false } }
const document = { id: 'doc-1', doc_type: 'sales_offer', version: 7, status: 'draft',
  currency: 'EUR', document_date: '2026-10-17T12:00:00', source_ref: 'reference',
  items: Array.from({ length: 75 }, (_, i) => ({ id: `line-${i}`, article_number: `A${i}`, quantity: i,
    unit_price: 220, unit: 't', batch_id: 'batch-1', charge: 'charge-1', discount_percent: 2,
    tax_rate: 7, tax_code: '9', expense_account: '3400', source_line_id: null })) }
const opts = { screenId: 'beleg/sales-offer', entityId: 'doc-1', permissions: ['belege.bearbeiten'],
  entityData: { version: 7, aktion_bearbeiten: true, aktionen: [{ key: 'bearbeiten', erlaubt: true }] } }
const req = { actionKey: 'bearbeiten', entityId: 'doc-1', mode: 'execute' as const, expectedVersion: 7 }

describe('Canonical document edit input and transport', () => {
  it('uses all rows and preserves supported hidden metadata without mutating the DTO', () => {
    const values = docflowEditInput(action, document, 'doc-1', 7, 'sales_offer')
    const rows = values.items as Record<string, unknown>[]
    expect(rows).toHaveLength(75)
    expect(rows[74]).toMatchObject({ article_number: 'A74', batch_id: 'batch-1', charge: 'charge-1', tax_code: '9', expense_account: '3400' })
    expect(rows[0]).not.toHaveProperty('id')
    rows[0].quantity = 900
    expect(document.items[0].quantity).toBe(0)
  })
  it.each([{ id: 'foreign' }, { version: 8 }, { doc_type: 'purchase_invoice' }, { status: 'posted' }, { items: null },
    { items: [{ source_line_id: 'predecessor' }] }])('rejects mismatched or linked data %j', change => {
    expect(() => docflowEditInput(action, { ...document, ...change }, 'doc-1', 7, 'sales_offer')).toThrow()
  })
  it('sends the registered PUT contract with version and idempotency', () => {
    const prepared = prepareDocflowCommand(action, { ...req, payload: { items: [] } }, opts, 'stable-retry-key')
    expect(prepared).toEqual({ url: '/api/v1/docflow/doc-1', method: 'PUT',
      body: { items: [], expected_version: 7, idempotency_key: 'stable-retry-key' } })
  })
  it.each([{ method: 'POST' }, { commandEndpoint: '/api/v1/docflow/{entity_id}/post' }])('rejects transport drift %j', change => {
    expect(() => prepareDocflowCommand({ ...action, ...change } as ScreenActionDefinition, req, opts, 'stable-retry-key')).toThrow()
  })
  it('rejects forged actors, status changes, previews and agent writes', () => {
    for (const payload of [{ updated_by: 'forged' }, { status: 'posted' }]) {
      expect(() => prepareDocflowCommand(action, { ...req, payload }, opts, 'stable-retry-key')).toThrow()
    }
    expect(() => prepareDocflowCommand(action, { ...req, mode: 'dryRun' }, opts, 'stable-retry-key')).toThrow()
    expect(() => prepareDocflowCommand(action, req, { ...opts, isAgentCaller: true }, 'stable-retry-key')).toThrow()
  })
  it('requires a confirmed draft snapshot of exactly this document and next version', () => {
    const result = { ...document, version: 8 }
    expect(docflowCommandResult(action, req, opts, result).success).toBe(true)
    for (const change of [{ id: 'foreign' }, { version: 7 }, { status: 'posted' }, { items: null }]) {
      expect(docflowCommandResult(action, req, opts, { ...result, ...change }).success).toBe(false)
    }
  })
})
