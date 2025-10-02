/**
 * VALEO NeuroERP 3.0 - In-Memory SyncJobRepository Repository
 *
 * In-memory implementation of SyncJobRepository repository for testing.
 * Stores data in memory with no persistence.
 */

import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@packages/data-models/branded-types';
import { SyncJobRepositoryRepository } from './syncjobrepository-repository';

export class InMemorySyncJobRepositoryRepository implements SyncJobRepositoryRepository {
  private storage = new Map<SyncJobRepositoryId, SyncJobRepository>();

  async findById(id: SyncJobRepositoryId): Promise<SyncJobRepository | null> {
    return this.storage.get(id) || null;
  }

  async findAll(): Promise<SyncJobRepository[]> {
    return Array.from(this.storage.values());
  }

  async create(entity: SyncJobRepository): Promise<void> {
    this.storage.set(entity.id, { ...entity });
  }

  async update(id: SyncJobRepositoryId, entity: SyncJobRepository): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('SyncJobRepository not found: ${id}');
    }
    this.storage.set(id, { ...entity });
  }

  async delete(id: SyncJobRepositoryId): Promise<void> {
    if (!this.storage.has(id)) {
      throw new Error('SyncJobRepository not found: ${id}');
    }
    this.storage.delete(id);
  }

  async exists(id: SyncJobRepositoryId): Promise<boolean> {
    return this.storage.has(id);
  }

  async count(): Promise<number> {
    return this.storage.size;
  }

  async findByName(value: string): Promise<SyncJobRepository[]> {
    return Array.from(this.storage.values())
      .filter(entity => entity.name === value);
  }
  async findByStatus(value: string): Promise<SyncJobRepository[]> {
    return Array.from(this.storage.values())
      .filter(entity => entity.status === value);
  }

  // Test utilities
  clear(): void {
    this.storage.clear();
  }

  seed(data: SyncJobRepository[]): void {
    data.forEach(entity => this.storage.set(entity.id, entity));
  }
}
