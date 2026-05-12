/**
 * Unit tests für {@link ../../src/core/entities/product.ProductEntity}.
 */
import {
  ProductEntity,
  CreateProductCommand,
  UpdateProductCommand,
  ProductCreatedEvent,
  ProductUpdatedEvent,
} from '../../src/core/entities/product'

const baseCreate = (): CreateProductCommand => ({
  name: 'Test Product',
  status: 'active',
  sku: 'SKU-TST-1',
  price: 9.99,
  category: 'TestCategory',
})

describe('ProductEntity', () => {
  const now = new Date('2025-01-01T00:00:00Z')

  describe('create', () => {
    it('should create a valid product entity', () => {
      const originalDate = global.Date
      global.Date = class extends Date {
        constructor(...args: unknown[]) {
          if (args.length === 0) {
            super(now)
          } else {
            super(...(args as ConstructorParameters<typeof Date>))
          }
        }

        static now() {
          return now.getTime()
        }
      } as typeof Date

      try {
        const entity = ProductEntity.create(baseCreate())
        expect(entity.name).toBe('Test Product')
        expect(entity.status).toBe('active')
        expect(entity.sku).toBe('SKU-TST-1')
        expect(entity.createdAt.getTime()).toBe(now.getTime())
        expect(entity.updatedAt.getTime()).toBe(now.getTime())
        expect(entity.isActive()).toBe(true)
      } finally {
        global.Date = originalDate
      }
    })

    it('should throw error for invalid name', () => {
      const command: CreateProductCommand = {
        ...baseCreate(),
        name: '',
      }
      expect(() => ProductEntity.create(command)).toThrow('Product name is required')
    })

    it('should throw error for whitespace-only name', () => {
      const command: CreateProductCommand = {
        ...baseCreate(),
        name: '   ',
      }
      expect(() => ProductEntity.create(command)).toThrow('Product name is required')
    })
  })

  describe('update', () => {
    let entity: ProductEntity

    beforeEach(() => {
      entity = ProductEntity.create({
        name: 'Original Product',
        status: 'active',
        sku: 'SKU-ORG',
        price: 12,
        category: 'Cat',
      })
    })

    it('should update entity properties', () => {
      const before = entity.updatedAt
      const updateCommand: UpdateProductCommand = {
        name: 'Updated Product',
        status: 'inactive',
      }
      const updatedEntity = entity.update(updateCommand)
      expect(updatedEntity).toBe(entity)
      expect(updatedEntity.name).toBe('Updated Product')
      expect(updatedEntity.status).toBe('inactive')
      expect(updatedEntity.updatedAt.getTime()).toBeGreaterThanOrEqual(before.getTime())
    })

    it('should partially update entity', () => {
      const updateCommand: UpdateProductCommand = {
        status: 'inactive',
      }
      const updatedEntity = entity.update(updateCommand)
      expect(updatedEntity.name).toBe('Original Product')
      expect(updatedEntity.status).toBe('inactive')
    })
  })

  describe('business methods', () => {
    it('should return correct active status', () => {
      const active = ProductEntity.create({ ...baseCreate(), status: 'active' })
      const inactive = ProductEntity.create({
        ...baseCreate(),
        sku: 'SKU-2',
        name: 'Inactive Product',
        status: 'inactive',
      })
      expect(active.isActive()).toBe(true)
      expect(inactive.isActive()).toBe(false)
    })
  })

  describe('domain events', () => {
    it('should create ProductCreatedEvent', () => {
      const entity = ProductEntity.create(baseCreate())
      const event = new ProductCreatedEvent(entity)
      expect(event.type).toBe('ProductCreated')
      expect(event.aggregateId).toBe(entity.id)
      expect(event.occurredOn).toBeInstanceOf(Date)
      expect(event.product).toBe(entity)
    })

    it('should create ProductUpdatedEvent', () => {
      const entity = ProductEntity.create(baseCreate())
      const changes = { status: 'inactive' }
      const event = new ProductUpdatedEvent(entity, changes)
      expect(event.type).toBe('ProductUpdated')
      expect(event.aggregateId).toBe(entity.id)
      expect(event.occurredOn).toBeInstanceOf(Date)
      expect(event.changes).toBe(changes)
    })
  })
})
