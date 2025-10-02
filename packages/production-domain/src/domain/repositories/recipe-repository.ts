/**
 * Recipe Repository Interface for VALEO NeuroERP 3.0 Production Domain
 * Repository interface for recipe management with GMP+/QS compliance
 */

import type { Recipe } from '../entities/recipe';

export interface RecipeFilters {
  status?: 'Active' | 'Archived';
  medicated?: boolean;
  hasAllergens?: boolean;
  requiresFlush?: boolean;
  search?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  filters?: RecipeFilters;
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export interface RecipeRepository {
  // Basic CRUD operations
  save(tenantId: string, recipe: Recipe): Promise<Recipe>;
  findById(tenantId: string, id: string): Promise<Recipe | null>;
  findByCode(tenantId: string, code: string): Promise<Recipe | null>;
  findAll(tenantId: string, filters?: RecipeFilters): Promise<Recipe[]>;
  delete(tenantId: string, id: string): Promise<void>;

  // Pagination support
  findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<Recipe>>;

  // Business queries
  findActive(tenantId: string): Promise<Recipe[]>;
  findArchived(tenantId: string): Promise<Recipe[]>;
  findMedicated(tenantId: string): Promise<Recipe[]>;
  findWithAllergens(tenantId: string): Promise<Recipe[]>;
  findRequiringFlush(tenantId: string): Promise<Recipe[]>;
  findByIngredient(tenantId: string, ingredientSku: string): Promise<Recipe[]>;

  // Version management
  findVersions(tenantId: string, code: string): Promise<Recipe[]>;
  findLatestVersion(tenantId: string, code: string): Promise<Recipe | null>;

  // Bulk operations
  bulkSave(tenantId: string, recipes: Recipe[]): Promise<Recipe[]>;
  bulkDelete(tenantId: string, ids: string[]): Promise<void>;

  // Statistics
  getRecipeCount(tenantId: string, filters?: RecipeFilters): Promise<number>;
  getActiveRecipeCount(tenantId: string): Promise<number>;
  getMedicatedRecipeCount(tenantId: string): Promise<number>;
}

