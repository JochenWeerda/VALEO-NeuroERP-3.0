"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpportunityEntity = exports.UpdateOpportunityInputSchema = exports.CreateOpportunityInputSchema = exports.OpportunitySchema = exports.OpportunityStage = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Enums
exports.OpportunityStage = {
    LEAD: 'Lead',
    QUALIFIED: 'Qualified',
    PROPOSAL: 'Proposal',
    WON: 'Won',
    LOST: 'Lost'
};
// Opportunity Entity Schema
exports.OpportunitySchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    title: zod_1.z.string().min(1),
    stage: zod_1.z.enum([
        exports.OpportunityStage.LEAD,
        exports.OpportunityStage.QUALIFIED,
        exports.OpportunityStage.PROPOSAL,
        exports.OpportunityStage.WON,
        exports.OpportunityStage.LOST
    ]),
    expectedCloseDate: zod_1.z.date().optional(),
    amountNet: zod_1.z.number().nonnegative().optional(),
    currency: zod_1.z.string().length(3).optional(), // ISO 4217 currency code
    probability: zod_1.z.number().min(0).max(1), // 0-1 (0% to 100%)
    ownerUserId: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Opportunity Input Schema (for API)
exports.CreateOpportunityInputSchema = exports.OpportunitySchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true
});
// Update Opportunity Input Schema (for API)
exports.UpdateOpportunityInputSchema = zod_1.z.object({
    title: zod_1.z.string().min(1).optional(),
    stage: zod_1.z.enum([
        exports.OpportunityStage.LEAD,
        exports.OpportunityStage.QUALIFIED,
        exports.OpportunityStage.PROPOSAL,
        exports.OpportunityStage.WON,
        exports.OpportunityStage.LOST
    ]).optional(),
    expectedCloseDate: zod_1.z.date().nullish(),
    amountNet: zod_1.z.number().nonnegative().nullish(),
    currency: zod_1.z.string().length(3).nullish(),
    probability: zod_1.z.number().min(0).max(1).optional(),
    ownerUserId: zod_1.z.string().uuid().nullish()
});
// Opportunity Aggregate Root
class OpportunityEntity {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        const now = new Date();
        const opportunity = {
            ...props,
            id: (0, uuid_1.v4)(),
            stage: props.stage || exports.OpportunityStage.LEAD,
            probability: props.probability !== undefined ? props.probability : 0.1, // Default 10% for leads
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new OpportunityEntity(opportunity);
    }
    static fromPersistence(props) {
        return new OpportunityEntity({
            ...props,
            ownerUserId: props.ownerUserId ?? undefined,
            expectedCloseDate: props.expectedCloseDate ?? undefined,
            amountNet: props.amountNet ? Number(props.amountNet) : undefined,
            currency: props.currency ?? undefined,
        });
    }
    update(props) {
        if (props.title !== undefined) {
            this.props.title = props.title;
        }
        if (props.stage !== undefined) {
            this.props.stage = props.stage;
        }
        if (props.expectedCloseDate !== undefined) {
            this.props.expectedCloseDate = props.expectedCloseDate;
        }
        if (props.amountNet !== undefined) {
            this.props.amountNet = props.amountNet;
        }
        if (props.currency !== undefined) {
            this.props.currency = props.currency;
        }
        if (props.probability !== undefined) {
            this.props.probability = props.probability;
        }
        if (props.ownerUserId !== undefined) {
            this.props.ownerUserId = props.ownerUserId;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    changeStage(newStage) {
        if (this.props.stage !== newStage) {
            this.props.stage = newStage;
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    markAsWon() {
        this.props.stage = exports.OpportunityStage.WON;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    markAsLost() {
        this.props.stage = exports.OpportunityStage.LOST;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    updateProbability(probability) {
        if (probability < 0 || probability > 1) {
            throw new Error('Probability must be between 0 and 1');
        }
        this.props.probability = probability;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    updateAmount(amountNet, currency) {
        this.props.amountNet = amountNet;
        if (currency !== undefined) {
            this.props.currency = currency;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    updateExpectedCloseDate(date) {
        this.props.expectedCloseDate = date;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    // Business logic methods
    isOpen() {
        return this.props.stage !== exports.OpportunityStage.WON && this.props.stage !== exports.OpportunityStage.LOST;
    }
    isWon() {
        return this.props.stage === exports.OpportunityStage.WON;
    }
    isLost() {
        return this.props.stage === exports.OpportunityStage.LOST;
    }
    getWeightedValue() {
        if (!this.props.amountNet)
            return 0;
        return this.props.amountNet * this.props.probability;
    }
    // Getters
    get id() { return this.props.id; }
    get tenantId() { return this.props.tenantId; }
    get customerId() { return this.props.customerId; }
    get title() { return this.props.title; }
    get stage() { return this.props.stage; }
    get expectedCloseDate() { return this.props.expectedCloseDate; }
    get amountNet() { return this.props.amountNet; }
    get currency() { return this.props.currency; }
    get probability() { return this.props.probability; }
    get ownerUserId() { return this.props.ownerUserId; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...opportunityWithoutTenant } = this.props;
        return opportunityWithoutTenant;
    }
}
exports.OpportunityEntity = OpportunityEntity;
//# sourceMappingURL=opportunity.js.map