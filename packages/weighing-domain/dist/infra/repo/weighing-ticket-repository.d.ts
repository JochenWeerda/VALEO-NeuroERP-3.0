import { NodePgDatabase } from 'drizzle-orm/node-postgres';
import { WeighingTicketEntity as DomainWeighingTicket } from '../../domain/entities/weighing-ticket';
export interface WeighingTicketQuery {
    tenantId?: string;
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
    page?: number;
    pageSize?: number;
}
export interface WeighingTicketListResult {
    data: DomainWeighingTicket[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export declare class WeighingTicketRepository {
    private db;
    constructor(db: NodePgDatabase<any>);
    create(ticket: DomainWeighingTicket): Promise<DomainWeighingTicket>;
    findById(id: string, tenantId?: string): Promise<DomainWeighingTicket | null>;
    findByTicketNumber(ticketNumber: string, tenantId?: string): Promise<DomainWeighingTicket | null>;
    findByLicensePlate(licensePlate: string, tenantId?: string): Promise<DomainWeighingTicket[]>;
    findMany(query: WeighingTicketQuery): Promise<WeighingTicketListResult>;
    update(id: string, updates: Partial<DomainWeighingTicket>, tenantId?: string): Promise<DomainWeighingTicket | null>;
    delete(id: string, tenantId?: string): Promise<boolean>;
    getNextTicketNumber(tenantId: string, prefix?: string): Promise<string>;
    private mapToDomain;
}
//# sourceMappingURL=weighing-ticket-repository.d.ts.map