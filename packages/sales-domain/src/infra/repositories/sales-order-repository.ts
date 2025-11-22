/**
 * Sales Order Repository
 * Complete CRUD operations for Sales Orders
 */

import { SalesOrder, SalesOrderStatus } from '../../domain/entities/sales-order';

export interface SalesOrderFilter {
  customerId?: string;
  status?: SalesOrderStatus;
  sourceOfferId?: string;
  orderDateFrom?: Date;
  orderDateTo?: Date;
  deliveryDateFrom?: Date;
  deliveryDateTo?: Date;
  totalAmountMin?: number;
  totalAmountMax?: number;
  createdBy?: string;
  search?: string; // Search in orderNumber, subject, description
}

export interface SalesOrderSort {
  field: 'createdAt' | 'updatedAt' | 'orderDate' | 'deliveryDate' | 'totalAmount' | 'orderNumber' | 'status';
  direction: 'asc' | 'desc';
}

export interface PaginatedSalesOrderResult {
  items: SalesOrder[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class SalesOrderRepository {
  private orders: Map<string, SalesOrder> = new Map();

  async create(order: SalesOrder): Promise<SalesOrder> {
    this.orders.set(order.id, order);
    return order;
  }

  async findById(id: string): Promise<SalesOrder | null> {
    return this.orders.get(id) || null;
  }

  async findByOrderNumber(orderNumber: string): Promise<SalesOrder | null> {
    for (const order of this.orders.values()) {
      if (order.orderNumber === orderNumber) {
        return order;
      }
    }
    return null;
  }

  async update(order: SalesOrder): Promise<SalesOrder> {
    if (!this.orders.has(order.id)) {
      throw new Error('Order not found');
    }
    this.orders.set(order.id, order);
    return order;
  }

  async delete(id: string): Promise<boolean> {
    return this.orders.delete(id);
  }

  async findByCustomerId(customerId: string): Promise<SalesOrder[]> {
    const orders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (order.customerId === customerId) {
        orders.push(order);
      }
    }
    return orders.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findBySourceOfferId(sourceOfferId: string): Promise<SalesOrder[]> {
    const orders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (order.sourceOfferId === sourceOfferId) {
        orders.push(order);
      }
    }
    return orders.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByStatus(status: SalesOrderStatus): Promise<SalesOrder[]> {
    const orders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (order.status === status) {
        orders.push(order);
      }
    }
    return orders.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findOverdueOrders(): Promise<SalesOrder[]> {
    const now = new Date();
    const overdueOrders: SalesOrder[] = [];
    
    for (const order of this.orders.values()) {
      if (['CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED'].includes(order.status) &&
          order.deliveryDate < now) {
        overdueOrders.push(order);
      }
    }
    
    return overdueOrders.sort((a, b) => a.deliveryDate.getTime() - b.deliveryDate.getTime());
  }

  async findPendingConfirmation(): Promise<SalesOrder[]> {
    return this.findByStatus('DRAFT');
  }

  async findInProgress(): Promise<SalesOrder[]> {
    const inProgressOrders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (['CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED'].includes(order.status)) {
        inProgressOrders.push(order);
      }
    }
    return inProgressOrders.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByDeliveryDateRange(startDate: Date, endDate: Date): Promise<SalesOrder[]> {
    const orders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (order.deliveryDate >= startDate && order.deliveryDate <= endDate) {
        orders.push(order);
      }
    }
    return orders.sort((a, b) => a.deliveryDate.getTime() - b.deliveryDate.getTime());
  }

  async list(
    filter: SalesOrderFilter = {},
    sort: SalesOrderSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedSalesOrderResult> {
    let filteredOrders = Array.from(this.orders.values());

    // Apply filters
    if (filter.customerId) {
      filteredOrders = filteredOrders.filter(order => order.customerId === filter.customerId);
    }

    if (filter.status) {
      filteredOrders = filteredOrders.filter(order => order.status === filter.status);
    }

    if (filter.sourceOfferId) {
      filteredOrders = filteredOrders.filter(order => order.sourceOfferId === filter.sourceOfferId);
    }

    if (filter.orderDateFrom) {
      filteredOrders = filteredOrders.filter(order => order.orderDate >= filter.orderDateFrom!);
    }

    if (filter.orderDateTo) {
      filteredOrders = filteredOrders.filter(order => order.orderDate <= filter.orderDateTo!);
    }

    if (filter.deliveryDateFrom) {
      filteredOrders = filteredOrders.filter(order => order.deliveryDate >= filter.deliveryDateFrom!);
    }

    if (filter.deliveryDateTo) {
      filteredOrders = filteredOrders.filter(order => order.deliveryDate <= filter.deliveryDateTo!);
    }

    if (filter.totalAmountMin !== undefined) {
      filteredOrders = filteredOrders.filter(order => order.totalAmount >= filter.totalAmountMin!);
    }

    if (filter.totalAmountMax !== undefined) {
      filteredOrders = filteredOrders.filter(order => order.totalAmount <= filter.totalAmountMax!);
    }

    if (filter.createdBy) {
      filteredOrders = filteredOrders.filter(order => order.createdBy === filter.createdBy);
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredOrders = filteredOrders.filter(order => 
        order.orderNumber.toLowerCase().includes(searchLower) ||
        order.subject.toLowerCase().includes(searchLower) ||
        order.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply sorting
    filteredOrders.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'orderDate':
          aValue = a.orderDate.getTime();
          bValue = b.orderDate.getTime();
          break;
        case 'deliveryDate':
          aValue = a.deliveryDate.getTime();
          bValue = b.deliveryDate.getTime();
          break;
        case 'totalAmount':
          aValue = a.totalAmount;
          bValue = b.totalAmount;
          break;
        case 'orderNumber':
          aValue = a.orderNumber;
          bValue = b.orderNumber;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    // Apply pagination
    const total = filteredOrders.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredOrders.slice(startIndex, endIndex);

    return {
      items,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesOrderStatus, number>;
    totalValue: number;
    averageValue: number;
    overdueCount: number;
    pendingConfirmationCount: number;
    completionRate: number;
  }> {
    const allOrders = Array.from(this.orders.values());
    const total = allOrders.length;

    // Count by status
    const byStatus: Record<SalesOrderStatus, number> = {
      'DRAFT': 0,
      'CONFIRMED': 0,
      'IN_PROGRESS': 0,
      'PARTIALLY_DELIVERED': 0,
      'DELIVERED': 0,
      'INVOICED': 0,
      'COMPLETED': 0,
      'CANCELLED': 0
    };

    let totalValue = 0;
    let overdueCount = 0;
    const now = new Date();

    for (const order of allOrders) {
      byStatus[order.status]++;
      totalValue += order.totalAmount;

      // Check if overdue
      if (['CONFIRMED', 'IN_PROGRESS', 'PARTIALLY_DELIVERED'].includes(order.status) &&
          order.deliveryDate < now) {
        overdueCount++;
      }
    }

    const averageValue = total > 0 ? totalValue / total : 0;
    const pendingConfirmationCount = byStatus['DRAFT'];
    const completedCount = byStatus['COMPLETED'];
    const completionRate = total > 0 ? (completedCount / total) * 100 : 0;

    return {
      total,
      byStatus,
      totalValue,
      averageValue,
      overdueCount,
      pendingConfirmationCount,
      completionRate
    };
  }

  async isOrderNumberUnique(orderNumber: string, excludeId?: string): Promise<boolean> {
    for (const order of this.orders.values()) {
      if (order.orderNumber === orderNumber && order.id !== excludeId) {
        return false;
      }
    }
    return true;
  }

  async findRecentOrdersForCustomer(customerId: string, limit: number = 5): Promise<SalesOrder[]> {
    const customerOrders = await this.findByCustomerId(customerId);
    return customerOrders.slice(0, limit);
  }

  async findHighValueOrders(minAmount: number): Promise<SalesOrder[]> {
    const orders: SalesOrder[] = [];
    for (const order of this.orders.values()) {
      if (order.totalAmount >= minAmount) {
        orders.push(order);
      }
    }
    return orders.sort((a, b) => b.totalAmount - a.totalAmount);
  }

  async countOrdersByDate(startDate: Date, endDate: Date): Promise<number> {
    let count = 0;
    for (const order of this.orders.values()) {
      if (order.orderDate >= startDate && order.orderDate <= endDate) {
        count++;
      }
    }
    return count;
  }
}
