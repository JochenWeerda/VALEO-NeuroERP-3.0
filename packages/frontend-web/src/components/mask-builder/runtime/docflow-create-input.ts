import type { ScreenDefinition } from '../schema'

export function prepareDocflowCreation(screen: ScreenDefinition, values: Record<string, unknown>, key: string): Record<string, unknown> {
  const creation = screen.creation
  const kind = screen.documentVariant?.variantId
  const context = screen.creationContext
  if (creation?.adapter !== 'docflow.create.v1' || creation.endpoint !== '/api/v1/docflow/' ||
    screen.documentVariant?.family !== 'beleg' || !kind || context?.screen_id !== screen.id ||
    !/^[a-f0-9]{64}$/.test(context.definition_hash) || key.length < 8 || key.length > 120) {
    throw new Error('Gepruefter Erstellungskontext fehlt. Bitte die Maske neu laden.')
  }
  const supplier = kind.startsWith('purchase_') || kind === 'goods_receipt'
  const partnerKey = supplier ? 'supplier_id' : 'customer_id'
  if (typeof values[partnerKey] !== 'string' || !values[partnerKey]) throw new Error('Bitte einen Partner auswaehlen.')
  const allowed = new Set((creation.fields ?? []).filter(field => !field.readOnly).map(field => field.key))
  const payload = Object.fromEntries(Object.entries(values).filter(([field, value]) => allowed.has(field) && value !== undefined && value !== ''))
  return { ...payload, doc_type: kind, status: 'draft', screen_context: context, idempotency_key: key }
}
