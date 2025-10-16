/**
 * Recipe Service for VALEO NeuroERP 3.0 Production Domain
 * Business logic for recipe management with GMP+/QS compliance
 */

import { RecipeEntity } from '../entities/recipe';
import { RecipeRepository } from '../repositories/recipe-repository';
import {
  createRecipeArchivedEvent,
  createRecipeCreatedEvent, 
  createRecipeUpdatedEvent 
} from '../events/event-factories';

// Constants
const DEFAULT_TOLERANCE_PERCENT = 5;
const TOLERANCE_UPPER_LIMIT = 105;
const TOLERANCE_LOWER_LIMIT = 95;

export interface RecipeService {
  // Recipe Management
  createRecipe(input: CreateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
  updateRecipe(id: string, input: UpdateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
  archiveRecipe(id: string, reason?: string, tenantId?: string, userId?: string): Promise<RecipeEntity>;
  activateRecipe(id: string, tenantId: string, userId: string): Promise<RecipeEntity>;
  
  // Recipe Queries
  getRecipe(id: string, tenantId: string): Promise<RecipeEntity | null>;
  getRecipeByCode(code: string, tenantId: string): Promise<RecipeEntity | null>;
  listRecipes(filters: RecipeFilters, tenantId: string): Promise<RecipeEntity[]>;
  listActiveRecipes(tenantId: string): Promise<RecipeEntity[]>;
  listMedicatedRecipes(tenantId: string): Promise<RecipeEntity[]>;
  
  // Recipe Line Management
  addRecipeLine(id: string, line: AddRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
  removeRecipeLine(id: string, ingredientSku: string, tenantId: string, userId: string): Promise<RecipeEntity>;
  updateRecipeLine(id: string, ingredientSku: string, line: UpdateRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
  
  // QA Requirements
  updateQARequirements(id: string, qa: UpdateQARequirementsInput, tenantId: string, userId: string): Promise<RecipeEntity>;
  
  // Validation
  validateRecipe(recipe: RecipeEntity): Promise<ValidationResult>;
  checkSequencingCompatibility(recipe1Id: string, recipe2Id: string, tenantId: string): Promise<SequencingResult>;
}

export interface CreateRecipeInput {
  code: string;
  name: string;
  targetBatchSizeKg: number;
  tolerancePercent?: number;
  lines: CreateRecipeLineInput[];
  qa: CreateQARequirementsInput;
}

export interface CreateRecipeLineInput {
  ingredientSku: string;
  inclusionKgOrPercent: number;
  seqOrder: number;
  isPremix?: boolean;
}

export interface CreateQARequirementsInput {
  requiresFlushAfter?: boolean;
  medicated?: boolean;
  allergenTags?: string[];
}

export interface UpdateRecipeInput {
  name?: string;
  targetBatchSizeKg?: number;
  tolerancePercent?: number;
}

export interface AddRecipeLineInput {
  ingredientSku: string;
  inclusionKgOrPercent: number;
  isPremix?: boolean;
}

export interface UpdateRecipeLineInput {
  inclusionKgOrPercent?: number;
  isPremix?: boolean;
}

export interface UpdateQARequirementsInput {
  requiresFlushAfter?: boolean;
  medicated?: boolean;
  allergenTags?: string[];
}

export interface RecipeFilters {
  status?: 'Active' | 'Archived';
  medicated?: boolean;
  hasAllergens?: boolean;
  requiresFlush?: boolean;
  search?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface SequencingResult {
  compatible: boolean;
  requiresFlush: boolean;
  flushType?: 'DryClean' | 'Vacuum' | 'Flush' | 'WetClean';
  reasons: string[];
}

export class RecipeServiceImpl implements RecipeService {
  constructor(
    private readonly recipeRepository: RecipeRepository,
    private readonly eventPublisher: (event: unknown) => Promise<void>
  ) {}

  async createRecipe(input: CreateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity> {
    // Validate recipe code uniqueness
    const existingRecipe = await this.recipeRepository.findByCode(tenantId, input.code);
    if (existingRecipe) {
      throw new Error(`Recipe with code ${input.code} already exists`);
    }

    // Create recipe entity
    const recipe = RecipeEntity.create({
      tenantId,
      code: input.code,
      name: input.name,
      status: 'Active',
      targetBatchSizeKg: input.targetBatchSizeKg,
      tolerancePercent: (input.tolerancePercent !== undefined && input.tolerancePercent !== null && input.tolerancePercent !== 0) ? input.tolerancePercent : DEFAULT_TOLERANCE_PERCENT,
      lines: input.lines.map(line => ({
        ingredientSku: line.ingredientSku,
        inclusionKgOrPercent: line.inclusionKgOrPercent,
        seqOrder: line.seqOrder,
        isPremix: line.isPremix ?? false
      })),
      qa: {
        requiresFlushAfter: input.qa.requiresFlushAfter ?? false,
        medicated: input.qa.medicated ?? false,
        allergenTags: input.qa.allergenTags ?? []
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
    await this.eventPublisher(createRecipeCreatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      medicated: savedRecipe.qa.medicated,
      allergenTags: savedRecipe.qa.allergenTags
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async updateRecipe(id: string, input: UpdateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const changes: string[] = [];

    // Update fields
    if (input.name != null && input.name !== '' && input.name !== recipe.name) {
      if (input.targetBatchSizeKg !== undefined && input.targetBatchSizeKg !== null) {
        recipe.updateTargetBatchSize(input.targetBatchSizeKg, userId);
      }
      changes.push('name');
    }

    if (input.targetBatchSizeKg != null && input.targetBatchSizeKg !== 0 && input.targetBatchSizeKg !== recipe.targetBatchSizeKg) {
      recipe.updateTargetBatchSize(input.targetBatchSizeKg, userId);
      changes.push('targetBatchSizeKg');
    }

    if (input.tolerancePercent != null && input.tolerancePercent !== 0 && input.tolerancePercent !== recipe.tolerancePercent) {
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
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async archiveRecipe(id: string, reason?: string, tenantId?: string, userId?: string): Promise<RecipeEntity> {
    if (tenantId == null || userId == null) {
      throw new Error('TenantId and userId are required');
    }

    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const archivedRecipe = recipe.archive(userId);

    // Save archived recipe
    const savedRecipe = await this.recipeRepository.save(tenantId, archivedRecipe.toJSON());

    // Emit domain event
    await this.eventPublisher(createRecipeArchivedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      reason
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async activateRecipe(id: string, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const activatedRecipe = recipe.activate(userId);

    // Save activated recipe
    const savedRecipe = await this.recipeRepository.save(tenantId, activatedRecipe.toJSON());

    // Emit domain event
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes: ['status']
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async getRecipe(id: string, tenantId: string): Promise<RecipeEntity | null> {
    const recipe = await this.recipeRepository.findById(tenantId, id);
    return recipe ? RecipeEntity.fromJSON(recipe) : null;
  }

  async getRecipeByCode(code: string, tenantId: string): Promise<RecipeEntity | null> {
    const recipe = await this.recipeRepository.findByCode(tenantId, code);
    return recipe ? RecipeEntity.fromJSON(recipe) : null;
  }

  async listRecipes(filters: RecipeFilters, tenantId: string): Promise<RecipeEntity[]> {
    const recipes = await this.recipeRepository.findAll(tenantId, filters);
    return recipes.map(recipe => RecipeEntity.fromJSON(recipe));
  }

  async listActiveRecipes(tenantId: string): Promise<RecipeEntity[]> {
    const recipes = await this.recipeRepository.findActive(tenantId);
    return recipes.map(recipe => RecipeEntity.fromJSON(recipe));
  }

  async listMedicatedRecipes(tenantId: string): Promise<RecipeEntity[]> {
    const recipes = await this.recipeRepository.findMedicated(tenantId);
    return recipes.map(recipe => RecipeEntity.fromJSON(recipe));
  }

  async addRecipeLine(id: string, line: AddRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const updatedRecipe = recipe.addLine({
      ingredientSku: line.ingredientSku,
      inclusionKgOrPercent: line.inclusionKgOrPercent,
      isPremix: line.isPremix ?? false
    }, userId);

    // Validate updated recipe
    const validation = await this.validateRecipe(updatedRecipe);
    if (!validation.valid) {
      throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
    }

    // Save updated recipe
    const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());

    // Emit domain event
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes: ['lines']
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async removeRecipeLine(id: string, ingredientSku: string, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const updatedRecipe = recipe.removeLine(ingredientSku, userId);

    // Validate updated recipe
    const validation = await this.validateRecipe(updatedRecipe);
    if (!validation.valid) {
      throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
    }

    // Save updated recipe
    const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());

    // Emit domain event
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes: ['lines']
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async updateRecipeLine(id: string, ingredientSku: string, line: UpdateRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    
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
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes: ['lines']
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async updateQARequirements(id: string, qa: UpdateQARequirementsInput, tenantId: string, userId: string): Promise<RecipeEntity> {
    const existingRecipe = await this.recipeRepository.findById(tenantId, id);
    if (!existingRecipe) {
      throw new Error(`Recipe with id ${id} not found`);
    }

    const recipe = RecipeEntity.fromJSON(existingRecipe);
    const updatedRecipe = recipe.updateQARequirements(qa, userId);

    // Validate updated recipe
    const validation = await this.validateRecipe(updatedRecipe);
    if (!validation.valid) {
      throw new Error(`Recipe validation failed: ${validation.errors.join(', ')}`);
    }

    // Save updated recipe
    const savedRecipe = await this.recipeRepository.save(tenantId, updatedRecipe.toJSON());

    // Emit domain event
    await this.eventPublisher(createRecipeUpdatedEvent({
      id: savedRecipe.id,
      code: savedRecipe.code,
      name: savedRecipe.name,
      version: savedRecipe.version,
      changes: ['qa']
    }, tenantId));

    return RecipeEntity.fromJSON(savedRecipe);
  }

  async validateRecipe(recipe: RecipeEntity): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check total inclusion percentage
    const totalPercent = recipe.getTotalInclusionPercent();
    if (totalPercent > TOLERANCE_UPPER_LIMIT) {
      warnings.push(`Total inclusion percentage is ${totalPercent}%, which exceeds ${TOLERANCE_UPPER_LIMIT}%`);
    } else if (totalPercent < TOLERANCE_LOWER_LIMIT) {
      warnings.push(`Total inclusion percentage is ${totalPercent}%, which is below ${TOLERANCE_LOWER_LIMIT}%`);
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

  async checkSequencingCompatibility(recipe1Id: string, recipe2Id: string, tenantId: string): Promise<SequencingResult> {
    const recipe1 = await this.getRecipe(recipe1Id, tenantId);
    const recipe2 = await this.getRecipe(recipe2Id, tenantId);

    if (!recipe1 || !recipe2) {
      throw new Error('One or both recipes not found');
    }

    const reasons: string[] = [];
    let requiresFlush = false;
    let flushType: SequencingResult['flushType'] = undefined;

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
        flushType = flushType ?? 'Flush';
        reasons.push('Different allergen profiles require flush');
      }
    }

    // Recipe-specific flush requirements
    if (recipe1.requiresFlushAfter()) {
      requiresFlush = true;
      flushType = flushType ?? 'Flush';
      reasons.push('Previous recipe requires flush after production');
    }

    return {
      compatible: !requiresFlush,
      requiresFlush,
      flushType: flushType as any,
      reasons
    };
  }
}
