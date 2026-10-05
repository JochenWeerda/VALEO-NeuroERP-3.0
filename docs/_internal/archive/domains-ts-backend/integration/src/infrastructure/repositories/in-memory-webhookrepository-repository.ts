/**
 * VALEO NeuroERP 3.0 - In-Memory WebhookRepository Repository
 *
 * In-memory implementation of WebhookRepository repository for testing.
 * Stores data in memory with no persistence.
 */

import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@packages/data-models/branded-types';
import { WebhookRepositoryRepository } from './webhookrepository-repository';

export class InMemoryWebhookRepositoryRepository implements WebhookRepositoryRepository {
  private storage = new Map<WebhookRepositoryId, WebhookRepository>();

  async findById(id: WebhookRepositoryId): Promise<WebhookRepository | null> {
    return this.storage.get(id) || null;
  }

  async findAll(): Promise<WebhookRepository[]> {
    return Array.from(this.storage.values());
  }

  async create(entity: WebhookRepository): Promise<void> {
    this.storage.set(entity.id, { ...entity });
  }

  async update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('WebhookRepository not found: ${id}');
    }
    this.storage.set(id, { ...entity });
  }

  async delete(id: WebhookRepositoryId): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('WebhookRepository not found: ${id}');
    }
    this.storage.delete(id);
  }

  async exists(id: WebhookRepositoryId): Promise<boolean> {
    return this.storage.has(id);
  }

  async count(): Promise<number> {
    return this.storage.size;
  }

  async findByName(value: string): Promise<WebhookRepository[]> {
    return Array.from(this.storage.values())
      .filter(entity => entity.name === value);
  }
  async findByStatus(value: string): Promise<WebhookRepository[]> {
    return Array.from(this.storage.values())
      .filter(entity => entity.status === value);
  }

  // Test utilities
  clear(): void {
    this.storage.clear();
  }

  seed(data: WebhookRepository[]): void {
    data.forEach(entity => this.storage.set(entity.id, entity));
  }
}
