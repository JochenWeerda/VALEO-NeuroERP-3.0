/** Real HTTP evidence for o2c-001/002. Creates its own tenant-owned customer through the canonical API.
 * Invoice, payment, dunning and external export remain unimplemented matrix gaps;
 * the removed legacy smoke accepted failures and provided no evidence for them.
 */
import { randomUUID } from 'node:crypto'
import { test, expect, request, type APIRequestContext } from '@playwright/test'
import { E2E_MANDANT, holeTokens } from '../../helpers/anmeldung'

const ROOT = '/api/v1/docflow'
const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000'

type Header = {
  id: string; tenant_id: string; doc_type: string; doc_number: string; status: string
  customer_id: string; source_ref: string | null; version: number
  total_net: number; total_tax: number; total_gross: number
  items: Array<{ id: string; source_line_id: string | null; article_number: string
    quantity: number; unit_price: number; line_total_net: number }>
}
type Options = { source_doc_id: string; source_doc_type: string; target_doc_type: string
  version: number; items: Array<{ source_item_id: string; quantity: number; remaining_quantity: number }> }

// Each request uses a fresh client: readback cannot come from an earlier response/cache.
async function http<T>(token: string, method: 'get' | 'post', path: string,
  status: number, data?: unknown, tenant = E2E_MANDANT): Promise<T> {
  const client: APIRequestContext = await request.newContext({ baseURL: BASE,
    extraHTTPHeaders: { ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Tenant-ID': tenant, 'Content-Type': 'application/json' } })
  try {
    const response = await client[method](path, { data, maxRedirects: 0 })
    // Do not attach response bodies or authentication data to failure messages.
    expect(response.status(), `${method.toUpperCase()} ${path}: expected ${status}`).toBe(status)
    return await response.json() as T
  } finally { await client.dispose() }
}
async function login(role: 'POWER' | 'READ'): Promise<string> {
  const user = process.env[`VALEO_USER_${role}`] ?? ''
  const password = process.env[`VALEO_PASS_${role}`] ?? ''
  expect(Boolean(user && password), `Required VALEO_USER_${role}/VALEO_PASS_${role} missing`).toBe(true)
  return (await holeTokens(user, password)).access
}
const read = (token: string, id: string) => http<Header>(token, 'get', `${ROOT}/${id}`, 200)
const options = (token: string, id: string) => http<Options>(token, 'get',
  `${ROOT}/${id}/conversion-options?target_doc_type=sales_delivery`, 200)

async function createOrder(token: string) {
  const run = randomUUID()
  const definition = await http<{ creationContext: { screen_id: string; definition_hash: string } }>(
    token, 'get', '/api/v1/masks/beleg/sales-order/screen-definition', 200)
  expect(definition.creationContext?.screen_id).toBe('beleg/sales-order')
  expect(definition.creationContext?.definition_hash).toMatch(/^[a-f0-9]{64}$/)
  // Customer creation always persists a local tenant anchor, including remote crm-core success.
  // Prove both HTTP readback and local partner selection; never assume shared external storage.
  const customerPayload = { customer_number: `O2C-${run}`, company_name: `O2C HTTP ${run}`,
    country: 'DE', is_active: true }
  type Customer = { id: string; tenant_id: string; customer_number: string; company_name: string }
  const customer = await http<Customer>(token, 'post', '/api/v1/crm/customers/', 201, customerPayload)
  expect(customer.id).toMatch(/^[0-9a-f-]{36}$/i)
  const customerReadback = await http<Customer>(token, 'get', `/api/v1/crm/customers/${customer.id}`, 200)
  expect(customerReadback).toMatchObject({ id: customer.id, tenant_id: E2E_MANDANT,
    customer_number: customerPayload.customer_number, company_name: customerPayload.company_name })
  const partners = await http<{ items: Array<{ value: string }> }>(token, 'get',
    `/api/v1/belege/sales_order/partner-auswahl?q=${encodeURIComponent(customerPayload.customer_number)}&limit=2`, 200)
  expect(partners.items, 'Own customer must be selectable from the local authenticated tenant').toHaveLength(1)
  expect(partners.items[0].value).toBe(customer.id)
  const payload = {
    doc_type: 'sales_order', doc_number: `O2C-HTTP-${run}`, status: 'draft',
    idempotency_key: `create-${run}`, customer_id: partners.items[0].value,
    currency: 'EUR', screen_context: definition.creationContext,
    items: [
      { article_number: `O2C-A-${run}`, quantity: 10, unit: 'Stk', unit_price: 20, tax_rate: 0 },
      { article_number: `O2C-B-${run}`, quantity: 3, unit: 'Stk', unit_price: 7, tax_rate: 0 },
    ],
  }
  const created = await http<Header>(token, 'post', `${ROOT}/`, 200, payload)
  expect(created.id).toMatch(/^[0-9a-f-]{36}$/i)
  const saved = await read(token, created.id)
  expect(saved).toMatchObject({ id: created.id, tenant_id: E2E_MANDANT, doc_type: 'sales_order',
    doc_number: payload.doc_number, customer_id: payload.customer_id, status: 'draft',
    total_net: 221, total_tax: 0, total_gross: 221, version: 1 })
  expect(saved.items).toHaveLength(2)
  expect(saved.items.map(i => [i.article_number, i.quantity, i.unit_price])).toEqual(
    payload.items.map(i => [i.article_number, i.quantity, i.unit_price]))
  return { saved, payload, run }
}

test('o2c-001 @critical — signed sales role creates and reads a real tenant order', async () => {
  await createOrder(await login('POWER'))
})

test('o2c-002 @critical — partial delivery persists, replay and rejected writes preserve quantities', async () => {
  const power = await login('POWER')
  const readonly = await login('READ')
  const { saved, payload, run } = await createOrder(power)
  expect((await read(readonly, saved.id)).id).toBe(saved.id)
  const initial = await options(power, saved.id)
  expect(initial).toMatchObject({ source_doc_id: saved.id, source_doc_type: 'sales_order',
    target_doc_type: 'sales_delivery', version: saved.version })
  expect(initial.items).toHaveLength(2)
  const [first, omitted] = saved.items
  expect(initial.items).toEqual(expect.arrayContaining([
    expect.objectContaining({ source_item_id: first.id, quantity: 10, remaining_quantity: 10 }),
    expect.objectContaining({ source_item_id: omitted.id, quantity: 3, remaining_quantity: 3 }),
  ]))
  const command = { target_doc_type: 'sales_delivery', idempotency_key: `convert-${run}`,
    expected_version: initial.version, quantities_by_source_item_id: { [first.id]: 4 } }
  // Auth, role and tenant rejection use valid inputs, so validation cannot mask a missing guard.
  await http('', 'post', `${ROOT}/`, 401, { ...payload, idempotency_key: `noauth-${run}` })
  await http(readonly, 'post', `${ROOT}/`, 403, { ...payload, idempotency_key: `readonly-${run}` })
  await http('', 'post', `${ROOT}/${saved.id}/convert`, 401, command)
  await http(readonly, 'post', `${ROOT}/${saved.id}/convert`, 403, command)
  const otherTenant = randomUUID()
  await http(power, 'post', `${ROOT}/${saved.id}/convert`, 403, command, otherTenant)
  await http(power, 'post', `${ROOT}/${saved.id}/convert?tenant_id=${otherTenant}`, 403, command)
  expect(await options(power, saved.id)).toEqual(initial)
  expect(await read(power, saved.id)).toEqual(saved)

  const result = await http<{ command: string; status: string; target_doc_id: string;
    source_doc_id: string; idempotent_hit: boolean }>(power, 'post', `${ROOT}/${saved.id}/convert`, 200, command)
  expect(result).toMatchObject({ command: 'convert', status: 'ok', source_doc_id: saved.id, idempotent_hit: false })
  expect(result.target_doc_id).toMatch(/^[0-9a-f-]{36}$/i)
  expect(result.target_doc_id).not.toBe(saved.id)
  const delivery = await read(power, result.target_doc_id)
  expect(delivery).toMatchObject({ doc_type: 'sales_delivery', status: 'open', tenant_id: E2E_MANDANT,
    customer_id: saved.customer_id, source_ref: saved.id, total_net: 80, total_tax: 0, total_gross: 80 })
  expect(delivery.items).toHaveLength(1)
  expect(delivery.items[0]).toMatchObject({ source_line_id: first.id, article_number: first.article_number,
    quantity: 4, unit_price: 20, line_total_net: 80 })
  const remaining = await options(power, saved.id)
  expect(remaining.version).toBe(initial.version + 1)
  expect(remaining.items).toHaveLength(2)
  expect(remaining.items).toEqual(expect.arrayContaining([
    expect.objectContaining({ source_item_id: first.id, remaining_quantity: 6 }),
    expect.objectContaining({ source_item_id: omitted.id, remaining_quantity: 3 }),
  ]))
  const sourceAfter = await read(power, saved.id)
  expect(sourceAfter.items).toEqual(saved.items)
  const replay = await http<typeof result>(power, 'post', `${ROOT}/${saved.id}/convert`, 200, command)
  expect(replay).toMatchObject({ ...result, idempotent_hit: true })
  await http(power, 'post', `${ROOT}/${saved.id}/convert`, 409,
    { ...command, idempotency_key: `stale-${run}`, quantities_by_source_item_id: { [first.id]: 1 } })
  await http(power, 'post', `${ROOT}/${saved.id}/convert`, 400,
    { ...command, idempotency_key: `overqty-${run}`, expected_version: remaining.version,
      quantities_by_source_item_id: { [first.id]: 7 } })
  expect(await options(power, saved.id)).toEqual(remaining)
  expect(await read(power, saved.id)).toEqual(sourceAfter)
  expect(await read(power, delivery.id)).toEqual(delivery)
  // HTTP commits are real. Retain the uniquely numbered own customers and documents as evidence;
  // no database reset or unsafe broad cleanup. Foreign-token isolation needs tenant B.
})
