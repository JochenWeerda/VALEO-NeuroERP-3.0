/**
 * Recipe Service for VALEO NeuroERP 3.0 Production Domain
 * Business logic for recipe management with GMP+/QS compliance
 */
import { RecipeEntity } from '../entities/recipe';
import { RecipeRepository } from '../repositories/recipe-repository';
export interface RecipeService {
    createRecipe(input: CreateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateRecipe(id: string, input: UpdateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    archiveRecipe(id: string, reason?: string, tenantId?: string, userId?: string): Promise<RecipeEntity>;
    activateRecipe(id: string, tenantId: string, userId: string): Promise<RecipeEntity>;
    getRecipe(id: string, tenantId: string): Promise<RecipeEntity | null>;
    getRecipeByCode(code: string, tenantId: string): Promise<RecipeEntity | null>;
    listRecipes(filters: RecipeFilters, tenantId: string): Promise<RecipeEntity[]>;
    listActiveRecipes(tenantId: string): Promise<RecipeEntity[]>;
    listMedicatedRecipes(tenantId: string): Promise<RecipeEntity[]>;
    addRecipeLine(id: string, line: AddRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    removeRecipeLine(id: string, ingredientSku: string, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateRecipeLine(id: string, ingredientSku: string, line: UpdateRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateQARequirements(id: string, qa: UpdateQARequirementsInput, tenantId: string, userId: string): Promise<RecipeEntity>;
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
export declare class RecipeServiceImpl implements RecipeService {
    private recipeRepository;
    private eventPublisher;
    constructor(recipeRepository: RecipeRepository, eventPublisher: (event: any) => Promise<void>);
    createRecipe(input: CreateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateRecipe(id: string, input: UpdateRecipeInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    archiveRecipe(id: string, reason?: string, tenantId?: string, userId?: string): Promise<RecipeEntity>;
    activateRecipe(id: string, tenantId: string, userId: string): Promise<RecipeEntity>;
    getRecipe(id: string, tenantId: string): Promise<RecipeEntity | null>;
    getRecipeByCode(code: string, tenantId: string): Promise<RecipeEntity | null>;
    listRecipes(filters: RecipeFilters, tenantId: string): Promise<RecipeEntity[]>;
    listActiveRecipes(tenantId: string): Promise<RecipeEntity[]>;
    listMedicatedRecipes(tenantId: string): Promise<RecipeEntity[]>;
    addRecipeLine(id: string, line: AddRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    removeRecipeLine(id: string, ingredientSku: string, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateRecipeLine(id: string, ingredientSku: string, line: UpdateRecipeLineInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    updateQARequirements(id: string, qa: UpdateQARequirementsInput, tenantId: string, userId: string): Promise<RecipeEntity>;
    validateRecipe(recipe: RecipeEntity): Promise<ValidationResult>;
    checkSequencingCompatibility(recipe1Id: string, recipe2Id: string, tenantId: string): Promise<SequencingResult>;
}
//# sourceMappingURL=recipe-service.d.ts.map