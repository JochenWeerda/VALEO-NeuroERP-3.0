/**
 * VALEO NeuroERP 3.0 - Inventory Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */

import { InventoryId, createInventoryId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';

export interface Inventory {
  readonly id: InventoryId;
  name: string;
  status?: string;
  productId: string;
  quantity: number;
  reservedQuantity: number;
  availableQuantity: number;
  reorderLevel: number;
  reorderQuantity: number;
  lastUpdated: Date;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateInventoryCommand {
  name: string;
  status?: string;
  productId: string;
  quantity: number;
  reservedQuantity: number;
  availableQuantity: number;
  reorderLevel: number;
  reorderQuantity: number;
  lastUpdated: Date;
}

export interface UpdateInventoryCommand {
  name?: string;
  status?: string;
  productId?: string;
  quantity?: number;
  reservedQuantity?: number;
  availableQuantity?: number;
  reorderLevel?: number;
  reorderQuantity?: number;
  lastUpdated?: Date;
}

export class InventoryCreatedEvent implements DomainEvent {
  readonly id: string;
  readonly type = 'InventoryCreated';
  readonly aggregateId: InventoryId;
  readonly aggregateType = 'Inventory';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;

  constructor(
    public readonly inventory: Inventory
  ) {
    this.id = `inventory-created-${Date.now()}`;
    this.aggregateId = inventory.id;
    this.version = 1;
    this.occurredOn = new Date();
    this.data = { inventory };
  }
}

export class InventoryUpdatedEvent implements DomainEvent {
  readonly id: string;
  readonly type = 'InventoryUpdated';
  readonly aggregateId: InventoryId;
  readonly aggregateType = 'Inventory';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;

  constructor(
    public readonly inventory: Inventory,
    public readonly changes: Record<string, any>
  ) {
    this.id = `inventory-updated-${Date.now()}`;
    this.aggregateId = inventory.id;
    this.version = 1;
    this.occurredOn = new Date();
    this.data = { inventory, changes };
  }
}

export class InventoryEntity implements Inventory {
  public readonly id: InventoryId;
  public name: string;
  public status?: string;
  public productId: string;
  public quantity: number;
  public reservedQuantity: number;
  public availableQuantity: number;
  public reorderLevel: number;
  public reorderQuantity: number;
  public lastUpdated: Date;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  private constructor(
    id: InventoryId,
    name: string,
    productId: string,
    quantity: number,
    reservedQuantity: number,
    availableQuantity: number,
    reorderLevel: number,
    reorderQuantity: number,
    lastUpdated: Date,
    createdAt: Date,
    updatedAt: Date,
    status?: string
  ) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.productId = productId;
    this.quantity = quantity;
    this.reservedQuantity = reservedQuantity;
    this.availableQuantity = availableQuantity;
    this.reorderLevel = reorderLevel;
    this.reorderQuantity = reorderQuantity;
    this.lastUpdated = lastUpdated;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  static create(command: CreateInventoryCommand): InventoryEntity {
    // Validate command
    InventoryEntity.validateCreateCommand(command);

    const id = createInventoryId(crypto.randomUUID());
    const now = new Date();

    return new InventoryEntity(
      id,
      command.name ?? '',
      command.productId ?? '',
      command.quantity ?? 0,
      command.reservedQuantity ?? 0,
      command.availableQuantity ?? 0,
      command.reorderLevel ?? 0,
      command.reorderQuantity ?? 0,
      command.lastUpdated ?? new Date(),
      now,
      now,
      command.status ?? undefined
    );
  }

  update(command: UpdateInventoryCommand): InventoryEntity {
    // Validate command
    InventoryEntity.validateUpdateCommand(command);

    const changes: Record<string, any> = {};

    if (command.name !== undefined) {
      this.name = command.name;
      changes.name = command.name;
    }
    if (command.status !== undefined) {
      this.status = command.status;
      changes.status = command.status;
    }
    if (command.productId !== undefined) {
      this.productId = command.productId;
      changes.productId = command.productId;
    }
    if (command.quantity !== undefined) {
      this.quantity = command.quantity;
      changes.quantity = command.quantity;
    }
    if (command.reservedQuantity !== undefined) {
      this.reservedQuantity = command.reservedQuantity;
      changes.reservedQuantity = command.reservedQuantity;
    }
    if (command.availableQuantity !== undefined) {
      this.availableQuantity = command.availableQuantity;
      changes.availableQuantity = command.availableQuantity;
    }
    if (command.reorderLevel !== undefined) {
      this.reorderLevel = command.reorderLevel;
      changes.reorderLevel = command.reorderLevel;
    }
    if (command.reorderQuantity !== undefined) {
      this.reorderQuantity = command.reorderQuantity;
      changes.reorderQuantity = command.reorderQuantity;
    }
    if (command.lastUpdated !== undefined) {
      this.lastUpdated = command.lastUpdated;
      changes.lastUpdated = command.lastUpdated;
    }

    (this as any).updatedAt = new Date();
    changes.updatedAt = this.updatedAt;

    return this;
  }

  // Business methods
  isActive(): boolean {
    return this.status === 'active';
  }

  // Validation methods
  private static validateCreateCommand(command: CreateInventoryCommand): void {
    if (!command.name || command.name.trim().length === 0) {
      throw new Error('Inventory name is required');
    }
    // Add additional validation rules here
  }

  private static validateUpdateCommand(command: UpdateInventoryCommand): void {
    // Add update validation rules here
  }
}

// Utility functions
function getDefaultValue(type: string): any {
  switch (type) {
    case 'string': return '';
    case 'number': return 0;
    case 'boolean': return false;
    case 'Date': return new Date();
    default: return null;
  }
}
