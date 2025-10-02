import { eq, and, sql, desc, gte, lte, like, or } from 'drizzle-orm';
import { drizzle, NodePgDatabase } from 'drizzle-orm/node-postgres';
import { weighingTickets } from '../db/schema';
import { WeighingTicket, WeighingTicketEntity as DomainWeighingTicket } from '../../domain/entities/weighing-ticket';

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

export class WeighingTicketRepository {
  constructor(private db: NodePgDatabase<any>) {}

  async create(ticket: DomainWeighingTicket): Promise<DomainWeighingTicket> {
    const insertData = {
      id: ticket.id,
      tenantId: ticket.tenantId,
      ticketNumber: ticket.ticketNumber,
      type: ticket.type,
      status: ticket.status,
      licensePlate: ticket.licensePlate || null,
      containerNumber: ticket.containerNumber || null,
      siloId: ticket.siloId || null,
      commodity: ticket.commodity,
      commodityDescription: ticket.commodityDescription || null,
      grossWeight: ticket.grossWeight ? JSON.parse(JSON.stringify(ticket.grossWeight)) : null,
      tareWeight: ticket.tareWeight ? JSON.parse(JSON.stringify(ticket.tareWeight)) : null,
      netWeight: ticket.netWeight?.toString() || null,
      netWeightUnit: ticket.netWeightUnit || null,
      expectedWeight: ticket.expectedWeight?.toString() || null,
      tolerancePercent: ticket.tolerancePercent.toString(),
      isWithinTolerance: ticket.isWithinTolerance || null,
      contractId: ticket.contractId || null,
      orderId: ticket.orderId || null,
      deliveryNoteId: ticket.deliveryNoteId || null,
      anprRecordId: ticket.anprRecordId || null,
      autoAssigned: ticket.autoAssigned,
      gateId: ticket.gateId || null,
      slotId: ticket.slotId || null,
      createdAt: ticket.createdAt,
      updatedAt: ticket.updatedAt,
      completedAt: ticket.completedAt || null,
      version: ticket.version,
    };

    const [result] = await this.db.insert(weighingTickets).values(insertData).returning();

    return this.mapToDomain(result);
  }

  async findById(id: string, tenantId?: string): Promise<DomainWeighingTicket | null> {
    const conditions = [eq(weighingTickets.id, id)];
    if (tenantId) {
      conditions.push(eq(weighingTickets.tenantId, tenantId));
    }

    const [result] = await this.db
      .select()
      .from(weighingTickets)
      .where(and(...conditions))
      .limit(1);

    return result ? this.mapToDomain(result) : null;
  }

  async findByTicketNumber(ticketNumber: string, tenantId?: string): Promise<DomainWeighingTicket | null> {
    const conditions = [eq(weighingTickets.ticketNumber, ticketNumber)];
    if (tenantId) {
      conditions.push(eq(weighingTickets.tenantId, tenantId));
    }

    const [result] = await this.db
      .select()
      .from(weighingTickets)
      .where(and(...conditions))
      .limit(1);

    return result ? this.mapToDomain(result) : null;
  }

  async findByLicensePlate(licensePlate: string, tenantId?: string): Promise<DomainWeighingTicket[]> {
    const conditions = [eq(weighingTickets.licensePlate, licensePlate)];
    if (tenantId) {
      conditions.push(eq(weighingTickets.tenantId, tenantId));
    }

    const results = await this.db
      .select()
      .from(weighingTickets)
      .where(and(...conditions));

    return results.map(result => this.mapToDomain(result));
  }

