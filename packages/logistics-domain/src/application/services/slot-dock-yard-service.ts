import { YardVisit } from '../../core/entities/yard-visit';
import { YardRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus, buildEvent } from '../../infrastructure/messaging/logistics-event-bus';
import { SlotBookingDto } from '../dto/logistics-dtos';

export class SlotDockYardService {
  constructor(private readonly yardRepository: YardRepository, private readonly eventBus: LogisticsEventBus) {}

  async bookSlot(dto: SlotBookingDto): Promise<YardVisit> {
    const yardVisit = YardVisit.create({
      tenantId: dto.tenantId,
      shipmentId: dto.shipmentId,
      gate: dto.gate,
      dock: dto.dock,
      scheduledWindow: dto.window
        ? { from: new Date(dto.window.from), to: new Date(dto.window.to) }
        : undefined,
    });

    await this.yardRepository.saveYardVisit(yardVisit);
    this.publish('logistics.slot.booked', dto.tenantId, { yardVisit });

    if (dto.dock) {
      this.publish('logistics.dock.assigned', dto.tenantId, { yardVisit });
    }

    return yardVisit;
  }

  async checkIn(tenantId: string, shipmentId: string): Promise<YardVisit> {
    return this.updateStatus(tenantId, shipmentId, 'checked_in');
  }

  async checkOut(tenantId: string, shipmentId: string): Promise<YardVisit> {
    return this.updateStatus(tenantId, shipmentId, 'checked_out');
  }

  private async updateStatus(
    tenantId: string,
    shipmentId: string,
    status: YardVisit['status'],
  ): Promise<YardVisit> {
    const yardVisit = await this.yardRepository.findYardVisitByShipmentId(tenantId, shipmentId);
    if (!yardVisit) {
      throw new Error(`Yard visit not found for shipment ${shipmentId}`);
    }
    yardVisit.updateStatus(status);
    await this.yardRepository.saveYardVisit(yardVisit);

    this.publish('logistics.yard.statusChanged', tenantId, { yardVisit });
    return yardVisit;
  }

  private publish(
    eventType:
      | 'logistics.slot.booked'
      | 'logistics.dock.assigned'
      | 'logistics.yard.statusChanged',
    tenantId: string,
    payload: { yardVisit: YardVisit } | { yardVisit: YardVisit } | { yardVisit: YardVisit },
  ): void {
    const event = buildEvent(eventType, tenantId, payload);
    this.eventBus.publish(event);
  }
}
