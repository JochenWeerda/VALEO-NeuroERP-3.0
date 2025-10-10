/**
 * Recipe Entity for VALEO NeuroERP 3.0 Production Domain
 * Recipe management with GMP+/QS compliance and sequencing rules
 */

import { z } from 'zod';

// Recipe Line Schema
const RecipeLineSchema = z.object({
  ingredientSku: z.string().min(1).max(100),
  inclusionKgOrPercent: z.number().positive(),
  seqOrder: z.number().int().min(1),
  isPremix: z.boolean().default(false)
});

// QA Requirements Schema
const QARequirementsSchema = z.object({
  requiresFlushAfter: z.boolean().default(false),
  medicated: z.boolean().default(false),
  allergenTags: z.array(z.string()).default([])
});

// Main Recipe Schema
export const RecipeSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  code: z.string().min(1).max(50),
  name: z.string().min(1).max(200),
  version: z.number().int().min(1).default(1),
  status: z.enum(['Active', 'Archived']).default('Active'),
  targetBatchSizeKg: z.number().positive(),
  tolerancePercent: z.number().min(0).max(100).default(5),
  lines: z.array(RecipeLineSchema).min(1),
  qa: QARequirementsSchema,
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Recipe = z.infer<typeof RecipeSchema>;
export type RecipeLine = z.infer<typeof RecipeLineSchema>;
export type QARequirements = z.infer<typeof QARequirementsSchema>;

export class RecipeEntity {
  private readonly data: Recipe;

  constructor(data: Recipe) {
    this.data = RecipeSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get code(): string { return this.data.code; }
  get name(): string { return this.data.name; }
  get version(): number { return this.data.version; }
  get status(): string { return this.data.status; }
  get targetBatchSizeKg(): number { return this.data.targetBatchSizeKg; }
  get tolerancePercent(): number { return this.data.tolerancePercent; }
  get lines(): RecipeLine[] { return [...this.data.lines]; }
  get qa(): QARequirements { return this.data.qa; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  isActive(): boolean {
    return this.data.status === 'Active';
  }

  isArchived(): boolean {
    return this.data.status === 'Archived';
  }

  isMedicated(): boolean {
    return this.data.qa.medicated;
  }

  hasAllergens(): boolean {
    return this.data.qa.allergenTags.length > 0;
  }

  requiresFlushAfter(): boolean {
    return this.data.qa.requiresFlushAfter;
  }

  getTotalInclusionPercent(): number {
    const percentLines = this.data.lines.filter(line => 
      line.inclusionKgOrPercent <= 100 // Assuming values <= 100 are percentages
    );
    return percentLines.reduce((sum, line) => sum + line.inclusionKgOrPercent, 0);
  }

  getTotalInclusionKg(): number {
    const kgLines = this.data.lines.filter(line => 
      line.inclusionKgOrPercent > 100 // Assuming values > 100 are kg amounts
    );
    return kgLines.reduce((sum, line) => sum + line.inclusionKgOrPercent, 0);
  }

  getSortedLines(): RecipeLine[] {
    return [...this.data.lines].sort((a, b) => a.seqOrder - b.seqOrder);
  }

  getPremixLines(): RecipeLine[] {
    return this.data.lines.filter(line => line.isPremix);
  }

  getIngredientSkus(): string[] {
    return this.data.lines.map(line => line.ingredientSku);
  }

  // Validation
  private validateBusinessRules(): void {
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
  archive(updatedBy?: string): RecipeEntity {
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

  activate(updatedBy?: string): RecipeEntity {
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

  updateTargetBatchSize(targetBatchSizeKg: number, updatedBy?: string): RecipeEntity {
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

  updateTolerance(tolerancePercent: number, updatedBy?: string): RecipeEntity {
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

  addLine(line: Omit<RecipeLine, 'seqOrder'>, updatedBy?: string): RecipeEntity {
    const maxSeqOrder = Math.max(...this.data.lines.map(l => l.seqOrder), 0);
    const newLine: RecipeLine = {
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

  removeLine(ingredientSku: string, updatedBy?: string): RecipeEntity {
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

  updateQARequirements(qa: Partial<QARequirements>, updatedBy?: string): RecipeEntity {
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
  toJSON(): Recipe {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<Recipe, 'id' | 'createdAt' | 'updatedAt' | 'version'>): RecipeEntity {
    const now = new Date().toISOString();
    return new RecipeEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now,
      version: 1
    });
  }

  static fromJSON(data: Recipe): RecipeEntity {
    return new RecipeEntity(data);
  }
}

