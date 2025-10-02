/**
 * PostgreSQL Integration Repository Implementation
 */
import { Integration } from '@domain/entities/integration.js';
export class PostgresIntegrationRepository {
    connection;
    constructor(connection) {
        this.connection = connection;
    }
    async findById(id) {
        try {
            const result = await this.connection.query('SELECT * FROM integrations WHERE id = $1', [id]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const integration = this.mapRowToIntegration(result.rows[0]);
            return { success: true, data: integration };
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
            const countResult = await this.connection.query('SELECT COUNT(*) as total FROM integrations');
            const total = parseInt(countResult.rows[0].total);
            // Get paginated data
            const result = await this.connection.query(`SELECT * FROM integrations 
         ORDER BY ${this.mapSortField(sortBy)} ${sortOrder.toUpperCase()}
         LIMIT $1 OFFSET $2`, [limit, offset]);
            const integrations = result.rows.map(row => this.mapRowToIntegration(row));
            const totalPages = Math.ceil(total / limit);
            const paginatedResult = {
                data: integrations,
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
    async create(integration) {
        try {
            await this.connection.query(`INSERT INTO integrations (
          id, name, type, status, config, description, tags, is_active, 
          created_at, updated_at, created_by, updated_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`, [
                integration.id,
                integration.name,
                integration.type,
                integration.status,
                JSON.stringify(integration.config),
                integration.description,
                JSON.stringify(integration.tags),
                integration.isActive,
                integration.createdAt,
                integration.updatedAt,
                integration.createdBy,
                integration.updatedBy
            ]);
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async update(integration) {
        try {
            await this.connection.query(`UPDATE integrations SET 
          name = $2, type = $3, status = $4, config = $5, description = $6, 
          tags = $7, is_active = $8, updated_at = $9, updated_by = $10
        WHERE id = $1`, [
                integration.id,
                integration.name,
                integration.type,
                integration.status,
                JSON.stringify(integration.config),
                integration.description,
                JSON.stringify(integration.tags),
                integration.isActive,
                integration.updatedAt,
                integration.updatedBy
            ]);
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async delete(id) {
        try {
            await this.connection.query('DELETE FROM integrations WHERE id = $1', [id]);
            return { success: true, data: undefined };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByName(name) {
        try {
            const result = await this.connection.query('SELECT * FROM integrations WHERE name = $1', [name]);
            if (result.rows.length === 0) {
                return { success: true, data: null };
            }
            const integration = this.mapRowToIntegration(result.rows[0]);
            return { success: true, data: integration };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByType(type) {
        try {
            const result = await this.connection.query('SELECT * FROM integrations WHERE type = $1 ORDER BY created_at DESC', [type]);
            const integrations = result.rows.map(row => this.mapRowToIntegration(row));
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByStatus(status) {
        try {
            const result = await this.connection.query('SELECT * FROM integrations WHERE status = $1 ORDER BY created_at DESC', [status]);
            const integrations = result.rows.map(row => this.mapRowToIntegration(row));
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findByTags(tags) {
        try {
            const result = await this.connection.query(`SELECT * FROM integrations 
         WHERE tags ?| $1 
         ORDER BY created_at DESC`, [tags]);
            const integrations = result.rows.map(row => this.mapRowToIntegration(row));
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    async findActive() {
        try {
            const result = await this.connection.query('SELECT * FROM integrations WHERE is_active = true ORDER BY created_at DESC');
            const integrations = result.rows.map(row => this.mapRowToIntegration(row));
            return { success: true, data: integrations };
        }
        catch (error) {
            return { success: false, error: error };
        }
    }
    mapRowToIntegration(row) {
        return Integration.fromJSON({
            id: row.id,
            name: row.name,
            type: row.type,
            status: row.status,
            config: row.config,
            description: row.description,
            tags: row.tags,
            isActive: row.is_active,
            createdAt: row.created_at,
            updatedAt: row.updated_at,
            createdBy: row.created_by,
            updatedBy: row.updated_by
        });
    }
    mapSortField(field) {
        const fieldMap = {
            'name': 'name',
            'type': 'type',
            'status': 'status',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'created_by': 'created_by',
            'updated_by': 'updated_by'
        };
        return fieldMap[field] || 'created_at';
    }
}
//# sourceMappingURL=postgres-integration-repository.js.map