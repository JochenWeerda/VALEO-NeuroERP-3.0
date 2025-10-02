"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpportunityService = void 0;
class OpportunityService {
    deps;
    constructor(deps) {
        this.deps = deps;
    }
    async createOpportunity(data) {
        // Business validation
        if (data.amountNet && data.amountNet < 0) {
            throw new Error('Opportunity amount cannot be negative');
        }
        if (data.probability !== undefined && (data.probability < 0 || data.probability > 1)) {
            throw new Error('Opportunity probability must be between 0 and 1');
        }
        const opportunity = await this.deps.opportunityRepo.create(data);
        return opportunity;
    }
    async getOpportunity(id, tenantId) {
        return this.deps.opportunityRepo.findById(id, tenantId);
    }
    async getOpportunitiesByCustomer(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        return this.deps.opportunityRepo.findByCustomerId(customerId, tenantId, filters, pagination);
    }
    async updateOpportunity(id, data) {
        const existingOpportunity = await this.deps.opportunityRepo.findById(id, data.tenantId);
        if (!existingOpportunity) {
            throw new Error(`Opportunity ${id} not found`);
        }
        // Business validation
        if (data.amountNet !== undefined && data.amountNet < 0) {
            throw new Error('Opportunity amount cannot be negative');
        }
        if (data.probability !== undefined && (data.probability < 0 || data.probability > 1)) {
            throw new Error('Opportunity probability must be between 0 and 1');
        }
        // Business rules for stage changes
        if (data.stage && data.stage !== existingOpportunity.stage) {
            this.validateStageTransition(existingOpportunity.stage, data.stage);
        }
        const updatedOpportunity = await this.deps.opportunityRepo.update(id, data.tenantId, data);
        if (!updatedOpportunity) {
            throw new Error(`Failed to update opportunity ${id}`);
        }
        return updatedOpportunity;
    }
    async changeOpportunityStage(id, tenantId, stage) {
        const opportunity = await this.deps.opportunityRepo.findById(id, tenantId);
        if (!opportunity) {
            throw new Error(`Opportunity ${id} not found`);
        }
        this.validateStageTransition(opportunity.stage, stage);
        const updatedOpportunity = await this.deps.opportunityRepo.updateStage(id, tenantId, stage);
        if (!updatedOpportunity) {
            throw new Error(`Failed to update opportunity stage`);
        }
        return updatedOpportunity;
    }
    async markOpportunityAsWon(id, tenantId) {
        const opportunity = await this.deps.opportunityRepo.findById(id, tenantId);
        if (!opportunity) {
            throw new Error(`Opportunity ${id} not found`);
        }
        if (opportunity.isWon()) {
            return opportunity; // Already won
        }
        if (opportunity.isLost()) {
            throw new Error('Cannot mark a lost opportunity as won');
        }
        const updatedOpportunity = await this.deps.opportunityRepo.markAsWon(id, tenantId);
        if (!updatedOpportunity) {
            throw new Error(`Failed to mark opportunity as won`);
        }
        return updatedOpportunity;
    }
    async markOpportunityAsLost(id, tenantId) {
        const opportunity = await this.deps.opportunityRepo.findById(id, tenantId);
        if (!opportunity) {
            throw new Error(`Opportunity ${id} not found`);
        }
        if (opportunity.isLost()) {
            return opportunity; // Already lost
        }
        if (opportunity.isWon()) {
            throw new Error('Cannot mark a won opportunity as lost');
        }
        const updatedOpportunity = await this.deps.opportunityRepo.markAsLost(id, tenantId);
        if (!updatedOpportunity) {
            throw new Error(`Failed to mark opportunity as lost`);
        }
        return updatedOpportunity;
    }
    async deleteOpportunity(id, tenantId) {
        const opportunity = await this.deps.opportunityRepo.findById(id, tenantId);
        if (!opportunity) {
            throw new Error(`Opportunity ${id} not found`);
        }
        // Business rule: don't allow deletion of won opportunities
        if (opportunity.isWon()) {
            throw new Error('Cannot delete a won opportunity');
        }
        return this.deps.opportunityRepo.delete(id, tenantId);
    }
    async getOpenOpportunities(tenantId) {
        return this.deps.opportunityRepo.getOpenOpportunities(tenantId);
    }
    async getOpportunitiesByStage(stage, tenantId) {
        return this.deps.opportunityRepo.getByStage(stage, tenantId);
    }
    validateStageTransition(currentStage, newStage) {
        // Define valid stage transitions
        const validTransitions = {
            'Lead': ['Qualified', 'Lost'],
            'Qualified': ['Proposal', 'Lost'],
            'Proposal': ['Won', 'Lost'],
            'Won': [], // Terminal stage
            'Lost': [] // Terminal stage
        };
        const allowedStages = validTransitions[currentStage];
        if (!allowedStages?.includes(newStage)) {
            throw new Error(`Cannot change stage from ${currentStage} to ${newStage}`);
        }
    }
}
exports.OpportunityService = OpportunityService;
//# sourceMappingURL=opportunity-service.js.map