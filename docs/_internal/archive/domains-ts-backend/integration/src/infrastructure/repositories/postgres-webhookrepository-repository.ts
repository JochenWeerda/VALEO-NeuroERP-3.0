/**
 * VALEO NeuroERP 3.0 - Postgres WebhookRepository Repository
 *
 * PostgreSQL implementation of WebhookRepository repository.
 * Handles database operations with proper error handling and transactions.
 */

import { WebhookRepository } from '../../core/entities/webhookrepository';
import { WebhookRepositoryId } from '@packages/data-models/branded-types';
import { PostgresConnection } from '@packages/utilities/postgres';
import { WebhookRepositoryRepository } from './webhookrepository-repository';

export class PostgresWebhookRepositoryRepository implements WebhookRepositoryRepository {
  constructor(private db: PostgresConnection) {}

  async findById(id: WebhookRepositoryId): Promise<WebhookRepository | null> {
    const query = 'SELECT * FROM webhookrepositorys WHERE id = $1';
    const result = await this.db.query(query, [id]);

    if (result.rows.length === 0) {
      return null;
    }

    return this.mapRowToEntity(result.rows[0]);
  }

  async findAll(): Promise<WebhookRepository[]> {
    const query = 'SELECT * FROM webhookrepositorys ORDER BY created_at DESC';
    const result = await this.db.query(query);
    return result.rows.map(row => this.mapRowToEntity(row));
  }

  async create(entity: WebhookRepository): Promise<void> {
    const columns = ['id', 'name', 'status', 'createdAt', 'updatedAt'];
    const values = [$1, $2, $3, $4, $5];
    const params = [entity.id, entity.name, entity.status, entity.createdAt, entity.updatedAt];

    const query = `INSERT INTO webhookrepositorys (${columns.join(', ')}) VALUES (${values.join(', ')})`;

    await this.db.query(query, params);
  }

  async update(id: WebhookRepositoryId, entity: WebhookRepository): Promise<void> {
    const setClause = 'name = $2, status = $3, createdAt = $4, updatedAt = $5';
    const params = [id, entity.name, entity.status, entity.createdAt, entity.updatedAt];

    const query = `UPDATE webhookrepositorys SET ${setClause}, updated_at = NOW() WHERE id = $1`;

    const result = await this.db.query(query, params);
    if (result.rowCount === 0) {
      throw new Error('WebhookRepository not found: ${id}');
    }
  }

  async delete(id: WebhookRepositoryId): Promise<void> {
    const query = 'DELETE FROM webhookrepositorys WHERE id = $1';
    const result = await this.db.query(query, [id]);

    if (result.rowCount === 0) {
      throw new Error('WebhookRepository not found: ${id}');
    }
  }

  async exists(id: WebhookRepositoryId): Promise<boolean> {
    const query = 'SELECT 1 FROM webhookrepositorys WHERE id = $1 LIMIT 1';
    const result = await this.db.query(query, [id]);
    return result.rows.length > 0;
  }

  async count(): Promise<number> {
    const query = 'SELECT COUNT(*) as count FROM webhookrepositorys';
    const result = await this.db.query(query);
    return parseInt(result.rows[0].count);
  }

  async findByName(value: string): Promise<WebhookRepository[]> {
    const query = 'SELECT * FROM webhookrepositorys WHERE name = $1 ORDER BY created_at DESC';
    const result = await this.db.query(query, [value]);
    return result.rows.map(row => this.mapRowToEntity(row));
  }
  async findByStatus(value: string): Promise<WebhookRepository[]> {
    const query = 'SELECT * FROM webhookrepositorys WHERE status = $1 ORDER BY created_at DESC';
    const result = await this.db.query(query, [value]);
    return result.rows.map(row => this.mapRowToEntity(row));
  }

  private mapRowToEntity(row: any): WebhookRepository {
    return {
      id: row.id,
      name: row.name,
      status: row.status,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }
}
