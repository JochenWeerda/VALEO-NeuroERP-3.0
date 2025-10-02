"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionService = void 0;
const uuid_1 = require("uuid");
class InteractionService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createInteraction(data) {
        // Business validation
        if (data.occurredAt > new Date()) {
            throw new Error('Interaction cannot be scheduled for the future');
        }
        const interaction = await this.deps.interactionRepo.create(data);
        return interaction;
    }
    async getInteraction(id, tenantId) {
        return this.deps.interactionRepo.findById(id, tenantId);
    }
    async getInteractionsByCustomer(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.interactionRepo.findByCustomerId(customerId, tenantId, filters, pagination);
    }
    async updateInteraction(id, data) {
        const existingInteraction = await this.deps.interactionRepo.findById(id, data.tenantId);
        if (!existingInteraction) {
            throw new Error(`Interaction ${id} not found`);
        }
        // Business validation
        if (data.occurredAt && data.occurredAt > new Date()) {
            throw new Error('Interaction cannot be scheduled for the future');
        }
        const updatedInteraction = await this.deps.interactionRepo.update(id, data.tenantId, data);
        if (!updatedInteraction) {
            throw new Error(`Failed to update interaction ${id}`);
        }
        return updatedInteraction;
    }
    async deleteInteraction(id, tenantId) {
        const interaction = await this.deps.interactionRepo.findById(id, tenantId);
        if (!interaction) {
            throw new Error(`Interaction ${id} not found`);
        }
        return this.deps.interactionRepo.delete(id, tenantId);
    }
    async getUpcomingInteractions(tenantId, from) {
        return this.deps.interactionRepo.getUpcomingInteractions(tenantId, from);
    }
    async getOverdueInteractions(tenantId) {
        return this.deps.interactionRepo.getOverdueInteractions(tenantId);
    }
    async getTodaysInteractions(tenantId) {
        return this.deps.interactionRepo.getTodaysInteractions(tenantId);
    }
    async getInteractionsByType(type, tenantId) {
        return this.deps.interactionRepo.getByType(type, tenantId);
    }
    async addAttachment(interactionId, tenantId, attachment) {
        const interaction = await this.deps.interactionRepo.findById(interactionId, tenantId);
        if (!interaction) {
            throw new Error(`Interaction ${interactionId} not found`);
        }
        // Create attachment with ID
        const newAttachment = {
            id: (0, uuid_1.v4)(),
            ...attachment
        };
        // Update interaction with new attachment
        const updatedInteraction = await this.deps.interactionRepo.update(interactionId, tenantId, {
            attachments: [...interaction.attachments, newAttachment]
        });
        if (!updatedInteraction) {
            throw new Error(`Failed to add attachment to interaction`);
        }
        return updatedInteraction;
    }
    async removeAttachment(interactionId, tenantId, attachmentId) {
        const interaction = await this.deps.interactionRepo.findById(interactionId, tenantId);
        if (!interaction) {
            throw new Error(`Interaction ${interactionId} not found`);
        }
        const attachmentExists = interaction.attachments.some(att => att.id === attachmentId);
        if (!attachmentExists) {
            throw new Error(`Attachment ${attachmentId} not found`);
        }
        const updatedAttachments = interaction.attachments.filter(att => att.id !== attachmentId);
        const updatedInteraction = await this.deps.interactionRepo.update(interactionId, tenantId, { attachments: updatedAttachments });
        if (!updatedInteraction) {
            throw new Error(`Failed to remove attachment from interaction`);
        }
        return updatedInteraction;
    }
}
exports.InteractionService = InteractionService;
//# sourceMappingURL=interaction-service.js.map