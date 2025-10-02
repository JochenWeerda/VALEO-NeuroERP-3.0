"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighingService = void 0;
const uuid_1 = require("uuid");
class WeighingService {
    ticketRepository;
    constructor(ticketRepository) {
        this.ticketRepository = ticketRepository;
    }
    async createTicket(request) {
        const ticketNumber = await this.ticketRepository.getNextTicketNumber(request.tenantId);
        const ticketData = {
            id: (0, uuid_1.v4)(),
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
        if (request.licensePlate)
            ticketData.licensePlate = request.licensePlate;
        if (request.containerNumber)
            ticketData.containerNumber = request.containerNumber;
        if (request.siloId)
            ticketData.siloId = request.siloId;
        if (request.commodityDescription)
            ticketData.commodityDescription = request.commodityDescription;
        if (request.expectedWeight)
            ticketData.expectedWeight = request.expectedWeight;
        if (request.contractId)
            ticketData.contractId = request.contractId;
        if (request.orderId)
            ticketData.orderId = request.orderId;
        if (request.deliveryNoteId)
            ticketData.deliveryNoteId = request.deliveryNoteId;
        if (request.gateId)
            ticketData.gateId = request.gateId;
        return await this.ticketRepository.create(ticketData);
    }
    async getTicket(id, tenantId) {
        return await this.ticketRepository.findById(id, tenantId);
    }
    async getTicketByNumber(ticketNumber, tenantId) {
        return await this.ticketRepository.findByTicketNumber(ticketNumber, tenantId);
    }
    async findTicketsByLicensePlate(licensePlate, tenantId) {
        return await this.ticketRepository.findByLicensePlate(licensePlate, tenantId);
    }
    async recordWeight(request) {
        const ticket = await this.ticketRepository.findById(request.ticketId, request.tenantId);
        if (!ticket) {
            throw new Error('Ticket not found');
        }
        if (ticket.status === 'Completed' || ticket.status === 'Cancelled') {
            throw new Error('Ticket cannot be modified');
        }
        const weightData = {
            weight: request.weight,
            unit: request.unit,
            timestamp: new Date().toISOString(),
            scaleId: request.scaleId,
            operatorId: request.operatorId || undefined,
            notes: request.notes || undefined,
        };
        const updates = {};
        if (request.mode === 'Gross') {
            updates.grossWeight = weightData;
            updates.status = ticket.status === 'Draft' ? 'InProgress' : ticket.status;
        }
        else if (request.mode === 'Tare') {
            updates.tareWeight = weightData;
            updates.status = ticket.status === 'Draft' ? 'InProgress' : ticket.status;
        }
        else {
            throw new Error('Invalid weighing mode');
        }
        if ((request.mode === 'Gross' && ticket.tareWeight) || (request.mode === 'Tare' && ticket.grossWeight)) {
            const gross = request.mode === 'Gross' ? request.weight : ticket.grossWeight?.weight || 0;
            const tare = request.mode === 'Tare' ? request.weight : ticket.tareWeight?.weight || 0;
            const netWeight = gross - tare;
            updates.netWeight = netWeight.toString();
            updates.netWeightUnit = request.unit;
            if (ticket.expectedWeight) {
                const tolerance = (ticket.expectedWeight * ticket.tolerancePercent) / 100;
                updates.isWithinTolerance = Math.abs(netWeight - ticket.expectedWeight) <= tolerance;
            }
        }
        const updatedTicket = await this.ticketRepository.update(request.ticketId, updates, request.tenantId);
        if (!updatedTicket) {
            throw new Error('Failed to update ticket');
        }
        return updatedTicket;
    }
    async completeTicket(id, tenantId) {
        const ticket = await this.ticketRepository.findById(id, tenantId);
        if (!ticket) {
            throw new Error('Ticket not found');
        }
        if (ticket.status === 'Completed') {
            throw new Error('Ticket is already completed');
        }
        if (!ticket.netWeight) {
            throw new Error('Ticket must have net weight to be completed');
        }
        const updatedTicket = await this.ticketRepository.update(id, {
            status: 'Completed',
            completedAt: new Date(),
        }, tenantId);
        if (!updatedTicket) {
            throw new Error('Failed to complete ticket');
        }
        return updatedTicket;
    }
    async cancelTicket(id, tenantId, reason) {
        const ticket = await this.ticketRepository.findById(id, tenantId);
        if (!ticket) {
            throw new Error('Ticket not found');
        }
        const updatedTicket = await this.ticketRepository.update(id, {
            status: 'Cancelled',
        }, tenantId);
        if (!updatedTicket) {
            throw new Error('Failed to cancel ticket');
        }
        return updatedTicket;
    }
    async updateTicket(id, tenantId, updates) {
        const ticket = await this.ticketRepository.findById(id, tenantId);
        if (!ticket) {
            throw new Error('Ticket not found');
        }
        if (ticket.status === 'Completed' || ticket.status === 'Cancelled') {
            throw new Error('Ticket cannot be modified');
        }
        const updatedTicket = await this.ticketRepository.update(id, updates, tenantId);
        if (!updatedTicket) {
            throw new Error('Failed to update ticket');
        }
        return updatedTicket;
    }
    async getTickets(tenantId, filters, pagination) {
        return await this.ticketRepository.findMany({
            tenantId,
            ...filters,
            ...pagination,
        });
    }
    async deleteTicket(id, tenantId) {
        const ticket = await this.ticketRepository.findById(id, tenantId);
        if (!ticket) {
            return false;
        }
        if (ticket.status !== 'Draft') {
            throw new Error('Only draft tickets can be deleted');
        }
        return await this.ticketRepository.delete(id, tenantId);
    }
    async getActiveTickets(tenantId) {
        const result = await this.ticketRepository.findMany({
            tenantId,
            status: 'InProgress',
        });
        return result.data;
    }
    async getCompletedTicketsToday(tenantId) {
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
exports.WeighingService = WeighingService;
//# sourceMappingURL=weighing-service.js.map