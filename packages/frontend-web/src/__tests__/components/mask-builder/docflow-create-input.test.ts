import { describe, expect, it } from 'vitest'
import { prepareDocflowCreation } from '@/components/mask-builder/runtime/docflow-create-input'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const definition = { schemaVersion: 1, domain: 'sales', mode: 'detail', title: 'Angebot', id: 'beleg/sales-offer', documentVariant: { family: 'beleg', variantId: 'sales_offer', baseVersion: '1.2.0', variantVersion: '1.2.0', baseHash: 'a'.repeat(64), variantHash: 'b'.repeat(64), materializedHash: 'c'.repeat(64) },
  creationContext: { screen_id: 'beleg/sales-offer', definition_hash: 'a'.repeat(64) },
  creation: { adapter: 'docflow.create.v1', endpoint: '/api/v1/docflow/', fields: [
    { key: 'customer_id', label: 'Kunde', type: 'lookup' }, { key: 'doc_number', label: 'Bezeichnung', type: 'text' }, { key: 'items', label: 'Positionen', type: 'table' }] },
} as ScreenDefinition
const values = { customer_id: 'synthetic-customer', doc_number: 'SYNTHETIC', items: [{ article_number: 'SYNTHETIC', quantity: 2 }] }
describe('Bound document creation transport', () => {
  it('derives type, draft state, proof and key from the registered context, never caller overrides', () => {
    const result = prepareDocflowCreation(definition, { ...values, doc_type: 'purchase_invoice', status: 'posted', tenant_id: 'foreign', created_by: 'forged', idempotency_key: 'forged' }, 'stable-create-key')
    expect(result).toEqual({ ...values, doc_type: 'sales_offer', status: 'draft', screen_context: definition.creationContext, idempotency_key: 'stable-create-key' })
    expect(values.items[0].quantity).toBe(2)
  })
  it.each([{ creationContext: undefined }, { creationContext: { screen_id: 'foreign', definition_hash: 'a'.repeat(64) } },
    { creationContext: { screen_id: definition.id, definition_hash: 'invalid' } },
    { creation: { ...definition.creation, endpoint: '/unsafe' } }])('rejects incomplete or changed proof %j', change => {
    expect(() => prepareDocflowCreation({ ...definition, ...change } as ScreenDefinition, values, 'stable-create-key')).toThrow()
  })
  it('requires a selected partner and a valid repeat key', () => {
    expect(() => prepareDocflowCreation(definition, { ...values, customer_id: '' }, 'stable-create-key')).toThrow()
    expect(() => prepareDocflowCreation(definition, values, 'bad')).toThrow()
  })
})
