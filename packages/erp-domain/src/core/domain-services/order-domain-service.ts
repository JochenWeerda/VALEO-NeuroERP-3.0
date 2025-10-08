import type { OrderId } from '@valero-neuroerp/data-models';
import {
  CreateOrderInput,
  DEFAULT_ORDER_LIMIT,
  Order,
  OrderFilters,
  OrderStatus,
  createOrder,
} from '../entities/order';
import { OrderRepository } from '../repositories/order-repository';

const STATUS_FLOW: Record<OrderStatus, OrderStatus[]> = {
  draft: ['confirmed', 'cancelled'],
  confirmed: ['processing', 'cancelled'],
  processing: ['shipped', 'cancelled'],
  shipped: ['delivered', 'cancelled'],
  delivered: ['invoiced'],
  invoiced: [],
  cancelled: [],
};

const STATUS_WEIGHTS: Record<OrderStatus, number> = {
  draft: 0,
  confirmed: 1,
  processing: 2,
  shipped: 3,
  delivered: 4,
  invoiced: 5,
  cancelled: 99,
};

const DECIMAL_PRECISION = 2;
const MAX_ORDER_LIMIT_CAP = 500;
const CURRENCY_REGEX = /^[A-Z]{3}$/;
const MAX_TOLERANCE = 0.01;

export class OrderDomainService {
  constructor(private readonly repository: OrderRepository) {}

  async listOrders(filters: OrderFilters = {}): Promise<Order[]> {
    const normalized: OrderFilters = {
      status: filters.status,
      documentType: filters.documentType,
      customerNumber: filters.customerNumber?.trim() ?? undefined,
      debtorNumber: filters.debtorNumber?.trim() ?? undefined,
      from: filters.from,
      to: filters.to,
      limit: clampLimit(filters.limit),
      offset: Math.max(filters.offset ?? 0, 0),
    };
    return this.repository.list(normalized);
  }

  async getOrder(id: OrderId): Promise<Order | null> {
    return this.repository.findById(id);
  }

  async createOrder(input: CreateOrderInput): Promise<Order> {
    this.assertCurrency(input.currency);
    this.assertAmountConsistency(input);

    const targetStatus = input.status ?? 'draft';
    this.assertStatus(targetStatus);

    const order = createOrder({ ...input, status: targetStatus });
    return this.repository.create(order);
  }

  async updateOrderStatus(id: OrderId, status: OrderStatus): Promise<Order> {
    this.assertStatus(status);
    const current = await this.repository.findById(id);
    if (current === undefined || current === null) {
      throw new Error(`Order ${String(id)} not found`);
    }

    if (current.status === status) {
      return current;
    }

    const allowedTargets = STATUS_FLOW[current.status];
    if (!allowedTargets.includes(status)) {
      throw new Error(`Cannot transition order ${current.orderNumber} from ${current.status} to ${status}`);
    }

    return this.repository.updateStatus(id, status);
  }

  async deleteOrder(id: OrderId): Promise<void> {
    const existing = await this.repository.findById(id);
    if (existing === undefined || existing === null) {
      return;
    }
    if (STATUS_WEIGHTS[existing.status] >= STATUS_WEIGHTS.invoiced) {
      throw new Error('Invoiced or cancelled orders cannot be deleted.');
    }
    await this.repository.delete(id);
  }

  private assertStatus(status: OrderStatus): void {
    if (!(status in STATUS_FLOW)) {
      throw new Error(`Unsupported order status: ${status}`);
    }
  }

  private assertCurrency(currency: string): void {
    if (!currency || !CURRENCY_REGEX.test(currency)) {
      throw new Error(`Invalid ISO currency provided: ${currency}`);
    }
  }

  private assertAmountConsistency(order: CreateOrderInput): void {
    const sum = order.items.reduce((acc, item) => acc + item.netPrice, 0);
    if (Math.abs(sum - order.netAmount) > MAX_TOLERANCE) {
      throw new Error(`Net amount ${order.netAmount} does not match item total ${sum.toFixed(DECIMAL_PRECISION)}.`);
    }

    const gross = Number((order.netAmount + order.vatAmount).toFixed(DECIMAL_PRECISION));
    if (Math.abs(gross - order.totalAmount) > MAX_TOLERANCE) {
      throw new Error(`Total amount ${order.totalAmount} does not equal net + VAT (${gross}).`);
    }
  }
}

function clampLimit(limit?: number): number | undefined {
  if (limit === undefined) {
    return DEFAULT_ORDER_LIMIT;
  }
  if (limit <= 0) {
    return DEFAULT_ORDER_LIMIT;
  }
  return Math.min(limit, MAX_ORDER_LIMIT_CAP);
}

