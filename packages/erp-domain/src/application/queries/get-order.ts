import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { OrderDTO } from '../dto/order-dto';
import { toOrderDTO } from '../mappers/order-mapper';
import type { OrderId } from '../../core/entities/order';

export class GetOrderQuery {
  constructor(private readonly service: OrderDomainService) {}

  async execute(id: OrderId): Promise<OrderDTO | null> {
    const order = await this.service.getOrder(id);
    return (order !== undefined && order !== null) ? toOrderDTO(order) : null;
  }
}
