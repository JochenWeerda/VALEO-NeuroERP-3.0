/**
 * PostgreSQL Webhook Repository Implementation
 */
import { Webhook } from '@domain/entities/webhook.js';
export class PostgresWebhookRepository {
    connection;
    constructor(connection) {
        this.connection = connection;
    }
    async findById(id) {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE id = $1', [id]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const webhook = this.mapRowToWebhook(result.rows[0]);
            return { success: true, data: webhook };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findAll(options) {
        try {
            const { page = 1, limit = 10, sortBy = 'created_at', sortOrder = 'DESC' } = options || {};
            const offset = (page - 1) * limit;
            // Get total count
            const countResult = await this.connection.query('SELECT COUNT(*) as total FROM webhooks');
            const total = parseInt(countResult.rows[0].total);
            // Get paginated data
            const result = await this.connection.query(`SELECT * FROM webhooks 
         ORDER BY ${this.mapSortField(sortBy)} ${sortOrder.toUpperCase()}
         LIMIT $1 OFFSET $2`, [limit, offset]);
            const webhooks = result.rows.map(row => this.mapRowToWebhook(row));
            const totalPages = Math.ceil(total / limit);
            const paginatedResult = {
                data: webhooks,
                pagination: {
                    page,
                    limit,
                    total,
                    totalPages,
                    hasNext: page < totalPages,
                    hasPrev: page > 1
                }
            };
            return { success: true, data: paginatedResult };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async create(webhook) {
        try {
            await this.connection.query(`INSERT INTO webhooks (
          id, name, integration_id, config, events, status, is_active, 
          description, tags, created_at, updated_at, created_by, updated_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`, [
                webhook.id,
                webhook.name,
                webhook.integrationId,
                JSON.stringify(webhook.config),
                JSON.stringify(webhook.events),
                webhook.status,
                webhook.isActive,
                webhook.description,
                JSON.stringify(webhook.tags),
                webhook.createdAt,
                webhook.updatedAt,
                webhook.createdBy,
                webhook.updatedBy
            ]);
            return { success: true, data: webhook };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async update(webhook) {
        try {
            await this.connection.query(`UPDATE webhooks SET 
          name = $2, integration_id = $3, config = $4, events = $5, status = $6, 
          is_active = $7, description = $8, tags = $9, updated_at = $10, updated_by = $11
        WHERE id = $1`, [
                webhook.id,
                webhook.name,
                webhook.integrationId,
                JSON.stringify(webhook.config),
                JSON.stringify(webhook.events),
                webhook.status,
                webhook.isActive,
                webhook.description,
                JSON.stringify(webhook.tags),
                webhook.updatedAt,
                webhook.updatedBy
            ]);
            return { success: true, data: webhook };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async delete(id) {
        try {
            await this.connection.query('DELETE FROM webhooks WHERE id = $1', [id]);
            return { success: true, data: undefined };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByIntegrationId(integrationId) {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE integration_id = $1 ORDER BY created_at DESC', [integrationId]);
            const webhooks = result.rows.map(row => this.mapRowToWebhook(row));
            return { success: true, data: webhooks };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByName(name) {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE name = $1 LIMIT 1', [name]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const webhook = this.mapRowToWebhook(result.rows[0]);
            return { success: true, data: webhook };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByEvent(event) {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE events ? $1 ORDER BY created_at DESC', [event]);
            const webhooks = result.rows.map(row => this.mapRowToWebhook(row));
            return { success: true, data: webhooks };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findActive() {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE is_active = true ORDER BY created_at DESC');
            const webhooks = result.rows.map(row => this.mapRowToWebhook(row));
            return { success: true, data: webhooks };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findFailed() {
        try {
            const result = await this.connection.query('SELECT * FROM webhooks WHERE status = $1 ORDER BY created_at DESC', ['error']);
            const webhooks = result.rows.map(row => this.mapRowToWebhook(row));
            return { success: true, data: webhooks };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    mapRowToWebhook(row) {
        return Webhook.fromJSON({
            id: row.id,
            name: row.name,
            integrationId: row.integration_id,
            config: row.config,
            events: row.events,
            status: row.status,
            isActive: row.is_active,
            description: row.description,
            tags: row.tags,
            createdAt: row.created_at,
            updatedAt: row.updated_at,
            createdBy: row.created_by,
            updatedBy: row.updated_by
        });
    }
    mapSortField(field) {
        const fieldMap = {
            'name': 'name',
            'status': 'status',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'integrationId': 'integration_id',
            'created_by': 'created_by',
            'updated_by': 'updated_by'
        };
        return fieldMap[field] || 'created_at';
    }
}
//# sourceMappingURL=postgres-webhook-repository.js.map