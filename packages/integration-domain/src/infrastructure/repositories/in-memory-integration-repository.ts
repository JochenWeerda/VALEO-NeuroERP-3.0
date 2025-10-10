/**
 * InMemory Integration Repository Implementation
 */

import { Integration } from '@domain/entities/integration.js';
import type { IntegrationRepository, PaginatedResult, PaginationOptions, Result } from '@domain/interfaces/repositories.js';
import type { IntegrationId } from '@domain/values/integration-id.js';

export class InMemoryIntegrationRepository implements IntegrationRepository {
  private integrations = new Map<string, Integration>();
  private nameIndex = new Map<string, string>();
  private typeIndex = new Map<string, Set<string>>();
  private statusIndex = new Map<string, Set<string>>();
  private tagsIndex = new Map<string, Set<string>>();

  async findById(id: string): Promise<Result<Integration | null, Error>> {
    try {
      const integration = this.integrations.get(id) || null;
      return { success: true, data: integration };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<Integration>, Error>> {
    try {
      const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = options || {};
      
      const integrations = Array.from(this.integrations.values());
      
      // Sort
      integrations.sort((a, b) => {
        const aValue = this.getSortValue(a, sortBy);
        const bValue = this.getSortValue(b, sortBy);
        
        if (sortOrder === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        } else {
          return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        }
      });

      // Paginate
      const offset = (page - 1) * limit;
      const paginatedData = integrations.slice(offset, offset + limit);
      const total = integrations.length;
      const totalPages = Math.ceil(total / limit);

      const result: PaginatedResult<Integration> = {
        data: paginatedData,
        pagination: {
          page,
          limit,
          total,
          totalPages,
          hasNext: page < totalPages,
          hasPrev: page > 1
        }
      };

      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async create(integration: Integration): Promise<Result<Integration, Error>> {
    try {
      const id = integration.id;
      
      // Check for duplicate name
      if (this.nameIndex.has(integration.name)) {
        return { 
          success: false, 
          error: new Error(`Integration with name '${integration.name}' already exists`) 
        };
      }

      // Store integration
      this.integrations.set(id, integration);
      
      // Update indexes
      this.nameIndex.set(integration.name, id);
      this.addToTypeIndex(integration.type, id);
      this.addToStatusIndex(integration.status, id);
      this.addToTagsIndex(integration.tags, id);

      return { success: true, data: integration };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async update(integration: Integration): Promise<Result<Integration, Error>> {
    try {
      const id = integration.id;
      const existing = this.integrations.get(id);
      
      if (!existing) {
        return { 
          success: false, 
          error: new Error(`Integration with id '${id}' not found`) 
        };
      }

      // Check for duplicate name (if name changed)
      if (existing.name !== integration.name && this.nameIndex.has(integration.name)) {
        return { 
          success: false, 
          error: new Error(`Integration with name '${integration.name}' already exists`) 
        };
      }

      // Remove from old indexes
      this.removeFromTypeIndex(existing.type, id);
      this.removeFromStatusIndex(existing.status, id);
      this.removeFromTagsIndex(existing.tags, id);
      if (existing.name !== integration.name) {
        this.nameIndex.delete(existing.name);
      }

      // Update integration
      this.integrations.set(id, integration);

      // Update indexes
      if (existing.name !== integration.name) {
        this.nameIndex.set(integration.name, id);
      }
      this.addToTypeIndex(integration.type, id);
      this.addToStatusIndex(integration.status, id);
      this.addToTagsIndex(integration.tags, id);

      return { success: true, data: integration };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async delete(id: string): Promise<Result<void, Error>> {
    try {
      const integration = this.integrations.get(id);
      
      if (!integration) {
        return { 
          success: false, 
          error: new Error(`Integration with id '${id}' not found`) 
        };
      }

      // Remove from indexes
      this.nameIndex.delete(integration.name);
      this.removeFromTypeIndex(integration.type, id);
      this.removeFromStatusIndex(integration.status, id);
      this.removeFromTagsIndex(integration.tags, id);

      // Remove integration
      this.integrations.delete(id);

      return { success: true, data: undefined };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByName(name: string): Promise<Result<Integration | null, Error>> {
    try {
      const id = this.nameIndex.get(name);
      if (!id) {
        return { success: true, data: null };
      }
      
      const integration = this.integrations.get(id) || null;
      return { success: true, data: integration };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByType(type: string): Promise<Result<Integration[], Error>> {
    try {
      const ids = this.typeIndex.get(type) || new Set();
      const integrations = Array.from(ids)
        .map(id => this.integrations.get(id))
        .filter((integration): integration is Integration => integration !== undefined);
      
      return { success: true, data: integrations };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByStatus(status: string): Promise<Result<Integration[], Error>> {
    try {
      const ids = this.statusIndex.get(status) || new Set();
      const integrations = Array.from(ids)
        .map(id => this.integrations.get(id))
        .filter((integration): integration is Integration => integration !== undefined);
      
      return { success: true, data: integrations };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByTags(tags: string[]): Promise<Result<Integration[], Error>> {
    try {
      const matchingIds = new Set<string>();
      
      for (const tag of tags) {
        const ids = this.tagsIndex.get(tag) || new Set();
        ids.forEach(id => matchingIds.add(id));
      }

      const integrations = Array.from(matchingIds)
        .map(id => this.integrations.get(id))
        .filter((integration): integration is Integration => integration !== undefined);
      
      return { success: true, data: integrations };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findActive(): Promise<Result<Integration[], Error>> {
    try {
      const integrations = Array.from(this.integrations.values())
        .filter(integration => integration.isActive);
      
      return { success: true, data: integrations };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  // Helper methods
  private getSortValue(integration: Integration, sortBy: string): string | number {
    switch (sortBy) {
      case 'name': return integration.name;
      case 'type': return integration.type;
      case 'status': return integration.status;
      case 'createdAt': return integration.createdAt.getTime();
      case 'updatedAt': return integration.updatedAt.getTime();
      default: return integration.createdAt.getTime();
    }
  }

  private addToTypeIndex(type: string, id: string): void {
    if (!this.typeIndex.has(type)) {
      this.typeIndex.set(type, new Set());
    }
    this.typeIndex.get(type)!.add(id);
  }

  private removeFromTypeIndex(type: string, id: string): void {
    const ids = this.typeIndex.get(type);
    if (ids) {
      ids.delete(id);
      if (ids.size === 0) {
        this.typeIndex.delete(type);
      }
    }
  }

  private addToStatusIndex(status: string, id: string): void {
    if (!this.statusIndex.has(status)) {
      this.statusIndex.set(status, new Set());
    }
    this.statusIndex.get(status)!.add(id);
  }

  private removeFromStatusIndex(status: string, id: string): void {
    const ids = this.statusIndex.get(status);
    if (ids) {
      ids.delete(id);
      if (ids.size === 0) {
        this.statusIndex.delete(status);
      }
    }
  }

  private addToTagsIndex(tags: string[], id: string): void {
    for (const tag of tags) {
      if (!this.tagsIndex.has(tag)) {
        this.tagsIndex.set(tag, new Set());
      }
      this.tagsIndex.get(tag)!.add(id);
    }
  }

  private removeFromTagsIndex(tags: string[], id: string): void {
    for (const tag of tags) {
      const ids = this.tagsIndex.get(tag);
      if (ids) {
        ids.delete(id);
        if (ids.size === 0) {
          this.tagsIndex.delete(tag);
        }
      }
    }
  }

  // Test utilities
  clear(): void {
    this.integrations.clear();
    this.nameIndex.clear();
    this.typeIndex.clear();
    this.statusIndex.clear();
    this.tagsIndex.clear();
  }

  getCount(): number {
    return this.integrations.size;
  }
}
