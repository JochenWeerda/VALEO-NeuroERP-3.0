import { OrderDomainService } from '../../core/domain-services/order-domain-service';
import type { CreateOrderDTO, OrderDTO } from '../dto/order-dto';
import { toCreateOrderInput, toOrderDTO } from '../mappers/order-mapper';

export class CreateOrderCommand {
  constructor(private readonly service: OrderDomainService) {}

  async execute(payload: CreateOrderDTO): Promise<OrderDTO> {
    const created = await this.service.createOrder(toCreateOrderInput(payload));
    return toOrderDTO(created);
  }
}
