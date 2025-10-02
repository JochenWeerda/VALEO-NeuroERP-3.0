import { WeighingTicketRepository } from '../../infra/repo/weighing-ticket-repository';
export interface CreateWeighingTicketRequest {
    tenantId: string;
    type: 'Vehicle' | 'Container' | 'Silo' | 'Manual';
    licensePlate?: string;
    containerNumber?: string;
    siloId?: string;
    commodity: 'WHEAT' | 'BARLEY' | 'RAPESEED' | 'SOYMEAL' | 'COMPOUND_FEED' | 'FERTILIZER' | 'OTHER';
    commodityDescription?: string;
    expectedWeight?: number;
    tolerancePercent?: number;
    contractId?: string;
    orderId?: string;
    deliveryNoteId?: string;
    gateId?: string;
}
export interface RecordWeightRequest {
    ticketId: string;
    tenantId: string;
    mode: 'Gross' | 'Tare';
    weight: number;
    unit: 'kg' | 't';
    scaleId: string;
    operatorId?: string;
    notes?: string;
}
export declare class WeighingService {
    private ticketRepository;
    constructor(ticketRepository: WeighingTicketRepository);
    createTicket(request: CreateWeighingTicketRequest): Promise<import("../entities/weighing-ticket").WeighingTicketEntity>;
    getTicket(id: string, tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity | null>;
    getTicketByNumber(ticketNumber: string, tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity | null>;
    findTicketsByLicensePlate(licensePlate: string, tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity[]>;
    recordWeight(request: RecordWeightRequest): Promise<import("../entities/weighing-ticket").WeighingTicketEntity>;
    completeTicket(id: string, tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity>;
    cancelTicket(id: string, tenantId: string, reason?: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity>;
    updateTicket(id: string, tenantId: string, updates: Partial<{
        commodityDescription: string;
        expectedWeight: number;
        tolerancePercent: number;
        contractId: string;
        orderId: string;
        deliveryNoteId: string;
        gateId: string;
    }>): Promise<import("../entities/weighing-ticket").WeighingTicketEntity>;
    getTickets(tenantId: string, filters?: {
        status?: string;
        type?: string;
        commodity?: string;
        licensePlate?: string;
        gateId?: string;
        contractId?: string;
        orderId?: string;
        fromDate?: Date;
        toDate?: Date;
        isWithinTolerance?: boolean;
        search?: string;
    }, pagination?: {
        page?: number;
        pageSize?: number;
    }): Promise<import("../../infra/repo/weighing-ticket-repository").WeighingTicketListResult>;
    deleteTicket(id: string, tenantId: string): Promise<boolean>;
    getActiveTickets(tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity[]>;
    getCompletedTicketsToday(tenantId: string): Promise<import("../entities/weighing-ticket").WeighingTicketEntity[]>;
}
//# sourceMappingURL=weighing-service.d.ts.map