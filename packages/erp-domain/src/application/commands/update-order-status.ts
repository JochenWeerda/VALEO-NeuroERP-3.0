import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { UpdateOrderStatusDTO, OrderDTO } from '../dto/order-dto';
import { toOrderDTO } from '../mappers/order-mapper';
import type { OrderId, OrderStatus } from '../../core/entities/order';

export class UpdateOrderStatusCommand {
  constructor(private readonly service: OrderDomainService) {}

  async execute(id: OrderId, payload: UpdateOrderStatusDTO): Promise<OrderDTO> {
    const status = payload.status as OrderStatus;
    const updated = await this.service.updateOrderStatus(id, status);
    return toOrderDTO(updated);
  }
}
