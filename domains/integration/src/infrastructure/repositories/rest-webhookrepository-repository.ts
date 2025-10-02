/**
 * VALEO NeuroERP 3.0 - REST WebhookRepository Repository
 *
 * REST API implementation of WebhookRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */

import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@packages/data-models/branded-types';
import { WebhookRepositoryRepository } from './webhookrepository-repository';

export class RestWebhookRepositoryRepository implements WebhookRepositoryRepository {
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

  async findById(id: WebhookRepositoryId): Promise<WebhookRepository | null> {
    try {
      const data = await this.request<WebhookRepository>(`/webhookrepositorys/${id}`);
      return data;
    } catch (error) {
      if (error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  async findAll(): Promise<WebhookRepository[]> {
    return this.request<WebhookRepository[]>(`/webhookrepositorys`);
  }

  async create(entity: WebhookRepository): Promise<void> {
    await this.request(`/webhookrepositorys`, {
      method: 'POST',
      body: JSON.stringify(entity)
    });
  }

  async update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void> {
    await this.request(`/webhookrepositorys/${id}`, {
      method: 'PUT',
      body: JSON.stringify(entity)
    });
  }

  async delete(id: WebhookRepositoryId): Promise<void> {
    await this.request(`/webhookrepositorys/${id}`, {
      method: 'DELETE'
    });
  }

  async exists(id: WebhookRepositoryId): Promise<boolean> {
    try {
      await this.request(`/webhookrepositorys/${id}`);
      return true;
    } catch (error) {
      return false;
    }
  }

  async count(): Promise<number> {
    const items = await this.findAll();
    return items.length;
  }

  async findByName(value: string): Promise<WebhookRepository[]> {
    return this.request<WebhookRepository[]>(`/webhookrepositorys?name=${encodeURIComponent(value)}`);
  }
  async findByStatus(value: string): Promise<WebhookRepository[]> {
    return this.request<WebhookRepository[]>(`/webhookrepositorys?status=${encodeURIComponent(value)}`);
  }}
