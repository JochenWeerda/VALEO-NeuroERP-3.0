/**
 * VALEO NeuroERP 3.0 - Product Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */

import { ProductId, createId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';

export interface Product {
  readonly id: ProductId;
  name: string;
  status?: string;
  sku: string;
  price: number;
  category: string;
  description?: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateProductCommand {
  name: string;
  status?: string;
  sku: string;
  price: number;
  category: string;
  description?: string;
}

export interface UpdateProductCommand {
  name?: string;
  status?: string;
  sku?: string;
  price?: number;
  category?: string;
  description?: string;
}

export class ProductCreatedEvent implements DomainEvent {
  readonly id: string;
  readonly type = 'ProductCreated';
  readonly aggregateId: ProductId;
  readonly aggregateType = 'Product';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;

  constructor(
    public readonly product: Product
  ) {
    this.id = `product-created-${Date.now()}`;
    this.aggregateId = product.id;
    this.version = 1;
    this.occurredOn = new Date();
    this.data = { product };
  }
}

export class ProductUpdatedEvent implements DomainEvent {
  readonly id: string;
  readonly type = 'ProductUpdated';
  readonly aggregateId: ProductId;
  readonly aggregateType = 'Product';
  readonly version: number;
  readonly occurredOn: Date;
  readonly data: Record<string, unknown>;

  constructor(
    public readonly product: Product,
    public readonly changes: Record<string, any>
  ) {
    this.id = `product-updated-${Date.now()}`;
    this.aggregateId = product.id;
    this.version = 1;
    this.occurredOn = new Date();
    this.data = { product, changes };
  }
}

export class ProductEntity implements Product {
  public readonly id: ProductId;
  public name: string;
  public status?: string;
  public sku: string;
  public price: number;
  public category: string;
  public description?: string;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  private constructor(
    id: ProductId,
    name: string,
    sku: string,
    price: number,
    category: string,
    createdAt: Date,
    updatedAt: Date,
    status?: string,
    description?: string
  ) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.sku = sku;
    this.price = price;
    this.category = category;
    this.description = description;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  static create(command: CreateProductCommand): ProductEntity {
    // Validate command
    ProductEntity.validateCreateCommand(command);

    const id = createId('ProductId') as ProductId;
    const now = new Date();

    return new ProductEntity(
      id,
      command.name,
      command.sku,
      command.price,
      command.category,
      now,
      now,
      command.status,
      command.description
    );
  }

  update(command: UpdateProductCommand): ProductEntity {
    // Validate command
    ProductEntity.validateUpdateCommand(command);

    const changes: Record<string, any> = {};

    if (command.name !== undefined) {
      this.name = command.name;
      changes.name = command.name;
    }
    if (command.status !== undefined) {
      this.status = command.status;
      changes.status = command.status;
    }
    if (command.sku !== undefined) {
      this.sku = command.sku;
      changes.sku = command.sku;
    }
    if (command.price !== undefined) {
      this.price = command.price;
      changes.price = command.price;
    }
    if (command.category !== undefined) {
      this.category = command.category;
      changes.category = command.category;
    }
    if (command.description !== undefined) {
      this.description = command.description;
      changes.description = command.description;
    }

    (this as any).updatedAt = new Date();
    changes.updatedAt = this.updatedAt;

    return this;
  }

  // Business methods
  isActive(): boolean {
    return this.status === 'active';
  }

  isInStock(): boolean {
    // This would typically check inventory levels
    return true;
  }

  calculateTotalPrice(quantity: number, taxRate: number = 0.19): number {
    const netTotal = this.price * quantity;
    return netTotal * (1 + taxRate);
  }

  // Validation methods
  private static validateCreateCommand(command: CreateProductCommand): void {
    if (!command.name || command.name.trim().length === 0) {
      throw new Error('Product name is required');
    }
    if (!command.sku || command.sku.trim().length === 0) {
      throw new Error('Product SKU is required');
    }
    if (command.price <= 0) {
      throw new Error('Product price must be greater than zero');
    }
    if (!command.category || command.category.trim().length === 0) {
      throw new Error('Product category is required');
    }
  }

  private static validateUpdateCommand(command: UpdateProductCommand): void {
    if (command.name !== undefined && command.name.trim().length === 0) {
      throw new Error('Product name cannot be empty');
    }
    if (command.sku !== undefined && command.sku.trim().length === 0) {
      throw new Error('Product SKU cannot be empty');
    }
    if (command.price !== undefined && command.price <= 0) {
      throw new Error('Product price must be greater than zero');
    }
    if (command.category !== undefined && command.category.trim().length === 0) {
      throw new Error('Product category cannot be empty');
    }
  }
}

// Utility functions
export function createProduct(command: CreateProductCommand): ProductEntity {
  return ProductEntity.create(command);
}

export function isValidProductId(id: string): boolean {
  return typeof id === 'string' && id.length > 0;
}

export function formatPrice(price: number, currency: string = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency
  }).format(price);
}