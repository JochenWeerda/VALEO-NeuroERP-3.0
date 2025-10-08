import { v4 as uuidv4 } from 'uuid';
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

export class WeighingService {
  constructor(private ticketRepository: WeighingTicketRepository) {}

  async createTicket(request: CreateWeighingTicketRequest) {
    // Generate ticket number
    const ticketNumber = await this.ticketRepository.getNextTicketNumber(request.tenantId);

    // Create ticket data
    const ticketData: any = {
      id: uuidv4(),
      tenantId: request.tenantId,
      ticketNumber,
      type: request.type,
      status: 'Draft',
      commodity: request.commodity,
      tolerancePercent: request.tolerancePercent || 2,
      autoAssigned: false,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1,
    };

    // Add optional fields only if they exist
    if (request.licensePlate) ticketData.licensePlate = request.licensePlate;
    if (request.containerNumber) ticketData.containerNumber = request.containerNumber;
    if (request.siloId) ticketData.siloId = request.siloId;
    if (request.commodityDescription) ticketData.commodityDescription = request.commodityDescription;
    if (request.expectedWeight) ticketData.expectedWeight = request.expectedWeight;
    if (request.contractId) ticketData.contractId = request.contractId;
    if (request.orderId) ticketData.orderId = request.orderId;
    if (request.deliveryNoteId) ticketData.deliveryNoteId = request.deliveryNoteId;
    if (request.gateId) ticketData.gateId = request.gateId;

    // Save to repository
    return await this.ticketRepository.create(ticketData);
  }

  async getTicket(id: string, tenantId: string) {
    return await this.ticketRepository.findById(id, tenantId);
  }

  async getTicketByNumber(ticketNumber: string, tenantId: string) {
    return await this.ticketRepository.findByTicketNumber(ticketNumber, tenantId);
  }

  async findTicketsByLicensePlate(licensePlate: string, tenantId: string) {
    return await this.ticketRepository.findByLicensePlate(licensePlate, tenantId);
  }

  async recordWeight(request: RecordWeightRequest) {
    // Get ticket
    const ticket = await this.ticketRepository.findById(request.ticketId, request.tenantId);
    if (ticket === undefined || ticket === null) {
      throw new Error('Ticket not found');
    }

    // Basic validation - only allow draft or in-progress tickets
    if (ticket.status === 'Completed' || ticket.status === 'Cancelled') {
      throw new Error('Ticket cannot be modified');
    }

    // Create weight data
    const weightData = {
      weight: request.weight,
      unit: request.unit,
      timestamp: new Date().toISOString(),
      scaleId: request.scaleId,
      operatorId: request.operatorId || undefined,
      notes: request.notes || undefined,
    };

    // Update ticket based on mode
    const updates: any = {};

    if (request.mode === 'Gross') {
      updates.grossWeight = weightData;
      updates.status = ticket.status === 'Draft' ? 'InProgress' : ticket.status;
    } else if (request.mode === 'Tare') {
      updates.tareWeight = weightData;
      updates.status = ticket.status === 'Draft' ? 'InProgress' : ticket.status;
    } else {
      throw new Error('Invalid weighing mode');
    }

    // Calculate net weight if both gross and tare are available
    if ((request.mode === 'Gross' && ticket.tareWeight) || (request.mode === 'Tare' && ticket.grossWeight)) {
      const gross = request.mode === 'Gross' ? request.weight : ticket.grossWeight?.weight || 0;
      const tare = request.mode === 'Tare' ? request.weight : ticket.tareWeight?.weight || 0;
      const netWeight = gross - tare;

      updates.netWeight = netWeight.toString();
      updates.netWeightUnit = request.unit;

      // Check tolerance if expected weight is set
      if (ticket.expectedWeight) {
        const tolerance = (ticket.expectedWeight * ticket.tolerancePercent) / 100;
        updates.isWithinTolerance = Math.abs(netWeight - ticket.expectedWeight) <= tolerance;
      }
    }

    // Save changes
    const updatedTicket = await this.ticketRepository.update(request.ticketId, updates, request.tenantId);

    if (updatedTicket === undefined || updatedTicket === null) {
      throw new Error('Failed to update ticket');
    }

    return updatedTicket;
  }

  async completeTicket(id: string, tenantId: string) {
    const ticket = await this.ticketRepository.findById(id, tenantId);
    if (ticket === undefined || ticket === null) {
      throw new Error('Ticket not found');
    }

    if (ticket.status === 'Completed') {
      throw new Error('Ticket is already completed');
    }

    // Basic validation - should have net weight
    if (ticket.netWeight === undefined || ticket.netWeight === null) {
      throw new Error('Ticket must have net weight to be completed');
    }

    const updatedTicket = await this.ticketRepository.update(id, {
      status: 'Completed',
      completedAt: new Date(),
    }, tenantId);

    if (updatedTicket === undefined || updatedTicket === null) {
      throw new Error('Failed to complete ticket');
    }

    return updatedTicket;
  }

  async cancelTicket(id: string, tenantId: string, reason?: string) {
    const ticket = await this.ticketRepository.findById(id, tenantId);
    if (ticket === undefined || ticket === null) {
      throw new Error('Ticket not found');
    }

    const updatedTicket = await this.ticketRepository.update(id, {
      status: 'Cancelled',
    }, tenantId);

    if (updatedTicket === undefined || updatedTicket === null) {
      throw new Error('Failed to cancel ticket');
    }

    return updatedTicket;
  }

  async updateTicket(
    id: string,
    tenantId: string,
    updates: Partial<{
      commodityDescription: string;
      expectedWeight: number;
      tolerancePercent: number;
      contractId: string;
      orderId: string;
      deliveryNoteId: string;
      gateId: string;
    }>
  ) {
    const ticket = await this.ticketRepository.findById(id, tenantId);
    if (ticket === undefined || ticket === null) {
      throw new Error('Ticket not found');
    }

    // Only allow updates on draft or in-progress tickets
    if (ticket.status === 'Completed' || ticket.status === 'Cancelled') {
      throw new Error('Ticket cannot be modified');
    }

    const updatedTicket = await this.ticketRepository.update(id, updates, tenantId);
    if (updatedTicket === undefined || updatedTicket === null) {
      throw new Error('Failed to update ticket');
    }

    return updatedTicket;
  }

  async getTickets(
    tenantId: string,
    filters?: {
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
    },
    pagination?: {
      page?: number;
      pageSize?: number;
    }
  ) {
    return await this.ticketRepository.findMany({
      tenantId,
      ...filters,
      ...pagination,
    });
  }

  async deleteTicket(id: string, tenantId: string): Promise<boolean> {
    const ticket = await this.ticketRepository.findById(id, tenantId);
    if (ticket === undefined || ticket === null) {
      return false;
    }

    // Only allow deletion of draft tickets
    if (ticket.status !== 'Draft') {
      throw new Error('Only draft tickets can be deleted');
    }

    return await this.ticketRepository.delete(id, tenantId);
  }

  async getActiveTickets(tenantId: string) {
    const result = await this.ticketRepository.findMany({
      tenantId,
      status: 'InProgress',
    });

    return result.data;
  }

  async getCompletedTicketsToday(tenantId: string) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const result = await this.ticketRepository.findMany({
      tenantId,
      status: 'Completed',
      fromDate: today,
      toDate: tomorrow,
    });

    return result.data;
  }
}

