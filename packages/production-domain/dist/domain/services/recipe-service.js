"use strict";
/**
 * Recipe Service for VALEO NeuroERP 3.0 Production Domain
 * Business logic for recipe management with GMP+/QS compliance
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecipeServiceImpl = void 0;
const recipe_1 = require("../entities/recipe");
const event_factories_1 = require("../events/event-factories");
class RecipeServiceImpl {
    recipeRepository;
    eventPublisher;
    constructor(recipeRepository, eventPublisher) {
        this.recipeRepository = recipeRepository;
        this.eventPublisher = eventPublisher;
    }
    async createRecipe(input, tenantId, userId) {
        // Validate recipe code uniqueness
        const existingRecipe = await this.recipeRepository.findByCode(tenantId, input.code);
        if (existingRecipe) {
            throw new Error(`Recipe with code ${input.code} already exists`);
        }
        // Create recipe entity
        const recipe = recipe_1.RecipeEntity.create({
            tenantId,
            code: input.code,
            name: input.name,
            status: 'Active',
            targetBatchSizeKg: input.targetBatchSizeKg,
            tolerancePercent: input.tolerancePercent || 5,
            lines: input.lines.map(line => ({
                ingredientSku: line.ingredientSku,
                inclusionKgOrPercent: line.inclusionKgOrPercent,
                seqOrder: line.seqOrder,
                isPremix: line.isPremix || false
            })),
            qa: {
                requiresFlushAfter: input.qa.requiresFlushAfter || false,
                medicated: input.qa.medicated || false,
                allergenTags: input.qa.allergenTags || []
            },
            createdBy: userId
        });
        // Validate business rules
        const validation = await this.validateRecipe(recipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, recipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeCreatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            medicated: savedRecipe.qa.medicated,
            allergenTags: savedRecipe.qa.allergenTags
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async updateRecipe(id, input, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const changes = [];
        // Update fields
        if (input.name && input.name !== recipe.name) {
            recipe.updateTargetBatchSize(input.targetBatchSizeKg, userId);
            changes.push('name');
        }
        if (input.targetBatchSizeKg && input.targetBatchSizeKg !== recipe.targetBatchSizeKg) {
            recipe.updateTargetBatchSize(input.targetBatchSizeKg, userId);
            changes.push('targetBatchSizeKg');
        }
        if (input.tolerancePercent && input.tolerancePercent !== recipe.tolerancePercent) {
            recipe.updateTolerance(input.tolerancePercent, userId);
            changes.push('tolerancePercent');
        }
        if (changes.length === 0) {
            return recipe;
        }
        // Validate updated recipe
        const validation = await this.validateRecipe(recipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save updated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, recipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async archiveRecipe(id, reason, tenantId, userId) {
        if (!tenantId || !userId) {
            throw new Error('TenantId and userId are required');
        }
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const archivedRecipe = recipe.archive(userId);
        // Save archived recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, archivedRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeArchivedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            reason
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async activateRecipe(id, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const activatedRecipe = recipe.activate(userId);
        // Save activated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, activatedRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes: ['status']
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async getRecipe(id, tenantId) {
        const recipe = await this.recipeRepository.findById(tenantId, id);
        return recipe ? recipe_1.RecipeEntity.fromJSON(recipe) : null;
    }
    async getRecipeByCode(code, tenantId) {
        const recipe = await this.recipeRepository.findByCode(tenantId, code);
        return recipe ? recipe_1.RecipeEntity.fromJSON(recipe) : null;
    }
    async listRecipes(filters, tenantId) {
        const recipes = await this.recipeRepository.findAll(tenantId, filters);
        return recipes.map(recipe => recipe_1.RecipeEntity.fromJSON(recipe));
    }
    async listActiveRecipes(tenantId) {
        const recipes = await this.recipeRepository.findActive(tenantId);
        return recipes.map(recipe => recipe_1.RecipeEntity.fromJSON(recipe));
    }
    async listMedicatedRecipes(tenantId) {
        const recipes = await this.recipeRepository.findMedicated(tenantId);
        return recipes.map(recipe => recipe_1.RecipeEntity.fromJSON(recipe));
    }
    async addRecipeLine(id, line, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const updatedRecipe = recipe.addLine({
            ingredientSku: line.ingredientSku,
            inclusionKgOrPercent: line.inclusionKgOrPercent,
            isPremix: line.isPremix || false
        }, userId);
        // Validate updated recipe
        const validation = await this.validateRecipe(updatedRecipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save updated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes: ['lines']
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async removeRecipeLine(id, ingredientSku, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const updatedRecipe = recipe.removeLine(ingredientSku, userId);
        // Validate updated recipe
        const validation = await this.validateRecipe(updatedRecipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save updated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes: ['lines']
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async updateRecipeLine(id, ingredientSku, line, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        // Find and update the line
        const lines = recipe.lines;
        const lineIndex = lines.findIndex(l => l.ingredientSku === ingredientSku);
        if (lineIndex === -1) {
            throw new Error(`Recipe line with ingredient SKU ${ingredientSku} not found`);
        }
        const updatedLine = { ...lines[lineIndex], ...line };
        const updatedRecipe = recipe.removeLine(ingredientSku, userId);
        const finalRecipe = updatedRecipe.addLine(updatedLine, userId);
        // Validate updated recipe
        const validation = await this.validateRecipe(finalRecipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save updated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, finalRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes: ['lines']
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async updateQARequirements(id, qa, tenantId, userId) {
        const existingRecipe = await this.recipeRepository.findById(tenantId, id);
        if (!existingRecipe) {
            throw new Error(`Recipe with id ${id} not found`);
        }
        const recipe = recipe_1.RecipeEntity.fromJSON(existingRecipe);
        const updatedRecipe = recipe.updateQARequirements(qa, userId);
        // Validate updated recipe
        const validation = await this.validateRecipe(updatedRecipe);
        if (!validation.valid) {
            throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
        }
        // Save updated recipe
        const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());
        // Emit domain event
        await this.eventPublisher((0, event_factories_1.createRecipeUpdatedEvent)({
            id: savedRecipe.id,
            code: savedRecipe.code,
            name: savedRecipe.name,
            version: savedRecipe.version,
            changes: ['qa']
        }, tenantId));
        return recipe_1.RecipeEntity.fromJSON(savedRecipe);
    }
    async validateRecipe(recipe) {
        const errors = [];
        const warnings = [];
        // Check total inclusion percentage
        const totalPercent = recipe.getTotalInclusionPercent();
        if (totalPercent > 105) {
            warnings.push(`Total inclusion percentage is ${totalPercent}%, which exceeds 105%`);
        }
        else if (totalPercent < 95) {
            warnings.push(`Total inclusion percentage is ${totalPercent}%, which is below 95%`);
        }
        // Check for duplicate sequence orders
        const seqOrders = recipe.lines.map(line => line.seqOrder);
        const uniqueSeqOrders = new Set(seqOrders);
        if (seqOrders.length !== uniqueSeqOrders.size) {
            errors.push('Duplicate sequence orders found in recipe lines');
        }
        // Check for duplicate ingredient SKUs
        const skus = recipe.lines.map(line => line.ingredientSku);
        const uniqueSkus = new Set(skus);
        if (skus.length !== uniqueSkus.size) {
            errors.push('Duplicate ingredient SKUs found in recipe lines');
        }
        // Medicated recipes must require flush after
        if (recipe.isMedicated() && !recipe.requiresFlushAfter()) {
            errors.push('Medicated recipes must require flush after production');
        }
        return {
            valid: errors.length === 0,
            errors,
            warnings
        };
    }
    async checkSequencingCompatibility(recipe1Id, recipe2Id, tenantId) {
        const recipe1 = await this.getRecipe(recipe1Id, tenantId);
        const recipe2 = await this.getRecipe(recipe2Id, tenantId);
        if (!recipe1 || !recipe2) {
            throw new Error('One or both recipes not found');
        }
        const reasons = [];
        let requiresFlush = false;
        let flushType = undefined;
        // Medicated to non-medicated requires wet cleaning
        if (recipe1.isMedicated() && !recipe2.isMedicated()) {
            requiresFlush = true;
            flushType = 'WetClean';
            reasons.push('Medicated to non-medicated transition requires wet cleaning');
        }
        // Allergen transition requires flush
        if (recipe1.hasAllergens() && recipe2.hasAllergens()) {
            const allergens1 = new Set(recipe1.qa.allergenTags);
            const allergens2 = new Set(recipe2.qa.allergenTags);
            // Check if there are different allergens
            const hasDifferentAllergens = [...allergens1].some(a => !allergens2.has(a)) ||
                [...allergens2].some(a => !allergens1.has(a));
            if (hasDifferentAllergens) {
                requiresFlush = true;
                flushType = flushType || 'Flush';
                reasons.push('Different allergen profiles require flush');
            }
        }
        // Recipe-specific flush requirements
        if (recipe1.requiresFlushAfter()) {
            requiresFlush = true;
            flushType = flushType || 'Flush';
            reasons.push('Previous recipe requires flush after production');
        }
        return {
            compatible: !requiresFlush,
            requiresFlush,
            flushType,
            reasons
        };
    }
}
exports.RecipeServiceImpl = RecipeServiceImpl;
//# sourceMappingURL=recipe-service.js.map