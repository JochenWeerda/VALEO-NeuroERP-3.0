import { PurchaseOrderItem } from './purchaseOrderItem.entity'

export class PurchaseOrder {
  public readonly id: string;
  public readonly tenantId: string;
  public readonly no: string;
  public readonly supplierId: string;
  public readonly status: string;
  public readonly currency: string;
  public readonly items: PurchaseOrderItem[];
  public readonly version: number;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly deletedAt?: Date;

  constructor(data: {
    id: string;
    tenantId: string;
    no: string;
    supplierId: string;
    status: string;
    currency: string;
    items: PurchaseOrderItem[];
    version: number;
    createdAt: Date;
    updatedAt: Date;
    deletedAt?: Date;
  }) {
    this.id = data.id;
    this.tenantId = data.tenantId;
    this.no = data.no;
    this.supplierId = data.supplierId;
    this.status = data.status;
    this.currency = data.currency;
    this.items = data.items;
    this.version = data.version;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.deletedAt = data.deletedAt;
  }

  static create(data: {
    tenantId: string
    no: string
    supplierId: string
    currency?: string
    items?: PurchaseOrderItem[]
  }): PurchaseOrder {
    return new PurchaseOrder({
      id: '', // ID will be generated
      tenantId: data.tenantId,
      no: data.no,
      supplierId: data.supplierId,
      status: 'ENTWURF',
      currency: data.currency || 'EUR',
      items: data.items || [],
      version: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    })
  }

  get totalAmount(): number {
    return this.items.reduce((sum, item) => sum + (item.qty * item.price), 0)
  }

  get totalQuantity(): number {
    return this.items.reduce((sum, item) => sum + item.qty, 0)
  }

  isEditable(): boolean {
    return ['ENTWURF'].includes(this.status)
  }

  canBeSubmitted(): boolean {
    return this.status === 'ENTWURF' && this.items.length > 0
  }

  canBeCancelled(): boolean {
    return ['ENTWURF', 'FREIGEGEBEN'].includes(this.status)
  }

  withStatus(newStatus: string): PurchaseOrder {
    return new PurchaseOrder({
      id: this.id,
      tenantId: this.tenantId,
      no: this.no,
      supplierId: this.supplierId,
      status: newStatus,
      currency: this.currency,
      items: this.items,
      version: this.version + 1,
      createdAt: this.createdAt,
      updatedAt: new Date(),
      deletedAt: this.deletedAt
    })
  }

  withItems(newItems: PurchaseOrderItem[]): PurchaseOrder {
    return new PurchaseOrder({
      id: this.id,
      tenantId: this.tenantId,
      no: this.no,
      supplierId: this.supplierId,
      status: this.status,
      currency: this.currency,
      items: newItems,
      version: this.version + 1,
      createdAt: this.createdAt,
      updatedAt: new Date(),
      deletedAt: this.deletedAt
    })
  }
}