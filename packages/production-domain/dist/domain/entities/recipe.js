"use strict";
/**
 * Recipe Entity for VALEO NeuroERP 3.0 Production Domain
 * Recipe management with GMP+/QS compliance and sequencing rules
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecipeEntity = exports.RecipeSchema = void 0;
const zod_1 = require("zod");
// Recipe Line Schema
const RecipeLineSchema = zod_1.z.object({
    ingredientSku: zod_1.z.string().min(1).max(100),
    inclusionKgOrPercent: zod_1.z.number().positive(),
    seqOrder: zod_1.z.number().int().min(1),
    isPremix: zod_1.z.boolean().default(false)
});
// QA Requirements Schema
const QARequirementsSchema = zod_1.z.object({
    requiresFlushAfter: zod_1.z.boolean().default(false),
    medicated: zod_1.z.boolean().default(false),
    allergenTags: zod_1.z.array(zod_1.z.string()).default([])
});
// Main Recipe Schema
exports.RecipeSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    code: zod_1.z.string().min(1).max(50),
    name: zod_1.z.string().min(1).max(200),
    version: zod_1.z.number().int().min(1).default(1),
    status: zod_1.z.enum(['Active', 'Archived']).default('Active'),
    targetBatchSizeKg: zod_1.z.number().positive(),
    tolerancePercent: zod_1.z.number().min(0).max(100).default(5),
    lines: zod_1.z.array(RecipeLineSchema).min(1),
    qa: QARequirementsSchema,
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class RecipeEntity {
    data;
    constructor(data) {
        this.data = exports.RecipeSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get code() { return this.data.code; }
    get name() { return this.data.name; }
    get version() { return this.data.version; }
    get status() { return this.data.status; }
    get targetBatchSizeKg() { return this.data.targetBatchSizeKg; }
    get tolerancePercent() { return this.data.tolerancePercent; }
    get lines() { return [...this.data.lines]; }
    get qa() { return this.data.qa; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    isActive() {
        return this.data.status === 'Active';
    }
    isArchived() {
        return this.data.status === 'Archived';
    }
    isMedicated() {
        return this.data.qa.medicated;
    }
    hasAllergens() {
        return this.data.qa.allergenTags.length > 0;
    }
    requiresFlushAfter() {
        return this.data.qa.requiresFlushAfter;
    }
    getTotalInclusionPercent() {
        const percentLines = this.data.lines.filter(line => line.inclusionKgOrPercent <= 100 // Assuming values <= 100 are percentages
        );
        return percentLines.reduce((sum, line) => sum + line.inclusionKgOrPercent, 0);
    }
    getTotalInclusionKg() {
        const kgLines = this.data.lines.filter(line => line.inclusionKgOrPercent > 100 // Assuming values > 100 are kg amounts
        );
        return kgLines.reduce((sum, line) => sum + line.inclusionKgOrPercent, 0);
    }
    getSortedLines() {
        return [...this.data.lines].sort((a, b) => a.seqOrder - b.seqOrder);
    }
    getPremixLines() {
        return this.data.lines.filter(line => line.isPremix);
    }
    getIngredientSkus() {
        return this.data.lines.map(line => line.ingredientSku);
    }
    // Validation
    validateBusinessRules() {
        // Check for duplicate sequence orders
        const seqOrders = this.data.lines.map(line => line.seqOrder);
        const uniqueSeqOrders = new Set(seqOrders);
        if (seqOrders.length !== uniqueSeqOrders.size) {
            throw new Error('Duplicate sequence orders found in recipe lines');
        }
        // Check for duplicate ingredient SKUs
        const skus = this.data.lines.map(line => line.ingredientSku);
        const uniqueSkus = new Set(skus);
        if (skus.length !== uniqueSkus.size) {
            throw new Error('Duplicate ingredient SKUs found in recipe lines');
        }
        // Validate total inclusion percentage (should be close to 100%)
        const totalPercent = this.getTotalInclusionPercent();
        if (totalPercent > 105 || totalPercent < 95) {
            console.warn(`Total inclusion percentage is ${totalPercent}%, expected ~100%`);
        }
        // Medicated recipes must require flush after
        if (this.data.qa.medicated && !this.data.qa.requiresFlushAfter) {
            throw new Error('Medicated recipes must require flush after production');
        }
    }
    // State Changes
    archive(updatedBy) {
        if (this.isArchived()) {
            return this;
        }
        return new RecipeEntity({
            ...this.data,
            status: 'Archived',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    activate(updatedBy) {
        if (this.isActive()) {
            return this;
        }
        return new RecipeEntity({
            ...this.data,
            status: 'Active',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateTargetBatchSize(targetBatchSizeKg, updatedBy) {
        if (targetBatchSizeKg <= 0) {
            throw new Error('Target batch size must be positive');
        }
        return new RecipeEntity({
            ...this.data,
            targetBatchSizeKg,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateTolerance(tolerancePercent, updatedBy) {
        if (tolerancePercent < 0 || tolerancePercent > 100) {
            throw new Error('Tolerance must be between 0 and 100 percent');
        }
        return new RecipeEntity({
            ...this.data,
            tolerancePercent,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addLine(line, updatedBy) {
        const maxSeqOrder = Math.max(...this.data.lines.map(l => l.seqOrder), 0);
        const newLine = {
            ...line,
            seqOrder: maxSeqOrder + 1
        };
        return new RecipeEntity({
            ...this.data,
            lines: [...this.data.lines, newLine],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    removeLine(ingredientSku, updatedBy) {
        const filteredLines = this.data.lines.filter(line => line.ingredientSku !== ingredientSku);
        if (filteredLines.length === this.data.lines.length) {
            throw new Error(`Ingredient SKU ${ingredientSku} not found in recipe`);
        }
        return new RecipeEntity({
            ...this.data,
            lines: filteredLines,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateQARequirements(qa, updatedBy) {
        const newQA = { ...this.data.qa, ...qa };
        // Validate medicated + flush requirement
        if (newQA.medicated && !newQA.requiresFlushAfter) {
            throw new Error('Medicated recipes must require flush after production');
        }
        return new RecipeEntity({
            ...this.data,
            qa: newQA,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new RecipeEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now,
            version: 1
        });
    }
    static fromJSON(data) {
        return new RecipeEntity(data);
    }
}
exports.RecipeEntity = RecipeEntity;
//# sourceMappingURL=recipe.js.map