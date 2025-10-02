/**
 * Recipe Entity for VALEO NeuroERP 3.0 Production Domain
 * Recipe management with GMP+/QS compliance and sequencing rules
 */
import { z } from 'zod';
declare const RecipeLineSchema: z.ZodObject<{
    ingredientSku: z.ZodString;
    inclusionKgOrPercent: z.ZodNumber;
    seqOrder: z.ZodNumber;
    isPremix: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    ingredientSku: string;
    inclusionKgOrPercent: number;
    seqOrder: number;
    isPremix: boolean;
}, {
    ingredientSku: string;
    inclusionKgOrPercent: number;
    seqOrder: number;
    isPremix?: boolean | undefined;
}>;
declare const QARequirementsSchema: z.ZodObject<{
    requiresFlushAfter: z.ZodDefault<z.ZodBoolean>;
    medicated: z.ZodDefault<z.ZodBoolean>;
    allergenTags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    requiresFlushAfter: boolean;
    medicated: boolean;
    allergenTags: string[];
}, {
    requiresFlushAfter?: boolean | undefined;
    medicated?: boolean | undefined;
    allergenTags?: string[] | undefined;
}>;
export declare const RecipeSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    code: z.ZodString;
    name: z.ZodString;
    version: z.ZodDefault<z.ZodNumber>;
    status: z.ZodDefault<z.ZodEnum<["Active", "Archived"]>>;
    targetBatchSizeKg: z.ZodNumber;
    tolerancePercent: z.ZodDefault<z.ZodNumber>;
    lines: z.ZodArray<z.ZodObject<{
        ingredientSku: z.ZodString;
        inclusionKgOrPercent: z.ZodNumber;
        seqOrder: z.ZodNumber;
        isPremix: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        ingredientSku: string;
        inclusionKgOrPercent: number;
        seqOrder: number;
        isPremix: boolean;
    }, {
        ingredientSku: string;
        inclusionKgOrPercent: number;
        seqOrder: number;
        isPremix?: boolean | undefined;
    }>, "many">;
    qa: z.ZodObject<{
        requiresFlushAfter: z.ZodDefault<z.ZodBoolean>;
        medicated: z.ZodDefault<z.ZodBoolean>;
        allergenTags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        requiresFlushAfter: boolean;
        medicated: boolean;
        allergenTags: string[];
    }, {
        requiresFlushAfter?: boolean | undefined;
        medicated?: boolean | undefined;
        allergenTags?: string[] | undefined;
    }>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    code: string;
    status: "Active" | "Archived";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    name: string;
    version: number;
    targetBatchSizeKg: number;
    tolerancePercent: number;
    lines: {
        ingredientSku: string;
        inclusionKgOrPercent: number;
        seqOrder: number;
        isPremix: boolean;
    }[];
    qa: {
        requiresFlushAfter: boolean;
        medicated: boolean;
        allergenTags: string[];
    };
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}, {
    code: string;
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    name: string;
    targetBatchSizeKg: number;
    lines: {
        ingredientSku: string;
        inclusionKgOrPercent: number;
        seqOrder: number;
        isPremix?: boolean | undefined;
    }[];
    qa: {
        requiresFlushAfter?: boolean | undefined;
        medicated?: boolean | undefined;
        allergenTags?: string[] | undefined;
    };
    status?: "Active" | "Archived" | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    version?: number | undefined;
    tolerancePercent?: number | undefined;
}>;
export type Recipe = z.infer<typeof RecipeSchema>;
export type RecipeLine = z.infer<typeof RecipeLineSchema>;
export type QARequirements = z.infer<typeof QARequirementsSchema>;
export declare class RecipeEntity {
    private data;
    constructor(data: Recipe);
    get id(): string;
    get tenantId(): string;
    get code(): string;
    get name(): string;
    get version(): number;
    get status(): string;
    get targetBatchSizeKg(): number;
    get tolerancePercent(): number;
    get lines(): RecipeLine[];
    get qa(): QARequirements;
    get createdAt(): string;
    get updatedAt(): string;
    isActive(): boolean;
    isArchived(): boolean;
    isMedicated(): boolean;
    hasAllergens(): boolean;
    requiresFlushAfter(): boolean;
    getTotalInclusionPercent(): number;
    getTotalInclusionKg(): number;
    getSortedLines(): RecipeLine[];
    getPremixLines(): RecipeLine[];
    getIngredientSkus(): string[];
    private validateBusinessRules;
    archive(updatedBy?: string): RecipeEntity;
    activate(updatedBy?: string): RecipeEntity;
    updateTargetBatchSize(targetBatchSizeKg: number, updatedBy?: string): RecipeEntity;
    updateTolerance(tolerancePercent: number, updatedBy?: string): RecipeEntity;
    addLine(line: Omit<RecipeLine, 'seqOrder'>, updatedBy?: string): RecipeEntity;
    removeLine(ingredientSku: string, updatedBy?: string): RecipeEntity;
    updateQARequirements(qa: Partial<QARequirements>, updatedBy?: string): RecipeEntity;
    toJSON(): Recipe;
    static create(data: Omit<Recipe, 'id' | 'createdAt' | 'updatedAt' | 'version'>): RecipeEntity;
    static fromJSON(data: Recipe): RecipeEntity;
}
export {};
//# sourceMappingURL=recipe.d.ts.map