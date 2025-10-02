import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderId } from '../../core/entities/order';

export class DeleteOrderCommand {
  constructor(private readonly service: OrderDomainService) {}

  async execute(id: OrderId): Promise<void> {
    await this.service.deleteOrder(id);
  }
}
