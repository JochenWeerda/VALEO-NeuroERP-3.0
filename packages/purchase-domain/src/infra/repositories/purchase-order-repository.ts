/**
 * Purchase Order Repository
 * ISO 27001 Communications Security Compliant
 */

import { PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus } from '../../domain/entities/purchase-order';

export interface PurchaseOrderFilter {
  supplierId?: string;
  status?: PurchaseOrderStatus;
  createdBy?: string;
  approvedBy?: string;
  orderedBy?: string;
  orderDateFrom?: Date;
  orderDateTo?: Date;
  deliveryDateFrom?: Date;
  deliveryDateTo?: Date;
  totalAmountMin?: number;
  totalAmountMax?: number;
}

export interface PurchaseOrderSort {
  field: 'createdAt' | 'updatedAt' | 'orderDate' | 'deliveryDate' | 'totalAmount' | 'purchaseOrderNumber';
  direction: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class PurchaseOrderRepository {
  private readonly tenantId: string;
  
  constructor(tenantId: string) {
    this.tenantId = tenantId;
  }
  private orders: Map<string, PurchaseOrder> = new Map();
  private items: Map<string, PurchaseOrderItem[]> = new Map();

  /**
   * Create a new purchase order
   */
  async create(order: PurchaseOrder): Promise<PurchaseOrder> {
    // Validate order data
    this.validateOrder(order);

    // Store order
    this.orders.set(order.id, order);

    // Store items
    this.items.set(order.id, [...order.items]);

    return order;
  }

  /**
   * Update an existing purchase order
   */
  async update(id: string, order: PurchaseOrder): Promise<PurchaseOrder> {
    if (!this.orders.has(id)) {
      throw new Error(`Purchase order with id ${id} not found`);
    }

    // Validate order data
    this.validateOrder(order);

    // Store updated order
    this.orders.set(id, order);

    // Store updated items
    this.items.set(id, [...order.items]);

    return order;
  }

  /**
   * Find purchase order by ID
   */
  async findById(id: string): Promise<PurchaseOrder | null> {
    return this.orders.get(id) || null;
  }

  /**
   * Find purchase order by purchase order number
   */
  async findByPurchaseOrderNumber(purchaseOrderNumber: string): Promise<PurchaseOrder | null> {
    for (const order of Array.from(this.orders.values())) {
      if (order.purchaseOrderNumber === purchaseOrderNumber) {
        return order;
      }
    }
    return null;
  }

  /**
   * Find purchase orders by supplier ID
   */
  async findBySupplierId(supplierId: string): Promise<PurchaseOrder[]> {
    const result: PurchaseOrder[] = [];
    for (const order of Array.from(this.orders.values())) {
      if (order.supplierId === supplierId) {
        result.push(order);
      }
    }
    return result;
  }

  /**
   * Find purchase orders by delivery date range
   */
  async findByDeliveryDateRange(startDate: Date, endDate: Date): Promise<PurchaseOrder[]> {
    const result: PurchaseOrder[] = [];
    for (const order of Array.from(this.orders.values())) {
      if (order.deliveryDate >= startDate && order.deliveryDate <= endDate) {
        result.push(order);
      }
    }
    return result;
  }

  /**
   * Find all purchase orders with filtering and pagination
   */
  async findAll(
    filter: PurchaseOrderFilter = {},
    sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<PurchaseOrder>> {
    let orders = Array.from(this.orders.values());

    // Apply filters
    orders = this.applyFilters(orders, filter);

    // Apply sorting
    orders = this.applySorting(orders, sort);

    // Apply pagination
    const total = orders.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedOrders = orders.slice(startIndex, endIndex);

    return {
      items: paginatedOrders,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  /**
   * Find overdue purchase orders
   */
  async findOverdue(): Promise<PurchaseOrder[]> {
    const now = new Date();
    const result: PurchaseOrder[] = [];

    for (const order of Array.from(this.orders.values())) {
      if (order.deliveryDate < now && order.status !== PurchaseOrderStatus.GELIEFERT && order.status !== PurchaseOrderStatus.STORNIERT) {
        result.push(order);
      }
    }

    return result;
  }

  /**
   * Find purchase orders requiring approval
   */
  async findPendingApproval(): Promise<PurchaseOrder[]> {
    const result: PurchaseOrder[] = [];

    for (const order of Array.from(this.orders.values())) {
      if (order.status === PurchaseOrderStatus.ENTWURF) {
        result.push(order);
      }
    }

    return result;
  }

  /**
   * Delete purchase order by ID
   */
  async delete(id: string): Promise<boolean> {
    if (!this.orders.has(id)) {
      return false;
    }

    this.orders.delete(id);
    this.items.delete(id);
    return true;
  }

  /**
   * Get purchase order statistics
   */
  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<PurchaseOrderStatus, number>;
    totalValue: number;
    averageValue: number;
    overdueCount: number;
    pendingApprovalCount: number;
  }> {
    const orders = Array.from(this.orders.values());
    const byStatus: Record<PurchaseOrderStatus, number> = {
      [PurchaseOrderStatus.ENTWURF]: 0,
      [PurchaseOrderStatus.FREIGEGEBEN]: 0,
      [PurchaseOrderStatus.BESTELLT]: 0,
      [PurchaseOrderStatus.TEILGELIEFERT]: 0,
      [PurchaseOrderStatus.GELIEFERT]: 0,
      [PurchaseOrderStatus.STORNIERT]: 0
    };

    let totalValue = 0;
    let overdueCount = 0;
    let pendingApprovalCount = 0;
    const now = new Date();

    for (const order of orders) {
      byStatus[order.status]++;
      totalValue += order.totalAmount;

      if (order.deliveryDate < now && order.status !== PurchaseOrderStatus.GELIEFERT && order.status !== PurchaseOrderStatus.STORNIERT) {
        overdueCount++;
      }

      if (order.status === PurchaseOrderStatus.ENTWURF) {
        pendingApprovalCount++;
      }
    }

    return {
      total: orders.length,
      byStatus,
      totalValue,
      averageValue: orders.length > 0 ? totalValue / orders.length : 0,
      overdueCount,
      pendingApprovalCount
    };
  }

  /**
   * Check if order exists
   */
  async exists(id: string): Promise<boolean> {
    return this.orders.has(id);
  }

  /**
   * Get items for a specific order
   */
  async getItems(orderId: string): Promise<PurchaseOrderItem[]> {
    return this.items.get(orderId) || [];
  }

  private validateOrder(order: PurchaseOrder): void {
    if (!order.supplierId) {
      throw new Error('Supplier ID is required');
    }

    if (!order.subject || order.subject.trim().length === 0) {
      throw new Error('Subject is required');
    }

    if (!order.description || order.description.trim().length === 0) {
      throw new Error('Description is required');
    }

    if (!order.deliveryDate) {
      throw new Error('Delivery date is required');
    }

    if (!order.items || order.items.length === 0) {
      throw new Error('At least one item is required');
    }

    if (!order.createdBy) {
      throw new Error('Created by is required');
    }

    // Validate items
    for (const item of order.items) {
      if (!item.description || item.description.trim().length === 0) {
        throw new Error('Item description is required');
      }

      if (item.quantity <= 0) {
        throw new Error('Item quantity must be positive');
      }

      if (item.unitPrice < 0) {
        throw new Error('Item unit price cannot be negative');
      }

      if (item.discountPercent < 0 || item.discountPercent > 100) {
        throw new Error('Item discount percent must be between 0 and 100');
      }
    }
  }

  private applyFilters(orders: PurchaseOrder[], filter: PurchaseOrderFilter): PurchaseOrder[] {
    return orders.filter(order => {
      if (filter.supplierId && order.supplierId !== filter.supplierId) {
        return false;
      }

      if (filter.status && order.status !== filter.status) {
        return false;
      }

      if (filter.createdBy && order.createdBy !== filter.createdBy) {
        return false;
      }

      if (filter.approvedBy && order.approvedBy !== filter.approvedBy) {
        return false;
      }

      if (filter.orderedBy && order.orderedBy !== filter.orderedBy) {
        return false;
      }

      if (filter.orderDateFrom && order.orderDate < filter.orderDateFrom) {
        return false;
      }

      if (filter.orderDateTo && order.orderDate > filter.orderDateTo) {
        return false;
      }

      if (filter.deliveryDateFrom && order.deliveryDate < filter.deliveryDateFrom) {
        return false;
      }

      if (filter.deliveryDateTo && order.deliveryDate > filter.deliveryDateTo) {
        return false;
      }

      if (filter.totalAmountMin !== undefined && order.totalAmount < filter.totalAmountMin) {
        return false;
      }

      if (filter.totalAmountMax !== undefined && order.totalAmount > filter.totalAmountMax) {
        return false;
      }

      return true;
    });
  }

  private applySorting(orders: PurchaseOrder[], sort: PurchaseOrderSort): PurchaseOrder[] {
    return orders.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt;
          bValue = b.createdAt;
          break;
        case 'updatedAt':
          aValue = a.updatedAt;
          bValue = b.updatedAt;
          break;
        case 'orderDate':
          aValue = a.orderDate;
          bValue = b.orderDate;
          break;
        case 'deliveryDate':
          aValue = a.deliveryDate;
          bValue = b.deliveryDate;
          break;
        case 'totalAmount':
          aValue = a.totalAmount;
          bValue = b.totalAmount;
          break;
        case 'purchaseOrderNumber':
          aValue = a.purchaseOrderNumber;
          bValue = b.purchaseOrderNumber;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sort.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sort.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }
}