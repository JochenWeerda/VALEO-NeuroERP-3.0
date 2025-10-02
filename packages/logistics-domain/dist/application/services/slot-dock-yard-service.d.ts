import { YardVisit } from '../../core/entities/yard-visit';
import { YardRepository } from '../../infrastructure/repositories/interfaces/logistics-repositories';
import { LogisticsEventBus } from '../../infrastructure/messaging/logistics-event-bus';
import { SlotBookingDto } from '../dto/logistics-dtos';
export declare class SlotDockYardService {
    private readonly yardRepository;
    private readonly eventBus;
    constructor(yardRepository: YardRepository, eventBus: LogisticsEventBus);
    bookSlot(dto: SlotBookingDto): Promise<YardVisit>;
    checkIn(tenantId: string, shipmentId: string): Promise<YardVisit>;
    checkOut(tenantId: string, shipmentId: string): Promise<YardVisit>;
    private updateStatus;
    private publish;
}
//# sourceMappingURL=slot-dock-yard-service.d.ts.map