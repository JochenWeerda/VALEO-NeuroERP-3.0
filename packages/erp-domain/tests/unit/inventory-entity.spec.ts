/**
 * Unit tests für {@link ../../src/core/entities/inventory.InventoryEntity}.
 */
import {
  InventoryEntity,
  InventoryCreatedEvent,
  InventoryUpdatedEvent,
  CreateInventoryCommand,
  UpdateInventoryCommand,
} from '../../src/core/entities/inventory'

const fixedLastUpdated = (): Date => new Date('2025-01-01T00:00:00Z')

function baseCreate(overrides: Partial<CreateInventoryCommand> = {}): CreateInventoryCommand {
  return {
    name: 'Test Inventory',
    status: 'active',
    productId: 'prod-1',
    quantity: 10,
    reservedQuantity: 0,
    availableQuantity: 10,
    reorderLevel: 2,
    reorderQuantity: 5,
    lastUpdated: fixedLastUpdated(),
    ...overrides,
  }
}

describe('InventoryEntity', () => {
  const now = new Date('2026-05-07T12:00:00Z')

  describe('create', () => {
    it('should create a valid inventory entity', () => {
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
        const entity = InventoryEntity.create(baseCreate())
        expect(entity.name).toBe('Test Inventory')
        expect(entity.status).toBe('active')
        expect(entity.productId).toBe('prod-1')
        expect(entity.quantity).toBe(10)
        expect(entity.createdAt.getTime()).toBe(now.getTime())
        expect(entity.updatedAt.getTime()).toBe(now.getTime())
        expect(entity.isActive()).toBe(true)
      } finally {
        global.Date = originalDate
      }
    })

    it('should throw for empty name', () => {
      expect(() => InventoryEntity.create(baseCreate({ name: '' }))).toThrow('Inventory name is required')
    })

    it('should throw for whitespace-only name', () => {
      expect(() => InventoryEntity.create(baseCreate({ name: '   ' }))).toThrow('Inventory name is required')
    })
  })

  describe('update', () => {
    let entity: InventoryEntity

    beforeEach(() => {
      entity = InventoryEntity.create(baseCreate({ name: 'Original Inventory', status: 'active' }))
    })

    it('should update mutable properties', () => {
      const prevUpdated = entity.updatedAt
      const updated = entity.update({
        name: 'Updated Inventory',
        status: 'inactive',
      })
      expect(updated).toBe(entity)
      expect(entity.name).toBe('Updated Inventory')
      expect(entity.status).toBe('inactive')
      expect(entity.updatedAt.getTime()).toBeGreaterThanOrEqual(prevUpdated.getTime())
    })

    it('should partially update', () => {
      entity.update({
        quantity: 5,
      })
      expect(entity.name).toBe('Original Inventory')
      expect(entity.quantity).toBe(5)
    })
  })

  describe('domain events', () => {
    it('should create InventoryCreatedEvent', () => {
      const entity = InventoryEntity.create(baseCreate({ name: 'Ev' }))
      const event = new InventoryCreatedEvent(entity)
      expect(event.type).toBe('InventoryCreated')
      expect(event.aggregateId).toBe(entity.id)
      expect(event.inventory).toBe(entity)
      expect(event.occurredOn).toBeInstanceOf(Date)
    })

    it('should create InventoryUpdatedEvent', () => {
      const entity = InventoryEntity.create(baseCreate())
      const changes = { quantity: 1 }
      const event = new InventoryUpdatedEvent(entity, changes)
      expect(event.type).toBe('InventoryUpdated')
      expect(event.aggregateId).toBe(entity.id)
      expect(event.changes).toEqual(changes)
      expect(event.occurredOn).toBeInstanceOf(Date)
    })
  })
})
