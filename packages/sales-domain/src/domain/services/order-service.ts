import { OrderEntity, CreateOrderInput, UpdateOrderInput, OrderStatusType } from '../entities';
import { OrderRepository } from '../../infra/repo';

export interface OrderServiceDependencies {
  orderRepo: OrderRepository;
}

export interface CreateOrderData extends CreateOrderInput {
  tenantId: string;
  orderNumber: string;
  lines: any[];
}

export interface UpdateOrderData extends UpdateOrderInput {
  tenantId: string;
  lines?: any[];
}

export class OrderService {
  constructor(private deps: OrderServiceDependencies) {}

  async createOrder(data: CreateOrderData): Promise<OrderEntity> {
    // Business validation
    if (data.lines.length === 0) {
      throw new Error('Order must have at least one line item');
    }

    // Check if order number already exists
    const existingOrder = await this.deps.orderRepo.findByNumber(data.orderNumber, data.tenantId);
    if (existingOrder) {
      throw new Error(`Order number ${data.orderNumber} already exists`);
    }

    // Validate line items
    for (const line of data.lines) {
      if (line.quantity <= 0) {
        throw new Error('Line item quantity must be positive');
      }
      if (line.unitPrice < 0) {
        throw new Error('Line item unit price cannot be negative');
      }
    }

    const order = await this.deps.orderRepo.create(data);
    return order;
  }

  async getOrder(id: string, tenantId: string): Promise<OrderEntity | null> {
    return this.deps.orderRepo.findById(id, tenantId);
  }

  async updateOrder(id: string, data: UpdateOrderData): Promise<OrderEntity> {
    const existingOrder = await this.deps.orderRepo.findById(id, data.tenantId);
    if (!existingOrder) {
      throw new Error(`Order ${id} not found`);
    }

    // Business validation
    if (data.lines) {
      if (data.lines.length === 0) {
        throw new Error('Order must have at least one line item');
      }

      for (const line of data.lines) {
        if (line.quantity <= 0) {
          throw new Error('Line item quantity must be positive');
        }
        if (line.unitPrice < 0) {
          throw new Error('Line item unit price cannot be negative');
        }
      }
    }

    const updatedOrder = await this.deps.orderRepo.update(id, data.tenantId, data);

    if (!updatedOrder) {
      throw new Error(`Failed to update order ${id}`);
    }

    return updatedOrder;
  }

  async confirmOrder(id: string, tenantId: string): Promise<OrderEntity> {
    const order = await this.deps.orderRepo.findById(id, tenantId);
    if (!order) {
      throw new Error(`Order ${id} not found`);
    }

    if (!order.canBeConfirmed()) {
      throw new Error('Order cannot be confirmed in its current state');
    }

    const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Confirmed');

    if (!updatedOrder) {
      throw new Error(`Failed to confirm order`);
    }

    return updatedOrder;
  }

  async markOrderAsInvoiced(id: string, tenantId: string): Promise<OrderEntity> {
    const order = await this.deps.orderRepo.findById(id, tenantId);
    if (!order) {
      throw new Error(`Order ${id} not found`);
    }

    if (!order.canBeInvoiced()) {
      throw new Error('Order cannot be invoiced in its current state');
    }

    const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Invoiced');

    if (!updatedOrder) {
      throw new Error(`Failed to mark order as invoiced`);
    }

    return updatedOrder;
  }

  async cancelOrder(id: string, tenantId: string): Promise<OrderEntity> {
    const order = await this.deps.orderRepo.findById(id, tenantId);
    if (!order) {
      throw new Error(`Order ${id} not found`);
    }

    if (!order.canBeCancelled()) {
      throw new Error('Order cannot be cancelled in its current state');
    }

    const updatedOrder = await this.deps.orderRepo.updateStatus(id, tenantId, 'Cancelled');

    if (!updatedOrder) {
      throw new Error(`Failed to cancel order`);
    }

    return updatedOrder;
  }

  async searchOrders(
    tenantId: string,
    filters: {
      customerId?: string;
      status?: OrderStatusType;
      search?: string;
      expectedDeliveryDateFrom?: Date;
      expectedDeliveryDateTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.orderRepo.findAll(tenantId, filters, pagination);
  }

  async getOrdersByCustomer(
    customerId: string,
    tenantId: string,
    filters: {
      status?: OrderStatusType;
      search?: string;
      expectedDeliveryDateFrom?: Date;
      expectedDeliveryDateTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.orderRepo.findByCustomerId(customerId, tenantId, filters, pagination);
  }
}