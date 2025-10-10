/**
 * InMemory Webhook Repository Implementation
 */

import { Webhook } from '@domain/entities/webhook.js';
import type { PaginatedResult, PaginationOptions, Result, WebhookRepository } from '@domain/interfaces/repositories.js';

export class InMemoryWebhookRepository implements WebhookRepository {
  private webhooks = new Map<string, Webhook>();
  private integrationIndex = new Map<string, Set<string>>();
  private nameIndex = new Map<string, string>();
  private eventIndex = new Map<string, Set<string>>();
  private statusIndex = new Map<string, Set<string>>();

  async findById(id: string): Promise<Result<Webhook | null, Error>> {
    try {
      const webhook = this.webhooks.get(id) || null;
      return { success: true, data: webhook };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<Webhook>, Error>> {
    try {
      const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = options || {};
      
      const webhooks = Array.from(this.webhooks.values());
      
      // Sort
      webhooks.sort((a, b) => {
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
      const paginatedData = webhooks.slice(offset, offset + limit);
      const total = webhooks.length;
      const totalPages = Math.ceil(total / limit);

      const result: PaginatedResult<Webhook> = {
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

  async create(webhook: Webhook): Promise<Result<Webhook, Error>> {
    try {
      const id = webhook.id;
      
      // Check for duplicate name within integration
      const existingNameKey = `${webhook.integrationId}:${webhook.name}`;
      if (this.nameIndex.has(existingNameKey)) {
        return { 
          success: false, 
          error: new Error(`Webhook with name '${webhook.name}' already exists for integration '${webhook.integrationId}'`) 
        };
      }

      // Store webhook
      this.webhooks.set(id, webhook);
      
      // Update indexes
      this.nameIndex.set(existingNameKey, id);
      this.addToIntegrationIndex(webhook.integrationId, id);
      this.addToEventIndex(webhook.events, id);
      this.addToStatusIndex(webhook.status, id);

      return { success: true, data: webhook };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async update(webhook: Webhook): Promise<Result<Webhook, Error>> {
    try {
      const id = webhook.id;
      const existing = this.webhooks.get(id);
      
      if (!existing) {
        return { 
          success: false, 
          error: new Error(`Webhook with id '${id}' not found`) 
        };
      }

      // Check for duplicate name (if name changed)
      const existingNameKey = `${existing.integrationId}:${existing.name}`;
      const newNameKey = `${webhook.integrationId}:${webhook.name}`;
      
      if (existingNameKey !== newNameKey && this.nameIndex.has(newNameKey)) {
        return { 
          success: false, 
          error: new Error(`Webhook with name '${webhook.name}' already exists for integration '${webhook.integrationId}'`) 
        };
      }

      // Remove from old indexes
      this.removeFromIntegrationIndex(existing.integrationId, id);
      this.removeFromEventIndex(existing.events, id);
      this.removeFromStatusIndex(existing.status, id);
      if (existingNameKey !== newNameKey) {
        this.nameIndex.delete(existingNameKey);
      }

      // Update webhook
      this.webhooks.set(id, webhook);

      // Update indexes
      if (existingNameKey !== newNameKey) {
        this.nameIndex.set(newNameKey, id);
      }
      this.addToIntegrationIndex(webhook.integrationId, id);
      this.addToEventIndex(webhook.events, id);
      this.addToStatusIndex(webhook.status, id);

      return { success: true, data: webhook };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async delete(id: string): Promise<Result<void, Error>> {
    try {
      const webhook = this.webhooks.get(id);
      
      if (!webhook) {
        return { 
          success: false, 
          error: new Error(`Webhook with id '${id}' not found`) 
        };
      }

      // Remove from indexes
      const nameKey = `${webhook.integrationId}:${webhook.name}`;
      this.nameIndex.delete(nameKey);
      this.removeFromIntegrationIndex(webhook.integrationId, id);
      this.removeFromEventIndex(webhook.events, id);
      this.removeFromStatusIndex(webhook.status, id);

      // Remove webhook
      this.webhooks.delete(id);

      return { success: true, data: undefined };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByIntegrationId(integrationId: string): Promise<Result<Webhook[], Error>> {
    try {
      const ids = this.integrationIndex.get(integrationId) || new Set();
      const webhooks = Array.from(ids)
        .map(id => this.webhooks.get(id))
        .filter((webhook): webhook is Webhook => webhook !== undefined);
      
      return { success: true, data: webhooks };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByName(name: string): Promise<Result<Webhook | null, Error>> {
    try {
      // Find by exact name match (first occurrence)
      for (const [nameKey, id] of this.nameIndex.entries()) {
        if (nameKey.endsWith(`:${name}`)) {
          const webhook = this.webhooks.get(id) || null;
          return { success: true, data: webhook };
        }
      }
      
      return { success: true, data: null };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByEvent(event: string): Promise<Result<Webhook[], Error>> {
    try {
      const ids = this.eventIndex.get(event) || new Set();
      const webhooks = Array.from(ids)
        .map(id => this.webhooks.get(id))
        .filter((webhook): webhook is Webhook => webhook !== undefined);
      
      return { success: true, data: webhooks };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findActive(): Promise<Result<Webhook[], Error>> {
    try {
      const webhooks = Array.from(this.webhooks.values())
        .filter(webhook => webhook.isActive);
      
      return { success: true, data: webhooks };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findFailed(): Promise<Result<Webhook[], Error>> {
    try {
      const ids = this.statusIndex.get('error') || new Set();
      const webhooks = Array.from(ids)
        .map(id => this.webhooks.get(id))
        .filter((webhook): webhook is Webhook => webhook !== undefined);
      
      return { success: true, data: webhooks };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  // Helper methods
  private getSortValue(webhook: Webhook, sortBy: string): string | number {
    switch (sortBy) {
      case 'name': return webhook.name;
      case 'status': return webhook.status;
      case 'createdAt': return webhook.createdAt.getTime();
      case 'updatedAt': return webhook.updatedAt.getTime();
      default: return webhook.createdAt.getTime();
    }
  }

  private addToIntegrationIndex(integrationId: string, id: string): void {
    if (!this.integrationIndex.has(integrationId)) {
      this.integrationIndex.set(integrationId, new Set());
    }
    this.integrationIndex.get(integrationId)!.add(id);
  }

  private removeFromIntegrationIndex(integrationId: string, id: string): void {
    const ids = this.integrationIndex.get(integrationId);
    if (ids) {
      ids.delete(id);
      if (ids.size === 0) {
        this.integrationIndex.delete(integrationId);
      }
    }
  }

  private addToEventIndex(events: string[], id: string): void {
    for (const event of events) {
      if (!this.eventIndex.has(event)) {
        this.eventIndex.set(event, new Set());
      }
      this.eventIndex.get(event)!.add(id);
    }
  }

  private removeFromEventIndex(events: string[], id: string): void {
    for (const event of events) {
      const ids = this.eventIndex.get(event);
      if (ids) {
        ids.delete(id);
        if (ids.size === 0) {
          this.eventIndex.delete(event);
        }
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

  // Test utilities
  clear(): void {
    this.webhooks.clear();
    this.integrationIndex.clear();
    this.nameIndex.clear();
    this.eventIndex.clear();
    this.statusIndex.clear();
  }

  getCount(): number {
    return this.webhooks.size;
  }
}
