/**
 * Tests für Auftrags-Factory-Funktionen in {@link ../../src/core/entities/order}.
 */
import {
  type CreateOrderInput,
  createOrder,
  withOrderStatus,
  cloneOrder,
} from '../../src/core/entities/order'

function sampleCreateInput(overrides: Partial<CreateOrderInput> = {}): CreateOrderInput {
  const documentDate = new Date('2024-01-10')
  return {
    customerNumber: 'CUST-001',
    debtorNumber: 'DEB-001',
    contactPerson: 'Max Mustermann',
    documentType: 'order',
    documentDate,
    currency: 'EUR',
    netAmount: 100,
    vatAmount: 19,
    totalAmount: 119,
    notes: 'n',
    items: [
      {
        articleNumber: 'ART-001',
        description: 'Demo',
        quantity: 1,
        unit: 'piece',
        unitPrice: 100,
        netPrice: 100,
      },
    ],
    ...overrides,
  }
}

describe('order entity factories', () => {
  describe('createOrder', () => {
    it('builds draft order', () => {
      const order = createOrder(sampleCreateInput({ status: 'draft' }))
      expect(order.customerNumber).toBe('CUST-001')
      expect(order.status).toBe('draft')
      expect(order.items).toHaveLength(1)
      expect(order.orderNumber).toMatch(/^ORD-/)
    })

    it('defaults status to draft', () => {
      const input = { ...sampleCreateInput() }
      delete input.status
      expect(createOrder(input).status).toBe('draft')
    })

    it('requires customerNumber', () => {
      expect(() => createOrder(sampleCreateInput({ customerNumber: '' }))).toThrow('customerNumber is required')
    })

    it('requires debtorNumber', () => {
      expect(() => createOrder(sampleCreateInput({ debtorNumber: ' ' }))).toThrow('debtorNumber is required')
    })
  })

  describe('withOrderStatus', () => {
    it('updates status and updatedAt', () => {
      const order = createOrder(sampleCreateInput())
      const next = withOrderStatus(order, 'confirmed')
      expect(next.status).toBe('confirmed')
      expect(next.updatedAt.getTime()).toBeGreaterThanOrEqual(order.updatedAt.getTime())
      expect(order.status).toBe('draft')
    })
  })

  describe('cloneOrder', () => {
    it('deep-clones items', () => {
      const order = createOrder(sampleCreateInput())
      const copy = cloneOrder(order)
      expect(copy).not.toBe(order)
      expect(copy.items[0]).not.toBe(order.items[0])
      expect(copy.items[0]?.articleNumber).toBe(order.items[0]?.articleNumber)
    })
  })
})
