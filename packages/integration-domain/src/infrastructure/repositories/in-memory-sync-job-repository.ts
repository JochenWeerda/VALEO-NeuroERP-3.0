/**
 * InMemory Sync Job Repository Implementation
 */

import { SyncJob } from '@domain/entities/sync-job.js';
import type { PaginatedResult, PaginationOptions, Result, SyncJobRepository } from '@domain/interfaces/repositories.js';

export class InMemorySyncJobRepository implements SyncJobRepository {
  private syncJobs = new Map<string, SyncJob>();
  private integrationIndex = new Map<string, Set<string>>();
  private nameIndex = new Map<string, string>();
  private statusIndex = new Map<string, Set<string>>();
  private nextRunIndex = new Map<number, Set<string>>(); // timestamp -> job IDs

  async findById(id: string): Promise<Result<SyncJob | null, Error>> {
    try {
      const syncJob = this.syncJobs.get(id) || null;
      return { success: true, data: syncJob };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findAll(options?: PaginationOptions): Promise<Result<PaginatedResult<SyncJob>, Error>> {
    try {
      const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = options || {};
      
      const syncJobs = Array.from(this.syncJobs.values());
      
      // Sort
      syncJobs.sort((a, b) => {
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
      const paginatedData = syncJobs.slice(offset, offset + limit);
      const total = syncJobs.length;
      const totalPages = Math.ceil(total / limit);

      const result: PaginatedResult<SyncJob> = {
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

  async create(syncJob: SyncJob): Promise<Result<SyncJob, Error>> {
    try {
      const id = syncJob.id;
      
      // Check for duplicate name within integration
      const existingNameKey = `${syncJob.integrationId}:${syncJob.name}`;
      if (this.nameIndex.has(existingNameKey)) {
        return { 
          success: false, 
          error: new Error(`Sync job with name '${syncJob.name}' already exists for integration '${syncJob.integrationId}'`) 
        };
      }

      // Store sync job
      this.syncJobs.set(id, syncJob);
      
      // Update indexes
      this.nameIndex.set(existingNameKey, id);
      this.addToIntegrationIndex(syncJob.integrationId, id);
      this.addToStatusIndex(syncJob.status, id);
      if (syncJob.nextRun) {
        this.addToNextRunIndex(syncJob.nextRun.getTime(), id);
      }

      return { success: true, data: syncJob };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async update(syncJob: SyncJob): Promise<Result<SyncJob, Error>> {
    try {
      const id = syncJob.id;
      const existing = this.syncJobs.get(id);
      
      if (!existing) {
        return { 
          success: false, 
          error: new Error(`Sync job with id '${id}' not found`) 
        };
      }

      // Check for duplicate name (if name changed)
      const existingNameKey = `${existing.integrationId}:${existing.name}`;
      const newNameKey = `${syncJob.integrationId}:${syncJob.name}`;
      
      if (existingNameKey !== newNameKey && this.nameIndex.has(newNameKey)) {
        return { 
          success: false, 
          error: new Error(`Sync job with name '${syncJob.name}' already exists for integration '${syncJob.integrationId}'`) 
        };
      }

      // Remove from old indexes
      this.removeFromIntegrationIndex(existing.integrationId, id);
      this.removeFromStatusIndex(existing.status, id);
      if (existing.nextRun) {
        this.removeFromNextRunIndex(existing.nextRun.getTime(), id);
      }
      if (existingNameKey !== newNameKey) {
        this.nameIndex.delete(existingNameKey);
      }

      // Update sync job
      this.syncJobs.set(id, syncJob);

      // Update indexes
      if (existingNameKey !== newNameKey) {
        this.nameIndex.set(newNameKey, id);
      }
      this.addToIntegrationIndex(syncJob.integrationId, id);
      this.addToStatusIndex(syncJob.status, id);
      if (syncJob.nextRun) {
        this.addToNextRunIndex(syncJob.nextRun.getTime(), id);
      }

      return { success: true, data: syncJob };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async delete(id: string): Promise<Result<void, Error>> {
    try {
      const syncJob = this.syncJobs.get(id);
      
      if (!syncJob) {
        return { 
          success: false, 
          error: new Error(`Sync job with id '${id}' not found`) 
        };
      }

      // Remove from indexes
      const nameKey = `${syncJob.integrationId}:${syncJob.name}`;
      this.nameIndex.delete(nameKey);
      this.removeFromIntegrationIndex(syncJob.integrationId, id);
      this.removeFromStatusIndex(syncJob.status, id);
      if (syncJob.nextRun) {
        this.removeFromNextRunIndex(syncJob.nextRun.getTime(), id);
      }

      // Remove sync job
      this.syncJobs.delete(id);

      return { success: true, data: undefined };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByIntegrationId(integrationId: string): Promise<Result<SyncJob[], Error>> {
    try {
      const ids = this.integrationIndex.get(integrationId) || new Set();
      const syncJobs = Array.from(ids)
        .map(id => this.syncJobs.get(id))
        .filter((syncJob): syncJob is SyncJob => syncJob !== undefined);
      
      return { success: true, data: syncJobs };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByName(name: string): Promise<Result<SyncJob | null, Error>> {
    try {
      // Find by exact name match (first occurrence)
      for (const [nameKey, id] of this.nameIndex.entries()) {
        if (nameKey.endsWith(`:${name}`)) {
          const syncJob = this.syncJobs.get(id) || null;
          return { success: true, data: syncJob };
        }
      }
      
      return { success: true, data: null };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findByStatus(status: string): Promise<Result<SyncJob[], Error>> {
    try {
      const ids = this.statusIndex.get(status) || new Set();
      const syncJobs = Array.from(ids)
        .map(id => this.syncJobs.get(id))
        .filter((syncJob): syncJob is SyncJob => syncJob !== undefined);
      
      return { success: true, data: syncJobs };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findScheduled(): Promise<Result<SyncJob[], Error>> {
    try {
      const now = Date.now();
      const scheduledJobs: SyncJob[] = [];
      
      // Find all jobs with nextRun <= now and status = 'pending'
      for (const [timestamp, ids] of this.nextRunIndex.entries()) {
        if (timestamp <= now) {
          for (const id of ids) {
            const syncJob = this.syncJobs.get(id);
            if (syncJob && syncJob.status === 'pending' && syncJob.isActive) {
              scheduledJobs.push(syncJob);
            }
          }
        }
      }
      
      return { success: true, data: scheduledJobs };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findRunning(): Promise<Result<SyncJob[], Error>> {
    try {
      const ids = this.statusIndex.get('running') || new Set();
      const syncJobs = Array.from(ids)
        .map(id => this.syncJobs.get(id))
        .filter((syncJob): syncJob is SyncJob => syncJob !== undefined);
      
      return { success: true, data: syncJobs };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  async findFailed(): Promise<Result<SyncJob[], Error>> {
    try {
      const ids = this.statusIndex.get('failed') || new Set();
      const syncJobs = Array.from(ids)
        .map(id => this.syncJobs.get(id))
        .filter((syncJob): syncJob is SyncJob => syncJob !== undefined);
      
      return { success: true, data: syncJobs };
    } catch (error) {
      return { success: false, error: error as Error };
    }
  }

  // Helper methods
  private getSortValue(syncJob: SyncJob, sortBy: string): string | number {
    switch (sortBy) {
      case 'name': return syncJob.name;
      case 'status': return syncJob.status;
      case 'lastRun': return syncJob.lastRun?.getTime() || 0;
      case 'nextRun': return syncJob.nextRun?.getTime() || 0;
      case 'recordsProcessed': return syncJob.recordsProcessed;
      case 'createdAt': return syncJob.createdAt.getTime();
      case 'updatedAt': return syncJob.updatedAt.getTime();
      default: return syncJob.createdAt.getTime();
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

  private addToNextRunIndex(timestamp: number, id: string): void {
    if (!this.nextRunIndex.has(timestamp)) {
      this.nextRunIndex.set(timestamp, new Set());
    }
    this.nextRunIndex.get(timestamp)!.add(id);
  }

  private removeFromNextRunIndex(timestamp: number, id: string): void {
    const ids = this.nextRunIndex.get(timestamp);
    if (ids) {
      ids.delete(id);
      if (ids.size === 0) {
        this.nextRunIndex.delete(timestamp);
      }
    }
  }

  // Test utilities
  clear(): void {
    this.syncJobs.clear();
    this.integrationIndex.clear();
    this.nameIndex.clear();
    this.statusIndex.clear();
    this.nextRunIndex.clear();
  }

  getCount(): number {
    return this.syncJobs.size;
  }
}
