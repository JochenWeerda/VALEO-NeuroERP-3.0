import type { OrderId } from '@valero-neuroerp/data-models';
import { InMemoryRepository } from '@valero-neuroerp/utilities';
import { Order, OrderFilters, OrderStatus, createOrder, CreateOrderInput, withOrderStatus, cloneOrder } from '../../core/entities/order';
import { OrderRepository, buildOrderQuery } from '../../core/repositories/order-repository';

export class InMemoryOrderRepository
  extends InMemoryRepository<Order, 'id', OrderId>
  implements OrderRepository {
  constructor(seed: CreateOrderInput[] = []) {
    super('id');
    seed.forEach((input) => {
      const entity = createOrder(input);
      void this.create(entity);
    });
  }

  async list(filters?: OrderFilters): Promise<Order[]> {
    const base = await this.findMany(buildOrderQuery(filters));
    const results = base.filter((order) => {
      if (filters?.from && order.documentDate < filters.from) {
        return false;
      }
      if (filters?.to && order.documentDate > filters.to) {
        return false;
      }
      return true;
    });
    return results.map(cloneOrder);
  }

  async create(order: Order): Promise<Order> {
    await super.create(order);
    return cloneOrder(order);
  }

  async update(id: OrderId, order: Order): Promise<Order> {
    await super.update(id, order);
    return cloneOrder(order);
  }

  async updateStatus(id: OrderId, status: OrderStatus): Promise<Order> {
    const existing = await this.findById(id);
    if (!existing) {
      throw new Error(`Order ${String(id)} not found`);
    }
    const updated = withOrderStatus(existing, status);
    await super.update(id, updated);
    return cloneOrder(updated);
  }
}
