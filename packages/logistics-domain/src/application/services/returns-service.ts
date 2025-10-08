import { ReturnOrder } from '../../core/entities/return-order';
import { ReturnOrderRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { ReturnRequestDto } from '../dto/logistics-dtos';

export class ReturnsService {
  constructor(private readonly repository: ReturnOrderRepository, private readonly eventBus: LogisticsEventBus) {}

  async create(dto: ReturnRequestDto): Promise<ReturnOrder> {
    const order = ReturnOrder.create({
      tenantId: dto.tenantId,
      originalShipmentId: dto.originalShipmentId,
      pickupAddress: dto.pickupAddress,
      returnReason: dto.returnReason,
    });
    await this.repository.saveReturnOrder(order);
    const event = buildEvent('logistics.return.created', dto.tenantId, { returnOrder: order });
    this.eventBus.publish(event);
    return order;
  }

  async receive(tenantId: string, returnId: string): Promise<ReturnOrder> {
    const order = await this.repository.findReturnOrderById(tenantId, returnId);
    if (order === undefined || order === null) {
      throw new Error(`Return order ${returnId} not found for tenant ${tenantId}`);
    }
    order.updateStatus('received');
    await this.repository.saveReturnOrder(order);
    const event = buildEvent('logistics.return.received', tenantId, { returnOrder: order });
    this.eventBus.publish(event);
    return order;
  }
}