  async findMany(query: WeighingTicketQuery): Promise<WeighingTicketListResult> {
    const conditions = [];

    if (query.tenantId) {
      conditions.push(eq(weighingTickets.tenantId, query.tenantId));
    }

    if (query.status) {
      conditions.push(sql`${weighingTickets.status} = ${query.status}`);
    }

    if (query.type) {
      conditions.push(sql`${weighingTickets.type} = ${query.type}`);
    }

    if (query.commodity) {
      conditions.push(sql`${weighingTickets.commodity} = ${query.commodity}`);
    }

    if (query.licensePlate) {
      conditions.push(eq(weighingTickets.licensePlate, query.licensePlate));
    }

    if (query.gateId) {
      conditions.push(eq(weighingTickets.gateId, query.gateId));
    }

    if (query.contractId) {
      conditions.push(eq(weighingTickets.contractId, query.contractId));
    }

    if (query.orderId) {
      conditions.push(eq(weighingTickets.orderId, query.orderId));
    }

    if (query.fromDate) {
      conditions.push(gte(weighingTickets.createdAt, query.fromDate));
    }

    if (query.toDate) {
      conditions.push(lte(weighingTickets.createdAt, query.toDate));
    }

    if (query.isWithinTolerance !== undefined) {
      conditions.push(eq(weighingTickets.isWithinTolerance, query.isWithinTolerance));
    }

    if (query.search) {
      conditions.push(or(
        like(weighingTickets.ticketNumber, `%${query.search}%`),
        like(weighingTickets.licensePlate, `%${query.search}%`),
        like(weighingTickets.containerNumber, `%${query.search}%`)
      ));
    }

    const page = query.page || 1;
    const pageSize = query.pageSize || 20;
    const offset = (page - 1) * pageSize;

    // Get total count
    const countResult = await this.db
      .select({ count: sql<number>`count(*)` })
      .from(weighingTickets)
      .where(conditions.length > 0 ? and(...conditions) : undefined);

    const total = countResult[0]?.count || 0;

    // Get paginated results
    const results = await this.db
      .select()
      .from(weighingTickets)
      .where(conditions.length > 0 ? and(...conditions) : undefined)
      .orderBy(desc(weighingTickets.createdAt))
      .limit(pageSize)
      .offset(offset);

    return {
      data: results.map(result => this.mapToDomain(result)),
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize),
      },
    };
  }

  async update(id: string, updates: Partial<DomainWeighingTicket>, tenantId?: string): Promise<DomainWeighingTicket | null> {
    const updateData: any = {
      updatedAt: new Date(),
      version: sql`${weighingTickets.version} + 1`
    };

    if (updates.ticketNumber) updateData.ticketNumber = updates.ticketNumber;
    if (updates.status) updateData.status = updates.status;
    if (updates.licensePlate !== undefined) updateData.licensePlate = updates.licensePlate;
    if (updates.containerNumber !== undefined) updateData.containerNumber = updates.containerNumber;
    if (updates.siloId !== undefined) updateData.siloId = updates.siloId;
    if (updates.commodity) updateData.commodity = updates.commodity;
    if (updates.commodityDescription !== undefined) updateData.commodityDescription = updates.commodityDescription;

    if (updates.grossWeight) {
      updateData.grossWeight = JSON.parse(JSON.stringify(updates.grossWeight));
    }

    if (updates.tareWeight) {
      updateData.tareWeight = JSON.parse(JSON.stringify(updates.tareWeight));
    }

    if (updates.netWeight !== undefined) updateData.netWeight = updates.netWeight?.toString();
    if (updates.netWeightUnit) updateData.netWeightUnit = updates.netWeightUnit;
    if (updates.expectedWeight !== undefined) updateData.expectedWeight = updates.expectedWeight?.toString();
    if (updates.tolerancePercent) updateData.tolerancePercent = updates.tolerancePercent.toString();
    if (updates.isWithinTolerance !== undefined) updateData.isWithinTolerance = updates.isWithinTolerance;

    if (updates.contractId !== undefined) updateData.contractId = updates.contractId;
    if (updates.orderId !== undefined) updateData.orderId = updates.orderId;
    if (updates.deliveryNoteId !== undefined) updateData.deliveryNoteId = updates.deliveryNoteId;
    if (updates.anprRecordId !== undefined) updateData.anprRecordId = updates.anprRecordId;
    if (updates.autoAssigned) updateData.autoAssigned = updates.autoAssigned;
    if (updates.gateId !== undefined) updateData.gateId = updates.gateId;
    if (updates.slotId !== undefined) updateData.slotId = updates.slotId;

    if (updates.completedAt) updateData.completedAt = updates.completedAt;

    const conditions = [eq(weighingTickets.id, id)];
    if (tenantId) {
      conditions.push(eq(weighingTickets.tenantId, tenantId));
    }

    const [result] = await this.db
      .update(weighingTickets)
      .set(updateData)
      .where(and(...conditions))
      .returning();

    return result ? this.mapToDomain(result) : null;
  }

  async delete(id: string, tenantId?: string): Promise<boolean> {
    const conditions = [eq(weighingTickets.id, id)];
    if (tenantId) {
      conditions.push(eq(weighingTickets.tenantId, tenantId));
    }

    const result = await this.db
      .delete(weighingTickets)
      .where(and(...conditions));

    return (result.rowCount || 0) > 0;
  }

  async getNextTicketNumber(tenantId: string, prefix: string = 'WT'): Promise<string> {
    const today = new Date().toISOString().split('T')![0]!.replace(/-/g, '');

    const countResult = await this.db
      .select({ count: sql<number>`count(*)` })
      .from(weighingTickets)
      .where(and(
        eq(weighingTickets.tenantId, tenantId),
        like(weighingTickets.ticketNumber, `${prefix}-${today}%`)
      ));

    const count = countResult[0]?.count || 0;
    const sequence = (count + 1).toString().padStart(4, '0');
    return `${prefix}-${today}-${sequence}`;
  }

  private mapToDomain(dbEntity: any): DomainWeighingTicket {
    const entity: any = {
      id: dbEntity.id,
      tenantId: dbEntity.tenantId,
      ticketNumber: dbEntity.ticketNumber,
      type: dbEntity.type,
      status: dbEntity.status,
      commodity: dbEntity.commodity,
      tolerancePercent: parseFloat(dbEntity.tolerancePercent),
      autoAssigned: dbEntity.auto_assigned,
      createdAt: dbEntity.created_at,
      updatedAt: dbEntity.updated_at,
      version: dbEntity.version,
    };

    if (dbEntity.license_plate) entity.licensePlate = dbEntity.license_plate;
    if (dbEntity.container_number) entity.containerNumber = dbEntity.container_number;
    if (dbEntity.silo_id) entity.siloId = dbEntity.silo_id;
    if (dbEntity.commodity_description) entity.commodityDescription = dbEntity.commodity_description;
    if (dbEntity.gross_weight) entity.grossWeight = dbEntity.gross_weight;
    if (dbEntity.tare_weight) entity.tareWeight = dbEntity.tare_weight;
    if (dbEntity.net_weight) entity.netWeight = parseFloat(dbEntity.net_weight);
    if (dbEntity.net_weight_unit) entity.netWeightUnit = dbEntity.net_weight_unit;
    if (dbEntity.expected_weight) entity.expectedWeight = parseFloat(dbEntity.expected_weight);
    if (dbEntity.is_within_tolerance !== null) entity.isWithinTolerance = dbEntity.is_within_tolerance;
    if (dbEntity.contract_id) entity.contractId = dbEntity.contract_id;
    if (dbEntity.order_id) entity.orderId = dbEntity.order_id;
    if (dbEntity.delivery_note_id) entity.deliveryNoteId = dbEntity.delivery_note_id;
    if (dbEntity.anpr_record_id) entity.anprRecordId = dbEntity.anpr_record_id;
    if (dbEntity.gate_id) entity.gateId = dbEntity.gate_id;
    if (dbEntity.slot_id) entity.slotId = dbEntity.slot_id;
    if (dbEntity.completed_at) entity.completedAt = dbEntity.completed_at;

    return new WeighingTicket(entity);
  }
}