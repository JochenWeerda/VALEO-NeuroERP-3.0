/**
 * VALEO NeuroERP 3.0 - REST SyncJobRepository Repository
 *
 * REST API implementation of SyncJobRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */

import { SyncJobRepository } from '../../core/entities/syncjobrepository';
import { SyncJobRepositoryId } from '@packages/data-models/branded-types';
import { SyncJobRepositoryRepository } from './syncjobrepository-repository';

export class RestSyncJobRepositoryRepository implements SyncJobRepositoryRepository {
  constructor(
    private baseUrl: string,
    private apiToken?: string
  ) {}

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiToken) {
      headers['Authorization'] = `Bearer ${this.apiToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers: { ...headers, ...options.headers }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async findById(id: SyncJobRepositoryId): Promise<SyncJobRepository | null> {
    try {
      const data = await this.request<SyncJobRepository>(`/syncjobrepositorys/${id}`);
      return data;
    } catch (error) {
      if (error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  async findAll(): Promise<SyncJobRepository[]> {
    return this.request<SyncJobRepository[]>(`/syncjobrepositorys`);
  }

  async create(entity: SyncJobRepository): Promise<void> {
    await this.request(`/syncjobrepositorys`, {
      method: 'POST',
      body: JSON.stringify(entity)
    });
  }

  async update(id: SyncJobRepositoryId, entity: SyncJobRepository): Promise<void> {
    await this.request(`/syncjobrepositorys/${id}`, {
      method: 'PUT',
      body: JSON.stringify(entity)
    });
  }

  async delete(id: SyncJobRepositoryId): Promise<void> {
    await this.request(`/syncjobrepositorys/${id}`, {
      method: 'DELETE'
    });
  }

  async exists(id: SyncJobRepositoryId): Promise<boolean> {
    try {
      await this.request(`/syncjobrepositorys/${id}`);
      return true;
    } catch (error) {
      return false;
    }
  }

  async count(): Promise<number> {
    const items = await this.findAll();
    return items.length;
  }

  async findByName(value: string): Promise<SyncJobRepository[]> {
    return this.request<SyncJobRepository[]>(`/syncjobrepositorys?name=${encodeURIComponent(value)}`);
  }
  async findByStatus(value: string): Promise<SyncJobRepository[]> {
    return this.request<SyncJobRepository[]>(`/syncjobrepositorys?status=${encodeURIComponent(value)}`);
  }}
